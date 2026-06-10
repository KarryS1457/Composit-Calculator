import tkinter as tk
from PIL import Image, ImageTk
import core.calculations as calc
import core.data as data
from ui.menu import MainMenu
from ui.tab_weld import TabWeld
from ui.tab_lathe import TabLathe
from ui.tab_lathe_otp import TabLatheOtp
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
        self.view.mainloop()

    # --- НАВИГАЦИЯ ---

    def show_main_menu(self):
        """Переход в главное меню"""
        self.view.clear_screen()
        self.current_screen = MainMenu(self.view.container, self)
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

            # Отправляем текст обратно во View для отображения
            self.current_screen.show_results(res_text)

        except Exception as e:
            self.view.show_error(f"Сбой расчета: {e}")

    def _format_time(self, seconds):
        """Вспомогательный метод для форматирования секунд в минуты и секунды"""
        minutes_float = seconds / 60
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{seconds:.2f} сек. ({minutes_float:.2f} мин. или {m}м {s}с)"

    def _process_turning_calculation(self, item_type, raw_data):
        """Единая логика для расчетов токарной обработки (обычной и ОТП)"""
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

        # 2. Расчет для альтернативных станков, в диапазон которых попадает диаметр D
        D = float(raw_data.get('D', 0) or 0)
        alt_machines = [
            name for name, (diams, _) in data.TURNING_DATA.items()
            if name != main_res['machine'] and min(diams) <= D <= max(diams)
        ]

        if alt_machines:
            res_text += "АЛЬТЕРНАТИВНЫЕ ВАРИАНТЫ:\n"
            for alt_machine in alt_machines:
                alt_res = calc.calculate_lathe_time(item_type, raw_data, force_machine=alt_machine)
                alt_total = alt_res['time_sec'] + alt_res.get('thread_sec', 0)
                res_text += f"- {alt_machine}: {self._format_time(alt_total)}\n"

        self.current_screen.show_results(res_text)

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