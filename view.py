import tkinter as tk

class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        # Базовые настройки окна (берем из твоего исходного кода)
        self.title("Калькулятор Composit")
        self.geometry("700x850")
        self.minsize(400, 650)

        try:
            self.app_icon=tk.PhotoImage(file="icon.ico")
            self.iconphoto(False, self.app_icon)
        except Exception as e:
            print ("Ошибка загрузки иконки: {e}")

        # Контейнер для экранов (MainMenu, TabWeld и т.д.)
        # Мы будем удалять старые виджеты внутри него и вставлять новые
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
        from tkinter import messagebox
        messagebox.showerror("Ошибка", message)
