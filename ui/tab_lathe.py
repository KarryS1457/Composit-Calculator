import tkinter as tk
from core.utils import ScrollableFrame
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
       
        sf = ScrollableFrame(self)
        sf.pack(fill="both", expand=True)
        self.scrollable_frame = sf.inner_frame

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

