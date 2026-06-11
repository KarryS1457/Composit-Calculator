import tkinter as tk
from tkinter import messagebox

import core.data as data
from core.utils import ScrollableFrame


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
        tk.Label(self, text="Измените значения и нажмите «СОХРАНИТЬ». "
                            "Нормы применяются сразу, без перезапуска.",
                 font=("Arial", 9), fg="#7f8c8d").pack(pady=(0, 10))

        scroll = ScrollableFrame(self)
        scroll.pack(fill="both", expand=True)
        body = scroll.inner_frame

        self.norms = data.norms_as_dict()
        for section, table in self.norms.items():
            self._render_section(body, section, table)

        # Привязываем прокрутку к созданным полям (они появились после
        # конструктора ScrollableFrame)
        scroll.bind_mouse_scroll(body, recursive=True)

        bottom = tk.Frame(self)
        bottom.pack(fill="x", pady=10)
        tk.Button(bottom, text="СОХРАНИТЬ", bg="#27ae60", fg="white",
                  font=("Arial", 12, "bold"),
                  command=self._save).pack(fill="x", ipady=5)
        self.lbl_status = tk.Label(bottom, text="", font=("Arial", 10))
        self.lbl_status.pack(pady=(5, 0))

    def _render_section(self, parent, section, table):
        box = tk.LabelFrame(parent, text=section, font=("Arial", 11, "bold"),
                            fg="#2c3e50", padx=10, pady=10)
        box.pack(fill="x", pady=10, padx=5)

        help_text = data.NORMS_HELP.get(section)
        if help_text:
            tk.Label(box, text=help_text, font=("Arial", 8), fg="#7f8c8d",
                     wraplength=550, justify="left").pack(anchor="w", pady=(0, 8))

        grid = tk.Frame(box)
        grid.pack(anchor="w")

        first_val = next(iter(table.values()))
        if isinstance(first_val, dict):
            self._render_nested(grid, section, table)
        elif isinstance(first_val, list):
            self._render_ranges(grid, section, table)
        else:
            self._render_flat(grid, section, table)

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
        self.lbl_status.config(text="Нормы сохранены и применены", fg="#27ae60")

    def _collect(self):
        out = {}
        for section, table in self.norms.items():
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
