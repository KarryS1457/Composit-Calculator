import os
import tkinter as tk
from tkinter import messagebox

from core import data
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
            self._build_norms_switch()

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

    # ------------------------------------------------------------------
    # Переключатель источника норм (только в бете)
    # ------------------------------------------------------------------
    def _build_norms_switch(self):
        """Ползунок "серверные / локальные нормы" прямо в главном меню.

        Тот же выбор есть в редакторе норм, но он спрятан за паролем. В бете
        нужно быстро переключаться между заводскими нормами и своими, чтобы
        сравнивать расчеты, поэтому выносим переключатель на видное место.
        Оба места вызывают одну и ту же data.set_active_source().
        """
        box = tk.LabelFrame(self, text=" Нормы для расчета ",
                            font=("Arial", 9, "bold"), fg="#2c3e50",
                            padx=10, pady=8)
        box.pack(fill="x", pady=(0, 15))

        row = tk.Frame(box)
        row.pack()

        self.lbl_server = tk.Label(row, text="СЕРВЕРНЫЕ", font=("Arial", 9, "bold"))
        self.lbl_server.pack(side="left", padx=(0, 8))

        self.var_source = tk.IntVar(
            value=0 if data.get_active_source() == data.SOURCE_SHARED else 1)
        tk.Scale(row, from_=0, to=1, orient="horizontal", showvalue=False,
                 length=64, sliderlength=30, width=16, troughcolor="#dfe4e6",
                 variable=self.var_source, command=self._on_source_switch,
                 highlightthickness=0).pack(side="left")

        self.lbl_local = tk.Label(row, text="ЛОКАЛЬНЫЕ", font=("Arial", 9, "bold"))
        self.lbl_local.pack(side="left", padx=(8, 0))

        self.lbl_source_info = tk.Label(box, font=("Arial", 8), fg="#7f8c8d",
                                        wraplength=560, justify="center")
        self.lbl_source_info.pack(pady=(6, 0))

        self._refresh_source_view()

    def _on_source_switch(self, _value=None):
        src = data.SOURCE_MY if self.var_source.get() else data.SOURCE_SHARED
        if src == data.get_active_source():
            return  # ползунок вернули в то же положение — писать файл незачем
        try:
            data.set_active_source(src)
        except Exception as e:
            messagebox.showerror("Нормы", f"Не удалось переключить нормы: {e}")
            # возвращаем ползунок к реальному состоянию, чтобы подпись не врала
            self.var_source.set(
                0 if data.get_active_source() == data.SOURCE_SHARED else 1)
        self._refresh_source_view()

    def _refresh_source_view(self):
        """Подсвечивает выбранную сторону и показывает, какой файл реально
        используется. Это важно: если личного файла норм еще нет, выбор
        "локальные" молча откатывается на серверные."""
        active = data.get_active_source()
        is_local = active == data.SOURCE_MY
        self.lbl_server.config(fg="#95a5a6" if is_local else "#2c3e50")
        self.lbl_local.config(fg="#2c3e50" if is_local else "#95a5a6")

        path = data.active_norms_path()
        if is_local and not data.my_norms_exist():
            self.lbl_source_info.config(
                fg="#c0392b",
                text="Личный файл норм на этом компьютере не создан — расчет "
                     "идет по серверным нормам. Сохраните нормы в редакторе, "
                     "чтобы появились локальные.")
        else:
            self.lbl_source_info.config(
                fg="#7f8c8d", text=f"Файл: {os.path.basename(path)}")