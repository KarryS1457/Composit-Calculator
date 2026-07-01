# =====================================================================
# УНИВЕРСАЛЬНЫЙ ЖУРНАЛ РАСЧЕТОВ / СОБЫТИЙ  (standalone-модуль)
# =====================================================================
# Самодостаточный модуль без внешних зависимостей — можно просто
# скопировать файл в любой проект. Дописывает записи в текстовый лог
# в человекочитаемом виде (Блокнот) и/или в формате JSON Lines для
# машинной обработки.
#
# Быстрый старт
# -------------
#   from calc_logger import CalcLogger
#
#   log = CalcLogger(app_name="My3DApp")          # -> %APPDATA%/My3DApp/ или ~/.config/My3DApp/
#   log.log(section="ЭКСПОРТ",
#           title="Модель кронштейна",
#           inputs={"file": "bracket.step", "units": "mm", "faces": 128},
#           result="Объём=42.7 см³, площадь=311 см², масса=0.33 кг")
#
# Или без создания объекта — глобальный логгер по умолчанию:
#   import calc_logger
#   calc_logger.configure(app_name="My3DApp")
#   calc_logger.log("ИМПОРТ", "деталь.stl", {"tris": 24000}, "OK, водонепроницаема")
#
# Куда пишется файл
# ----------------
#   * По умолчанию — в папку профиля пользователя:
#       Windows : %APPDATA%\<app_name>\<filename>
#       *nix    : ~/.config/<app_name>/<filename>
#   * Можно задать точный путь: CalcLogger(log_path="C:/logs/calc.log")
#   * Можно писать рядом с программой: CalcLogger(app_name="X", next_to_program=True)
#
# Форматы
# -------
#   * text (по умолчанию) — читаемые блоки с рамкой из даты/времени.
#   * jsonl               — по одной JSON-записи на строку (для парсинга).
#   * both                — и то, и другое (два файла: .log и .jsonl).
#
# Надежность
# ----------
#   Любые ошибки записи глушатся: журнал никогда не должен ронять
#   основную программу. При желании передайте raise_errors=True.
# =====================================================================

import os
import sys
import json
import threading
from datetime import datetime

__all__ = ["CalcLogger", "configure", "log", "get_logger", "log_path"]


class CalcLogger:
    """Потокобезопасный дописывающий логгер расчетов/событий."""

    def __init__(self, app_name="CalcLog", filename="расчеты.log",
                 log_path=None, log_dir=None, next_to_program=False,
                 fmt="text", raise_errors=False, max_bytes=0, encoding="utf-8"):
        """
        app_name        имя папки в профиле пользователя (если путь не задан явно)
        filename        имя файла журнала (для fmt='jsonl' расширение меняется на .jsonl)
        log_path        точный путь к файлу — переопределяет всё остальное
        log_dir         каталог для файла (имя берётся из filename)
        next_to_program класть журнал рядом с exe/скриптом, а не в профиль
        fmt             'text' | 'jsonl' | 'both'
        raise_errors    True — пробрасывать ошибки записи (по умолчанию глушим)
        max_bytes       если >0 и файл превысил размер — старый переименуется в *.1
        encoding        кодировка файла
        """
        self.app_name = app_name
        self.filename = filename
        self.fmt = fmt
        self.raise_errors = raise_errors
        self.max_bytes = max_bytes
        self.encoding = encoding
        self._lock = threading.Lock()

        if log_path:
            self._path = os.path.abspath(log_path)
        else:
            directory = log_dir or self._default_dir(app_name, next_to_program)
            self._path = os.path.join(directory, filename)

    # ---- расположение файла -------------------------------------------------
    @staticmethod
    def _program_dir():
        if getattr(sys, "frozen", False):          # собранный exe (PyInstaller)
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def _default_dir(self, app_name, next_to_program):
        if next_to_program:
            return self._program_dir()
        base = os.environ.get("APPDATA") or os.path.join(
            os.path.expanduser("~"), ".config")
        path = os.path.join(base, app_name)
        try:
            os.makedirs(path, exist_ok=True)
        except OSError:
            return self._program_dir()             # профиль недоступен — запасной вариант
        return path

    def path(self, fmt=None):
        """Путь к файлу журнала (для 'jsonl' — с расширением .jsonl)."""
        fmt = fmt or self.fmt
        if fmt == "jsonl":
            root, _ = os.path.splitext(self._path)
            return root + ".jsonl"
        return self._path

    # ---- форматирование -----------------------------------------------------
    @staticmethod
    def _fmt_num(v):
        try:
            num = float(v)
            return str(int(num)) if num == int(num) else str(num)
        except (ValueError, TypeError):
            return str(v)

    @classmethod
    def _fmt_inputs(cls, inputs):
        """dict -> 'a=1 b=2' (нулевые/пустые значения опускаются)."""
        if not inputs:
            return ""
        parts = []
        for key, val in inputs.items():
            try:
                if float(val) == 0:
                    continue
            except (ValueError, TypeError):
                if val in (None, "", [], {}):
                    continue
            parts.append(f"{key}={cls._fmt_num(val)}")
        return " ".join(parts)

    def _text_block(self, stamp, section, title, inputs, result):
        indented = "\n".join("    " + line
                             for line in str(result).splitlines()) if result else ""
        block = f"===== {stamp} | {section} =====\n"
        if title:
            block += f"Изделие: {title}\n"
        block += f"Ввод: {self._fmt_inputs(inputs)}\n"
        if result is not None:
            block += f"Результат:\n{indented}\n"
        return block + "\n"

    # ---- запись -------------------------------------------------------------
    def _rotate_if_needed(self, path):
        if self.max_bytes and os.path.exists(path):
            try:
                if os.path.getsize(path) > self.max_bytes:
                    os.replace(path, path + ".1")
            except OSError:
                pass

    def _write(self, path, data):
        self._rotate_if_needed(path)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "a", encoding=self.encoding) as f:
            f.write(data)

    def log(self, section="", title="", inputs=None, result=None, **extra):
        """Дописать одну запись в журнал.

        section  метка раздела (например 'ЭКСПОРТ', 'ИМПОРТ', 'РАСЧЕТ')
        title    название объекта/детали/модели
        inputs   dict входных параметров
        result   готовый текст результата (или любой объект со str())
        **extra  любые доп. поля — попадают в JSON-запись
        """
        try:
            now = datetime.now()
            stamp = now.strftime("%Y-%m-%d %H:%M:%S")
            with self._lock:
                if self.fmt in ("text", "both"):
                    self._write(self.path("text"),
                                self._text_block(stamp, section, title, inputs, result))
                if self.fmt in ("jsonl", "both"):
                    record = {
                        "time": now.isoformat(timespec="seconds"),
                        "section": section,
                        "title": title,
                        "inputs": inputs or {},
                        "result": None if result is None else str(result),
                    }
                    if extra:
                        record.update(extra)
                    self._write(self.path("jsonl"),
                                json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            if self.raise_errors:
                raise
            # иначе — журнал не должен ломать основную программу


# =====================================================================
# Глобальный логгер по умолчанию — для использования без создания объекта
# =====================================================================
_default = CalcLogger()


def configure(**kwargs):
    """Переконфигурировать глобальный логгер по умолчанию.
    Пример: calc_logger.configure(app_name='My3DApp', fmt='both')"""
    global _default
    _default = CalcLogger(**kwargs)
    return _default


def get_logger():
    """Вернуть текущий глобальный логгер."""
    return _default


def log(section="", title="", inputs=None, result=None, **extra):
    """Записать через глобальный логгер."""
    return _default.log(section, title, inputs, result, **extra)


def log_path(fmt=None):
    """Путь к файлу глобального логгера."""
    return _default.path(fmt)


# =====================================================================
# Мини-демо: python calc_logger.py
# =====================================================================
if __name__ == "__main__":
    demo = CalcLogger(app_name="CalcLoggerDemo", fmt="both",
                      filename="demo.log")
    demo.log(
        section="РАСЧЕТ 3D",
        title="Кронштейн L-образный",
        inputs={"file": "bracket.step", "units": "mm",
                "faces": 128, "solids": 1, "empty": 0},
        result="Объём = 42.7 см³\nПлощадь = 311 см²\nМасса (сталь) = 0.335 кг",
        source="step-import", ok=True,
    )
    print("Текстовый журнал:", demo.path("text"))
    print("JSON-журнал:     ", demo.path("jsonl"))
    print("\n--- text ---")
    print(open(demo.path("text"), encoding="utf-8").read())
    print("--- jsonl ---")
    print(open(demo.path("jsonl"), encoding="utf-8").read())
