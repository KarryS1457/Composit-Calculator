import math
import core.data as data
from core.data import AWC_S, AWC_DATA
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

# Типы изделий из эталонной таблицы Excel (лист "Типы изделий")
TABLE_TYPES = frozenset({
    "swivel", "circle", "shell", "weldring",
    "welding_flange", "weldflange", "welding_tnf", "weldingtnf",
    "compensator", "forming", "adapter", "rotspher",
    "threaded_bushing", "bushing", "pin",
})

def calculate_lathe_time(item_type, p, m_info=None, force_machine=None):
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
        return {"time_sec": 0.0, "machine": None, "rpm": 0}


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


    m_info = m_info or {}
    log.debug(f"Старт расчета {item_type}. Параметры GUI: {p}, Станок: {m_info.get('machine')}")

    if force_machine:
        # Принудительно используем заданный станок (для расчета альтернатив)
        current_machine = force_machine
    else:
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
    m_params = data.FEEDRATE_DATA.get(current_machine, [3, 3, 0.15, 0.25, 500])
    siem_long, siem_transverse, feed_turn, feed_face, chamfer_speed = m_params

    # Локальная функция точного поиска оборотов шпинделя
    def get_rpm_for_diam(diameter):
        diams, rpms = data.TURNING_DATA.get(current_machine, ([], []))
        if diams:
            nearest_diam = min(diams, key=lambda x: abs(x - diameter))
            return rpms[diams.index(nearest_diam)]
        return to_float(m_info.get('rpm', 100))


    D1 = final_D1
    delta_S = S - t

    # Продольная скорость: единая для наружного и внутреннего точения (Excel B55)
    # Оба используют обороты по среднему диаметру заготовки/детали avg(D1, D)
    rpm_long = get_rpm_for_diam((D1 + D) / 2) if D1 > 0 and D > 0 else get_rpm_for_diam(D)
    speed_long = feed_turn * rpm_long

    def get_facing_time(d_start, d_end, thickness):
        if thickness <= 0 or abs(d_start - d_end) < 0.01: return 0
        path_length = abs(d_start - d_end)  # полный диаметр (как в Excel)
        # Excel B46: при отсутствии второго диаметра средний = первый (IFERROR → D1)
        avg_diameter = (d_start + d_end) / 2 if d_end > 0 else d_start
        rpm_f = get_rpm_for_diam(avg_diameter)
        speed_f = feed_face * rpm_f
        if speed_f <= 0: return 0
        passes_f = max(2, math.ceil((thickness / 2) / siem_transverse))
        return (path_length * passes_f) / speed_f

    def get_turning_time(d_start, d_end, length, boring=False):
        """Продольное точение (boring=True → внутреннее растачивание, siem_transverse)."""
        if length <= 0 or abs(d_start - d_end) < 0.1: return 0
        if speed_long <= 0: return 0
        radial_depth = abs(d_start - d_end) / 2
        siem = siem_transverse if boring else siem_long
        passes_t = max(2, math.ceil(radial_depth / siem))
        return (abs(length) * passes_t) / speed_long

    def get_chamfer_time(chamfers, angles=None):
        """chamfers: list of chamfer sizes (mm). angles: list of angles (same units as Excel cell,
        treated as radians directly — matches Excel COS(angle) behaviour). Default angle=0 (cos=1)."""
        if angles is None:
            angles = [0] * len(chamfers)
        total = sum(
            ch / math.cos(ang) for ch, ang in zip(chamfers, angles) if ch > 0
        )
        return total / chamfer_speed if chamfer_speed > 0 else 0


    def get_thread_time(th_diameter, th_pitch, th_lenght, th_pos):
        """Резьба по листу Excel "Расчет резьбы": глубина = (H/2)*1.1, съем 0.2 мм/проход.
        Обороты: внешняя — маш. 15 / ручная 10 (M<16); внутренняя — маш. 100 / ручная 12 (M<36)."""
        if th_pitch <= 0 or th_lenght <= 0: return 0.0
        th_depth = (th_pitch / 2) * 1.1
        th_passes = math.ceil(th_depth / 0.2)
        if th_pos:  # внешняя резьба
            rpm = 10 if th_diameter < 16 else 15
        else:       # внутренняя резьба
            rpm = 12 if th_diameter < 36 else 100
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
    thread_min = 0.0  # резьба считается отдельно (Excel E3), без коэфф. всп. работ

    # --- ЛОГИКА ПО ТИПАМ ---
    # Изделия эталонной таблицы считаются единым "движком", который построчно
    # повторяет лист "Получение данных для расчета" (строки B111-B125).
    # ВАЖНО: Excel суммирует ВСЕ строки для ЛЮБОГО типа изделия; строка дает 0,
    # только если ее параметров нет в списке параметров типа (IFERROR -> 0).
    if item_type in TABLE_TYPES:
        E_val = to_float(p.get('E', 0))
        Dw_val = to_float(p.get('Dw', p.get('DW', 0)))
        b_val = to_float(p.get('b', 0))
        c_val = to_float(p.get('c', 0))
        Dm1_val = to_float(p.get('Dm1', 0))
        dm2_val = to_float(p.get('dm2', 0))
        K_val = to_float(p.get('K', 0))
        Dk_val = to_float(p.get('Dk', 0))
        P_val = to_float(p.get('P', 0))
        n_val = to_float(p.get('n', 0))
        X_val = to_float(p.get('X', 0))

        def roundup(x):
            """Excel ROUNDUP(x,0): округление от нуля (в т.ч. для отрицательных)."""
            return math.ceil(x) if x >= 0 else -math.ceil(-x)

        def passes_if(x, siem):
            """Excel: IF(ROUNDUP(x/siem)=1, ROUNDUP+1, ROUNDUP)."""
            if siem <= 0: return 0
            r = roundup(x / siem)
            return r + 1 if r == 1 else r

        def feed_speed(diameter):
            """Поперечная подача (мм/мин) по ближайшему среднему диаметру."""
            return feed_face * get_rpm_for_diam(diameter)

        def rpm_in_col(col, diameter):
            """Обороты из заданной колонки таблицы оборотов (ближайший диаметр)."""
            diams, rpms = data.TURNING_DATA.get(col, ([], []))
            if not diams: return 0
            i = min(range(len(diams)), key=lambda k: abs(diams[k] - diameter))
            return rpms[i]

        def rpm_step_down(col, diameter):
            """Excel B63/B67: MATCH по столбцу данных + HLOOKUP по таблице с
            заголовком дают обороты на одну ступень диаметра НИЖЕ ближайшей.
            На первой ступени (50 мм) формула попадает в заголовок -> ошибка -> 0."""
            diams, rpms = data.TURNING_DATA.get(col, ([], []))
            if not diams: return 0
            i = min(range(len(diams)), key=lambda k: abs(diams[k] - diameter))
            return rpms[i - 1] if i > 0 else 0

        B80 = passes_if((D1 - D) / 2, siem_long)
        B81 = passes_if((S - t) / 2, siem_transverse)
        # B4=(d-D2)/2, а формула B82 берет еще B4/2 — итого четверть разницы
        B82 = passes_if((d - D2) / 4, siem_transverse) if d > 0 else 0

        # B111/B112: наружное и внутреннее точение (продольная скорость B55)
        B111 = (S * B80) / speed_long if speed_long > 0 else 0
        B112 = (t * B82) / speed_long if speed_long > 0 else 0

        # B115: торцовка — длина (D1-D2), скорость поперечная по среднему диаметру
        sp_face = feed_speed((D1 + D2) / 2 if D2 > 0 else D1)
        B115 = ((D1 - D2) * B81) / sp_face if sp_face > 0 else 0

        # B116: фаски ch1-ch10 (Excel B129:K129, каждая длина ROUND(...,2))
        ch_total = sum(
            round(to_float(p.get(f'ch{i}', 0)) / math.cos(to_float(p.get(f'angle_ch{i}', 0))), 2)
            for i in range(1, 11) if to_float(p.get(f'ch{i}', 0)) > 0
        )
        B116 = ch_total / chamfer_speed if chamfer_speed > 0 else 0

        # B113: 1-я внутренняя проточка DM, проходы по глубине (a+E)/2 (B5/B6/B83)
        B83 = passes_if((a + E_val) / 2, siem_transverse)
        B113 = 0
        if DM > 0 and d > 0 and B83 > 0:
            sp = feed_speed((DM + d) / 2)
            B113 = (((DM - d) / 2) * B83) / sp if sp > 0 else 0

        # B114: 2-я внутренняя проточка Dw, проходы (t-b) без /2 и c/2 (B27/B84/B85).
        # Скорость B58: приближенный HLOOKUP станка — подача и обороты берутся
        # из соседней колонки (16к20 -> обороты 0Л52, CK5126 -> данные 1М65)
        B84 = passes_if(t - b_val, siem_transverse) if b_val > 0 else 0
        B85 = passes_if(c_val / 2, siem_transverse)
        B114 = 0
        if Dw_val > 0 and d > 0 and (B84 + B85) > 0:
            feed_col = data.APPROX_FEED_COL.get(current_machine, current_machine)
            appr_feed = to_float(data.FEEDRATE_DATA.get(feed_col, [0] * 5)[3])
            rpm_col = data.APPROX_RPM_COL.get(current_machine, current_machine)
            sp = appr_feed * rpm_in_col(rpm_col, (Dw_val + d) / 2)
            B114 = (((Dw_val - d) / 2) * (B84 + B85)) / sp if sp > 0 else 0

        # B117/B118: компенсатор — расточка с канавой (Dm1) и сама канава (K-E)
        B117 = B118 = 0
        if Dm1_val > 0 and d > 0 and B83 > 0:
            # B63: обороты на ступень диаметра ниже ближайшего среднего
            sp = feed_face * rpm_step_down(current_machine, (Dm1_val + d) / 2)
            B117 = (((Dm1_val - d) / 2) * B83) / sp if sp > 0 else 0
        if Dm1_val > dm2_val > 0 and K_val - E_val > 0:
            # Ширина резца / подача на канаву не заданы для станка -> 0 (как в Excel)
            groove_w = to_float(data.GROOVE_INSERT_WIDTH.get(current_machine, 0))
            feed_col = data.APPROX_FEED_COL.get(current_machine, current_machine)
            groove_feed = to_float(data.GROOVE_FEED.get(feed_col, 0)) \
                if isinstance(data.GROOVE_FEED, dict) else to_float(data.GROOVE_FEED)
            if groove_w > 0 and groove_feed > 0:
                B86 = math.ceil(((Dm1_val - dm2_val) / 2) / groove_w) + 1
                # B67: соседняя колонка оборотов и ступень диаметра ниже
                rpm_col = data.APPROX_RPM_COL.get(current_machine, current_machine)
                sp = groove_feed * rpm_step_down(rpm_col, (D1 + D) / 2)
                B118 = ((K_val - E_val) * B86) / sp if sp > 0 else 0

        # B119: сферическая часть (F1-F10, B103)
        B119 = 0
        rs = to_float(p.get('RS', 0)); ra = to_float(p.get('RA', 0))
        a1 = to_float(p.get('A1', 0)); as_depth = to_float(p.get('as', 0))
        if rs > 0 and ra > 0:
            b5 = (DM - d) / 2
            f1 = (rs * 2) * math.sin((ra / 2) * math.pi / 180)
            f2 = math.sqrt(max(0.0, f1 ** 2 - as_depth ** 2))
            f3 = (rs ** 2 * ((math.pi * ra / 90) - math.sin(2 * ra * math.pi / 180))) / 4
            f4 = as_depth * (b5 - f2)
            f5 = ((b5 - f2) * ((b5 - f2) * math.tan(a1 * math.pi / 180))) / 2
            f7 = math.ceil(siem_long)
            f8 = (f3 + f4 + f5) / f7 if f7 > 0 else 0
            f9 = (2 * math.pi * a1 * ra) / 360
            cos_a1 = math.cos(a1 * math.pi / 180)
            f10 = (b5 - f2) / cos_a1 if cos_a1 != 0 else 0
            sp = feed_speed((DM + d) / 2)
            B119 = (f8 + f9 + f10) / sp if sp > 0 else 0

        # B120/B121: переходной — внешняя проточка глубиной ch5 и торцевые канавы
        B120 = B121 = 0
        if item_type == "adapter":
            B87 = passes_if(to_float(p.get('ch5', 0)), siem_transverse)
            if D - DM > 0 and B87 > 0:
                sp = feed_speed((D + DM) / 2)
                B120 = (((D - DM) / 2) * B87) / sp if sp > 0 else 0
        if P_val * n_val > 0:
            sp = feed_speed(Dk_val)
            B121 = (P_val * n_val) / sp if sp > 0 else 0

        # B122: внешняя проточка по габариту t — Excel добавляет ее ВСЕМ типам (F18/B106)
        B122 = (t * B80) / speed_long if speed_long > 0 else 0

        # B123: проточка по глубине a; глубина проходов (D-Dc)/2, без Dc — D/2 (F19/F20/B88)
        B123 = 0
        if a > 0:
            B88 = passes_if((D - Dc) / 2, siem_long)
            B123 = (a * B88) / speed_long if speed_long > 0 else 0

        # B125: внешняя канава втулки Dw -> Dk шириной X (F21/B89/B108)
        B125 = 0
        if X_val > 0 and Dw_val - Dk_val > 0:
            B89 = passes_if(X_val, siem_long)
            sp = feed_speed((D1 + D) / 2)
            B125 = (((Dw_val - Dk_val) / 2) * B89) / sp if sp > 0 else 0

        total_min = (B111 + B112 + B113 + B114 + B115 + B116 + B117 + B118 +
                     B119 + B120 + B121 + B122 + B123 + B125)

        # Резьба (E3, отдельной строкой): в таблице считается только для "Втулки" —
        # лишь у нее есть флаг "Внеш.=1/Внутр.=0"; у "Втулки резьбовой" параметры
        # флага нет, и формула E3 дает 0 (IFERROR) — повторяем поведение таблицы.
        if item_type == "bushing" and to_float(p.get('H', 0)) > 0 and to_float(p.get('L', 0)) > 0:
            thread_min = get_thread_time(
                th_diameter=to_float(p.get('M', D)),
                th_pitch=to_float(p.get('H', 0)),
                th_lenght=to_float(p.get('L', 0)),
                th_pos=to_float(p.get('th_pos', 1)) == 1
            )

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
        # Наружный диаметр приходит с экрана под именем Dt (turningotp/bearinghousing.py)
        t_turn_out = get_turning_time(D1, Dt, t)
        t_face = get_facing_time(D1, 0, delta_S)
        t_turn_Dc = get_turning_time(Dc, 0, t, boring=True)
        t_turn_Dm = get_turning_time(Dm, Dc, t - c, boring=True)
        total_min = t_turn_out + t_face + t_turn_Dc + t_turn_Dm

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
        t_drill_rough = get_turning_time(D2, 0, t_len, boring=True)

        # 3. Расточка внутренней ступени (от чернового D2 до Dm на заданную глубину)
        t_bore_left = get_turning_time(Dm, D2, len_bore, boring=True)
        
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


    final_time_sec = (total_min * 60) * get_AWC_coeff(final_D1, S)

    # Кольцо закладное: время удваивается (Excel E2, IF("Кольцо закладное ?"=1, 2, 1))
    if to_float(p.get('insert_ring', 0)) == 1:
        final_time_sec *= 2

    log.info(f"Успешный расчет {item_type}. Чистое машинное время: {total_min:.2f} мин. "
             f"Итоговое время (с коэфф): {final_time_sec:.2f} сек.")

    return {
        "time_sec": final_time_sec,
        "machine": current_machine,
        "rpm": get_rpm_for_diam(D),
        "thread_sec": thread_min * 60
    }