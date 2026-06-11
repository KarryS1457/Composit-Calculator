import tkinter as tk
import importlib

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

        # Прокрутку вешаем напрямую на canvas и все дочерние виджеты, а не
        # глобально через bind_all: иначе после ухода с экрана (виджеты
        # уничтожены) колесо мыши продолжает слать события в удаленный canvas.
        self._bind_mousewheel(self.canvas)
        self._bind_mousewheel(self.scrollable_frame)
        for child in self.scrollable_frame.winfo_children():
            self._bind_mousewheel(child)

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind("<Button-4>", self._on_mousewheel, add="+")
        widget.bind("<Button-5>", self._on_mousewheel, add="+")

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


    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if not self.canvas.winfo_exists():
            return
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")