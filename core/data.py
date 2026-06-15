WELD_DATA = {
    'C4': ([0.8, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8],
            [3.5, 3.6, 3.9, 4.1, 4.2, 5.5, 5.8, 7.7, 8.8, 9.8, 10.8]),
    'C15': ([8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60],
            [3.9, 4.3, 4.7, 5.6, 6.7, 8.0, 9.3, 11.4, 12.9, 14.8, 16.9, 19.6, 21.9, 22.7, 25.7, 28.2, 30.8, 34.1, 36.9, 40.4, 43.5, 46.6, 50.5, 53.9, 58.0, 61.6, 65.9, 69.7]),
    'C17': ([3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60], 
            [2.9, 3.8, 4.3, 5.2, 6.2, 7.8, 8.9, 10.1, 13.0, 16.8, 21.6, 26.5, 32.3, 35.8, 41.5, 48.3, 55.5, 63.2, 66.2, 74.0, 82.3, 91.0, 100.0, 110.0, 119.8, 130.0, 141.2, 152.1, 164.1, 175.8, 188.4, 200.9, 214.3]),
    'C54': ([3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 25], 
            [6.7, 9.6, 10.1, 12.1, 14.2, 17.0, 21.9, 26.1, 32.2, 40.4, 46.9, 60.2, 71.2, 76.9, 88.2, 94.4]),
    'T3':  ([1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30], 
            [1.4, 1.6, 1.9, 2.3, 2.7, 3.7, 4.2, 7.3, 9.2, 11.3, 13.6, 16.7, 20.5, 26.4, 33.6, 41.5, 46.4, 53.4, 59.9, 64.4, 72.2, 77.8]),
    'У18': ([2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26],
            [2.2, 2.8, 3.3, 4.8, 5.4, 7.6, 9.4, 11.4, 13.5, 16.4, 19.8, 25.7, 32.2, 38.7, 46.2, 53.9, 63.2, 73.1]),
    'У19': ([4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 25], 
            [14.1, 15.0, 19.0, 22.4, 26.7, 30.4, 34.9, 49.2, 61.4, 75.1, 88.8, 103.9, 109.6, 124.8, 131.8]),
    'У4':  ([0.8, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8], 
            [3.2, 4.4, 5.7, 7.1, 8.4, 10.0, 13.3, 15.8, 19.2, 23.0, 30.5]),
    'У6':  ([3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60], 
            [3.2, 4.1, 4.5, 5.4, 6.4, 8.8, 10.5, 12.3, 15.3, 20.4, 25.4, 31.6, 37.7, 41.6, 48.8, 56.6, 64.8, 73.5, 76.7, 85.7, 95.0, 105.4, 115.6, 126.2, 137.9, 149.3, 161.8, 174.7, 187.4, 201.1, 215.2, 229.8, 244.7]),
    'У8':  ([6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60], 
            [3.2, 3.6, 4.0, 4.5, 4.9, 5.6, 6.5, 7.4, 9.0, 11.4, 12.4, 14.2, 16.1, 18.9, 21.1, 21.9, 24.1, 27.2, 29.7, 32.3, 35.8, 38.6, 42.3, 45.4, 49.3, 52.6, 56.0, 60.2, 64.6, 68.3])
}

CHAMFER_DATA = [
    {'max_s': 12, 'x': [0, 10], 'y': [1.77, 1.77]},
    {'max_s': 52, 'x': [14, 16, 20, 25, 30, 36, 40, 45, 50], 'y': [4.64, 4.11, 2.92, 4.36, 3.63, 3.11, 3.24, 2.62, 2.35]},
    {'max_s': 73, 'x': [55, 60, 65, 70], 'y': [1.67, 1.40, 1.33, 1.25]},
    {'max_s': 999, 'x': [75, 80, 85, 90, 95, 100, 105, 110], 'y': [1.05, 0.95, 0.83, 0.70, 0.67, 0.59, 0.53, 0.46]}
]

# Матрица оборотов шпинделя — точная копия листа 'Лист1' (Таблица3) Excel.
# Общая ось диаметров 50..2000 мм; 0 — станок не работает на этом диаметре
# (в Excel ячейка пуста, и операция на таком диаметре дает 0 времени).
TURNING_AXIS = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450, 1500, 1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000]

TURNING_DATA = {
    '16K20': (TURNING_AXIS, [630, 630, 315, 160, 160, 125, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    'Кнуб(1M63)': (TURNING_AXIS, [0, 190, 190, 190, 190, 190, 140, 106, 106, 106, 80, 80, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    'Дип 500(1M65)': (TURNING_AXIS, [0, 0, 0, 0, 107, 107, 90, 90, 90, 76, 76, 76, 76, 63, 55, 45, 38, 38, 38, 38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    'VL-1600': (TURNING_AXIS, [0, 0, 0, 0, 0, 0, 0, 0, 0, 50, 50, 50, 50, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 0, 0, 0, 0, 0, 0, 0, 0]),
    'CK5126': (TURNING_AXIS, [0, 0, 0, 0, 0, 0, 0, 0, 0, 54, 54, 54, 54, 54, 54, 54, 54, 43, 43, 43, 43, 43, 43, 43, 36, 36, 36, 36, 36, 36, 36, 36, 36, 24, 24, 24, 24, 24, 24, 24]),
    '0Л52': (TURNING_AXIS, [6130, 6230, 3315, 1460, 1560, 1625] + [0]*34),
}

# Особенности формул эталонного Excel (лист "Получение данных для расчета"):
# в B58 (скорость 2-й внутренней проточки) и B67 (скорость канавы) приближенный
# HLOOKUP по названию станка попадает в СОСЕДНЮЮ колонку таблицы оборотов:
# '16к20' находит колонку '0Л52', 'CK5126' находит '1М65'.
APPROX_RPM_COL = {
    '16K20': '0Л52',
    'Кнуб(1M63)': 'Кнуб(1M63)',
    'Дип 500(1M65)': 'Дип 500(1M65)',
    'VL-1600': 'VL-1600',
    'CK5126': 'Дип 500(1M65)',
}
# Аналогично для таблицы подач ('Типы станков'): CK5126 берет подачи 1М65
APPROX_FEED_COL = {
    '16K20': '16K20',
    'Кнуб(1M63)': 'Кнуб(1M63)',
    'Дип 500(1M65)': 'Дип 500(1M65)',
    'VL-1600': 'VL-1600',
    'CK5126': 'Дип 500(1M65)',
}

# Выбор основного станка по готовому диаметру D (формула Excel B78):
# до 250 — 16к20, до 500 — 1М63, до 800 — 1М65, до 2500 — CK5126.
# VL-1600 в эталонной таблице основным станком не выбирается (только альтернатива).
RANGES_DATA = {
    '16K20': (0, 250),
    'Кнуб(1M63)': (251, 500),
    'Дип 500(1M65)': (501, 800),
    'CK5126': (801, 2500)
}

# Формат: [siem_long, siem_transverse, feed_turn, feed_face, chamfer_speed]
# siem_long     — глубина резания продольное точение (мм)
# siem_transverse — глубина резания поперечное точение / торцовка (мм)
# feed_turn     — подача продольная (мм/об)
# feed_face     — подача поперечная (мм/об)
# chamfer_speed — скорость резания фасок (мм/мин)
FEEDRATE_DATA = {
        '16K20':         [3, 3, 0.15, 0.25, 500],
        'Кнуб(1M63)':    [5, 3, 0.19, 0.31, 500],
        'Дип 500(1M65)': [8, 5, 0.3,  0.6,  500],
        'VL-1600':       [5, 4, 0,    0,    500],  # подачи в таблице не заданы
        'CK5126':        [6, 6, 0.5,  0.5,  500],
    }

# Ширина канавочного резца по станкам (лист "Типы станков", строка 12).
# 0 — в таблице не задана: канава на этом станке не считается (как в Excel)
GROOVE_INSERT_WIDTH = {
    '16K20': 4,
    'Кнуб(1M63)': 4,
    'Дип 500(1M65)': 6,
    'VL-1600': 0,
    'CK5126': 0,
}
# Подача на канаву по станкам (лист "Типы станков", строка 13); 0 — не задана
GROOVE_FEED = {
    '16K20': 0.1,
    'Кнуб(1M63)': 0.1,
    'Дип 500(1M65)': 0.1,
    'VL-1600': 0,
    'CK5126': 0,
}

AWC_S = [0, 9, 19, 29, 39, 49, 59, 69, 79]

# Точная копия листа "Кооф вспом работ" (Таблица6) эталонного Excel
AWC_DATA = {
    0:   [1.8,        1.728,      1.655,      1.5825,     1,          1.4375,     1.365,      1.2925,     1.22],
    100: [1.75428572, 1.68178572, 1.60928572, 1.53678572, 1.46428572, 1.39178572, 1.31928572, 1.24678572, 1.17428572],
    200: [1.70857144, 1.63607144, 1.56357144, 1.49107144, 1.41857144, 1.34607144, 1.27357144, 1.20107144, 1.12857144],
    300: [1.66285716, 1.59035716, 1.51785716, 1.275,      1.37285716, 1.30035716, 1.22785716, 1.15535716, 1.08285716],
    400: [1.61714288, 1.54464288, 1.47214288, 0.91,       1.32714288, 1.25464288, 1.18214288, 1.10964288, 1.03714288],
    500: [1.5714286,  1.4989286,  1.4264286,  1.75,       1.281,      1.2089286,  1.1364286,  1.0639286,  1.03],
    600: [1.52571432, 1.45321432, 1.38071432, 1.30821432, 2.14,       1.16321432, 1.09071432, 1.01821432, 1.02],
    700: [1.48000004, 1.40750004, 1.33500004, 1.26250004, 2.04,       1.11750004, 1.04500004, 1.03,       1.01],
    800: [1.43428576, 1.36178576, 1.28928576, 1.21678576, 1.14428576, 1.07178576, 0.99928576, 0.95553574, 0.9494898]
}

# Время на установку и снятие детали (в минутах)
# В зависимости от веса детали
CHAMFER_SETUP_TIME = {
    "manual": 1.2,    # до 15 кг (вручную)
    "crane_light": 3.5, # 15-50 кг (кран)
    "crane_heavy": 7.0  # выше 50 кг (кран + выверка)
}

# Коэффициент на сложность/состояние оборудования
# 1.0 - новое, 1.2 - среднее, 1.4 - тяжелые условия
CHAMFER_COMPLEXITY_K = 1.2

ADMISSION_DATA = {
    0: [6],
    20: [8],
    30: [10],
    60: [12]
}

SHEET_PRODUCTS = [
        "swivel", "rotspher", "compensator", "forming",
        "adapter", "weldring", "weldflange", "weldingtnf",
    ]


# =====================================================================
# ЗАГРУЗКА НОРМ ИЗ ВНЕШНЕГО ФАЙЛА "нормы.json"
# Технолог-нормировщик может править нормы без изменения кода:
# файл "нормы.json" лежит рядом с программой (или в корне проекта).
# Если файл отсутствует или какая-то секция в нем не заполнена —
# используются значения по умолчанию, заданные выше в этом модуле.
# =====================================================================
import json as _json
import os as _os
import sys as _sys
import base64 as _base64
import hashlib as _hashlib
import hmac as _hmac
import zlib as _zlib

def _base_dir():
    if getattr(_sys, 'frozen', False):
        return _os.path.dirname(_sys.executable)
    return _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

def _data_dir():
    """Служебные файлы программы (нормы, настройки) хранятся не рядом с exe,
    а в скрытой папке профиля пользователя — рядом с программой ничего
    не появляется."""
    base = _os.environ.get("APPDATA") or _os.path.join(
        _os.path.expanduser("~"), ".config")
    path = _os.path.join(base, "CompositCalculator")
    try:
        _os.makedirs(path, exist_ok=True)
    except OSError:
        return _base_dir()  # профиль недоступен — запасной вариант
    return path

def _norms_file_path():
    """Общие (заводские) нормы — синхронизируются с сетевой папкой."""
    return _os.path.join(_data_dir(), "нормы.json")

def _my_norms_file_path():
    """Личные нормы редактора — существуют только на этом компьютере."""
    return _os.path.join(_data_dir(), "мои_нормы.json")

def _settings_file_path():
    return _os.path.join(_data_dir(), "настройки_норм.json")

def _migrate_old_files():
    """Переносит файлы, которые раньше лежали рядом с программой,
    в папку профиля; рядом с exe они удаляются."""
    for name in ("нормы.json", "мои_нормы.json", "настройки_норм.json"):
        old = _os.path.join(_base_dir(), name)
        new = _os.path.join(_data_dir(), name)
        if old == new or not _os.path.exists(old):
            continue
        try:
            if not _os.path.exists(new):
                with open(old, 'rb') as f:
                    content = f.read()
                with open(new, 'wb') as f:
                    f.write(content)
            # удаляем старый файл только в собранной программе,
            # чтобы в режиме разработки не трогать файлы проекта
            if getattr(_sys, 'frozen', False):
                _os.remove(old)
        except OSError:
            pass

# Источники норм для расчетов
SOURCE_SHARED = "общие"   # заводской файл нормы.json (синхронизируется с сетью)
SOURCE_MY = "мои"         # личный файл мои_нормы.json (только этот компьютер)

def get_active_source():
    """Какие нормы сейчас используются в расчетах: 'общие' или 'мои'."""
    try:
        with open(_settings_file_path(), encoding='utf-8') as f:
            src = _json.load(f).get("активные_нормы", SOURCE_SHARED)
        return src if src in (SOURCE_SHARED, SOURCE_MY) else SOURCE_SHARED
    except Exception:
        return SOURCE_SHARED

def set_active_source(source):
    """Переключает, по каким нормам ведутся расчеты, и сразу применяет их."""
    if source not in (SOURCE_SHARED, SOURCE_MY):
        raise ValueError(f"Неизвестный источник норм: {source}")
    with open(_settings_file_path(), 'w', encoding='utf-8') as f:
        _json.dump({"активные_нормы": source}, f, ensure_ascii=False, indent=2)
    _load_external_norms()

def _active_norms_path():
    if get_active_source() == SOURCE_MY and _os.path.exists(_my_norms_file_path()):
        return _my_norms_file_path()
    return _norms_file_path()

def _to_float(val):
    try:
        return float(val or 0)
    except (ValueError, TypeError):
        return 0.0

def _to_num_keys(d):
    """Ключи JSON всегда строки — возвращаем числовые ключи для таблиц норм."""
    out = {}
    for k, v in d.items():
        try:
            num = float(k)
            out[int(num) if num == int(num) else num] = v
        except (ValueError, TypeError):
            out[k] = v
    return out

# Пароль для входа в редактор норм внутри программы
NORMS_PASSWORD = "composit"

# Именованные ключи режимов резания (порядок соответствует FEEDRATE_DATA)
NORMS_FEED_KEYS = ["глубина_продольная_мм", "глубина_поперечная_мм",
                   "подача_продольная_мм_об", "подача_поперечная_мм_об",
                   "скорость_фасок_мм_мин"]

# Пояснения к секциям файла норм (используются и в файле, и в редакторе)
NORMS_HELP = {
    "ОБОРОТЫ_ШПИНДЕЛЯ": "Обороты шпинделя (об/мин) по станкам: ключ — диаметр детали (мм), значение — обороты. 0 = станок не работает на этом диаметре.",
    "ДИАПАЗОНЫ_ДИАМЕТРОВ": "Диапазон диаметров детали [мин, макс] (мм), по которому выбирается основной станок.",
    "РЕЖИМЫ_РЕЗАНИЯ": "По станкам: глубина резания продольная/поперечная (мм за проход), подача продольная/поперечная (мм/об), скорость резания фасок (мм/мин).",
    "ШИРИНА_КАНАВОЧНОГО_РЕЗЦА": "Ширина канавочного резца по станкам (мм); 0 = не задана, канава не считается.",
    "ПОДАЧА_НА_КАНАВУ": "Подача при точении канавы по станкам (мм/об); 0 = не задана.",
    "КОЭФФИЦИЕНТ_ВСПОМОГАТЕЛЬНЫХ_РАБОТ": "Ключ верхнего уровня — диаметр заготовки D1 (мм), вложенный ключ — толщина листа S от (мм), значение — коэффициент.",
    "ПРИПУСК_НА_ДИАМЕТР": "Припуск на диаметр заготовки (мм): ключ — толщина листа от (мм), значение — припуск (мм).",
    "НОРМЫ_СВАРКИ": "По типам шва (ГОСТ): толщина S (мм) и норма времени сварки (мин на 1м шва) "
                    "для каждой точки таблицы. Списки должны быть одной длины и идти по возрастанию.",
    "ФАСКИ_СВАРКА": "Скорость снятия фасок (мм/мин) в зависимости от толщины S (мм). "
                    "Каждый диапазон действует до своей 'макс. толщины'.",
}

def norms_as_dict():
    """Текущие нормы в наглядном виде (структура файла нормы.json).
    Используется редактором норм и при создании файла с нуля."""
    turning = {}
    for machine, (diams, rpms) in TURNING_DATA.items():
        turning[machine] = {str(int(d)) if float(d) == int(d) else str(d): r
                            for d, r in zip(diams, rpms)}
    feed = {machine: dict(zip(NORMS_FEED_KEYS, vals))
            for machine, vals in FEEDRATE_DATA.items()}
    awc = {}
    for d1, vals in AWC_DATA.items():
        awc[str(d1)] = {str(s): v for s, v in zip(AWC_S, vals)}
    admission = {str(k): (v[0] if isinstance(v, list) else v)
                 for k, v in ADMISSION_DATA.items()}
    weld = {gost: {"толщина_мм": list(th), "норма_мин_м": list(tm)}
            for gost, (th, tm) in WELD_DATA.items()}
    chamfer = [{"макс_толщина_мм": cfg["max_s"], "толщина_мм": list(cfg["x"]),
                "норма_мм_мин": list(cfg["y"])} for cfg in CHAMFER_DATA]
    return {
        "ОБОРОТЫ_ШПИНДЕЛЯ": turning,
        "ДИАПАЗОНЫ_ДИАМЕТРОВ": {k: list(v) for k, v in RANGES_DATA.items()},
        "РЕЖИМЫ_РЕЗАНИЯ": feed,
        "ШИРИНА_КАНАВОЧНОГО_РЕЗЦА": dict(GROOVE_INSERT_WIDTH),
        "ПОДАЧА_НА_КАНАВУ": dict(GROOVE_FEED),
        "КОЭФФИЦИЕНТ_ВСПОМОГАТЕЛЬНЫХ_РАБОТ": awc,
        "ПРИПУСК_НА_ДИАМЕТР": admission,
        "НОРМЫ_СВАРКИ": weld,
        "ФАСКИ_СВАРКА": chamfer,
    }

# =====================================================================
# ЗАЩИЩЕННЫЙ ФОРМАТ ФАЙЛОВ НОРМ
# Нормы можно менять только через редактор внутри программы:
# содержимое файла кодируется и подписывается контрольной подписью.
# Файл, измененный вручную (Блокнотом и т.п.), не пройдет проверку
# подписи и будет проигнорирован.
# =====================================================================
_NORMS_KEY = b"composit-calculator-norms-protection-v1"
_NORMS_FORMAT = "composit-norms-1"

def _pack_norms(norms):
    """Нормы -> защищенные байты файла (сжатие + base64 + HMAC-подпись)."""
    raw = _json.dumps(norms, ensure_ascii=False).encode('utf-8')
    blob = _base64.b64encode(_zlib.compress(raw)).decode('ascii')
    sig = _hmac.new(_NORMS_KEY, blob.encode('ascii'), _hashlib.sha256).hexdigest()
    wrapper = {
        "формат": _NORMS_FORMAT,
        "ВНИМАНИЕ": "Файл создан программой расчета. Не редактируйте его вручную — "
                    "изменения не пройдут проверку подписи и файл будет отклонен. "
                    "Нормы меняются только в редакторе внутри программы.",
        "данные": blob,
        "подпись": sig,
    }
    return _json.dumps(wrapper, ensure_ascii=False, indent=2).encode('utf-8')

def _unpack_norms(data):
    """Байты файла -> нормы. None, если файл изменен вне программы
    (подпись не сошлась) или испорчен."""
    try:
        wrapper = _json.loads(data.decode('utf-8'))
        if wrapper.get("формат") != _NORMS_FORMAT:
            return None
        blob = wrapper["данные"].encode('ascii')
        expected = _hmac.new(_NORMS_KEY, blob, _hashlib.sha256).hexdigest()
        if not _hmac.compare_digest(expected, str(wrapper.get("подпись", ""))):
            return None
        return _json.loads(_zlib.decompress(_base64.b64decode(blob)).decode('utf-8'))
    except Exception:
        return None

def _read_norms_file(path):
    """Читает файл норм (защищенный или старый открытый формат).
    Возвращает словарь секций или None. Старый открытый файл при чтении
    сразу пересохраняется в защищенном виде."""
    try:
        with open(path, 'rb') as f:
            data = f.read()
    except OSError:
        return None
    norms = _unpack_norms(data)
    if norms is not None:
        return {k: v for k, v in norms.items() if not k.startswith("_")}
    # старый формат (обычный JSON) — принимаем один раз и защищаем
    try:
        legacy = _json.loads(data.decode('utf-8'))
        if not isinstance(legacy, dict) or "формат" in legacy:
            return None
        norms = {k: v for k, v in legacy.items() if not k.startswith("_")}
        try:
            with open(path, 'wb') as f:
                f.write(_pack_norms(norms))
        except OSError:
            pass
        return norms
    except Exception:
        return None

def load_norms_file(path):
    """Читает файл норм и возвращает его секции (без _СПРАВКА), либо None."""
    return _read_norms_file(path)

def my_norms_as_dict():
    """Личные нормы для редактора: содержимое мои_нормы.json, а если его
    еще нет — копия текущих общих норм (как стартовая точка для правок)."""
    return load_norms_file(_my_norms_file_path()) or norms_as_dict()

def save_norms(norms):
    """Сохраняет нормы в ЛИЧНЫЙ файл (мои_нормы.json) на этом компьютере.
    Общий заводской файл не трогается. Если в расчетах выбраны 'мои' нормы —
    они применяются сразу. Разослать на все компьютеры — publish_norms()."""
    with open(_my_norms_file_path(), 'wb') as f:
        f.write(_pack_norms(norms))
    _load_external_norms()

def publish_norms():
    """Копирует ЛИЧНЫЙ файл норм в сетевую папку обновлений — оттуда он
    разойдется на все компьютеры как общие нормы (они подтягивают его при
    старте). Возвращает True при успехе."""
    try:
        from core.updater import UPDATE_DIR
        with open(_my_norms_file_path(), 'rb') as f:
            text = f.read()
        with open(_os.path.join(UPDATE_DIR, "нормы.json"), 'wb') as f:
            f.write(text)
        # локальный общий файл тоже обновляем сразу, не дожидаясь перезапуска
        with open(_norms_file_path(), 'wb') as f:
            f.write(text)
        _load_external_norms()
        return True
    except Exception:
        return False

def _sync_norms_from_server():
    """Подтягивает нормы из сетевой папки обновлений (если она доступна
    и файл там отличается от локального). Так нормы централизованно
    'обновляются вместе с exe' на всех компьютерах завода."""
    try:
        from core.updater import UPDATE_DIR
        remote = _os.path.join(UPDATE_DIR, "нормы.json")
        if not _os.path.exists(remote):
            return
        with open(remote, 'rb') as f:
            remote_bytes = f.read()
        # принимаем только файл с верной подписью: битый или измененный
        # вручную (вне программы) файл не копируем
        if _unpack_norms(remote_bytes) is None:
            return
        local = _norms_file_path()
        if _os.path.exists(local):
            with open(local, 'rb') as f:
                if f.read() == remote_bytes:
                    return
        with open(local, 'wb') as f:
            f.write(remote_bytes)
    except Exception:
        pass  # нет сети/прав — работаем на локальных нормах

def _load_external_norms():
    path = _active_norms_path()
    if not _os.path.exists(path):
        return
    norms = _read_norms_file(path)
    if norms is None:
        print(f"ВНИМАНИЕ: файл норм '{path}' испорчен или изменен вне программы. "
              f"Используются нормы по умолчанию.")
        return

    g = globals()
    feed_keys = NORMS_FEED_KEYS
    try:
        # ОБОРОТЫ_ШПИНДЕЛЯ: {станок: {диаметр: обороты}} -> {станок: ([диаметры], [обороты])}
        if isinstance(norms.get("ОБОРОТЫ_ШПИНДЕЛЯ"), dict) and norms["ОБОРОТЫ_ШПИНДЕЛЯ"]:
            turning = {}
            for machine, table in norms["ОБОРОТЫ_ШПИНДЕЛЯ"].items():
                pairs = sorted(((float(d), r) for d, r in table.items()), key=lambda x: x[0])
                diams = [int(d) if d == int(d) else d for d, _ in pairs]
                rpms = [r for _, r in pairs]
                turning[machine] = (diams, rpms)
            g["TURNING_DATA"] = turning

        # ДИАПАЗОНЫ_ДИАМЕТРОВ: {станок: [мин, макс]} -> {станок: (мин, макс)}
        if isinstance(norms.get("ДИАПАЗОНЫ_ДИАМЕТРОВ"), dict) and norms["ДИАПАЗОНЫ_ДИАМЕТРОВ"]:
            g["RANGES_DATA"] = {k: tuple(v) for k, v in norms["ДИАПАЗОНЫ_ДИАМЕТРОВ"].items()}

        # РЕЖИМЫ_РЕЗАНИЯ: {станок: {именованные ключи}} -> {станок: [позиционный список]}
        if isinstance(norms.get("РЕЖИМЫ_РЕЗАНИЯ"), dict) and norms["РЕЖИМЫ_РЕЗАНИЯ"]:
            feed = {}
            for machine, params in norms["РЕЖИМЫ_РЕЗАНИЯ"].items():
                feed[machine] = [_to_float(params.get(key, 0)) for key in feed_keys]
            g["FEEDRATE_DATA"] = feed

        if isinstance(norms.get("ШИРИНА_КАНАВОЧНОГО_РЕЗЦА"), dict) and norms["ШИРИНА_КАНАВОЧНОГО_РЕЗЦА"]:
            g["GROOVE_INSERT_WIDTH"] = norms["ШИРИНА_КАНАВОЧНОГО_РЕЗЦА"]

        if isinstance(norms.get("ПОДАЧА_НА_КАНАВУ"), dict) and norms["ПОДАЧА_НА_КАНАВУ"]:
            g["GROOVE_FEED"] = norms["ПОДАЧА_НА_КАНАВУ"]

        # КОЭФФИЦИЕНТ_ВСПОМОГАТЕЛЬНЫХ_РАБОТ: {D1: {S: коэфф}} -> AWC_S + AWC_DATA{D1: [...]}
        if isinstance(norms.get("КОЭФФИЦИЕНТ_ВСПОМОГАТЕЛЬНЫХ_РАБОТ"), dict) and norms["КОЭФФИЦИЕНТ_ВСПОМОГАТЕЛЬНЫХ_РАБОТ"]:
            awc_raw = norms["КОЭФФИЦИЕНТ_ВСПОМОГАТЕЛЬНЫХ_РАБОТ"]
            first_table = next(iter(awc_raw.values()))
            awc_s = sorted(float(s) for s in first_table.keys())
            g["AWC_S"] = [int(s) if s == int(s) else s for s in awc_s]
            awc_data = {}
            for d1, table in awc_raw.items():
                d1_num = float(d1)
                d1_key = int(d1_num) if d1_num == int(d1_num) else d1_num
                awc_data[d1_key] = [table[s_key] for s_key in table]
            g["AWC_DATA"] = awc_data

        # ПРИПУСК_НА_ДИАМЕТР: {S: припуск} -> ADMISSION_DATA{S: припуск}
        if isinstance(norms.get("ПРИПУСК_НА_ДИАМЕТР"), dict) and norms["ПРИПУСК_НА_ДИАМЕТР"]:
            g["ADMISSION_DATA"] = _to_num_keys(norms["ПРИПУСК_НА_ДИАМЕТР"])

        # НОРМЫ_СВАРКИ: {ГОСТ: {толщина_мм: [...], норма_мин_м: [...]}} -> WELD_DATA{ГОСТ: ([...],[...])}
        if isinstance(norms.get("НОРМЫ_СВАРКИ"), dict) and norms["НОРМЫ_СВАРКИ"]:
            weld = {}
            for gost, table in norms["НОРМЫ_СВАРКИ"].items():
                th = [_to_float(x) for x in table.get("толщина_мм", [])]
                tm = [_to_float(x) for x in table.get("норма_мин_м", [])]
                weld[gost] = (th, tm)
            g["WELD_DATA"] = weld

        # ФАСКИ_СВАРКА: [{макс_толщина_мм, толщина_мм:[...], норма_мм_мин:[...]}] -> CHAMFER_DATA
        if isinstance(norms.get("ФАСКИ_СВАРКА"), list) and norms["ФАСКИ_СВАРКА"]:
            chamfer = []
            for cfg in norms["ФАСКИ_СВАРКА"]:
                chamfer.append({
                    "max_s": _to_float(cfg.get("макс_толщина_мм", 0)),
                    "x": [_to_float(x) for x in cfg.get("толщина_мм", [])],
                    "y": [_to_float(x) for x in cfg.get("норма_мм_мин", [])],
                })
            g["CHAMFER_DATA"] = chamfer
    except Exception as e:
        print(f"ВНИМАНИЕ: ошибка применения норм из '{path}' ({e}). "
              f"Часть норм может остаться по умолчанию.")


_migrate_old_files()
_sync_norms_from_server()
_load_external_norms()