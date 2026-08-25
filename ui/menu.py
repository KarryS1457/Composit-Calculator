import tkinter as tk

from core.updater import IS_BETA, VERSION


class MainMenu(tk.Frame):
    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter  # Сохраняем ссылку на презентер

        # Заголовок меню
        tk.Label(self, text="ГЛАВНОЕ МЕНЮ",
                 font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=(0, 30))

        if IS_BETA:
            banner = tk.Frame(self, bg="#c0392b")
            banner.pack(fill="x", pady=(0, 20))
            tk.Label(banner, bg="#c0392b", fg="white", justify="center",
                     font=("Arial", 10, "bold"), wraplength=600, pady=8,
                     text=("БЕТА-ВЕРСИЯ — ИСПРАВЛЕННЫЕ НОРМЫ\n"
                           "Время считается по новым формулам и заметно ниже, "
                           "чем в рабочей версии.\nНе используйте эти цифры для "
                           "выдачи заданий и расценок.")).pack(fill="x")

        # Кнопка СВАРКА
        self.btn_weld = tk.Button(
            self, 
            text="СВАРКА", 
            font=("Arial", 12, "bold"),
            bg="#34495e", 
            fg="white",
            height=2,
            command=self.presenter.show_weld_tab
        )
        self.btn_weld.pack(fill="x", pady=10)

        # Кнопка ТОКАРНАЯ ОБРАБОТКА
        self.btn_turning = tk.Button(
            self, 
            text="ТОКАРНАЯ ОБРАБОТКА", 
            font=("Arial", 12, "bold"),
            bg="#34495e", 
            fg="white",
            height=2,
            command=self.presenter.show_lathe_menu
        )
        self.btn_turning.pack(fill="x", pady=10)

        # Кнопка ТОКАРНАЯ ОБРАБОТКА ОТПиР
        self.btn_turning_otp = tk.Button(
            self, 
            text="ТОКАРНАЯ ОБРАБОТКА ОТПиР", 
            font=("Arial", 12, "bold"),
            bg="#34495e", 
            fg="white",
            height=2,
            command=self.presenter.show_lathe_otp_menu
        )
        self.btn_turning_otp.pack(fill="x", pady=10)

        # Кнопка РЕДАКТОР НОРМ (доступ по паролю)
        self.btn_norms = tk.Button(
            self,
            text="РЕДАКТОР НОРМ",
            font=("Arial", 10),
            bg="#7f8c8d",
            fg="white",
            command=self.presenter.show_norms_editor
        )
        self.btn_norms.pack(fill="x", pady=(30, 10))

        tk.Label(self, text=f"Версия {VERSION}", font=("Arial", 8),
                 fg="#95a5a6").pack(side="bottom", pady=(10, 0))