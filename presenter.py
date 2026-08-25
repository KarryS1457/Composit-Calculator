import sys
import threading
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

from core import calc_log, changelog, data, updater
from core import calculations as calc
from core.logger import log
from ui.menu import MainMenu
from ui.tab_lathe import TabLathe
from ui.tab_lathe_otp import TabLatheOtp
from ui.tab_norms import TabNorms
from ui.tab_weld import TabWeld
from ui.whatsnew import WhatsNew

# Добавь импорты для других табов, когда переделаешь их:
# from ui.tab_turning import TabTurning

class AppPresenter:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.typed_buffer = ""
        self.current_screen = None

        # 1. Регистрируем валидацию и сохраняем её в self.vcmd
        self.vcmd = (self.view.register(self.model.validate_numeric), '%P')
       
        # Передаем её во View
        self.view.set_vcmd(self.vcmd)

        # 2. Подписываемся на глобальные клавиши
        self.view.bind_all("<Key>", self._handle_keypress)

    def start(self):
        """Запуск приложения"""
        self.show_main_menu()
        self._check_updates_in_background()
        # Список изменений показываем с задержкой, чтобы главное окно успело
        # отрисоваться и окно "Что нового" встало по его центру
        self.view.after(400, self._show_whatsnew)
        self.view.mainloop()

    def _show_whatsnew(self):
        """Один раз после обновления показывает, что изменилось.

        Любая ошибка здесь гасится: список изменений не должен мешать
        работать с программой."""
        try:
            entries = changelog.pending_entries()
            if entries:
                WhatsNew(self.view, entries, updater.VERSION)
                log.info(f"Показан список изменений для версии {updater.VERSION}")
            changelog.set_seen_version()
        except Exception as e:
            log.warning(f"Не удалось показать список изменений: {e}")

    # --- АВТООБНОВЛЕНИЕ ---

    def _check_updates_in_background(self):
        """Проверяет сетевую папку обновлений в фоновом потоке,
        чтобы не тормозить запуск"""
        def worker():
            info = updater.check_for_update()
            if info:
                # Все обращения к Tkinter — только из главного потока
                self.view.after(0, lambda: self._offer_update(info))
        threading.Thread(target=worker, daemon=True).start()

    def _offer_update(self, info):
        if not messagebox.askyesno(
                "Доступно обновление",
                f"Вышла новая версия программы: {info['version']}\n"
                f"Текущая версия: {updater.VERSION}\n\n"
                f"Установить обновление сейчас?"):
            return

        # В режиме разработки (запуск из исходников) exe заменить нечего
        if not getattr(sys, 'frozen', False):
            messagebox.showinfo(
                "Обновление",
                f"Программа запущена не из exe — автообновление недоступно.\n"
                f"Новая версия лежит в папке:\n{updater.UPDATE_DIR}")
            return

        progress = tk.Toplevel(self.view)
        progress.title("Обновление")
        progress.geometry("320x90")
        progress.resizable(False, False)
        progress.transient(self.view)
        lbl = tk.Label(progress, text="Загрузка обновления...", font=("Arial", 11))
        lbl.pack(expand=True, pady=20)

        def set_progress(done, total):
            if total:
                self.view.after(0, lbl.config,
                                {"text": f"Загрузка обновления... {done * 100 // total}%"})

        def worker():
            try:
                new_exe = updater.download_update(info['exe_path'], set_progress)
                updater.apply_update(new_exe)
            except Exception as e:
                # Текст ошибки сохраняем в отдельную переменную: имя из
                # "except ... as e" удаляется на выходе из блока, а лямбда
                # выполняется позже (через view.after) — обращение к "e"
                # внутри нее упало бы с NameError.
                err = str(e)
                self.view.after(0, lambda: (
                    progress.destroy(),
                    self.view.show_error(f"Не удалось установить обновление: {err}")))
                return
            # Батник ждет закрытия программы, заменяет exe и перезапускает
            self.view.after(0, self.view.destroy)

        threading.Thread(target=worker, daemon=True).start()

    # --- НАВИГАЦИЯ ---

    def show_main_menu(self):
        """Переход в главное меню"""
        self.view.clear_screen()
        self.current_screen = MainMenu(self.view.container, self)
        self.current_screen.pack(fill="both", expand=True)

    def show_norms_editor(self):
        """Редактор норм (доступ по паролю внутри экрана)"""
        self.view.clear_screen()
        self.current_screen = TabNorms(self.view.container, self)
        self.current_screen.pack(fill="both", expand=True)

    def show_weld_tab(self):
        """Переход к расчету сварки"""
        self.view.clear_screen()
        self.current_screen = TabWeld(self.view.container, self)
        self.current_screen.pack(fill="both", expand=True)

    def show_lathe_menu(self):
        """Открывает список изделий для токарки"""
        self.view.clear_screen()
        self.current_screen = TabLathe(self.view.container, self)
        self.current_screen.pack(fill="both", expand=True)

    def show_lathe_detail(self, screen_class):
        """Открывает конкретный расчет (например, Фланец)"""
        self.view.clear_screen()
        self.current_screen = screen_class(self.view.container, self)
        self.current_screen.pack(fill="both", expand=True)

    def show_lathe_otp_menu(self):
        """Открывает список изделий для токарки отп"""
        self.view.clear_screen()
        self.current_screen = TabLatheOtp(self.view.container, self)
        self.current_screen.pack(fill="both", expand=True)

    def show_lathe_otp_detail(self, screen_class):
        """Открывает конкретный расчет"""
        self.view.clear_screen()
        self.current_screen = screen_class(self.view.container, self)
        self.current_screen.pack(fill="both", expand=True)

    # --- ЛОГИКА РАСЧЕТОВ ---

    def handle_weld_calculation(self, raw_data):
        """Метод, который вызывает TabWeld при нажатии 'РАССЧИТАТЬ'"""
        try:
            # Получаем коэффициенты из данных (слой Data)
            k_lp = [0.9, 1.0, 1.3][raw_data["lp_idx"]]
            k_pos = [1.0, 1.5, 2.0][raw_data["pos_idx"]]
            k_posture = [0.95, 1.0, 1.15][raw_data["posture_idx"]]

            # Вызываем расчетную логику (слой Calculations)
            result = calc.calculate_weld_logic(
                raw_data["gost"], raw_data["s"], raw_data["l_mm"], raw_data["m"],
                k_lp, k_pos, k_posture, data.WELD_DATA, data.CHAMFER_DATA
            )

            # Форматируем результат в красивый текст
            minutes = result["total_sec"] // 60
            seconds = result["total_sec"] % 60
           
            res_text = (
                f"РЕЗУЛЬТАТ (Шов {result['gost']}, S={result['s']:.1f}мм)\n"
                f"-----------------------------------\n"
                f"Подготовка: {result['prep']:.2f} мин\n"
                f"Снятие фасок: {result['chamfer']:.2f} мин\n"
                f"Время сварки: {result['weld']:.2f} мин\n"
                f"-----------------------------------\n"
                f"ОБЩАЯ НОРМА: {minutes} мин {seconds} сек"
            )

            if result["out_of_range"]:
                lo, hi = result["s_range"]
                res_text += (
                    f"\n\nВНИМАНИЕ: толщина S={result['s']:.1f}мм вне таблицы "
                    f"норм для шва {result['gost']} ({lo}-{hi}мм). "
                    f"Результат получен экстраполяцией и может быть неточным."
                )

            # Отправляем текст обратно во View для отображения
            self.current_screen.show_results(res_text)

            # Пишем расчет в журнал (с пошаговым ходом)
            calc_log.log_calc("СВАРКА", f"Шов {result['gost']}",
                              raw_data, res_text, steps=result.get('steps'))

        except Exception as e:
            self.view.show_error(f"Сбой расчета: {e}")

    def _format_time(self, seconds):
        """Вспомогательный метод для форматирования секунд в минуты и секунды"""
        minutes_float = seconds / 60
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{seconds:.2f} сек. ({minutes_float:.2f} мин. или {m}м {s}с)"

    def _validate_geometry(self, raw_data):
        """Проверка, что геометрия детали не превышает параметры заготовки."""
        def f(key):
            try:
                return float(raw_data.get(key, 0) or 0)
            except (ValueError, TypeError):
                return 0.0

        D, d, t = f('D'), f('d'), f('t')
        D1, D2, S = f('D1'), f('D2'), f('S')

        if D1 > 0 and D > D1:
            return ("ОШИБКА: Внешний диаметр детали (D) не может быть больше "
                    "внешнего диаметра заготовки (D1).")
        if S > 0 and t > S:
            return ("ОШИБКА: Габарит детали (t) не может быть больше "
                    "толщины заготовки (S).")
        if D2 > 0 and d > 0 and d < D2:
            return ("ОШИБКА: Внутренний диаметр детали (d) не может быть меньше "
                    "внутреннего диаметра заготовки (D2).")

        # Обе проточки растачиваются от внутреннего отверстия наружу, поэтому
        # их диаметры не могут быть меньше d. Проверяем только там, где деталь
        # вообще имеет внутренний диаметр: у втулки, круга и штифта d=0, и там
        # Dw означает совсем другое (диаметр наружной канавы).
        if d > 0:
            DM = f('DM')
            # экраны формующего фланца передают этот параметр как "DW"
            Dw = f('Dw') or f('DW')
            if DM > 0 and DM < d:
                return ("ОШИБКА: Диаметр проточки (Dm) не может быть меньше "
                        "внутреннего диаметра детали (d).")
            if Dw > 0 and Dw < d:
                return ("ОШИБКА: Диаметр 2-й проточки (Dw) не может быть меньше "
                        "внутреннего диаметра детали (d).")
        return None

    # Человекочитаемые названия изделий для журнала расчетов
    _ITEM_NAMES = {
        "swivel": "Фланец поворотный",
        "rotspher": "Фланец поворотный сферический",
        "compensator": "Фланец компенсатора",
        "forming": "Фланец формующий",
        "shell": "Обечайка",
        "circle": "Круг",
        "adapter": "Фланец переходной",
        "bushing": "Втулка",
        "threaded_bushing": "Втулка резьбовая",
        "weldring": "Кольцо приварное",
        "welding_flange": "Фланец приварной",
        "welding_tnf": "Фланец приварной ТНФ",
        "pin": "Штифт",
        "axle": "Ось",
        "axle2": "Ось",
        "shaft": "Вал",
        "bearinghousing": "Корпус подшипника",
    }

    def _process_turning_calculation(self, item_type, raw_data):
        """Единая логика для расчетов токарной обработки (обычной и ОТП)"""
        error = self._validate_geometry(raw_data)
        if error:
            self.current_screen.show_results(error)
            return

        # 1. Расчет на основном станке (определяется по готовому диаметру D, как в Excel)
        main_res = calc.calculate_lathe_time(item_type, raw_data)

        if not main_res.get('machine'):
            self.current_screen.show_results("ОШИБКА: Станок не найден.\n"
                                             "Проверьте внешний диаметр детали D.")
            return

        thread_sec = main_res.get('thread_sec', 0)
        res_text = (
            f"ОСНОВНОЙ СТАНОК: {main_res['machine']}\n"
            f"Обороты (D): {main_res['rpm']} об/мин\n"
        )
        if thread_sec > 0:
            res_text += (
                f"Время токарной обработки: {self._format_time(main_res['time_sec'])}\n"
                f"Время обработки резьбы: {self._format_time(thread_sec)}\n"
            )
        res_text += (
            f"ВРЕМЯ ИТОГО: {self._format_time(main_res['time_sec'] + thread_sec)}\n"
            f"{'-'*40}\n"
        )

        # 2. Расчет для альтернативных станков: станок подходит, если у него
        # заданы подачи (в таблице норм) и есть обороты в диапазоне диаметра
        # ЗАГОТОВКИ — по нему же выбирается и основной станок, ведь в патрон
        # зажимается заготовка. D1 берем из расчета: он мог быть получен там
        # из припуска по толщине листа, а не введен на экране.
        D1 = float(main_res.get('blank_D1', 0) or raw_data.get('D1', 0) or 0)
        alt_machines = []
        for name, (diams, rpms) in data.TURNING_DATA.items():
            if name == main_res['machine']:
                continue
            feeds = data.FEEDRATE_DATA.get(name, [0, 0, 0, 0, 0])
            covered = [dm for dm, r in zip(diams, rpms) if r > 0]
            if feeds[2] > 0 and covered and min(covered) <= D1 <= max(covered):
                alt_machines.append(name)

        if alt_machines:
            res_text += "АЛЬТЕРНАТИВНЫЕ ВАРИАНТЫ:\n"
            for alt_machine in alt_machines:
                alt_res = calc.calculate_lathe_time(item_type, raw_data, force_machine=alt_machine)
                alt_total = alt_res['time_sec'] + alt_res.get('thread_sec', 0)
                res_text += f"- {alt_machine}: {self._format_time(alt_total)}\n"

        self.current_screen.show_results(res_text)

        # Пишем расчет в журнал (с пошаговым ходом основного станка)
        title = self._ITEM_NAMES.get(item_type, item_type)
        calc_log.log_calc("ТОКАРКА", f"{title} ({item_type})", raw_data, res_text,
                          steps=main_res.get('steps'))

    def handle_lathe_calculation(self, item_type, raw_data):
        """Обертка для расчета стандартной токарки"""
        try:
            self._process_turning_calculation(item_type, raw_data)
        except Exception as e:
            self.view.show_error(f"Сбой расчета: {e}")

    def handle_lathe_otp_calculation(self, item_type, raw_data):
        """Обертка для расчета токарки ОТП"""
        try:
            self._process_turning_calculation(item_type, raw_data)
        except Exception as e:
            self.view.show_error(f"Сбой расчета: {e}")

    # --- СЕКРЕТНАЯ ЛОГИКА (Пасхалка) ---
    def _handle_keypress(self, event):
        char = event.char.lower()
        if not char:
            return
       
        # Логика замены раскладки
        replacements = {'с': 'c', 'р': 'h', 'г': 'u'}
        char = replacements.get(char, char)
       
        # Обновляем буфер (используем длину кода из модели)
        code_len = len(self.model.secret_code)
        self.typed_buffer = (self.typed_buffer + char)[-code_len:]
       
        # Проверяем секрет через модель
        if self.model.check_secret(self.typed_buffer):
            self.animate_secret(10)

    def animate_secret(self, size):
        try:
            img_path = self.model.get_image_data("pics/chuu.jfif")
            if not img_path: return

            original = Image.open(img_path)
            if size <= 450:
                resample_mode = getattr(Image, 'Resampling', Image).LANCZOS
                resized = original.resize((size, size), resample_mode)
                photo = ImageTk.PhotoImage(resized)
               
                self.view.show_secret_image(photo)
                # Зацикливаем анимацию через View
                self.view.after(15, lambda: self.animate_secret(size + 25))
            else:
                self.view.after(3000, self.view.hide_secret_image)
                self.typed_buffer = ""
        except Exception as e:
            print(f"Ошибка анимации: {e}")