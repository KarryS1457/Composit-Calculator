import tkinter as tk
from turning.swivel_flange import swivel
from turning.compensator_flange import compensator
from turning.forming_flange import forming
from turning.shell import shell
from turning.circle import circle
from turning.adapter_flange import adapter
from turning.rotary_spherical_flange import rotspher
from turning.threaded_bushing import thread
from turning.bushing import bushing
from turning.welding_flange_tnf import weldingtnf
from turning.welded_ring import weldring
from turning.welding_flange import weldflange
from turning.pin import pin

class TabLathe(tk.Frame):
    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter # В MVP это наш "пульт управления"
       
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

        # Кнопка назад через презентер
        tk.Button(self.scrollable_frame, text="← НАЗАД В МЕНЮ", font=("Arial", 9),
                  fg="#7f8c8d", relief="flat",
                  command=self.presenter.show_main_menu).pack(anchor="w", pady=(0, 20))
       
        tk.Label(self.scrollable_frame, text="ВЫБОР ИЗДЕЛИЙ", font=("Arial", 16, "bold")).pack(pady=30)
       
        menu_buttons = [
            ("Фланец поворотный", swivel),
            ("Фланец поворотный сферический", rotspher),
            ("Фланец компенсатора", compensator),
            ("Фланец формующий", forming),
            ("Обечайка", shell),
            ("Круг", circle),
            ("Фланец переходной", adapter),
            ("Втулка", bushing),
            ("Втулка резьбовая", thread),
            ("Кольцо приварное", weldring),
            ("Фланец приварной", weldflange),
            ("Фланец приварной ТНФ", weldingtnf),
            ("Штифт", pin)
        ]
       
        for text, screen_class in menu_buttons:
            # Теперь вызываем метод презентера для смены экрана изделия
            btn = tk.Button(self.scrollable_frame, text=text, font=("Arial", 12), bg="#34495e",
                            fg="white", height=2,
                            command=lambda sc=screen_class: self.presenter.show_lathe_detail(sc))
            btn.pack(fill="x", pady=10, padx=20)

        self.bind("<Enter>", lambda _: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.bind("<Leave>", lambda _: self.canvas.unbind_all("<MouseWheel>"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
