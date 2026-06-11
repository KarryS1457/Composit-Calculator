# =====================================================================
# АВТООБНОВЛЕНИЕ ПРОГРАММЫ ЧЕРЕЗ GITHUB RELEASES
#
# Как выпустить обновление:
#   1. Увеличьте VERSION ниже (например "1.0.1")
#   2. Соберите exe: pyinstaller main.spec
#   3. На GitHub создайте Release с тегом v1.0.1 (совпадает с VERSION)
#      и прикрепите собранный exe как Asset
# Программа при запуске сравнит свою версию с последним релизом и
# предложит пользователю обновиться в один клик.
# =====================================================================
import json
import os
import subprocess
import sys
import tempfile
import urllib.request

VERSION = "1.0.0"
GITHUB_REPO = "KarryS1457/Composit-Calculator"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def _parse_version(text):
    """'v1.2.3' / '1.2.3' -> (1, 2, 3). Нечисловые части отбрасываются."""
    parts = []
    for chunk in text.strip().lstrip("vV").split("."):
        digits = ""
        for ch in chunk:  # берем только ведущие цифры ('0-beta1' -> '0')
            if not ch.isdigit():
                break
            digits += ch
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts) if parts else (0,)


def check_for_update(timeout=10):
    """Возвращает dict {'version', 'exe_url', 'page_url'} если на GitHub
    есть релиз новее текущей версии, иначе None. Ошибки сети глотаются
    (нет интернета — программа просто работает без проверки)."""
    try:
        req = urllib.request.Request(
            API_URL, headers={"Accept": "application/vnd.github+json",
                              "User-Agent": "Composit-Calculator"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            release = json.load(resp)
    except Exception:
        return None

    remote = release.get("tag_name") or release.get("name") or ""
    if _parse_version(remote) <= _parse_version(VERSION):
        return None

    exe_url = None
    for asset in release.get("assets", []):
        if asset.get("name", "").lower().endswith(".exe"):
            exe_url = asset.get("browser_download_url")
            break

    return {
        "version": remote.lstrip("vV"),
        "exe_url": exe_url,
        "page_url": release.get("html_url", f"https://github.com/{GITHUB_REPO}/releases"),
    }


def download_update(exe_url, progress_cb=None):
    """Скачивает новый exe во временную папку. Возвращает путь к файлу.
    progress_cb(скачано_байт, всего_байт) вызывается по ходу загрузки."""
    req = urllib.request.Request(
        exe_url, headers={"User-Agent": "Composit-Calculator"})
    fd, tmp_path = tempfile.mkstemp(suffix=".exe", prefix="composit_update_")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp, os.fdopen(fd, "wb") as out:
            total = int(resp.headers.get("Content-Length") or 0)
            done = 0
            while True:
                chunk = resp.read(65536)
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
    bat_path = os.path.join(tempfile.gettempdir(), "composit_update.bat")
    # ping = пауза 2 сек; цикл повторяет copy, пока exe не освободится
    bat = f"""@echo off
chcp 65001 >nul
:wait
ping 127.0.0.1 -n 3 >nul
copy /y "{new_exe_path}" "{current_exe}" >nul 2>&1
if errorlevel 1 goto wait
del "{new_exe_path}" >nul 2>&1
start "" "{current_exe}"
del "%~f0"
"""
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat)

    subprocess.Popen(
        ["cmd", "/c", bat_path],
        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
        close_fds=True,
    )
