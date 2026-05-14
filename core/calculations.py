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

    #Поиск строки по Диаметру (D)
    d_keys = sorted(AWC_DATA.keys())
    row_key = d_keys[0]
    for d in d_keys:
        if d <= target_d:
            row_key = d
        else:
            break

    #Поиск столбца по Толщине (S)
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

    # ИЗМЕНЕНИЕ 1: Отменяем расчет фаски для C4
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

    #Доп. коэфф для типа шва С4
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
    m_params = data.FEEDRATE_DATA.get(m_name, [3, 0.15, 0.25])
    depth_limit, feed_turn, feed_face = m_params

    # Базовые параметры из интерфейса (убрано задвоение a)
    D, d, t, c, a, DM = p.get('D', 0), p.get('d', 0), p.get('t', 0), p.get('c', 0), p.get('a', 0), p.get('DM', 0)
    Dc, Dm, m, Da, Dt = p.get('Dc', 0), p.get('Dm', 0), p.get('m', 0), p.get('Da', 0), p.get('Dt', 0)
    c1, m1, c2, m2 = p.get('c1', 0), p.get('m1', 0), p.get('c2', 0), p.get('m2', 0)
    Dc1, Dm1, Dc2, Dm2 = p.get('Dc1', 0), p.get('Dm1', 0), p.get('Dc2', 0), p.get('Dm2', 0)
    D1, D2, S = p.get('D1', 0), p.get('D2', 0), p.get('S', 0)

    rpm_default = m_info.get('rpm', 100)
    delta_S = S - t

    def get_rpm_for_diam(diameter):
        """Поиск RPM по таблице Лист1 (ближайшее меньшее или равное)"""
        diams, rpms = data.TURNING_DATA.get(m_name, ([], []))
        if diams:
            # В Sheets VLOOKUP(..., TRUE) ищет наибольшее значение, которое <= искомого
            # Здесь используем простую логику поиска по порогам
            res_rpm = rpms[0]
            for i, val in enumerate(diams):
                if diameter >= val:
                    res_rpm = rpms[i]
                else:
                    break
            return res_rpm
        return rpm_default

    def get_facing_time(d_start, d_end, thickness):
        """Торцевание (поперечная подача)"""
        if thickness <= 0 or d_start <= d_end:
            return 0
        rpm_f = get_rpm_for_diam((d_start + d_end) / 2)
        speed_f = feed_face * rpm_f
        # Убрано max(2), используем реальное кол-во проходов
        passes_f = math.ceil(thickness / depth_limit)
        path_length = abs(d_start - d_end) / 2
        return (path_length * passes_f) / speed_f if speed_f > 0 else 0

    def get_turning_time(d_start, d_end, length):
        """Точение (продольная подача)"""
        if length <= 0 or abs(d_start - d_end) < 0.1:
            return 0
        rpm_t = get_rpm_for_diam(max(d_start, d_end))
        speed_t = feed_turn * rpm_t
        passes_t = math.ceil(abs(d_start - d_end) / 2 / depth_limit)
        return (abs(length) * passes_t) / speed_t if speed_t > 0 else 0

    total_min = 0

    def get_thread_time(th_diameter, th_pitch, th_lenght, th_pos, th_depth_cut):

        rpm = get_rpm_for_diam(max(th_diameter))

        if rpm <= 0 or th_pitch <= 0:
            return 0.0
        
        if th_pos:
            th_depth = 0.6134 * th_pitch
        else:
            th_depth = 0.5413 * th_pitch

        th_passses = math.ceil(th_depth / th_depth_cut)

        total_path = th_lenght * th_passses
        th_time = (total_path / (rpm * th_pitch)) * 60

        return round(th_time, 2)

    # --- ОСНОВНОЙ РАСЧЕТ ---
    total_min = 0

    # --- ЛОГИКА ПО ТИПАМ ---
    if item_type == "adapter":
        ch5_val = p.get('ch5', 0)
        t_turn_out = get_turning_time(D1, D, t - ch5_val)
        t_turn_in = get_turning_time(d, D2, t)  # Внутреннее: d больше D2

        t_face = get_facing_time(D1, D2, delta_S)
        t_face_groove = get_facing_time(D, DM, ch5_val)

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
        
        # 1. Наружное точение (D1 -> D) на всю длину детали t
        t_out = get_turning_time(D1, D, t)

        # 2. Внутреннее точение / Расточка (D2 -> d) на длину t
        t_in = get_turning_time(d, D2, t)

        # 3. Торцевание припуска (S -> t) - делается один раз на партию
        t_face_total = get_facing_time(D1, D2, delta_S)

        # 4. Обработка проточки (DM - диаметр проточки, a - глубина/длина)
        t_groove = 0
        if p.get('DM', 0) > 0 and p.get('a', 0) > 0:
            t_groove = get_facing_time(D, p.get('DM'), p.get('a'))

        # 5. Резьба (Thread)
        t_thread_min = 0
        if p.get('L', 0) > 0 and p.get('H', 0) > 0:
            # Вызываем вашу функцию. Поскольку она возвращает секунды, делим на 60
            t_thread_sec = get_thread_time(
                th_diameter=p.get('M', D), 
                th_pitch=p.get('H', 0), 
                th_lenght=p.get('L', 0), 
                th_pos=p.get('th_pos', True),
                th_depth_cut=0.2 # стандартный съем из таблицы
            )
            t_thread_min = t_thread_sec / 60

        # 6. Расчет фасок (ch1, ch2) - добавлено
        ch_total = p.get('ch1', 0) + p.get('ch2', 0)
        t_chams = 0
        if ch_total > 0:
            rpm_ch = get_rpm_for_diam(D)
            t_chams = (ch_total / (feed_turn * rpm_ch)) if rpm_ch > 0 else 0

        # --- ИТОГОВОЕ СУММИРОВАНИЕ ---
        # Складываем всё в минутах
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
        # 1. Наружное точение (D1 -> D)
        t_out = get_turning_time(D1, D, t)
        
        # 2. Внутреннее точение (d -> D2)
        t_in = get_turning_time(d, D2, t)
        
        # 3. Торцовка заготовки (S -> t)
        t_face = get_facing_time(D1, D2, delta_S)
        
        # 4. Обработка сферической части (RS - радиус, RA - угол, as - глубина)
        rs = p.get('RS', 0)
        ra = p.get('RA', 0)        # Угол в градусах
        as_depth = p.get('as', 0)  # Глубина съема для формирования сферы
        
        if rs > 0 and ra > 0:
            # Длина пути резца по дуге (длина дуги L = R * angle_rad)
            arc_path = rs * (ra * math.pi / 180)
            
            # Количество проходов по глубине сферы
            passes_sphere = math.ceil(as_depth / depth_limit) if as_depth > 0 else 1
            
            # Обороты берем по наружному диаметру сферы (обычно это D)
            rpm_s = get_rpm_for_diam(D)
            # Сферическая обработка обычно идет с продольной подачей
            t_sphere = (arc_path * passes_sphere) / (feed_turn * rpm_s) if rpm_s > 0 else 0
        else:
            t_sphere = 0

        # 5. Обработка проточки (DM - диаметр проточки)
        # Если DM задан, это обычно дополнительная торцовка или снятие слоя
        if DM > 0 and DM < D:
            # Считаем как торцовку от D до DM на глубину, например, 2-3 мм 
            # или используем разницу для определения времени
            t_protochka = get_facing_time(D, DM, depth_limit) 
        else:
            t_protochka = 0

        # 6. Фаски (ch1 - ch4)
        # Суммируем время на типовые фаски (упрощенно)
        total_ch_len = sum([p.get(f'ch{i}', 0) for i in range(1, 5)])
        t_chams = (total_ch_len / (feed_turn * rpm_default)) if rpm_default > 0 else 0

        total_min = t_out + t_in + t_face + t_sphere + t_protochka + t_chams

    elif item_type == "pin":
        n_qty = p.get('n', 1)
        
        # 1. Наружное точение (черновое и чистовое прутка D1 -> D)
        t_out_main = get_turning_time(D1, D, t)
        
        # 2. Точение ступени или проточки (D -> Dc) на длину 'a'
        # В штифтах 'a' обычно — это длина заниженного диаметра
        t_out_step = get_turning_time(D, Dc, a)
        
        # 3. Фаски (ch1 и ch2)
        ch_total = p.get('ch1', 0) + p.get('ch2', 0)
        rpm_ch = get_rpm_for_diam(D)
        t_chams = (ch_total / (feed_turn * rpm_ch)) if rpm_ch > 0 else 0
        
        # Циклические операции на ОДНО изделие
        t_cyclic_one = t_out_main + t_out_step + t_chams
        
        # 4. ТОРЦЕВАНИЕ (подрезка торца заготовки в размер)
        # Для штифта торцуем от D1 до 0 (так как он цельный)
        # Считаем торцовку припуска delta_S один раз на всю партию (как в твоем коде)
        t_face_total = get_facing_time(D1, 0, delta_S)
        
        # Итоговое время (цикл * кол-во + общая торцовка припуска)
        total_min = (t_cyclic_one * n_qty) + t_face_total

    # Применяем коэф. сложности и переводим в секунды
    return (total_min * 60) * get_AWC_coeff(D, S)