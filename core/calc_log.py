# =====================================================================
# ЖУРНАЛ РАСЧЕТОВ
#
# Каждый успешный расчет (токарка / сварка) дописывается в текстовый
# файл "расчеты.log" в папке профиля пользователя (рядом с нормами,
# %APPDATA%\CompositCalculator\ на Windows). Файл человекочитаемый —
# его можно открыть Блокнотом. Ошибки записи глушатся: если журнал
# недоступен, программа продолжает работать без него.
# =====================================================================
import os
import sys
from datetime import datetime


def _data_dir():
    """Та же папка профиля, что использует редактор норм."""
    base = os.environ.get("APPDATA") or os.path.join(
        os.path.expanduser("~"), ".config")
    path = os.path.join(base, "CompositCalculator")
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        # Профиль недоступен — кладем рядом с программой
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return path


def log_file_path():
    """Путь к файлу журнала расчетов."""
    return os.path.join(_data_dir(), "расчеты.log")


def _fmt_num(v):
    try:
        num = float(v)
        return str(int(num)) if num == int(num) else str(num)
    except (ValueError, TypeError):
        return str(v)


def _fmt_inputs(inputs):
    """dict исходных данных -> строка 'D=200 d=100 ...' (нулевые опускаем)."""
    parts = []
    for key, val in inputs.items():
        try:
            if float(val) == 0:
                continue
        except (ValueError, TypeError):
            if not val:
                continue
        parts.append(f"{key}={_fmt_num(val)}")
    return " ".join(parts)


def log_calc(kind, title, inputs, result_text):
    """Дописывает один расчет в журнал.

    kind         — 'ТОКАРКА' / 'СВАРКА' (метка раздела)
    title        — название изделия/шва
    inputs       — dict введенных параметров
    result_text  — готовый текст результата (как показан пользователю)
    """
    try:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        indented = "\n".join("    " + line
                             for line in str(result_text).splitlines())
        block = (
            f"===== {stamp} | {kind} =====\n"
            f"Изделие: {title}\n"
            f"Ввод: {_fmt_inputs(inputs)}\n"
            f"Результат:\n{indented}\n\n"
        )
        with open(log_file_path(), "a", encoding="utf-8") as f:
            f.write(block)
    except Exception:
        # Журнал не должен ломать расчет
        pass
