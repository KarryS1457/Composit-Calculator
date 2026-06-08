import ezdxf
import math
import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES

def analyze_dxf_geometry(dxf_file_path, target_layer=None):
    try:
        doc = ezdxf.readfile(dxf_file_path)
        msp = doc.modelspace()
        total_length = 0.0
        
        # Словарь для подсчета количества вхождений каждой точки
        point_counts = {}

        def add_point(p):
            # Округляем до 3 знаков (до микронов), чтобы сгладить мелкие погрешности CAD-систем
            coord = (round(p.x, 3), round(p.y, 3))
            point_counts[coord] = point_counts.get(coord, 0) + 1

        def process_primitive(entity):
            length = 0.0
            if entity.dxftype() == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                length = math.hypot(end.x - start.x, end.y - start.y)
                
                # Добавляем начало и конец отрезка в словарь
                add_point(start)
                add_point(end)

            elif entity.dxftype() == 'CIRCLE':
                length = 2 * math.pi * entity.dxf.radius
                # Круг всегда замкнут сам на себя, его точки учитывать не нужно

            elif entity.dxftype() == 'ARC':
                radius = entity.dxf.radius
                start_angle = math.radians(entity.dxf.start_angle)
                end_angle = math.radians(entity.dxf.end_angle)
                if end_angle < start_angle:
                    end_angle += 2 * math.pi
                length = radius * (end_angle - start_angle)
                
                # У дуги ezdxf есть встроенные свойства start_point и end_point
                add_point(entity.start_point)
                add_point(entity.end_point)

            return length

        for entity in msp:
            if target_layer and entity.dxf.layer != target_layer:
                continue

            if entity.dxftype() in ['LINE', 'CIRCLE', 'ARC']:
                total_length += process_primitive(entity)
            
            elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE', 'SPLINE']:
                for sub_entity in entity.virtual_entities():
                    total_length += process_primitive(sub_entity)

        # Анализ топологии: ищем точки, которые встречаются нечетное количество раз (обычно 1)
        open_ends = sum(1 for count in point_counts.values() if count % 2 != 0)
        
        # Если "висячих" концов нет, контур замкнут
        is_closed = (open_ends == 0)
        
        # Количество самих разрывов равно количеству свободных концов, поделенному на 2
        gaps_count = open_ends // 2

        return total_length, is_closed, gaps_count

    except Exception as e:
        raise Exception(f"Ошибка при чтении DXF: {e}")

# --- Логика интерфейса ---

def process_file(file_path):
    clean_path = file_path.strip('{}')
    filename = os.path.basename(clean_path)
    
    try:
        # Функция возвращает три параметра (Длина, замкнутость, кол-во разрывов)
        length_mm, is_closed, gaps_count = analyze_dxf_geometry(clean_path)
        length_m = length_mm / 1000
        
        # Формируем статус замкнутости
        if is_closed:
            closure_status = "Да (Контур цельный)"
            status_color = "#006600" # Зеленый
        else:
            closure_status = f"НЕТ! Обнаружено разрывов: {gaps_count}"
            status_color = "#CC0000" # Красный
        
        result_text.set(
            f"Файл: {filename}\n"
            f"────────────────────────\n"
            f"Длина контура: {length_mm:.2f} мм\n"
            f"В метрах: {length_m:.3f} м\n"
            f"────────────────────────\n"
            f"Замкнут: {closure_status}"
        )
        
        # Окрашиваем текст в зависимости от результата проверки замкнутости контура
        result_label.config(fg=status_color)
        
    except Exception as e:
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

# Настройка графического интерфейса

root = TkinterDnD.Tk()
root.title("Анализ контуров | Comp-Norm-Calc")
root.geometry("400x280")
root.eval('tk::PlaceWindow . center')

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', handle_drop)

label = tk.Label(root, text="Перетащите DXF-файл сюда\nили нажмите кнопку для выбора файла вручную", pady=10, font=("Arial", 10))
label.pack()

calc_btn = tk.Button(root, text="Выбрать файл вручную", command=select_file_and_calculate, height=2, width=30)
calc_btn.pack(pady=5)

result_text = tk.StringVar()
result_text.set("Ожидание файла...")

result_label = tk.Label(
    root, 
    textvariable=result_text, 
    font=("Consolas", 11), 
    pady=10, 
    justify="center"
)
result_label.pack()

root.mainloop()