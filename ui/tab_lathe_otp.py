import tkinter as tk
import importlib
from core.utils import ScrollableFrame

class TabLatheOtp(tk.Frame):
    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter 
       
        sf = ScrollableFrame(self)
        sf.pack(fill="both", expand=True)
        self.scrollable_frame = sf.inner_frame

        # Кнопка назад
        tk.Button(self.scrollable_frame, text="← НАЗАД В МЕНЮ", font=("Arial", 9),
                  fg="#7f8c8d", relief="flat",
                  command=self.presenter.show_main_menu).pack(anchor="w", pady=(0, 20))

        tk.Label(self.scrollable_frame, text="ВЫБОР ИЗДЕЛИЙ", font=("Arial", 16, "bold")).pack(pady=30)

        # Передаем не классы, а строковые названия (ключи)
        menu_buttons = [
            ("Ось", "axle"),
            ("Вал", "shaft"),
            ("Корпус подшипника", "bearinghousing")
       ]
       
        for text, screen_name in menu_buttons:
            # Вызываем наш специальный метод
            btn = tk.Button(self.scrollable_frame, text=text, font=("Arial", 12), bg="#34495e",
                            fg="white", height=2,
                            command=lambda sn=screen_name: self.open_detail_screen(sn))
            btn.pack(fill="x", pady=10, padx=20)

    def open_detail_screen(self, screen_name):
        """Динамический ленивый импорт"""
        try:
            # Подгружаем модуль по его строковому имени
            module = importlib.import_module(f"turningotp.{screen_name}")
            # Достаем из модуля класс с таким же именем
            screen_class = getattr(module, screen_name)
           
            # Вызываем экран только в случае успеха
            self.presenter.show_lathe_otp_detail(screen_class)
            
        except (ImportError, AttributeError) as e:
            # Если что-то пошло не так, просто печатаем ошибку и не ломаем программу
            print(f"Ошибка загрузки экрана {screen_name}: {e}")


