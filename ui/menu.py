import tkinter as tk

class MainMenu(tk.Frame):
    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter  # Сохраняем ссылку на презентер
        
        # Заголовок меню
        tk.Label(self, text="ГЛАВНОЕ МЕНЮ", 
                 font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=(0, 30))

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