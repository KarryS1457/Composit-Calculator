# =====================================================================
# ЖУРНАЛ РАСЧЕТОВ
#
# Каждый успешный расчет (токарка / сварка) дописывается в текстовый
# журнал. Основное место хранения — ОБЩАЯ СЕТЕВАЯ ПАПКА рядом с папкой
# обновлений (updater.LOG_DIR): туда стекаются логи со ВСЕХ компьютеров
# пользователей программы. Чтобы одновременная запись с разных машин не
# конфликтовала (дописывание в один файл по сети ненадежно), у каждого
# ПК свой файл с именем "имяПК_пользователь.log".
#
# Если сетевая папка недоступна (нет сети/прав), запись уходит в локальный
# профиль пользователя (%APPDATA%\CompositCalculator\расчеты.log), чтобы
# журнал не терялся. Любые ошибки записи глушатся — журнал не должен
# ломать расчет.
# =====================================================================
import os
import re
import sys
import getpass
import socket
from datetime import datetime

import core.updater as updater


def _local_data_dir():
    """Локальная папка профиля (запасной вариант, как у редактора норм)."""
    base = os.environ.get("APPDATA") or os.path.join(
        os.path.expanduser("~"), ".config")
    path = os.path.join(base, "CompositCalculator")
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return path


def _safe_name(text):
    """Оставляем только безопасные для имени файла символы."""
    cleaned = re.sub(r"[^\w.-]", "_", str(text), flags=re.UNICODE)
    return cleaned.strip("_") or "unknown"


def _pc_id():
    """Идентификатор компьютера/пользователя для имени файла и заголовка."""
    try:
        host = socket.gethostname()
    except Exception:
        host = "PC"
    try:
        user = getpass.getuser()
    except Exception:
        user = "user"
    return _safe_name(host), _safe_name(user)


def _shared_log_path():
    """Файл этого ПК в общей сетевой папке. Создает папку 'логи' при
    необходимости. Бросает OSError, если папка недоступна."""
    host, user = _pc_id()
    os.makedirs(updater.logs_dir(), exist_ok=True)
    return os.path.join(updater.logs_dir(), f"{host}_{user}.log")


def _local_log_path():
    """Запасной локальный файл журнала."""
    return os.path.join(_local_data_dir(), "расчеты.log")


def log_file_path():
    """Актуальный путь журнала: общий сетевой, если доступен, иначе локальный."""
    try:
        return _shared_log_path()
    except OSError:
        return _local_log_path()


def _fmt_num(v):
    try:
        num = float(v)
        return str(int(num)) if num == int(num) else str(num)
    except (ValueError, TypeError):
        return str(v)


def _fmt_inputs(inputs):
    """dict исходных данных -> строка 'D=200 d=100 ...' (нулевые опускаем)."""
    parts = []
    for key, val in (inputs or {}).items():
        try:
            if float(val) == 0:
                continue
        except (ValueError, TypeError):
            if not val:
                continue
        parts.append(f"{key}={_fmt_num(val)}")
    return " ".join(parts)


def log_calc(kind, title, inputs, result_text, steps=None):
    """Дописывает один расчет в журнал.

    kind         — 'ТОКАРКА' / 'СВАРКА' (метка раздела)
    title        — название изделия/шва
    inputs       — dict введенных параметров
    result_text  — готовый текст результата (как показан пользователю)
    steps        — список строк с пошаговым ходом расчета (необязательно)
    """
    try:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        host, user = _pc_id()
        indented = "\n".join("    " + line
                             for line in str(result_text).splitlines())
        block = (
            f"===== {stamp} | {kind} | ПК: {host}/{user} =====\n"
            f"Изделие: {title}\n"
            f"Ввод: {_fmt_inputs(inputs)}\n"
        )
        if steps:
            steps_text = "\n".join("    " + str(line) for line in steps)
            block += f"Ход расчета:\n{steps_text}\n"
        block += f"Результат:\n{indented}\n\n"

        # Сначала пробуем общую сетевую папку, при неудаче — локальный профиль
        try:
            path = _shared_log_path()
        except OSError:
            path = _local_log_path()

        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(block)
        except OSError:
            # Сетевой файл вдруг стал недоступен между проверкой и записью —
            # дублируем в локальный, чтобы запись не пропала
            with open(_local_log_path(), "a", encoding="utf-8") as f:
                f.write(block)
    except Exception:
        # Журнал не должен ломать расчет
        pass
