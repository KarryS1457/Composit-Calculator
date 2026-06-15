import tkinter as tk
from tkinter import messagebox, ttk

import core.data as data
from core.utils import ScrollableFrame

# Разбивка секций норм по вкладкам редактора
WELD_SECTIONS = ("НОРМЫ_СВАРКИ", "ФАСКИ_СВАРКА")


class TabNorms(tk.Frame):
    """Редактор норм: доступ по паролю, правка всех таблиц из нормы.json."""

    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter
        # entries[(секция, внешний_ключ, внутренний_ключ)] = Entry
        # для плоских таблиц внутренний_ключ = None
        self.entries = {}

        tk.Button(self, text="← НАЗАД В МЕНЮ", font=("Arial", 9),
                  fg="#7f8c8d", relief="flat",
                  command=self.presenter.show_main_menu).pack(anchor="w", pady=(0, 10))

        self._show_password_prompt()

    # ------------------------------------------------------------------
    # Экран ввода пароля
    # ------------------------------------------------------------------
    def _show_password_prompt(self):
        self.pass_frame = tk.Frame(self)
        self.pass_frame.pack(expand=True)

        tk.Label(self.pass_frame, text="РЕДАКТОР НОРМ",
                 font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=(0, 20))
        tk.Label(self.pass_frame, text="Введите пароль:",
                 font=("Arial", 11)).pack()

        self.ent_pass = tk.Entry(self.pass_frame, show="*", font=("Arial", 12),
                                 justify="center", width=24)
        self.ent_pass.pack(pady=10)
        self.ent_pass.bind("<Return>", lambda _: self._check_password())
        self.ent_pass.focus_set()

        tk.Button(self.pass_frame, text="ВОЙТИ", bg="#2c3e50", fg="white",
                  font=("Arial", 11, "bold"), width=20,
                  command=self._check_password).pack(pady=5)

        self.lbl_pass_error = tk.Label(self.pass_frame, text="", fg="red")
        self.lbl_pass_error.pack(pady=5)

    def _check_password(self):
        if self.ent_pass.get() == data.NORMS_PASSWORD:
            self.pass_frame.destroy()
            self._build_editor()
        else:
            self.lbl_pass_error.config(text="Неверный пароль")
            self.ent_pass.delete(0, "end")

    # ------------------------------------------------------------------
    # Редактор
    # ------------------------------------------------------------------
    def _build_editor(self):
        tk.Label(self, text="РЕДАКТОР НОРМ", font=("Arial", 16, "bold"),
                 fg="#2c3e50").pack(pady=(0, 5))
        tk.Label(self, text="Правки сохраняются в ваш личный файл норм. "
                            "Ниже выберите, по каким нормам вести расчеты.",
                 font=("Arial", 9), fg="#7f8c8d").pack(pady=(0, 5))

        # Выбор активного источника норм для расчетов
        src_box = tk.Frame(self)
        src_box.pack(pady=(0, 10))
        tk.Label(src_box, text="Расчеты вести по:", font=("Arial", 10, "bold"),
                 fg="#2c3e50").pack(side="left", padx=(0, 10))
        self.var_source = tk.StringVar(value=data.get_active_source())
        tk.Radiobutton(src_box, text="общим нормам (заводским)",
                       variable=self.var_source, value=data.SOURCE_SHARED,
                       font=("Arial", 10),
                       command=self._switch_source).pack(side="left", padx=5)
        tk.Radiobutton(src_box, text="моим нормам (этот компьютер)",
                       variable=self.var_source, value=data.SOURCE_MY,
                       font=("Arial", 10),
                       command=self._switch_source).pack(side="left", padx=5)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        turning_scroll = ScrollableFrame(notebook)
        weld_scroll = ScrollableFrame(notebook)
        notebook.add(turning_scroll, text="ТОКАРКА")
        notebook.add(weld_scroll, text="СВАРКА")

        self.norms = data.my_norms_as_dict()
        for section, table in self.norms.items():
            target = weld_scroll if section in WELD_SECTIONS else turning_scroll
            self._render_section(target.inner_frame, section, table)

        # Привязываем прокрутку к созданным полям (они появились после
        # конструктора ScrollableFrame)
        turning_scroll.bind_mouse_scroll(turning_scroll.inner_frame, recursive=True)
        weld_scroll.bind_mouse_scroll(weld_scroll.inner_frame, recursive=True)

        bottom = tk.Frame(self)
        bottom.pack(fill="x", pady=10)
        tk.Button(bottom, text="СОХРАНИТЬ В МОИ НОРМЫ", bg="#27ae60", fg="white",
                  font=("Arial", 12, "bold"),
                  command=self._save).pack(fill="x", ipady=5)
        tk.Button(bottom, text="ОПУБЛИКОВАТЬ МОИ НОРМЫ ДЛЯ ВСЕХ КОМПЬЮТЕРОВ",
                  bg="#2980b9", fg="white",
                  font=("Arial", 10, "bold"),
                  command=self._publish).pack(fill="x", ipady=4, pady=(5, 0))
        self.lbl_status = tk.Label(bottom, text="", font=("Arial", 10), wraplength=550, justify="left")
        self.lbl_status.pack(pady=(5, 0))

    def _switch_source(self):
        src = self.var_source.get()
        try:
            data.set_active_source(src)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось переключить нормы: {e}")
            return
        if src == data.SOURCE_MY:
            self.lbl_status.config(
                text="Расчеты теперь ведутся по ВАШИМ нормам (мои_нормы.json).",
                fg="#2980b9")
        else:
            self.lbl_status.config(
                text="Расчеты теперь ведутся по ОБЩИМ заводским нормам.",
                fg="#2980b9")

    def _render_section(self, parent, section, table):
        box = tk.LabelFrame(parent, text=section, font=("Arial", 11, "bold"),
                            fg="#2c3e50", padx=10, pady=10)
        box.pack(fill="x", pady=10, padx=5)

        help_text = data.NORMS_HELP.get(section)
        if help_text:
            tk.Label(box, text=help_text, font=("Arial", 8), fg="#7f8c8d",
                     wraplength=550, justify="left").pack(anchor="w", pady=(0, 8))

        if section == "НОРМЫ_СВАРКИ":
            self._render_weld_norms(box, section, table)
            return
        if section == "ФАСКИ_СВАРКА":
            self._render_weld_chamfer(box, section, table)
            return

        grid = tk.Frame(box)
        grid.pack(anchor="w")

        first_val = next(iter(table.values()))
        if isinstance(first_val, dict):
            self._render_nested(grid, section, table)
        elif isinstance(first_val, list):
            self._render_ranges(grid, section, table)
        else:
            self._render_flat(grid, section, table)

    def _render_weld_norms(self, parent, section, table):
        """Нормы сварки: для каждого ГОСТа — две строки (S, мм / норма, мин/м)."""
        for gost, axes in table.items():
            box = tk.LabelFrame(parent, text=f"Шов {gost}", font=("Arial", 10, "bold"),
                                 fg="#2c3e50", padx=8, pady=6)
            box.pack(fill="x", pady=4, anchor="w")

            th = axes.get("толщина_мм", [])
            tm = axes.get("норма_мин_м", [])
            tk.Label(box, text="S, мм:", font=("Arial", 9), anchor="w",
                     width=14).grid(row=0, column=0, sticky="w", pady=1)
            tk.Label(box, text="норма, мин/м:", font=("Arial", 9), anchor="w",
                     width=14).grid(row=1, column=0, sticky="w", pady=1)
            for i, v in enumerate(th):
                self._add_entry(box, 0, i + 1, (section, gost, "толщина_мм", i), v, width=7)
            for i, v in enumerate(tm):
                self._add_entry(box, 1, i + 1, (section, gost, "норма_мин_м", i), v, width=7)

    def _render_weld_chamfer(self, parent, section, table):
        """Фаски сварки: для каждого диапазона — макс. толщина и две строки (S, мм / мм/мин)."""
        for idx, cfg in enumerate(table):
            box = tk.LabelFrame(parent, text=f"Диапазон №{idx + 1}", font=("Arial", 10, "bold"),
                                 fg="#2c3e50", padx=8, pady=6)
            box.pack(fill="x", pady=4, anchor="w")

            tk.Label(box, text="макс. S, мм:", font=("Arial", 9), anchor="w",
                     width=14).grid(row=0, column=0, sticky="w", pady=1)
            self._add_entry(box, 0, 1, (section, idx, "макс_толщина_мм", None),
                            cfg.get("макс_толщина_мм", 0), width=7)

            x = cfg.get("толщина_мм", [])
            y = cfg.get("норма_мм_мин", [])
            tk.Label(box, text="S, мм:", font=("Arial", 9), anchor="w",
                     width=14).grid(row=1, column=0, sticky="w", pady=1)
            tk.Label(box, text="норма, мм/мин:", font=("Arial", 9), anchor="w",
                     width=14).grid(row=2, column=0, sticky="w", pady=1)
            for i, v in enumerate(x):
                self._add_entry(box, 1, i + 1, (section, idx, "толщина_мм", i), v, width=7)
            for i, v in enumerate(y):
                self._add_entry(box, 2, i + 1, (section, idx, "норма_мм_мин", i), v, width=7)

    def _render_flat(self, grid, section, table):
        """Плоская таблица: ключ -> значение (одна строка полей на ключ)."""
        for r, (key, val) in enumerate(table.items()):
            tk.Label(grid, text=key, font=("Arial", 10), anchor="w",
                     width=18).grid(row=r, column=0, sticky="w", pady=1)
            self._add_entry(grid, r, 1, (section, key, None), val)

    def _render_ranges(self, grid, section, table):
        """Таблица диапазонов: ключ -> [мин, макс]."""
        tk.Label(grid, text="", width=18).grid(row=0, column=0)
        tk.Label(grid, text="мин", font=("Arial", 9, "bold"), width=10).grid(row=0, column=1)
        tk.Label(grid, text="макс", font=("Arial", 9, "bold"), width=10).grid(row=0, column=2)
        for r, (key, val) in enumerate(table.items(), start=1):
            tk.Label(grid, text=key, font=("Arial", 10), anchor="w",
                     width=18).grid(row=r, column=0, sticky="w", pady=1)
            self._add_entry(grid, r, 1, (section, key, 0), val[0])
            self._add_entry(grid, r, 2, (section, key, 1), val[1])

    def _render_nested(self, grid, section, table):
        """Вложенная таблица: строки — внутренние ключи (диаметры/параметры),
        столбцы — внешние ключи (станки/диаметры заготовки)."""
        outer_keys = list(table.keys())
        inner_keys = list(next(iter(table.values())).keys())

        for c, outer in enumerate(outer_keys, start=1):
            tk.Label(grid, text=outer, font=("Arial", 9, "bold"),
                     width=14).grid(row=0, column=c, padx=1)
        for r, inner in enumerate(inner_keys, start=1):
            tk.Label(grid, text=inner, font=("Arial", 10), anchor="w",
                     width=22).grid(row=r, column=0, sticky="w", pady=1)
            for c, outer in enumerate(outer_keys, start=1):
                val = table[outer].get(inner, 0)
                self._add_entry(grid, r, c, (section, outer, inner), val, width=12)

    def _add_entry(self, grid, row, col, key, value, width=10):
        e = tk.Entry(grid, width=width, justify="center")
        e.insert(0, self._fmt(value))
        e.grid(row=row, column=col, padx=1, pady=1)
        self.entries[key] = e

    @staticmethod
    def _fmt(value):
        try:
            num = float(value)
            return str(int(num)) if num == int(num) else str(num)
        except (ValueError, TypeError):
            return str(value)

    # ------------------------------------------------------------------
    # Сохранение
    # ------------------------------------------------------------------
    def _save(self):
        try:
            new_norms = self._collect()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректное значение: {e}")
            return
        try:
            data.save_norms(new_norms)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл норм: {e}")
            return
        if data.get_active_source() == data.SOURCE_MY:
            extra = "Они уже применены в расчетах (выбраны «мои нормы»)."
        else:
            extra = ("В расчетах сейчас выбраны общие нормы — чтобы считать по "
                     "своим, переключите «Расчеты вести по» вверху.")
        self.lbl_status.config(
            text=f"Нормы сохранены в ваш личный файл (мои_нормы.json). {extra}",
            fg="#27ae60")

    def _publish(self):
        import os
        if not os.path.exists(data._my_norms_file_path()):
            messagebox.showwarning(
                "Публикация норм",
                "Сначала сохраните нормы кнопкой «СОХРАНИТЬ В МОИ НОРМЫ».")
            return
        if not messagebox.askyesno(
                "Публикация норм",
                "Ваши личные нормы (мои_нормы.json) станут ОБЩИМИ заводскими "
                "и будут разосланы на ВСЕ компьютеры. Продолжить?"):
            return
        try:
            ok = data.publish_norms()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось опубликовать нормы: {e}")
            return
        if ok:
            self.lbl_status.config(
                text="Нормы опубликованы в сетевую папку — разойдутся на все компьютеры.",
                fg="#27ae60")
        else:
            self.lbl_status.config(
                text="Не удалось опубликовать: сетевая папка недоступна.",
                fg="#e67e22")

    def _collect(self):
        out = {}
        for section, table in self.norms.items():
            if section == "НОРМЫ_СВАРКИ":
                out[section] = {
                    gost: {
                        "толщина_мм": [self._parse(self.entries[(section, gost, "толщина_мм", i)])
                                       for i in range(len(axes.get("толщина_мм", [])))],
                        "норма_мин_м": [self._parse(self.entries[(section, gost, "норма_мин_м", i)])
                                        for i in range(len(axes.get("норма_мин_м", [])))],
                    }
                    for gost, axes in table.items()
                }
                continue
            if section == "ФАСКИ_СВАРКА":
                out[section] = [
                    {
                        "макс_толщина_мм": self._parse(self.entries[(section, idx, "макс_толщина_мм", None)]),
                        "толщина_мм": [self._parse(self.entries[(section, idx, "толщина_мм", i)])
                                       for i in range(len(cfg.get("толщина_мм", [])))],
                        "норма_мм_мин": [self._parse(self.entries[(section, idx, "норма_мм_мин", i)])
                                         for i in range(len(cfg.get("норма_мм_мин", [])))],
                    }
                    for idx, cfg in enumerate(table)
                ]
                continue
            first_val = next(iter(table.values()))
            if isinstance(first_val, dict):
                out[section] = {
                    outer: {inner: self._parse(self.entries[(section, outer, inner)])
                            for inner in inner_table}
                    for outer, inner_table in table.items()
                }
            elif isinstance(first_val, list):
                out[section] = {
                    key: [self._parse(self.entries[(section, key, 0)]),
                          self._parse(self.entries[(section, key, 1)])]
                    for key in table
                }
            else:
                out[section] = {key: self._parse(self.entries[(section, key, None)])
                                for key in table}
        return out

    @staticmethod
    def _parse(entry):
        text = entry.get().strip().replace(",", ".")
        if not text:
            return 0
        num = float(text)  # ValueError перехватывается в _save
        return int(num) if num == int(num) else num
