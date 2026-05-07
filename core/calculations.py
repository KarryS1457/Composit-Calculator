import math
import core.data as data
from core.data import TURNING_DATA, RANGES_DATA, AWC_S, AWC_DATA

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
        # Проверяем, входит ли диаметр в физические границы таблицы станка
        if min(diams) <= target_diam <= max(diams):
            # Находим ближайший диаметр
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

    # 1. Поиск строки по Диаметру (D)
    d_keys = sorted(AWC_DATA.keys())
    row_key = d_keys[0]
    for d in d_keys:
        if d <= target_d:
            row_key = d
        else:
            break

    # 2. Поиск столбца по Толщине (S) - логика Excel "не более чем"
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

    k_obsl = 1.2

    # --- ИЗМЕНЕНИЕ 1: Отменяем расчет фаски для C4 ---
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

    t_kran = 3.5 if m >= 15 else 0.8
    t_kran = 4 if m >= 15 else 0.5
    t_mark = 0.83
    t_base = max(get_val_by_thickness(s, th_list, tm_list), 0.1)

    l_m = l_mm / 1000

    # --- ИЗМЕНЕНИЕ 2: Увеличиваем время сварки для C4 ---
    # Например, 1.15 означает увеличение на 15%. Можешь поменять на любое нужное значение (1.1, 1.2 и т.д.)
    k_c4_extra = 1.2 if gost == "C4" else 1.0 

    # Добавляем наш коэффициент k_c4_extra в формулу основного времени
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
    """Универсальное ядро расчетов с внутренней логикой адаптации RPM и технологическими проходами торцевания."""
    m_name = m_info['machine']
    m_params = data.FEEDRATE_DATA.get(m_name, [5, 0.19, 0.19])

    # Убрана лишняя запятая:
    depth_limit, feed_turn, feed_face = m_params

    # Базовые параметры из интерфейса (убрано задвоение a)
    D, d, t, c, a, DM = p.get('D', 0), p.get('d', 0), p.get('t', 0), p.get('c', 0), p.get('a', 0), p.get('DM', 0)
    Dc, Dm, m, Da, Dt = p.get('Dc', 0), p.get('Dm', 0), p.get('m', 0), p.get('Da', 0), p.get('Dt', 0)
    c1, m1, c2, m2 = p.get('c1', 0), p.get('m1', 0), p.get('c2', 0), p.get('m2', 0)
    Dc1, Dm1, Dc2, Dm2 = p.get('Dc1', 0), p.get('Dm1', 0), p.get('Dc2', 0), p.get('Dm2', 0)
    D1, D2, S = p.get('D1', 0), p.get('D2', 0), p.get('S', 0)

    rpm_default = m_info['rpm']
    delta_S = S - t

    # УЛУЧШЕННАЯ ФУНКЦИЯ ТОРЦЕВАНИЯ
    def get_rpm_for_diam(diameter):
        """Поиск оптимальных оборотов для конкретного диаметра по таблицам станка"""
        diams, rpms = data.TURNING_DATA.get(m_name, ([], []))
        if diams:
            idx = min(range(len(diams)), key=lambda i: abs(diams[i] - diameter))
            return rpms[idx]
        return rpm_default

    def get_facing_time(d_start, d_end, thickness):
        """Расчет торцевания с учетом изменения RPM и работы на 2 стороны"""
        if thickness <= 0 or d_start <= d_end:
            return 0

        # Определяем обороты по среднему диаметру зоны резания
        rpm_f = get_rpm_for_diam((d_start + d_end) / 2)
        speed_f = feed_face * rpm_f

        # Технологический минимум: 2 прохода (обработка с двух сторон заготовки)
        passes_f = max(2, math.ceil(thickness / depth_limit))

        # Путь резца = разница радиусов
        path_length = abs(d_start - d_end) / 2

        return (path_length * passes_f) / speed_f if speed_f > 0 else 0

    def get_turning_time(d_start, d_end, length):
        """Универсальная функция точения (внешнего и внутреннего)"""
        if length <= 0 or d_start <= d_end:
            return 0

        rpm_t = get_rpm_for_diam(d_start)
        speed_t = feed_turn * rpm_t

        passes_t = max(2, math.ceil(abs(d_start - d_end) / 2 / depth_limit))

        return (abs(length) * passes_t) / speed_t if speed_t > 0 else 0

    # --- ОСНОВНОЙ РАСЧЕТ ---
    total_min = 0

    # --- ЛОГИКА ПО ТИПАМ ---
    if item_type == "adapter":
        t_turn_out = get_turning_time(D1, D, t - p.get('ch5', 0))
        t_turn_in = get_turning_time(d, D2, t)  # Внутреннее: d больше D2

        t_face = get_facing_time(D1, D2, delta_S)
        t_face_groove = get_facing_time(D, p['DM'], p.get('ch5', 0))

        rpm_k = get_rpm_for_diam(p.get('Dk', 0))
        t_grooves = (p.get('P', 0) * p.get('n', 0)) / (feed_face * rpm_k) if rpm_k > 0 else 0

        total_min = t_turn_out + t_turn_in + t_face + t_face_groove + t_grooves

    elif item_type == "circle":
        t_turn_out = get_turning_time(D1, D, t)
        t_face = get_facing_time(D1, 0, delta_S)
        total_min = t_turn_out + t_face

    elif item_type == "compensator":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, t - p['E'])
        t_face = get_facing_time(D1, D2, delta_S)
        t_face_groove = get_facing_time(p['Dm1'], D2, p['E'])
        t_face_K = get_facing_time(p['Dm1'], p['dm2'], (p['K'] - p['E']))
        total_min = t_turn_out + t_turn_in + t_face + t_face_groove + t_face_K

    elif item_type == "shell":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, t)
        t_face = get_facing_time(D1, D, delta_S)
        total_min = t_turn_out + t_face + t_turn_in

    elif item_type == "forming":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, t)
        t_face = get_facing_time(D1, D2, delta_S)
        t_face_groove = get_facing_time(D, DM, a)
        total_min = t_turn_out + t_turn_in + t_face + t_face_groove

    elif item_type == "swivel":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, t)
        t_face = get_facing_time(D1, D2, delta_S)
        total_min = t_turn_out + t_turn_in + t_face

    elif item_type == "weldring":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, t - a)

        len_Dw = (S - p['b'] - (delta_S / 2))
        t_turn_Dw = get_turning_time(p['Dw'], d, len_Dw)

        t_face = get_facing_time(D1, D2, delta_S)
        t_face_groove = get_facing_time(p['DM'], D2, a)
        total_min = t_turn_out + t_turn_in + t_turn_Dw + t_face + t_face_groove

    elif item_type == "welding_tnf":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, t - a)
        t_face = get_facing_time(D1, D2, delta_S)
        t_face_groove = get_facing_time(DM, D2, a)
        total_min = t_turn_out + t_turn_in + t_face + t_face_groove

    elif item_type == "welding_flange":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_in = get_turning_time(d, D2, p['b'] - a)
        t_turn_Dw = get_turning_time(p['Dw'], d, t - p['b'])
        t_face = get_facing_time(D1, D2, delta_S)
        t_face_groove = get_facing_time(DM, D2, a)
        total_min = t_turn_out + t_turn_in + t_turn_Dw + t_face + t_face_groove

    elif item_type == "bushing":
        n_qty = p.get('n', 1)

        t_out_1 = get_turning_time(D1, D, t)
        t_in_dw_1 = get_turning_time(p['Dw'], p['d'], p['c'])

        thread_rpm = min(get_rpm_for_diam(p.get('M', D)), 200)
        t_thread_1 = (p.get('L', 0) / (p.get('H', 1) * thread_rpm)) * 6 if thread_rpm > 0 else 0

        t_groove_1 = get_facing_time(D, p.get('Dm'
                                              , 0), depth_limit)

        t_cyclic_total = (t_out_1 + t_in_dw_1 + t_thread_1 + t_groove_1) * n_qty

        delta_S_total = S - (t * n_qty)
        t_face_once = get_facing_time(D1, p['d'], delta_S_total)

        total_min = t_cyclic_total + t_face_once

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

    elif item_type == "Bearinghousing":
        t_turn_out = get_turning_time(D1, Dt, t)
        t_turn_Dc = get_turning_time(Dc, 0, c)
        t_turn_Dm = get_turning_time(Dm, 0, t-c)
        t_face = get_facing_time(D1, Dt, delta_S)
        total_min = t_turn_out + t_turn_Dc + t_turn_Dm + t_face

    # Применяем коэф. сложности и переводим в секунды
    aw_coeff = get_AWC_coeff(D, S)
    return (total_min * 60) * aw_coeff