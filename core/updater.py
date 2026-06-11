# =====================================================================
# АВТООБНОВЛЕНИЕ ПРОГРАММЫ ЧЕРЕЗ СЕТЕВУЮ ПАПКУ ЗАВОДА
#
# Как выпустить обновление:
#   1. Увеличьте VERSION ниже (например "1.0.1")
#   2. Соберите exe: pyinstaller main.spec
#   3. Скопируйте собранный exe в сетевую папку UPDATE_DIR
#   4. Там же создайте/обновите файл version.json:
#        {"version": "1.0.1", "file": "main.exe"}
#      ("file" — имя exe-файла в этой же папке)
# Программа при запуске сравнит свою версию с version.json и
# предложит пользователю обновиться в один клик.
# =====================================================================
import json
import os
import shutil
import subprocess
import sys
import tempfile

VERSION = "1.0.9"
UPDATE_DIR = r"\\storage\ФАЙЛООБМЕННИК\Сасин\updates"
VERSION_FILE = "version.json"


def _parse_version(text):
    """'v1.2.3' / '1.2.3' -> (1, 2, 3). Нечисловые части отбрасываются."""
    parts = []
    for chunk in str(text).strip().lstrip("vV").split("."):
        digits = ""
        for ch in chunk:  # берем только ведущие цифры ('0-beta1' -> '0')
            if not ch.isdigit():
                break
            digits += ch
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts) if parts else (0,)


def check_for_update():
    """Возвращает dict {'version', 'exe_path'} если в сетевой папке лежит
    версия новее текущей, иначе None. Папка недоступна (нет сети, нет прав)
    — ошибки глотаются, программа просто работает без проверки."""
    try:
        with open(os.path.join(UPDATE_DIR, VERSION_FILE), encoding="utf-8") as f:
            info = json.load(f)
        remote = str(info.get("version", ""))
        if _parse_version(remote) <= _parse_version(VERSION):
            return None
        exe_name = info.get("file", "")
        exe_path = os.path.join(UPDATE_DIR, exe_name) if exe_name else None
        if not exe_path or not os.path.exists(exe_path):
            return None
        return {"version": remote.lstrip("vV"), "exe_path": exe_path}
    except Exception:
        return None


def download_update(exe_path, progress_cb=None):
    """Копирует новый exe из сетевой папки во временную локальную папку.
    Возвращает путь к локальной копии.
    progress_cb(скопировано_байт, всего_байт) вызывается по ходу копирования."""
    fd, tmp_path = tempfile.mkstemp(suffix=".exe", prefix="composit_update_")
    try:
        total = os.path.getsize(exe_path)
        done = 0
        with open(exe_path, "rb") as src, os.fdopen(fd, "wb") as out:
            while True:
                chunk = src.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
                done += len(chunk)
                if progress_cb:
                    progress_cb(done, total)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise
    return tmp_path


def apply_update(new_exe_path):
    """Запускает батник, который дождется закрытия программы, заменит
    exe новым и перезапустит программу. Вызывающий код должен сразу
    после этого закрыть приложение (view.destroy()).
    Работает только в собранном exe (sys.frozen)."""
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Автообновление доступно только в собранной .exe версии")

    current_exe = sys.executable
    pid = os.getpid()
    bat_path = os.path.join(tempfile.gettempdir(), "composit_update.bat")
    # 1. ждем (не больше ~2 минут), пока процесс старой программы завершится:
    #    tasklist в формате CSV не зависит от языка Windows, ищем PID в кавычках
    # 2. копируем новый exe поверх старого; пока файл занят — copy падает,
    #    повторяем (не больше ~1 минуты)
    # 3. запускаем новую версию и проверяем, что она реально стартовала:
    #    если процесс упал в первые 60 секунд с ошибкой (антивирус еще
    #    сканировал файл и заблокировал загрузку DLL) — ждем и пробуем
    #    снова, до 3 попыток
    bat = f"""@echo off
chcp 65001 >nul
set tries=0
:wait_exit
set /a tries+=1
if %tries% gtr 60 goto copy_start
tasklist /FI "PID eq {pid}" /FO CSV /NH 2>nul | findstr /C:"\\"{pid}\\"" >nul
if errorlevel 1 goto copy_start
ping 127.0.0.1 -n 3 >nul
goto wait_exit
:copy_start
set tries=0
:copy_loop
set /a tries+=1
copy /y "{new_exe_path}" "{current_exe}" >nul 2>&1
if not errorlevel 1 goto run
if %tries% gtr 30 goto run
ping 127.0.0.1 -n 3 >nul
goto copy_loop
:run
del "{new_exe_path}" >nul 2>&1
set attempt=0
:start_try
set /a attempt+=1
ping 127.0.0.1 -n 6 >nul
call :seconds t0
start /wait "" "{current_exe}"
set rc=%errorlevel%
if "%rc%"=="0" goto done
call :seconds t1
set /a elapsed=t1-t0
if %elapsed% lss 0 set /a elapsed+=86400
if %elapsed% gtr 60 goto done
if %attempt% lss 3 goto start_try
goto done
:seconds
for /f "tokens=1-3 delims=:,." %%a in ("%TIME: =0%") do set /a %1=(1%%a %% 100)*3600+(1%%b %% 100)*60+(1%%c %% 100)
exit /b
:done
del "%~f0"
"""
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat)

    # ВАЖНО: только CREATE_NO_WINDOW. Комбинация с DETACHED_PROCESS
    # недопустима — из-за нее у пользователей появлялось черное окно консоли.
    subprocess.Popen(
        ["cmd", "/c", bat_path],
        creationflags=subprocess.CREATE_NO_WINDOW,
        close_fds=True,
    )
