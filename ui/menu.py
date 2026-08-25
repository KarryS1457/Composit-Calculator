import os
import tkinter as tk
from tkinter import messagebox

from core import data
from core.updater import IS_BETA, VERSION


class ToggleSwitch(tk.Canvas):
    """Двухпозиционный переключатель, который реагирует на клик.

    Раньше здесь стоял tk.Scale с диапазоном 0..1: при длине 64 и бегунке 30
    на ход оставалось около тридцати пикселей, попасть в них мышью почти
    невозможно, и виджет выглядел и вел себя как индикатор, а не как кнопка.
    Рисуем переключатель сами: любой клик по нему меняет положение.
    """

    W, H = 56, 26

    def __init__(self, parent, on_toggle, bg=None):
        super().__init__(parent, width=self.W, height=self.H,
                         highlightthickness=0, bd=0, cursor="hand2",
                         bg=bg or parent.cget("bg"))
        self._on_toggle = on_toggle
        self._state = False
        self.bind("<Button-1>", self._click)
        self._draw()

    def get(self):
        return self._state

    def set(self, state):
        """Задать положение снаружи — БЕЗ вызова обработчика, иначе
        обновление вида из _refresh_source_view() зациклилось бы."""
        state = bool(state)
        if state != self._state:
            self._state = state
        self._draw()

    def _click(self, _event):
        self._state = not self._state
        self._draw()
        self._on_toggle(self._state)

    def _draw(self):
        self.delete("all")
        h, w, r = self.H, self.W, self.H // 2
        track = "#2c3e50" if self._state else "#bdc3c7"
        # дорожка со скругленными краями: два круга и прямоугольник между ними
        self.create_oval(0, 0, h, h, fill=track, outline=track)
        self.create_oval(w - h, 0, w, h, fill=track, outline=track)
        self.create_rectangle(r, 0, w - r, h, fill=track, outline=track)
        # бегунок
        cx = (w - r) if self._state else r
        self.create_oval(cx - r + 3, 3, cx + r - 3, h - 3,
                         fill="white", outline="#7f8c8d")


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

        # Обе подписи тоже кликабельны: попасть по слову проще, чем по
        # переключателю, и это привычнее, чем тянуть ползунок.
        self.lbl_server = tk.Label(row, text="СЕРВЕРНЫЕ", font=("Arial", 9, "bold"),
                                   cursor="hand2")
        self.lbl_server.pack(side="left", padx=(0, 8))
        self.lbl_server.bind("<Button-1>",
                             lambda _e: self._set_source(data.SOURCE_SHARED))

        self.toggle = ToggleSwitch(row, self._on_toggle, bg=row.cget("bg"))
        self.toggle.pack(side="left")

        self.lbl_local = tk.Label(row, text="ЛОКАЛЬНЫЕ", font=("Arial", 9, "bold"),
                                  cursor="hand2")
        self.lbl_local.pack(side="left", padx=(8, 0))
        self.lbl_local.bind("<Button-1>",
                            lambda _e: self._set_source(data.SOURCE_MY))

        self.lbl_source_info = tk.Label(box, font=("Arial", 8), fg="#7f8c8d",
                                        wraplength=560, justify="center")
        self.lbl_source_info.pack(pady=(6, 0))

        self._refresh_source_view()

    def _on_toggle(self, is_local):
        """Вызывается самим переключателем после клика по нему."""
        self._set_source(data.SOURCE_MY if is_local else data.SOURCE_SHARED)

    def _set_source(self, src):
        if src == data.get_active_source():
            self._refresh_source_view()   # вернуть вид в согласованное состояние
            return
        try:
            data.set_active_source(src)
        except Exception as e:
            messagebox.showerror("Нормы", f"Не удалось переключить нормы: {e}")
        self._refresh_source_view()

    def _refresh_source_view(self):
        """Подсвечивает выбранную сторону и показывает, какой файл реально
        используется. Это важно: если личного файла норм еще нет, выбор
        "локальные" молча откатывается на серверные."""
        active = data.get_active_source()
        is_local = active == data.SOURCE_MY
        self.toggle.set(is_local)
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