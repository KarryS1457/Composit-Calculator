import tkinter as tk
from tkinter import ttk, messagebox
import core.data as data  # Обрати внимание на путь, если ты создал папку core

class TabWeld(tk.Frame):
    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter  # Теперь храним ссылку на презентер
        self.inputs = []

        # Кнопка назад через презентер
        tk.Button(self, text="← НАЗАД В МЕНЮ", font=("Arial", 9),
                  fg="#7f8c8d", relief="flat",
                  command=self.presenter.show_main_menu).pack(anchor="w", pady=(0, 20))
       
        # Заголовок
        self.add_label("Выберите тип шва:", bold=True)
        self.combo_type = ttk.Combobox(self, values=sorted(data.WELD_DATA.keys()), state="readonly")
        self.combo_type.set("C4")
        self.combo_type.pack(fill="x", pady=5)

        # Поля ввода (используем vcmd из view через презентер)
        self.add_label("Толщина S (мм):")
        self.ent_s = self.add_entry()
        
        self.add_label("Длина L (мм):")
        self.ent_l = self.add_entry()
        
        self.add_label("Масса M (кг):")
        self.ent_m = self.add_entry()

        self.add_label("\nУсловия работы:", bold=True)
        self.combo_lp = self.add_combo("Тип производства:", ["Массовое (0.9)", "Серийное (1.0)", "Единичное (1.3)"], 1)
        self.combo_pos = self.add_combo("Положение:", ["Нижнее (1.0)", "Вертикальное (1.5)", "Потолочное (2)"], 0)
        self.combo_posture = self.add_combo("Поза сварщика:", ["Сидя (0.95)", "Стоя (1.0)", "Другая (1.15)"], 1)

        # Кнопка расчета
        self.btn_calc = tk.Button(self, text="РАССЧИТАТЬ", bg="#2c3e50", fg="white",
                                 font=("Arial", 12, "bold"), command=self.on_calc_click)
        self.btn_calc.pack(fill="x", pady=20, ipady=10)

        # Окно результата
        self.res_box = tk.Label(self, text="Результат появится здесь", justify="left",
                               font=("Consolas", 10), bg="#ecf0f1", relief="sunken", padx=10, pady=10)
        self.res_box.pack(fill="both", expand=True)

    def add_label(self, text, bold=False):
        f = ("Arial", 10, "bold") if bold else ("Arial", 10)
        tk.Label(self, text=text, font=f).pack(anchor="w")

    def add_entry(self):
        # Берем валидацию presenter
        e = tk.Entry(self, validate="key", validatecommand=self.presenter.vcmd)
        e.pack(fill="x", pady=2)
        e.bind("<Return>", self.move_focus)
        e.bind("<Down>", self.move_focus)
        e.bind("<Up>", self.move_focus)
        self.inputs.append(e)
        return e

    def add_combo(self, label_text, values, default_idx):
        self.add_label(label_text)
        c = ttk.Combobox(self, values=values, state="readonly")
        c.current(default_idx)
        c.pack(fill="x", pady=2)
        return c

    def move_focus(self, event):
        current = event.widget
        if current in self.inputs:
            idx = self.inputs.index(current)
            if event.keysym in ("Down", "Return") and idx < len(self.inputs) - 1:
                self.inputs[idx+1].focus_set()
            elif event.keysym == "Return" and idx == len(self.inputs) - 1:
                self.on_calc_click()
            elif event.keysym == "Up" and idx > 0:
                self.inputs[idx-1].focus_set()
        return "break"

    def on_calc_click(self):
        """Собираем данные и отправляем презентеру"""
        try:
            # Формируем простой словарь с данными
            data_to_calc = {
                "gost": self.combo_type.get(),
                "s": float(self.ent_s.get()),
                "l_mm": float(self.ent_l.get()),
                "m": float(self.ent_m.get()),
                "lp_idx": self.combo_lp.current(),
                "pos_idx": self.combo_pos.current(),
                "posture_idx": self.combo_posture.current()
            }
            # Говорим презентеру: "На, посчитай это"
            self.presenter.handle_weld_calculation(data_to_calc)
        except ValueError:
            messagebox.showwarning("Внимание", "Пожалуйста, заполните все поля числами")

    def show_results(self, text):
        """Этот метод вызовет презентер, когда получит ответ от модели"""
        self.res_box.config(text=text)