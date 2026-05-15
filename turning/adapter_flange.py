import tkinter as tk
from core.utils import resource_path
from core.utils import ScrollableFrame
from PIL import Image, ImageTk


class adapter(tk.Frame):
    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.controller = presenter
        self.inputs = []
        
        self._resize_job = None
        
        # --- Кнопка "Назад" ---
        tk.Button(self, text="← НАЗАД В МЕНЮ", font=("Arial", 9),
                  fg="#7f8c8d", relief="flat",
                  command=self.go_back).pack(anchor="w", pady=(0, 20))


        main_content = tk.Frame(self)
        main_content.pack(fill="both", expand=True, padx=10)


        # Левый блок (Ввод параметров)
        left_frame = tk.Frame(main_content)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
                 
        self.add_label(left_frame, "--- ГЕОМЕТРИЯ ДЕТАЛИ ---", bold=True)
        self.ent_D = self.add_entry(left_frame, "Внешний диаметр D (мм):")
        self.ent_d = self.add_entry(left_frame, "Внутренний диаметр d (мм):")
        self.ent_t = self.add_entry(left_frame, "Габарит детали t (мм):")
        self.ent_DM = self.add_entry(left_frame, "Диаметр проточки DM (мм):")
        self.ent_ch5 = self.add_entry(left_frame, "Размер проточки ch5 (мм):")
        self.ent_Dk = self.add_entry(left_frame, "Диаметр торцевой канавы Dk max (мм):")
        self.ent_P = self.add_entry(left_frame, "Глубина канавы P (мм):")
        self.ent_n = self.add_entry(left_frame, "Количество канав n:")


        self.add_label(left_frame, "--- ПАРАМЕТРЫ ЗАГОТОВКИ ---", bold=True)
        self.ent_D1 = self.add_entry(left_frame, "Внешний диаметр заготовки D1 (мм):")
        self.ent_D2 = self.add_entry(left_frame, "Внутренний диаметр заготовки D2 (мм):")
        self.ent_S = self.add_entry(left_frame, "Толщина листа S (мм):")


        # Правый блок (Эскиз)
        self.right_frame = tk.Frame(main_content, bg="#ffffff", width=400)
        self.right_frame.pack(side="right", fill="both", expand=True)


        self.btn_show_img = tk.Button(self.right_frame, text="ПОКАЗАТЬ ЭСКИЗ",
                                     command=self.open_full_image)
        self.btn_show_img.pack(expand=True)


        self.img_label = tk.Label(self.right_frame, bg="#ffffff")
        self.img_label.pack(expand=True)
       
        self.bind("<Configure>", self.on_resize)
        self.set_image(resource_path("pics/adapterflange.jpg"))


        # Нижний блок
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)


        self.btn_calc = tk.Button(bottom_frame, text="РАССЧИТАТЬ", bg="#2c3e50", fg="white",
                                 font=("Arial", 12, "bold"), command=self.run_calculation)
        self.btn_calc.pack(fill="x", pady=(0, 10), ipady=5)


        self.res_box = tk.Label(bottom_frame, text="Результат появится здесь",
                               font=("Consolas", 10), bg="#ecf0f1", relief="sunken",
                               height=8, anchor="nw", justify="left", padx=10, pady=10)
        self.res_box.pack(fill="x")


    def add_label(self, parent, text, bold=False):
        f = ("Arial", 10, "bold") if bold else ("Arial", 10)
        tk.Label(parent, text=text, font=f).pack(anchor="w", pady=(10, 2))


    def add_entry(self, parent, text):
        tk.Label(parent, text=text).pack(anchor="w")
        e = tk.Entry(parent, validate="key", validatecommand=self.controller.vcmd)
        e.pack(fill="x", pady=(0, 5))
        e.bind("<Return>", self.move_focus)
        self.inputs.append(e)
        return e


    def set_image(self, path):
        try:
            # Загружаем оригинал и храним его в памяти
            self.original_img = Image.open(path)
            self._update_image_display()
        except Exception as e:
            self.img_label.config(text=f"Файл {path} не найден", image='')
            self.original_img = None

    def _update_image_display(self):
        """Метод для перерисовки картинки под текущий размер контейнера"""
        if not hasattr(self, 'original_img') or self.original_img is None:
            return

        # Берем актуальные размеры правой панели
        win_w = self.right_frame.winfo_width()
        win_h = self.right_frame.winfo_height()

        # Если окно только открылось, размеры могут быть 1x1, задаем минимум
        if win_w < 10: win_w, win_h = 350, 350

        # Рассчитываем размер картинки (с отступами)
        # Учитываем пропорции оригинала через thumbnail
        img_copy = self.original_img.copy()
        img_copy.thumbnail((win_w - 30, win_h - 30), Image.Resampling.LANCZOS)
        
        self.photo = ImageTk.PhotoImage(img_copy)
        self.img_label.config(image=self.photo)

    def on_resize(self, event):
        # Обрабатываем событие только если изменился размер всего фрейма детали
        if event.widget == self:
            
            # 1. Быстро переключаем элементы интерфейса (это легкая операция, делаем сразу)
            if event.width > 650:
                self.btn_show_img.pack_forget()
                self.img_label.pack(expand=True, fill="both")
            else:
                self.img_label.pack_forget()
                self.btn_show_img.pack(expand=True)

            # 2. Логика Debounce для тяжелой картинки
            # Если таймер уже был запущен, отменяем его
            if self._resize_job is not None:
                self.after_cancel(self._resize_job)
            
            # Запускаем новый таймер. 
            # Картинка перерисуется только если окно не меняло размер 150 миллисекунд
            if event.width > 650:
                self._resize_job = self.after(150, self._update_image_display)

    def open_full_image(self):
        top = tk.Toplevel(self)
        top.title("Чертеж")
        
        if hasattr(self, 'original_img') and self.original_img:
            top.full_photo = ImageTk.PhotoImage(self.original_img)
            tk.Label(top, image=top.full_photo).pack(padx=10, pady=10)

    def move_focus(self, event):
        idx = self.inputs.index(event.widget)
        if idx < len(self.inputs) - 1:
            self.inputs[idx+1].focus_set()
        else:
            self.run_calculation()
        return "break"

    def go_back(self):
        self.controller.show_lathe_menu()


    def run_calculation(self):
        try:
            payload = {
                "D": float(self.ent_D.get() or 0),
                "d": float(self.ent_d.get() or 0),
                "t": float(self.ent_t.get() or 0),
                "DM": float(self.ent_DM.get() or 0),
                "ch5": float(self.ent_ch5.get() or 0),
                "Dk": float(self.ent_Dk.get() or 0),
                "P": float(self.ent_P.get() or 0),
                "n": float(self.ent_n.get() or 0),
                "D1": float(self.ent_D1.get() or 0),
                "D2": float(self.ent_D2.get() or 0),
                "S": float(self.ent_S.get() or 0)
            }
            self.controller.handle_lathe_calculation("adapter", payload)
        except ValueError:
            self.res_box.config(text="ОШИБКА: Проверьте ввод", fg="red")


    def show_results(self, text):
        self.res_box.config(text=text, fg="#2c3e50")