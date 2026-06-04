import ezdxf
import math
import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES

def calculate_cutting_length(dxf_file_path, target_layer=None):
    try:
        doc = ezdxf.readfile(dxf_file_path)
        msp = doc.modelspace()
        total_length = 0.0

        def calc_primitive_length(entity):
            length = 0.0
            if entity.dxftype() == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                length = math.hypot(end.x - start.x, end.y - start.y)
            elif entity.dxftype() == 'CIRCLE':
                length = 2 * math.pi * entity.dxf.radius
            elif entity.dxftype() == 'ARC':
                radius = entity.dxf.radius
                start_angle = math.radians(entity.dxf.start_angle)
                end_angle = math.radians(entity.dxf.end_angle)
                if end_angle < start_angle:
                    end_angle += 2 * math.pi
                length = radius * (end_angle - start_angle)
            return length

        for entity in msp:
            if target_layer and entity.dxf.layer != target_layer:
                continue

            if entity.dxftype() in ['LINE', 'CIRCLE', 'ARC']:
                total_length += calc_primitive_length(entity)
            
            elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE', 'SPLINE']:
                for sub_entity in entity.virtual_entities():
                    total_length += calc_primitive_length(sub_entity)

        return total_length

    except Exception as e:
        raise Exception(f"Ошибка при чтении DXF: {e}")

# --- Логика интерфейса ---

def process_file(file_path):
    """Выполняет расчет и обновляет текст в главном окне"""
    clean_path = file_path.strip('{}')
    # Получаем только имя файла из полного пути
    filename = os.path.basename(clean_path)
    
    try:
        length_mm = calculate_cutting_length(clean_path)
        length_m = length_mm / 1000
        
        # Формируем строку с результатом и выводим в окно
        result_text.set(
            f"Файл: {filename}\n"
            f"────────────────────────\n"
            f"Длина контура: {length_mm:.2f} мм\n"
            f"В метрах: {length_m:.3f} м"
        )
        # Если до этого была ошибка (красный текст), возвращаем черный
        result_label.config(fg="#333333") 
        
    except Exception as e:
        # Выводим ошибку прямо в окно красным цветом
        result_text.set(f"Ошибка загрузки:\n{filename}\n{str(e)}")
        result_label.config(fg="red")

def select_file_and_calculate():
    file_path = filedialog.askopenfilename(
        title="Выберите DXF чертеж",
        filetypes=[("DXF Files", "*.dxf"), ("All Files", "*.*")]
    )
    if file_path:
        process_file(file_path)

def handle_drop(event):
    process_file(event.data)

# --- Настройка графического окна ---

root = TkinterDnD.Tk()
root.title("Анализ контуров | Comp-Norm-Calc")
# Немного увеличим окно, чтобы вместить текст
root.geometry("400x250")
root.eval('tk::PlaceWindow . center')

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', handle_drop)

label = tk.Label(root, text="Перетащите DXF-файл сюда\nили нажмите кнопку", pady=10, font=("Arial", 10))
label.pack()

calc_btn = tk.Button(root, text="Выбрать файл вручную", command=select_file_and_calculate, height=2, width=30)
calc_btn.pack(pady=5)

# --- Блок вывода результатов ---
# Переменная, которая будет динамически менять текст в Label
result_text = tk.StringVar()
result_text.set("Ожидание файла...")

# Само текстовое поле для результата
result_label = tk.Label(
    root, 
    textvariable=result_text, 
    font=("Consolas", 11), 
    pady=15, 
    justify="center",
    fg="#555555" # Темно-серый цвет по умолчанию
)
result_label.pack()

root.mainloop()