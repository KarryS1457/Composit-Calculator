import os
import sys
import tkinter as tk
from tkinter import messagebox  # Вынесли импорт наверх по стандарту PEP 8


def _resource_path(name):
    """Путь к файлу ресурса (icon.ico и т.п.) — как рядом со скриптом
    при разработке, так и внутри распакованной .exe (PyInstaller)."""
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, name)


class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        # Базовые настройки окна
        self.title("Калькулятор Composit")
        self.geometry("700x850")
        self.minsize(400, 650)

        # Загрузка иконки (заголовок окна, панель задач)
        try:
            # Для Windows и .exe сборок метод iconbitmap работает с .ico идеально
            self.iconbitmap(_resource_path("icon.ico"))
        except Exception as e:
            # Добавлена f перед строкой, чтобы переменная {e} сработала
            print(f"Ошибка загрузки иконки: {e}")

        # Контейнер для экранов (MainMenu, TabWeld и т.д.)
        self.container = tk.Frame(self, padx=20, pady=20)
        self.container.pack(fill="both", expand=True)

        # Слой для секретной пасхалки (поверх всего)
        self.secret_label = tk.Label(self, bg="white")

        # Переменная для функции валидации (будет назначена презентером)
        self.vcmd = None

    def set_vcmd(self, vcmd_tuple):
        """Метод для регистрации функции валидации из модели"""
        self.vcmd = vcmd_tuple

    def clear_screen(self):
        """Полностью очищает основной контейнер"""
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_secret_image(self, photo_image):
        """Метод для отображения секретной картинки"""
        self.secret_label.config(image=photo_image)
        self.secret_label.image = photo_image # Сохраняем ссылку, чтобы сборщик мусора не удалил фото
        self.secret_label.place(relx=0.5, rely=0.5, anchor="center")
        self.secret_label.lift()

    def hide_secret_image(self):
        """Прячет секретную картинку"""
        self.secret_label.place_forget()

    def show_error(self, message):
        """Универсальный метод для вывода критических ошибок в окно"""
        messagebox.showerror("Ошибка", message)