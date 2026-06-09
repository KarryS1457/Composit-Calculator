import math
import core.data as data
from core.data import TURNING_DATA, RANGES_DATA, AWC_S, AWC_DATA
from core.logger import log

def trend_extrapolation(x_val, x_list, y_list):
    n_points = min(4, len(x_list))
    x = x_list[:n_points] if x_val < x_list[0] else x_list[-n_points:]
    y = y_list[:n_points] if x_val < x_list[0] else y_list[-n_points:]
    n = len(x)
    sum_x, sum_y = sum(x), sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi**2 for xi in x)
    denom = (n * sum_x2 - sum_x**2)
    if denom == 0: return y[-1]
    m = (n * sum_xy - sum_x * sum_y) / denom
    b = (sum_y - m * sum_x) / n
    return m * x_val + b

def get_val_by_thickness(thickness, x_list, y_list):
    if thickness in x_list: return y_list[x_list.index(thickness)]
    if thickness < x_list[0] or thickness > x_list[-1]: 
        return trend_extrapolation(thickness, x_list, y_list)
    for i in range(len(x_list) - 1):
        if x_list[i] < thickness < x_list[i+1]:
            x1, x2, y1, y2 = x_list[i], x_list[i+1], y_list[i], y_list[i+1]
            return y1 + (thickness - x1) * (y2 - y1) / (x2 - x1)
    return y_list[-1]

def calculate_turning_parameters(target_diam):
    main_machine_name = None
    # Определяем основной станок по диапазонам из RANGES_DATA
    for name, (low, high) in RANGES_DATA.items():
        if low <= target_diam <= high:
            main_machine_name = name
            break

    main_res = None
    alternatives = []

    # Ищем данные в TURNING_DATA
    for machine, (diams, rpms) in TURNING_DATA.items():
        if min(diams) <= target_diam <= max(diams):
            nearest_diam = min(diams, key=lambda x: abs(x - target_diam))
            idx = diams.index(nearest_diam)
            rpm_value = rpms[idx]

            m_data = {
                "machine": machine,
                "rpm": rpm_value,
                "table_diam": nearest_diam
            }

            if machine == main_machine_name:
                main_res = m_data
            else:
                alternatives.append(m_data)

    return main_res, alternatives

def get_AWC_coeff(target_d, target_s):
    d_keys = sorted(AWC_DATA.keys())
    row_key = d_keys[0]
    for d in d_keys:
        if d <= target_d:
            row_key = d
        else:
            break

    col_idx = 0
    for i, s in enumerate(AWC_S):
        if s <= target_s:
            col_idx = i
        else:
            break

    return AWC_DATA[row_key][col_idx]

def calculate_weld_logic(gost, s, l_mm, m, k_lp, k_pos, k_posture, weld_data, chamfer_data):
    weld_info = weld_data[gost]
    th_list, tm_list = weld_info[0], weld_info[1]

    k_obsl = 1.14

    if gost == "C4":
        t_cham = 0
    else:
        sel_ch = chamfer_data[-1]
        for cfg in chamfer_data:
            if s <= cfg['max_s']:
                sel_ch = cfg
                break

        k_cham = 1 if s <= 70 else 2
        v_cham = get_val_by_thickness(s, sel_ch['x'], sel_ch['y'])
        t_cham = (l_mm / v_cham) * k_cham / 60 if v_cham > 0 else 0

    t_kran = 4 if m >= 15 else 0.5
    t_mark = 0.83
    t_base = max(get_val_by_thickness(s, th_list, tm_list), 0.1)

    l_m = l_mm / 1000
    k_c4_extra = 1.2 if gost == "C4" else 1.0 

    t_nsh = t_base * k_pos * k_posture * k_obsl * k_c4_extra
    t_prep = t_kran + t_mark
    t_vn = t_prep + t_cham
    t_sht_min = (t_nsh * l_m + t_vn) * k_lp

    return {
        "total_sec": int(t_sht_min * 60),
        "prep": t_prep,
        "chamfer": t_cham,
        "weld": t_nsh * l_m,
        "gost": gost,
        "s": s
    }

def calculate_lathe_time(item_type, p, m_info):
    # Вспомогательная функция для безопасного извлечения чисел
    def to_float(val):
        if isinstance(val, list):
            return to_float(val[0]) if val else 0.0
        try:
            return float(val or 0)
        except (ValueError, TypeError):
            return 0.0

    try:
        t = to_float(p.get('t', 0))
        S = to_float(p.get('S', 0))
        D = to_float(p.get('D', 0))
        d = to_float(p.get('d', 0))
        
        user_D1 = to_float(p.get('D1', 0))
        user_D2 = to_float(p.get('D2', 0))

        # Считываем остальные параметры за один проход во избежанию падений
        a = to_float(p.get('a', 0))
        c = to_float(p.get('c', 0))
        m = to_float(p.get('m', 0))
        DW = to_float(p.get('DW', 0))
        DM = to_float(p.get('DM', 0))
        Dc = to_float(p.get('Dc', 0))
        Dm = to_float(p.get('Dm', 0))
        Da = to_float(p.get('Da', 0))
        Dt = to_float(p.get('Dt', 0))
        c1 = to_float(p.get('c1', 0))
        c2 = to_float(p.get('c2', 0))
        m1 = to_float(p.get('m1', 0))
        m2 = to_float(p.get('m2', 0))
        Dc1 = to_float(p.get('Dc1', 0))
        Dc2 = to_float(p.get('Dc2', 0))
        Dm1 = to_float(p.get('Dm1', 0))
        Dm2 = to_float(p.get('Dm2', 0))
    except Exception:
        return 0.0


    # Синхронизация названий типов для SHEET_PRODUCTS во избежание багов со строками
    normalized_type = item_type
    if item_type == "welding_flange": normalized_type = "weldflange"
    if item_type == "welding_tnf": normalized_type = "weldingtnf"

    allowance = 6.0
    if normalized_type in data.SHEET_PRODUCTS:
        thresholds = sorted(data.ADMISSION_DATA.keys(), reverse=True)
        for thr in thresholds:
            if S >= thr:
                val = data.ADMISSION_DATA[thr]
                allowance = to_float(val[0] if isinstance(val, list) else val)
                break

    D1_auto = D + allowance
    
    # Фактический диаметр, по которому пойдёт обработка
    final_D1 = user_D1 if user_D1 > 0 else D1_auto
    D2 = user_D2 if user_D2 > 0 else (max(0.0, d - allowance) if d > 0 else 0.0)


    log.debug(f"Старт расчета {item_type}. Параметры GUI: {p}, Станок: {m_info.get('machine')}")

    # Определяем станок по готовому диаметру детали D (как в эталонном Excel)
    current_machine = m_info.get('machine')
    for name, (low, high) in data.RANGES_DATA.items():
        if low <= D <= high:
            if current_machine != name:
                log.warning(f"АВТОКОРРЕКЦИЯ: Станок изменен с {current_machine} на {name} "
                            f"(диаметр детали {D} мм)")
            current_machine = name
            break

    # Обновляем технологические параметры под актуальный станок
    m_params = data.FEEDRATE_DATA.get(current_machine, [3, 3, 0.15, 0.25, 1500])
    siem_long, siem_transverse, feed_turn, feed_face, chamfer_speed = m_params

    # Локальная функция точного поиска оборотов шпинделя
    def get_rpm_for_diam(diameter):
        diams, rpms = data.TURNING_DATA.get(current_machine, ([], []))
        if diams:
            nearest_diam = min(diams, key=lambda x: abs(x - diameter))
            return rpms[diams.index(nearest_diam)]
        return to_float(m_info.get('rpm', 100))


    D1 = user_D1 if user_D1 > 0 else D1_auto
    D2 = user_D2 if user_D2 > 0 else (max(0.0, d - allowance) if d > 0 else 0.0)

    p['D1'], p['D2'], p['S'] = D1, D2, S
    delta_S = S - t

    def get_facing_time(d_start, d_end, thickness):
        if thickness <= 0 or abs(d_start - d_end) < 0.01: return 0
        path_length = abs(d_start - d_end)  # полный диаметр (как в Excel)
        avg_diameter = (d_start + d_end) / 2
        rpm_f = get_rpm_for_diam(avg_diameter)
        speed_f = feed_face * rpm_f
        if speed_f <= 0: return 0
        passes_f = max(2, math.ceil((thickness / 2) / siem_transverse))
        return (path_length * passes_f) / speed_f

    def get_turning_time(d_start, d_end, length):
        if length <= 0 or abs(d_start - d_end) < 0.1: return 0
        rpm_t = get_rpm_for_diam(max(d_start, d_end))
        speed_t = feed_turn * rpm_t
        if speed_t <= 0: return 0
        radial_depth = abs(d_start - d_end) / 2
        passes_t = max(2, math.ceil(radial_depth / siem_long))
        return (abs(length) * passes_t) / speed_t

    def get_chamfer_time(chamfers):
        """chamfers: список длин фасок в мм (уже с учётом угла, или как есть)"""
        import math as _math
        total = sum(ch / _math.cos(_math.radians(45)) for ch in chamfers if ch > 0)
        return total / chamfer_speed if chamfer_speed > 0 else 0


    # th_diameter ну же ли???
    def get_thread_time(th_diameter, th_pitch, th_lenght, th_pos, th_depth_cut, is_machine=True):
        # Используем данные из "Обороты резьба машин.csv"
        if th_pos: # Внешняя резьба
            rpm = 15 if is_machine else 10
        else:      # Внутренняя резьба
            rpm = 100 if is_machine else 12
            
        if rpm <= 0 or th_pitch <= 0: return 0.0
       
        th_depth = 0.6134 * th_pitch if th_pos else 0.5413 * th_pitch
        th_passes = math.ceil(th_depth / th_depth_cut)
        return (th_lenght * th_passes) / (rpm * th_pitch)

    def get_grooving_time(D_max, D_min, width, insert_width=3.0, feed_groove=0.1):
        """
        Расчет машинного времени на прорезание канавки (наружной или внутренней).
    
        :param D_max: Больший диаметр канавки (мм)
        :param D_min: Меньший диаметр канавки (мм)
        :param width: Ширина канавки по чертежу (мм)
        :param insert_width: Ширина канавочного резца (мм). По умолчанию 3.0 мм.
        :param feed_groove: Подача при врезании (мм/об). Обычно она меньше продольной, по умолчанию 0.1.
        :return: Машинное время в минутах
        """
        D_max = float(D_max)
        D_min = float(D_min)
        width = float(width)

        # Защита от нулевых или некорректных значений
        if width <= 0 or D_max <= D_min:
            return 0.0

        # 1. Радиальная глубина врезания (на одну сторону)
        h = (D_max - D_min) / 2.0

        # 2. Количество проходов (врезаний)
        # Округляем вверх: если канавка 10 мм, а резец 3 мм, понадобится 4 врезания
        passes = math.ceil(width / insert_width)

        # 3. Расчет оборотов шпинделя
        # Берем средний диаметр обработки для определения скорости резания
        D_avg = (D_max + D_min) / 2.0
        rpm = get_rpm_for_diam(D_avg)  # Эта функция уже должна быть в твоем коде

        if rpm <= 0:
            return 0.0

        # 4. Расчет времени одного врезания
        time_per_pass = h / (feed_groove * rpm)

        # Итоговое время = время одного врезания умножить на количество проходов
        total_time = time_per_pass * passes

        return total_time

    total_min = 0.0

    # --- ЛОГИКА ПО ТИПАМ ---
    if item_type == "adapter":
        ch5_val = to_float(p.get('ch5', 0))
        
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, t)
        t_face = get_facing_time(D1, D2, delta_S)
        t_turn_step = get_turning_time(D, DM, ch5_val)
        
        rpm_k = get_rpm_for_diam(to_float(p.get('Dk', 0)))
        t_grooves = (to_float(p.get('P', 0)) * to_float(p.get('n', 0))) / (0.1 * rpm_k) if rpm_k > 0 else 0
        
        t_chams = get_chamfer_time([to_float(p.get(f'ch{i}', 0)) for i in range(1, 5)])

        total_min = t_turn_out + t_turn_in + t_face + t_turn_step + t_grooves + t_chams

    elif item_type == "circle":
        t_turn_out = get_turning_time(D1, D, t)
        t_face = get_facing_time(D1, 0, delta_S)
        total_min = t_turn_out + t_face

    elif item_type == "compensator":
        E_val = to_float(p.get('E', 0))
        Dm1_val = to_float(p.get('Dm1', 0))
        dm2_val = to_float(p.get('dm2', 0))
        K_val = to_float(p.get('K', 0))

        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, t)
        t_face = get_facing_time(D1, D2, delta_S)
        
        t_turn_K = get_turning_time(dm2_val, d, K_val)
        t_turn_E = get_turning_time(Dm1_val, dm2_val, E_val)
        
        t_chams = get_chamfer_time([to_float(p.get(f'ch{i}', 0)) for i in range(1, 4)])

        total_min = t_turn_out + t_turn_in + t_face + t_turn_K + t_turn_E + t_chams

    elif item_type == "shell":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, t)
        t_face = get_facing_time(D1, D2, delta_S)
        total_min = t_turn_out + t_face + t_turn_in

    elif item_type == "forming":
        # 1. Основное наружное точение (от заготовки D1 до D на всю длину t)
        t_turn_out = get_turning_time(D1, D, t)
        
        # 2. Основное внутреннее растачивание (от отверстия заготовки D2 до d на всю длину t)
        t_turn_in = get_turning_time(d, D2, t)
        
        # 3. Торцевание общее (снимаем припуск по торцу delta_S от D1 до D2)
        t_face = get_facing_time(D1, D2, delta_S)
        
        # 4. Наружная проточка (ступень от наружного D до DM на глубину a)
        t_face_a = get_facing_time(D, DM, a)
        
        # 5. Внутренняя расточка ступени (ИСПРАВЛЕНО: от готового d до DW на глубину c)
        t_face_c = get_facing_time(d, DW, c)
        
        # 6. ДОБАВЛЕНО: Снятие всех 4-х фасок по чертежу
        t_chams = get_chamfer_time([to_float(p.get(f'ch{i}', 0)) for i in range(1, 5)])
        
        total_min = t_turn_out + t_turn_in + t_face + t_face_a + t_face_c + t_chams

    elif item_type == "swivel":
        # 1. Наружное точение (от заготовки D1 до D на всю длину t)
        t_turn_out = get_turning_time(D1, D, t)
        
        # 2. Внутреннее растачивание (от отверстия заготовки D2 до d на всю длину t)
        t_turn_in = get_turning_time(d, D2, t)
        
        # 3. Торцевание (снимаем припуск по торцу delta_S от D1 до D2)
        t_face = get_facing_time(D1, D2, delta_S)
        
        # 4. ДОБАВЛЕНО: Снятие фасок (ch1 и ch2 по чертежу)
        t_chams = get_chamfer_time([to_float(p.get('ch1', 0)), to_float(p.get('ch2', 0))])
        
        total_min = t_turn_out + t_turn_in + t_face + t_chams


    elif item_type == "weldring":
        b_val = to_float(p.get('b', 0))
        Dw_val = to_float(p.get('Dw', 0))
        DM_val = to_float(p.get('DM', 0))

        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, t - a)
        len_Dw = (S - b_val - (delta_S / 2))
        t_turn_Dw = get_turning_time(Dw_val, d, len_Dw)
        t_face = get_facing_time(D1, D2, delta_S)
        t_face_groove = get_facing_time(DM_val, D2, a)
        total_min = t_turn_out + t_turn_in + t_turn_Dw + t_face + t_face_groove

    elif item_type == "welding_tnf":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, t)
        t_face = get_facing_time(D1, D2, delta_S)
        t_turn_step = get_turning_time(DM, d, a)
        t_chams = get_chamfer_time([to_float(p.get(f'ch{i}', 0)) for i in range(1, 4)])
        total_min = t_turn_out + t_turn_in + t_face + t_turn_step + t_chams


    elif item_type == "welding_flange":
        b_val = to_float(p.get('b', 0))
        Dw_val = to_float(p.get('Dw', 0))

        # Наружное точение: длина = S (ширина пояска), скорость по среднему диаметру заготовки/детали
        passes_ext = max(2, math.ceil(((D1 - D) / 2) / siem_long))
        rpm_ext = get_rpm_for_diam((D1 + D) / 2)
        speed_ext = feed_turn * rpm_ext
        t_turn_out = (S * passes_ext) / speed_ext if speed_ext > 0 else 0

        # Внутреннее точение: та же скорость, что и наружное (как в Excel)
        passes_int = max(2, math.ceil(((d - D2) / 2 / 2) / siem_transverse))
        t_turn_in = (t * passes_int) / speed_ext if speed_ext > 0 else 0

        # Торцовка: полный диаметр D1→D2
        t_face = get_facing_time(D1, D2, delta_S)

        # 1-й выступ DM (глубина a): путь = (DM-d)/2, скорость по среднему (DM+d)/2
        passes_prot1 = max(2, math.ceil((a / 2) / siem_transverse))
        rpm_prot1 = get_rpm_for_diam((DM + d) / 2)
        speed_prot1 = feed_face * rpm_prot1
        t_face_groove = ((DM - d) / 2 * passes_prot1) / speed_prot1 if speed_prot1 > 0 else 0

        # 2-й выступ Dw (глубина t-b): путь = (Dw-d)/2, скорость по среднему (Dw+d)/2
        passes_prot2 = max(2, math.ceil((t - b_val) / siem_transverse))
        rpm_prot2 = get_rpm_for_diam((Dw_val + d) / 2)
        speed_prot2 = feed_face * rpm_prot2
        t_turn_Dw = ((Dw_val - d) / 2 * passes_prot2) / speed_prot2 if speed_prot2 > 0 else 0

        # Фаски
        ch1 = to_float(p.get('ch1', 0))
        ch2 = to_float(p.get('ch2', 0))
        ch3 = to_float(p.get('ch3', 0))
        t_chams = get_chamfer_time([ch1, ch2, ch3])

        total_min = t_turn_out + t_turn_in + t_face + t_face_groove + t_turn_Dw + t_chams

    elif item_type == "bushing":
        n_qty = to_float(p.get('n', 1))
        t_out = get_turning_time(D1, D, t)
        t_in = get_turning_time(d, D2, t)
        t_face_total = get_facing_time(D1, D2, delta_S)

        t_groove = 0
        if to_float(p.get('DM', 0)) > 0 and to_float(p.get('a', 0)) > 0:
            t_groove = get_facing_time(D, to_float(p.get('DM')), to_float(p.get('a')))

        t_thread_min = 0
        if to_float(p.get('L', 0)) > 0 and to_float(p.get('H', 0)) > 0:
            t_thread_min = get_thread_time(
                th_diameter=to_float(p.get('M', D)), 
                th_pitch=to_float(p.get('H', 0)), 
                th_lenght=to_float(p.get('L', 0)), 
                th_pos=p.get('th_pos', True),
                th_depth_cut=0.2
            )

        t_chams = get_chamfer_time([to_float(p.get('ch1', 0)), to_float(p.get('ch2', 0))])

        t_one_piece = t_out + t_in + t_groove + t_thread_min + t_chams
        total_min = (t_one_piece * n_qty) + t_face_total

    elif item_type == "axle":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_Dc = get_turning_time(D, Dc, c)
        t_turn_Da = get_turning_time(Dc, Da, a)
        t_face = get_facing_time(D1, D2, delta_S)
        total_min = t_turn_out + t_turn_Dc + t_turn_Da + t_face

    elif item_type == "axle2":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_Dc = get_turning_time(D, Dc, c)
        t_turn_Dm = get_turning_time(Dc, Dm, m)
        t_turn_Da = get_turning_time(Dm, Da, a)
        t_face = get_facing_time(D1, D2, delta_S)
        total_min = t_turn_out + t_turn_Dc + t_turn_Dm + t_turn_Da + t_face

    elif item_type == "shaft":
        t_turn_out = get_turning_time(D1, Dt, t)
        t_turn_Dc1 = get_turning_time(Dt, Dc1, c1)
        t_turn_Dm1 = get_turning_time(Dc1, Dm1, m1)
        t_turn_Dc2 = get_turning_time(Dt, Dc2, c2)
        t_turn_Dm2 = get_turning_time(Dc2, Dm2, m2)
        t_turn_Da = get_turning_time(Dm1, Da, a)
        t_face = get_facing_time(D1, Dt, delta_S)
        total_min = t_turn_out + t_turn_Dc1 + t_turn_Dm1 + t_turn_Dc2 + t_turn_Dm2 + t_turn_Da + t_face

    elif item_type == "bearinghousing":
        t_turn_out = get_turning_time(D1, D, t)
        t_face = get_facing_time(D1, 0, delta_S)
        t_turn_Dc = get_turning_time(Dc, 0, t)
        t_turn_Dm = get_turning_time(Dm, Dc, t - c)
        total_min = t_turn_out + t_face + t_turn_Dc + t_turn_Dm

    elif item_type == "rotspher":
        t_out = get_turning_time(D1, D, t)
        t_in = get_turning_time(d, D2, t)
        t_face = get_facing_time(D1, D2, delta_S)
        
        rs = to_float(p.get('RS', 0))
        ra = to_float(p.get('RA', 0))        
        as_depth = to_float(p.get('as', 0))  
        
        if rs > 0 and ra > 0:
            arc_path = rs * (ra * math.pi / 180)
            passes_sphere = math.ceil(as_depth / siem_long) if as_depth > 0 else 1
            rpm_s = get_rpm_for_diam(D)
            t_sphere = (arc_path * passes_sphere) / (feed_turn * rpm_s) if rpm_s > 0 else 0
        else:
            t_sphere = 0

        if DM > 0 and DM < D:
            t_protochka = get_facing_time(D, DM, siem_long)
        else:
            t_protochka = 0

        total_ch_len = [to_float(p.get(f'ch{i}', 0)) for i in range(1, 5)]
        t_chams = get_chamfer_time(total_ch_len)

        total_min = t_out + t_in + t_face + t_sphere + t_protochka + t_chams

    elif item_type == "pin":
        n_qty = to_float(p.get('n', 1))
        t_out_main = get_turning_time(D1, D, t)
        t_out_step = get_turning_time(D, Dc, a)
        
        t_chams = get_chamfer_time([to_float(p.get('ch1', 0)), to_float(p.get('ch2', 0))])

        t_cyclic_one = t_out_main + t_out_step + t_chams
        t_face_total = get_facing_time(D1, 0, delta_S)
        
        total_min = (t_cyclic_one * n_qty) + t_face_total


    elif item_type == "hub_composite_solid":
        # =======================================================
        # ОПЕРАЦИЯ 1: Из кругляка (До сборки)
        # Универсальный расчет для любых размеров
        # =======================================================
        
        # Считываем габариты из интерфейса (по умолчанию 0, если поле пустое)
        D1 = to_float(p.get('D1', 0))             # Диаметр кругляка-заготовки
        t_len = to_float(p.get('t', 0))           # Общая длина детали
        
        # Наружные контуры
        Dt = to_float(p.get('Dt', 0))             # Максимальный наружный диаметр ступицы
        Dc1 = to_float(p.get('Dc1', 0))           # Диаметр левого концевого уступа
        Dc2 = to_float(p.get('Dc2', 0))           # Диаметр правого концевого уступа
        len_c1 = to_float(p.get('len_c1', 0))     # Длина левого уступа
        len_c2 = to_float(p.get('len_c2', 0))     # Длина правого уступа
        
        # Внутренние контуры
        D2 = to_float(p.get('D2', 0))             # Черновой диаметр центрального отверстия
        Dm = to_float(p.get('Dm', 0))             # Диаметр внутренней расточки (борта)
        len_bore = to_float(p.get('len_bore', 0)) # Глубина внутренней расточки (на чертеже было 80)
        m_val = to_float(p.get('m', 0))           # Ширина внутренней канавки
        
        # 1. Торцевание сплошного кругляка (от D1 до центра)
        t_face = get_facing_time(D1, 0, delta_S)
        
        # 2. Сверление и черновое растачивание (от сплошного металла 0 до чернового D2)
        t_drill_rough = get_turning_time(D2, 0, t_len)
        
        # 3. Расточка внутренней ступени (от чернового D2 до Dm на заданную глубину)
        t_bore_left = get_turning_time(Dm, D2, len_bore)
        
        # 4. Прорезание внутренней канавки
        t_groove = get_grooving_time(Dm, D2, m_val) 
        
        # 5. Наружная обточка базового цилиндра (со сплошного D1 до Dt)
        t_turn_outer_max = get_turning_time(D1, Dt, t_len)
        
        # 6. Проточка наружных концевых уступов
        t_step_left = get_turning_time(Dt, Dc1, len_c1)
        t_step_right = get_turning_time(Dt, Dc2, len_c2)
        
        # 7. Суммарное время на все фаски
        t_chams = get_chamfer_time([to_float(p.get(f'ch{i}', 0)) for i in range(1, 4)])

        # Итоговое время 1-й операции
        total_min = t_face + t_drill_rough + t_bore_left + t_groove + t_turn_outer_max + t_step_left + t_step_right + t_chams

    elif item_type == "hub_composite_assembly":
        # =======================================================
        # ОПЕРАЦИЯ 2: Доработка в сборе
        # Обрабатывается только чистовой внутренний размер [d2]
        # =======================================================
        
        t_len = to_float(p.get('t', 0))           # Общая длина
        len_bore = to_float(p.get('len_bore', 0)) # Глубина левой расточки (уже сделана на 1-й операции)
        
        D2 = to_float(p.get('D2', 0))             # Черновое отверстие, которое пришло со сварки
        d2 = to_float(p.get('d2', 0))             # Чистовой размер в квадратных скобках
        
        # Вычисляем длину, которую нужно расточить в сборе 
        # (общая длина минус та часть, которая уже расточена под Dm)
        bore_length = t_len - len_bore 
        
        if bore_length > 0 and d2 > D2:
            t_turn_assembly = get_turning_time(d2, D2, bore_length)
        else:
            t_turn_assembly = 0
            
        total_min = t_turn_assembly


    final_time_sec = (total_min * 60) * get_AWC_coeff(D, S)
    
    log.info(f"Успешный расчет {item_type}. Чистое машинное время: {total_min:.2f} мин. "
             f"Итоговое время (с коэфф): {final_time_sec:.2f} сек.")
             
    return final_time_sec