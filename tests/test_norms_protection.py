"""Тест: защита и синхронизация файлов норм (core/data.py).

Проверяет, что нормы нельзя менять в обход программы и что синхронизация
с сетевой папкой не теряет и не принимает поддельные данные:
  - упаковка/распаковка норм с контрольной подписью (HMAC)
  - файл, измененный вручную, отклоняется
  - старый «открытый» JSON читается один раз и пересохраняется защищенным
  - save_norms пишет только в личный файл, общий не трогает
  - publish_norms раскладывает подписанный файл в сетевую папку
  - _sync_norms_from_server тянет только корректно подписанный файл
Запуск: python tests/test_norms_protection.py
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core.data as data
import core.updater as updater

passed = 0
failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK   {name}")
    else:
        failed += 1
        print(f"  FAIL {name}")


def run():
    # Изолируем все файлы во временные папки: своя для локальных файлов
    # программы и своя — под «сетевую папку» завода.
    work = tempfile.mkdtemp(prefix="norms_local_")
    net = tempfile.mkdtemp(prefix="norms_net_")
    orig_data_dir = data._data_dir
    orig_update_dir = updater.UPDATE_DIR
    data._data_dir = lambda: work
    updater.UPDATE_DIR = net

    try:
        my = data._my_norms_file_path()
        shared = data._norms_file_path()
        net_file = os.path.join(net, "нормы.json")

        # --- 1. Упаковка/распаковка с подписью ---
        norms = data.norms_as_dict()
        norms["ПОДАЧА_НА_КАНАВУ"]["16K20"] = 0.777
        packed = data._pack_norms(norms)
        wrapper = json.loads(packed.decode("utf-8"))
        check("упакованный файл имеет формат и подпись",
              wrapper.get("формат") == "composit-norms-1" and "подпись" in wrapper)
        check("сырые значения не лежат открытым текстом",
              b"0.777" not in packed)
        check("распаковка восстанавливает данные",
              data._unpack_norms(packed)["ПОДАЧА_НА_КАНАВУ"]["16K20"] == 0.777)

        # --- 2. Подделанная подпись / содержимое отклоняются ---
        tampered = dict(wrapper)
        tampered["данные"] = tampered["данные"][:-4] + "AAA="
        check("подделанные данные отклоняются (подпись не сходится)",
              data._unpack_norms(json.dumps(tampered).encode("utf-8")) is None)
        check("мусор отклоняется",
              data._unpack_norms(b"\xff not json") is None)

        # --- 3. save_norms: только личный файл, общий не трогаем ---
        check("общего файла еще нет", not os.path.exists(shared))
        data.save_norms(norms)
        check("создан личный файл", os.path.exists(my))
        check("общий файл не создан save_norms", not os.path.exists(shared))
        check("личный файл защищен (есть подпись)",
              json.loads(open(my, "rb").read().decode("utf-8")).get("формат")
              == "composit-norms-1")
        check("чтение личного файла через программу работает",
              data.load_norms_file(my)["ПОДАЧА_НА_КАНАВУ"]["16K20"] == 0.777)

        # --- 4. Ручная правка личного файла отклоняется ---
        bad = json.loads(open(my, "rb").read().decode("utf-8"))
        bad["данные"] = bad["данные"][:-4] + "AAA="
        with open(my, "w", encoding="utf-8") as f:
            json.dump(bad, f)
        check("вручную измененный файл отклоняется", data.load_norms_file(my) is None)
        check("my_norms_as_dict не падает на битом файле",
              data.my_norms_as_dict() is not None)

        # --- 5. Старый «открытый» JSON принимается один раз и защищается ---
        legacy = {"ПРИПУСК_НА_ДИАМЕТР": {"0": 6, "20": 8, "30": 10, "60": 12}}
        with open(my, "w", encoding="utf-8") as f:
            json.dump(legacy, f, ensure_ascii=False)
        loaded = data.load_norms_file(my)
        check("старый формат прочитан", loaded
              and loaded["ПРИПУСК_НА_ДИАМЕТР"]["20"] == 8)
        check("старый файл пересохранен защищенным",
              json.loads(open(my, "rb").read().decode("utf-8")).get("формат")
              == "composit-norms-1")

        # --- 6. publish_norms: подписанный файл в сетевой папке + локальный общий ---
        data.save_norms(norms)
        check("публикация удалась", data.publish_norms() is True)
        check("в сетевую папку лег подписанный файл",
              os.path.exists(net_file) and data._unpack_norms(open(net_file, "rb").read())
              ["ПОДАЧА_НА_КАНАВУ"]["16K20"] == 0.777)
        check("локальный общий файл обновлен при публикации",
              os.path.exists(shared))

        # --- 7. _sync_norms_from_server: подделанный сетевой файл не тянется ---
        os.remove(shared)
        with open(net_file, "w", encoding="utf-8") as f:
            json.dump({"ПОДАЧА_НА_КАНАВУ": {"16K20": 99}}, f)
        data._sync_norms_from_server()
        check("подделанный сетевой файл не скопирован",
              not os.path.exists(shared))

        # корректно подписанный сетевой файл — синхронизируется
        with open(net_file, "wb") as f:
            f.write(data._pack_norms(norms))
        data._sync_norms_from_server()
        check("корректный сетевой файл синхронизирован", os.path.exists(shared))

        # --- 8. Переключение активного источника норм ---
        data.set_active_source(data.SOURCE_MY)
        check("активный источник сохранен", data.get_active_source() == data.SOURCE_MY)
        data.set_active_source(data.SOURCE_SHARED)
        check("источник переключается обратно",
              data.get_active_source() == data.SOURCE_SHARED)

    finally:
        data._data_dir = orig_data_dir
        updater.UPDATE_DIR = orig_update_dir
        shutil.rmtree(work, ignore_errors=True)
        shutil.rmtree(net, ignore_errors=True)
        # вернуть нормы модуля в исходное состояние
        data._load_external_norms()

    print(f"\nИтого: пройдено {passed}, провалено {failed}")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
