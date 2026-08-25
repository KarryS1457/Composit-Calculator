# =====================================================================
# СПИСОК ИЗМЕНЕНИЙ ПО ВЕРСИЯМ
#
# Показывается пользователю ОДИН РАЗ — при первом запуске после обновления.
# Программа помнит последнюю показанную версию в файле профиля и выводит
# все записи новее нее.
#
# САМ ТЕКСТ ЛЕЖИТ НЕ ЗДЕСЬ, а в файле "изменения.txt" рядом с программой:
# это обычный текст, его правит технолог в блокноте, без Python. Формат и
# правила описаны в шапке самого файла.
#
# Порядок поиска файла:
#   1. рядом с exe (или в корне проекта при запуске из исходников) —
#      так можно проверить правки, не пересобирая программу;
#   2. внутри собранной программы (туда его кладут main.spec и beta.spec).
# =====================================================================
import json
import os
import re
import sys

from core.updater import VERSION, _parse_version

CHANGELOG_FILE = "изменения.txt"

# ; комментарий | ## версия и дата | # раздел | - пункт
_RE_VERSION = re.compile(r"^##\s*(\S+)\s*(?:[—–-]\s*)?(.*)$")
_RE_SECTION = re.compile(r"^#\s*(.+)$")
_RE_ITEM = re.compile(r"^[-*]\s*(.+)$")


def _candidate_paths():
    """Где искать файл: сначала правка рядом с программой, потом свой."""
    paths = []
    if getattr(sys, "frozen", False):
        paths.append(os.path.join(os.path.dirname(sys.executable), CHANGELOG_FILE))
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            paths.append(os.path.join(meipass, CHANGELOG_FILE))
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        paths.append(os.path.join(root, CHANGELOG_FILE))
    return paths


def changelog_path():
    """Файл, который реально будет прочитан, или None."""
    for p in _candidate_paths():
        if os.path.exists(p):
            return p
    return None


def parse(text):
    """Текст файла -> [(версия, дата, [(раздел, [пункты])])].

    Формат намеренно прощающий: любая строка вне разметки просто
    приклеивается к предыдущему пункту, поэтому длинный пункт можно
    переносить, а лишние пустые строки ничего не ломают."""
    versions = []
    section = None
    items = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(";"):
            continue

        m = _RE_VERSION.match(line)
        if m:
            versions.append((m.group(1), m.group(2).strip(), []))
            section = items = None
            continue

        if not versions:
            continue  # текст до первого "##" игнорируем

        m = _RE_SECTION.match(line)
        if m:
            section = m.group(1).strip()
            items = []
            versions[-1][2].append((section, items))
            continue

        m = _RE_ITEM.match(line)
        if m:
            if items is None:                 # пункт без раздела
                items = []
                versions[-1][2].append(("", items))
            items.append(m.group(1).strip())
            continue

        if items:                             # перенос длинного пункта
            items[-1] = f"{items[-1]} {line}"

    # разделы без единого пункта не показываем
    return [(v, d, [(s, it) for s, it in blocks if it])
            for v, d, blocks in versions]


def load():
    """Разобранный список изменений. Любая ошибка -> пустой список:
    список изменений не должен мешать программе запускаться."""
    path = changelog_path()
    if not path:
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return parse(f.read())
    except Exception:
        return []


def _seen_file():
    """Файл, где хранится последняя показанная версия. У беты он свой —
    иначе показ в одной сборке гасил бы список в другой."""
    from core.data import _beta_suffix, _data_dir
    return os.path.join(_data_dir(), f"показанная_версия{_beta_suffix()}.json")


def get_seen_version():
    try:
        with open(_seen_file(), encoding="utf-8") as f:
            return str(json.load(f).get("версия", ""))
    except Exception:
        return ""


def set_seen_version(version=VERSION):
    try:
        with open(_seen_file(), "w", encoding="utf-8") as f:
            json.dump({"версия": str(version)}, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def pending_entries(current=VERSION, seen=None, history=None):
    """Записи, которые пользователь еще не видел: все версии новее
    последней показанной, сверху вниз.

    Если отметки нет, показываем все записи вплоть до текущей версии.
    Это главный случай, а не редкий: сам механизм появился в 1.2.0, и у
    всех, кто обновляется с 1.1.8, отметки заведомо нет — трактовать ее
    отсутствие как "первая установка, показывать нечего" значило бы, что
    список изменений не увидит вообще никто."""
    history = load() if history is None else history
    seen = get_seen_version() if seen is None else seen
    cur = _parse_version(current)
    low = _parse_version(seen) if seen else None
    return [(v, d, blocks) for v, d, blocks in history
            if _parse_version(v) <= cur and (low is None or low < _parse_version(v))]
