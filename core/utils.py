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
    """Универсальный фрейм с вертикальной прокруткой"""
    def init(self, container, *args, **kwargs):
        super().init(container, *args, **kwargs)

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
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 6. Обновляем область прокрутки при изменении размера внутреннего фрейма
        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # 7. Заставляем внутренний фрейм растягиваться по ширине Canvas
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # 8. Биндим прокрутку колесиком мыши
        self.bind_mouse_scroll(self.inner_frame)

    def _on_canvas_configure(self, event):
        """Растягиваем внутренний фрейм по ширине холста"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def bind_mouse_scroll(self, widget):
        """Рекурсивно биндим колесико мыши ко всем элементам (важно для Windows/Mac)"""
        widget.bind("<Enter>", self._bind_wheel)
        widget.bind("<Leave>", self._unbind_wheel)

    def _bind_wheel(self, event):
        # Для Windows и Mac
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_wheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:  # Вверх
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0: # Вниз
            self.canvas.yview_scroll(1, "units")