import tkinter as tk

class TabLatheOtp(tk.Frame):
    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter 
       
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

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

        self.bind("<Enter>", lambda _: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.bind("<Leave>", lambda _: self.canvas.unbind_all("<MouseWheel>"))

    def open_detail_screen(self, screen_name):
        """Ленивый импорт: загружаем класс только в момент нажатия на кнопку"""
        if screen_name == "axle":
            from turningotp.axle import axle as screen_class
        elif screen_name == "shaft":
            from turningotp.shaft import shaft as screen_class
        elif screen_name == "bearinghousing":
            from turningotp.bearinghousing import bearinghousing as screen_class
        else:
            return

        self.presenter.show_lathe_otp_detail(screen_class)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")