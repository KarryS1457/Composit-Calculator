import os
import sys
import tkinter as tk

def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу, работает для dev и для PyInstaller """
    try:
        # PyInstaller создает временную папку _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ScrollableFrame(tk.Frame):
    """Универсальный фрейм с вертикальной прокруткой.

    horizontal=True добавляет ещё и горизонтальную прокрутку. В этом режиме
    внутренний фрейм НЕ растягивается по ширине холста (иначе содержимое
    шире окна было бы обрезано), поэтому широкие таблицы можно проматывать
    вбок — ползунком снизу или Shift+колесо мыши."""
    # ИСПРАВЛЕНО: Добавлены двойные подчеркивания для __init__
    def __init__(self, container, *args, horizontal=False, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.horizontal = horizontal

        # 1. Создаем Canvas (он умеет прокручиваться)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)

        # 2. Создаем ползунок и привязываем его к Canvas
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 3. Создаем внутренний фрейм, в который будем класть виджеты
        self.inner_frame = tk.Frame(self.canvas)

        # 4. Помещаем inner_frame внутрь Canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # 5. Размещаем Canvas и Scrollbar
        if self.horizontal:
            self.hscrollbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.canvas.configure(xscrollcommand=self.hscrollbar.set)
            self.hscrollbar.pack(side="bottom", fill="x")
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # 6. Обновляем область прокрутки при изменении размера внутреннего
        #    фрейма. Делаем это с задержкой (debounce): во время перетаскивания
        #    окна события сыплются десятками в секунду, а пересчитывать
        #    scrollregion нужно лишь когда содержимое реально устоялось.
        #    Иначе при сотнях полей (редактор норм) тянучка окна тормозит.
        self._sr_job = None
        self.inner_frame.bind("<Configure>", self._schedule_scrollregion)

        # 7. Заставляем внутренний фрейм растягиваться по ширине Canvas
        #    (только без горизонтальной прокрутки — иначе широкое содержимое
        #    зажималось бы по ширине окна и прокручивать вбок было бы нечего)
        if not self.horizontal:
            self.canvas.bind("<Configure>", self._on_canvas_configure)

        # 8. Биндим прокрутку колесиком мыши на canvas и на все дочерние
        # виджеты (поля ввода, метки и т.д.), т.к. события Enter/Leave
        # внутреннего фрейма не доходят до области под дочерними виджетами.
        self.bind_mouse_scroll(self.canvas)
        # Дочерние виджеты добавляются позже (в конструкторе экрана-наследника),
        # поэтому привязываем рекурсивно после завершения построения интерфейса.
        self.after(100, lambda: self.bind_mouse_scroll(self.inner_frame, recursive=True))

    def _schedule_scrollregion(self, event=None):
        """Откладываем пересчет области прокрутки до паузы в потоке событий."""
        if self._sr_job is not None:
            self.canvas.after_cancel(self._sr_job)
        self._sr_job = self.canvas.after(120, self._update_scrollregion)

    def _update_scrollregion(self):
        self._sr_job = None
        if self.canvas.winfo_exists():
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Растягиваем внутренний фрейм по ширине холста"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def bind_mouse_scroll(self, widget, recursive=False):
        """Биндим колесико мыши напрямую на виджет (и опционально на всех потомков)"""
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind("<Button-4>", self._on_mousewheel, add="+")
        widget.bind("<Button-5>", self._on_mousewheel, add="+")
        if self.horizontal:
            # Shift+колесо — горизонтальная прокрутка
            widget.bind("<Shift-MouseWheel>", self._on_shift_mousewheel, add="+")
            widget.bind("<Shift-Button-4>", self._on_shift_mousewheel, add="+")
            widget.bind("<Shift-Button-5>", self._on_shift_mousewheel, add="+")
        if recursive:
            for child in widget.winfo_children():
                self.bind_mouse_scroll(child, recursive=True)

    def _on_mousewheel(self, event):
        # Универсальная обработка прокрутки
        if event.num == 4 or event.delta > 0:  # Вверх
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0: # Вниз
            self.canvas.yview_scroll(1, "units")

    def _on_shift_mousewheel(self, event):
        # Горизонтальная прокрутка (Shift + колесо)
        if event.num == 4 or event.delta > 0:  # Влево
            self.canvas.xview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:  # Вправо
            self.canvas.xview_scroll(1, "units")