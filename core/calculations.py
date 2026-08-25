import math

from core import data
from core.logger import log


def trend_extrapolation(x_val, x_list, y_list):
    if not x_list or not y_list:
        return 0
    n_points = min(4, len(x_list))
    x = x_list[:n_points] if x_val < x_list[0] else x_list[-n_points:]
    y = y_list[:n_points] if x_val < x_list[0] else y_list[-n_points:]
    n = len(x)
    sum_x, sum_y = sum(x), sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi**2 for xi in x)
    denom = (n * sum_x2 - sum_x**2)
    if denom == 0: 
        return y[-1]
    m = (n * sum_xy - sum_x * sum_y) / denom
    b = (sum_y - m * sum_x) / n
    return m * x_val + b

def get_val_by_thickness(thickness, x_list, y_list):
    if not x_list or not y_list: 
        return 0
    if thickness in x_list: 
        return y_list[x_list.index(thickness)]
    if thickness < x_list[0] or thickness > x_list[-1]: 
        return trend_extrapolation(thickness, x_list, y_list)
    for i in range(len(x_list) - 1):
        if x_list[i] < thickness < x_list[i+1]:
            x1, x2, y1, y2 = x_list[i], x_list[i+1], y_list[i], y_list[i+1]
            return y1 + (thickness - x1) * (y2 - y1) / (x2 - x1)
    return y_list[-1]

def chamfer_length(size, angle_deg):
    """Длина реза фаски: размер фаски, деленный на косинус ее угла.

    Угол приходит с экрана в ГРАДУСАХ. В эталонной таблице (лист "Получение
    данных для расчета", строка B129) стоит просто COS(угол), а COS в Excel
    принимает радианы — RADIANS() в формуле забыт. Из-за этого фаска 45°
    считалась как 9.52 мм вместо 7.07, фаска 30° — как 32.41 мм вместо 5.77,
    а начиная с 58° косинус уходил в минус и длина фаски получалась
    ОТРИЦАТЕЛЬНОЙ, уменьшая общее время обработки.

    Угол вне диапазона 0..90 для фаски бессмыслен; такой угол игнорируем и
    берем сам размер фаски (как при угле 0), чтобы не получить всплеск или
    отрицательное значение.
    """
    if size <= 0:
        return 0.0
    if not 0 <= angle_deg < 90:
        if angle_deg:
            log.warning(f"Угол фаски {angle_deg}° вне диапазона 0..90 — "
                        f"длина фаски взята равной ее размеру ({size} мм)")
        return float(size)
    return size / math.cos(math.radians(angle_deg))


def _interp_pos(value, axis):
    """Положение value на оси узлов axis для линейной интерполяции.

    Возвращает (i0, i1, w): результат = v[i0]*(1-w) + v[i1]*w.
    За пределами таблицы прижимаемся к крайнему узлу (i0 == i1, w = 0) —
    так поведение на краях остается прежним, ступенчатым."""
    if value <= axis[0]:
        return 0, 0, 0.0
    last = len(axis) - 1
    if value >= axis[last]:
        return last, last, 0.0
    for i in range(last):
        if axis[i] <= value <= axis[i + 1]:
            span = axis[i + 1] - axis[i]
            return i, i + 1, ((value - axis[i]) / span if span else 0.0)
    return last, last, 0.0


def get_AWC_coeff(target_d, target_s):
    """Коэффициент вспомогательных работ по диаметру заготовки и толщине листа.

    Значение берется билинейной интерполяцией между четырьмя ближайшими
    узлами таблицы, а НЕ ступенькой "ближайший узел снизу", как в эталонном
    Excel (B91 -> HLOOKUP с приблизительным совпадением).

    Причина: по строкам таблица падает на ~0.0457 на каждые 100 мм диаметра,
    по столбцам — на 0.0725 на столбец толщины, и при ступенчатом поиске весь
    этот спад приходится на ОДИН миллиметр — на границу диапазона. Машинное
    время на том же миллиметре прибавляет доли процента, поэтому итог на
    границе проваливался вниз: деталь большего диаметра нормировалась дешевле
    меньшей. Проверка по всем границам таблицы давала такой провал в 6 случаях
    из 8 по диаметру и в 6 из 8 по толщине.

    Интерполяция размазывает спад по всему диапазону, и время снова растет
    монотонно. За пределами таблицы (D1 больше последнего узла, толщина
    больше последнего) значение по-прежнему берется с края.

    Таблицы читаем через data.*, а не через "from core.data import ...":
    редактор норм подменяет их в core.data на лету (save_norms /
    set_active_source), и импортированные по значению копии остались бы
    старыми до перезапуска программы.
    """
    d_keys = sorted(data.AWC_DATA.keys(), key=float)
    if not d_keys:
        return 1.0
    d_axis = [float(k) for k in d_keys]
    s_axis = [float(s) for s in data.AWC_S]

    i0, i1, wd = _interp_pos(float(target_d), d_axis)
    j0, j1, ws = _interp_pos(float(target_s), s_axis)

    row_lo = data.AWC_DATA[d_keys[i0]]
    row_hi = data.AWC_DATA[d_keys[i1]]
    lo = float(row_lo[j0]) * (1 - ws) + float(row_lo[j1]) * ws
    hi = float(row_hi[j0]) * (1 - ws) + float(row_hi[j1]) * ws
    return lo * (1 - wd) + hi * wd

def calculate_weld_logic(gost, s, l_mm, m, k_lp, k_pos, k_posture, weld_data, chamfer_data):
    weld_info = weld_data.get(gost)
    if not weld_info or not weld_info[0] or not weld_info[1]:
        raise ValueError(f"Нет норм сварки для шва {gost}")
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

    # Толщина за пределами таблицы выбранного ГОСТ — результат экстраполирован
    # и может быть неточным (расчет не блокируем, только предупреждаем).
    out_of_range = s < th_list[0] or s > th_list[-1]

    steps = [
        f"Базовая норма по S={s:g} мм: {t_base:.3f} мин/м",
        f"Коэффициенты: положение ×{k_pos:g}, поза ×{k_posture:g}, "
        f"обслуживание ×{k_obsl:g}" + (f", доп. C4 ×{k_c4_extra:g}" if k_c4_extra != 1.0 else ""),
        f"Норма сварки шва: {t_nsh:.3f} мин/м × длина {l_m:g} м = {t_nsh*l_m:.3f} мин",
        f"Кран: {t_kran:g} мин (масса {m:g} кг), маркировка: {t_mark:g} мин",
    ]
    if gost != "C4":
        steps.append(f"Снятие фасок: {t_cham:.3f} мин")
    steps.append(f"Подготовительно-вспомогательное: {t_vn:.3f} мин")
    steps.append(f"Тип производства: ×{k_lp:g}")
    steps.append(f"ИТОГО: {t_sht_min:.3f} мин ({int(t_sht_min*60)} сек)")

    return {
        "total_sec": int(t_sht_min * 60),
        "prep": t_prep,
        "chamfer": t_cham,
        "weld": t_nsh * l_m,
        "gost": gost,
        "s": s,
        "out_of_range": out_of_range,
        "s_range": (th_list[0], th_list[-1]),
        "steps": steps,
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

    # У "вала" и "корпуса подшипника" наибольший наружный диаметр приходит
    # с экрана как Dt (поля D там нет). D используется ниже для выбора
    # станка и скорости резания — без этой подстановки они считались бы
    # по D=0 (т.е. всегда по самому маленькому станку 16K20).
    if item_type in ("shaft", "bearinghousing") and D == 0:
        D = Dt


    # Синхронизация названий типов для SHEET_PRODUCTS во избежание багов со строками
    normalized_type = item_type
    if item_type == "welding_flange": 
        normalized_type = "weldflange"
    if item_type == "welding_tnf": 
        normalized_type = "weldingtnf"

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
        # Определяем станок по готовому диаметру детали D (как в эталонном Excel,
        # лист "Получение данных для расчета" B78: выбор идёт строго по D).
        #
        # Берем первый станок, чей ВЕРХНИЙ предел не меньше D, перебирая их от
        # меньшего к большему — это ровно та же логика, что и вложенные
        # IF(D>250; IF(D>500; ...)) в B78. Сравнивать с нижней границей нельзя:
        # в нормах диапазоны заданы целыми (0-250, 251-500, 501-800, 801-2500),
        # и проверка "low <= D <= high" теряла дробные диаметры в стыках —
        # D=250.5, 500.5 и 800.5 не попадали ни в один диапазон, и расчет
        # завершался сообщением "Станок не найден".
        previous_machine = m_info.get('machine')
        current_machine = None
        for name, (_low, high) in sorted(data.RANGES_DATA.items(),
                                         key=lambda kv: kv[1][1]):
            if D <= high:
                current_machine = name
                break
        if current_machine is None:
            # Диаметр больше самого крупного станка — в таблице тут
            # "ошибка отсутствуют станки больших диаметров"
            log.warning(f"Станок не подобран: диаметр детали {D} мм больше "
                        f"максимального диаметра всех станков")
        elif previous_machine != current_machine:
            log.warning(f"АВТОКОРРЕКЦИЯ: Станок изменен с {previous_machine} на "
                        f"{current_machine} (диаметр детали {D} мм)")

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
        if thickness <= 0 or abs(d_start - d_end) < 0.01: 
            return 0
        path_length = abs(d_start - d_end)  # полный диаметр (как в Excel)
        # Excel B46: при отсутствии второго диаметра средний = первый (IFERROR → D1)
        avg_diameter = (d_start + d_end) / 2 if d_end > 0 else d_start
        rpm_f = get_rpm_for_diam(avg_diameter)
        speed_f = feed_face * rpm_f
        if speed_f <= 0: 
            return 0
        passes_f = max(2, math.ceil((thickness / 2) / siem_transverse))
        return (path_length * passes_f) / speed_f

    def get_turning_time(d_start, d_end, length, boring=False):
        """Продольное точение/растачивание.

        boring=True → внутреннее растачивание: глубина прохода siem_transverse,
        а обороты берутся по ФАКТИЧЕСКОМУ (меньшему) среднему диаметру расточки,
        как в строках B113/B114 эталонной таблицы. Иначе расточка считалась бы
        на оборотах большого наружного диаметра заготовки и выходила бы в ~1.5
        раза медленнее реальной. Подача при этом остаётся продольной (feed_turn),
        как для внутреннего точения B112."""
        if length <= 0 or abs(d_start - d_end) < 0.1: 
            return 0
        radial_depth = abs(d_start - d_end) / 2
        if boring:
            avg_d = (d_start + d_end) / 2 if d_end > 0 else d_start
            speed = feed_turn * get_rpm_for_diam(avg_d)
            siem = siem_transverse
        else:
            speed = speed_long
            siem = siem_long
        if speed <= 0: 
            return 0
        passes_t = max(2, math.ceil(radial_depth / siem))
        return (abs(length) * passes_t) / speed

    def get_chamfer_time(chamfers, angles=None):
        """chamfers: размеры фасок (мм), angles: углы фасок в ГРАДУСАХ."""
        if angles is None:
            angles = [0] * len(chamfers)
        total = sum(
            chamfer_length(ch, ang) for ch, ang in zip(chamfers, angles) if ch > 0
        )
        return total / chamfer_speed if chamfer_speed > 0 else 0


    def get_thread_time(th_diameter, th_pitch, th_lenght, th_pos):
        """Резьба по листу Excel "Расчет резьбы": глубина = (H/2)*1.1, съем 0.2 мм/проход.
        Обороты: внешняя — маш. 15 / ручная 10 (M<16); внутренняя — маш. 100 / ручная 12 (M<36)."""
        if th_pitch <= 0 or th_lenght <= 0: 
            return 0.0
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
    # Пошаговая разбивка: список (описание, время_в_минутах). Заполняется
    # по ходу расчета и возвращается для журнала расчетов.
    components = []

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
            if siem <= 0: 
                return 0
            r = roundup(x / siem)
            return r + 1 if r == 1 else r

        def feed_speed(diameter):
            """Поперечная подача (мм/мин) по ближайшему среднему диаметру."""
            return feed_face * get_rpm_for_diam(diameter)

        def rpm_in_col(col, diameter):
            """Обороты из заданной колонки таблицы оборотов (ближайший диаметр)."""
            diams, rpms = data.TURNING_DATA.get(col, ([], []))
            if not diams: 
                return 0
            i = min(range(len(diams)), key=lambda k: abs(diams[k] - diameter))
            return rpms[i]

        def rpm_step_down(col, diameter):
            """Excel B63/B67: MATCH по столбцу данных + HLOOKUP по таблице с
            заголовком дают обороты на одну ступень диаметра НИЖЕ ближайшей.
            На первой ступени (50 мм) формула попадает в заголовок -> ошибка -> 0."""
            diams, rpms = data.TURNING_DATA.get(col, ([], []))
            if not diams: 
                return 0
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

        # B116: фаски ch1-ch10 (Excel B129:K129, каждая длина ROUND(...,2)).
        # Угол считается в градусах — см. chamfer_length().
        ch_total = sum(
            round(chamfer_length(to_float(p.get(f'ch{i}', 0)),
                                 to_float(p.get(f'angle_ch{i}', 0))), 2)
            for i in range(1, 11) if to_float(p.get(f'ch{i}', 0)) > 0
        )
        B116 = ch_total / chamfer_speed if chamfer_speed > 0 else 0

        # B113: 1-я внутренняя проточка DM, проходы по глубине (a+E)/2 (B5/B6/B83).
        # Excel B98 обнуляет строку при отрицательной длине расточки (Dm < d):
        # IF(...>=0; ...; "Ошибка длинна расточки меньше 0!") -> деление на
        # скорость дает #ЗНАЧ! -> IFERROR -> 0. Без этой проверки опечатка в
        # диаметре давала бы отрицательное время и уводила итог в минус.
        B83 = passes_if((a + E_val) / 2, siem_transverse)
        B113 = 0
        if DM > 0 and d > 0 and B83 > 0:
            path_113 = ((DM - d) / 2) * B83
            if path_113 >= 0:
                sp = feed_speed((DM + d) / 2)
                B113 = path_113 / sp if sp > 0 else 0

        # B114: 2-я внутренняя проточка Dw, проходы (t-b) без /2 и c/2 (B27/B84/B85).
        # Скорость B58: приближенный HLOOKUP станка — подача и обороты берутся
        # из соседней колонки (16к20 -> обороты 0Л52, CK5126 -> данные 1М65)
        # Строка так же защищена в Excel (B99), как и B98 выше: при Dw < d
        # длина расточки отрицательная и строка дает 0, а не минусовое время.
        #
        # B28 = IFERROR(t - b; 0). Ноль тут дает только ОТСУТСТВИЕ параметра
        # у типа изделия (MATCH -> #Н/Д). Если поле на экране есть, но пустое,
        # таблица считает t - 0 = t, то есть проходы на всю толщину детали.
        # Прежнее условие "b > 0" в этом случае глушило строку целиком.
        B28 = (t - b_val) if 'b' in p else 0
        B84 = passes_if(B28, siem_transverse)
        B85 = passes_if(c_val / 2, siem_transverse)
        B114 = 0
        if Dw_val > 0 and d > 0 and (B84 + B85) > 0:
            path_114 = ((Dw_val - d) / 2) * (B84 + B85)
            if path_114 >= 0:
                feed_col = data.APPROX_FEED_COL.get(current_machine, current_machine)
                appr_feed = to_float(data.FEEDRATE_DATA.get(feed_col, [0] * 5)[3])
                rpm_col = data.APPROX_RPM_COL.get(current_machine, current_machine)
                sp = appr_feed * rpm_in_col(rpm_col, (Dw_val + d) / 2)
                B114 = path_114 / sp if sp > 0 else 0

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
        rs = to_float(p.get('RS', 0)) 
        ra = to_float(p.get('RA', 0))
        a1 = to_float(p.get('A1', 0)) 
        as_depth = to_float(p.get('as', 0))
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

        # B122 эталонной таблицы ("Общий путь наружнего точения (Штифт)",
        # F18/B106) здесь СОЗНАТЕЛЬНО не считается. Это то же самое наружное
        # продольное точение, что и B111: те же проходы B80 по тому же припуску
        # (D1-D)/2 и та же скорость B55, отличается только длина — габарит t
        # вместо толщины заготовки S. Проверка геометрии не пропускает t > S,
        # значит путь по S всегда не меньше пути по t и уже включает его,
        # а таблица добавляла обе строки всем типам изделий подряд.

        # B123: проточка по глубине a на глубину (D-Dc)/2 (F19/F20/B88).
        # Второй наружный диаметр Dc есть только у штифта. У остальных типов
        # IFERROR в F20 подставлял ноль, и таблица считала съем "до нулевого
        # диаметра": для фланца D=1170 это 585 мм на сторону и 98 проходов —
        # около четверти всего машинного времени из ниоткуда. Вдобавок сам
        # параметр a у фланцев уже задействован в B113, где задает число
        # проходов внутренней проточки. Считаем строку только когда есть
        # реальный второй диаметр, с которого идет съем.
        B123 = 0
        if a > 0 and Dc > 0 and D > Dc:
            B88 = passes_if((D - Dc) / 2, siem_long)
            B123 = (a * B88) / speed_long if speed_long > 0 else 0

        # B125: внешняя канава втулки Dw -> Dk шириной X (F21/B89/B108)
        B125 = 0
        if X_val > 0 and Dw_val - Dk_val > 0:
            B89 = passes_if(X_val, siem_long)
            sp = feed_speed((D1 + D) / 2)
            B125 = (((Dw_val - Dk_val) / 2) * B89) / sp if sp > 0 else 0

        total_min = (B111 + B112 + B113 + B114 + B115 + B116 + B117 + B118 +
                     B119 + B120 + B121 + B123 + B125)

        components += [
            ("Наружное точение", B111),
            ("Внутреннее точение", B112),
            ("1-я внутр. проточка (DM)", B113),
            ("2-я внутр. проточка (Dw)", B114),
            ("Торцовка", B115),
            ("Фаски", B116),
            ("Расточка с канавой (Dm1)", B117),
            ("Канава (K−E)", B118),
            ("Сферическая часть", B119),
            ("Внешняя проточка (ch5)", B120),
            ("Торцевые канавы", B121),
            ("Проточка по глубине a", B123),
            ("Внешняя канава втулки", B125),
        ]

        # Резьба (E3, отдельной строкой).
        # В эталонной таблице резьба считалась ТОЛЬКО для "Втулки": лист
        # "Расчет резьбы" требует флаг "Внеш. Рез.=1/Внутр. Рез.=0", а в списке
        # параметров "Втулки резьбовой" его нет — MATCH давал #Н/Д и E3
        # обнулялась. То есть деталь, названная резьбовой, нормировалась вообще
        # без резьбы, хотя шаг и длина на экране запрашивались. Считаем резьбу
        # для обоих типов; флаг теперь есть и на экране втулки резьбовой.
        if (item_type in ("bushing", "threaded_bushing")
                and to_float(p.get('H', 0)) > 0 and to_float(p.get('L', 0)) > 0):
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
        components += [
            ("Наружное точение (D1→D)", t_turn_out),
            ("Проточка D→Dc", t_turn_Dc),
            ("Проточка канавы Dc→Da", t_turn_Da),
            ("Торцовка", t_face),
        ]

    elif item_type == "axle2":
        t_turn_out = get_turning_time(D1, D, t)
        t_turn_Dc = get_turning_time(D, Dc, c)
        t_turn_Dm = get_turning_time(Dc, Dm, m)
        t_turn_Da = get_turning_time(Dm, Da, a)
        t_face = get_facing_time(D1, D2, delta_S)
        total_min = t_turn_out + t_turn_Dc + t_turn_Dm + t_turn_Da + t_face
        components += [
            ("Наружное точение (D1→D)", t_turn_out),
            ("Проточка D→Dc", t_turn_Dc),
            ("Проточка Dc→Dm", t_turn_Dm),
            ("Проточка канавы Dm→Da", t_turn_Da),
            ("Торцовка", t_face),
        ]

    elif item_type == "shaft":
        t_turn_out = get_turning_time(D1, Dt, t)
        t_turn_Dc1 = get_turning_time(Dt, Dc1, c1)
        t_turn_Dm1 = get_turning_time(Dc1, Dm1, m1)
        t_turn_Dc2 = get_turning_time(Dt, Dc2, c2)
        t_turn_Dm2 = get_turning_time(Dc2, Dm2, m2)
        t_turn_Da = get_turning_time(Dm1, Da, a)
        t_face = get_facing_time(D1, Dt, delta_S)
        total_min = t_turn_out + t_turn_Dc1 + t_turn_Dm1 + t_turn_Dc2 + t_turn_Dm2 + t_turn_Da + t_face
        components += [
            ("Наружное точение (D1→Dt)", t_turn_out),
            ("Проточка Dt→Dc1", t_turn_Dc1),
            ("Проточка Dc1→Dm1", t_turn_Dm1),
            ("Проточка Dt→Dc2", t_turn_Dc2),
            ("Проточка Dc2→Dm2", t_turn_Dm2),
            ("Проточка канавы Dm1→Da", t_turn_Da),
            ("Торцовка", t_face),
        ]

    elif item_type == "bearinghousing":
        # Наружный диаметр приходит с экрана под именем Dt (turningotp/bearinghousing.py)
        t_turn_out = get_turning_time(D1, Dt, t)
        t_face = get_facing_time(D1, 0, delta_S)
        t_turn_Dc = get_turning_time(Dc, 0, t, boring=True)
        t_turn_Dm = get_turning_time(Dm, Dc, t - c, boring=True)
        total_min = t_turn_out + t_face + t_turn_Dc + t_turn_Dm
        components += [
            ("Наружное точение (D1→Dt)", t_turn_out),
            ("Торцовка", t_face),
            ("Растачивание Dc", t_turn_Dc),
            ("Растачивание Dm→Dc", t_turn_Dm),
        ]

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


    awc = get_AWC_coeff(final_D1, S)
    final_time_sec = (total_min * 60) * awc

    # Кольцо закладное: время удваивается (Excel E2, IF("Кольцо закладное ?"=1, 2, 1))
    insert_ring = to_float(p.get('insert_ring', 0)) == 1
    if insert_ring:
        final_time_sec *= 2

    # Отрицательное время наружу не отдаем ни при каких данных: это заведомо
    # бессмысленный результат (обычно — опечатка в диаметре, из-за которой
    # какая-то строка ушла в минус). Факт отсечки попадает в журнал и в
    # пошаговую разбивку, чтобы он не остался незамеченным.
    negative_total = final_time_sec < 0
    if negative_total:
        log.warning(f"Расчет {item_type} дал отрицательное время "
                    f"({final_time_sec:.2f} сек) — результат обнулен. "
                    f"Параметры: {p}")
        final_time_sec = 0.0

    log.info(f"Успешный расчет {item_type}. Чистое машинное время: {total_min:.2f} мин. "
             f"Итоговое время (с коэфф): {final_time_sec:.2f} сек.")

    # --- Пошаговая разбивка для журнала расчетов ---
    steps = []
    steps.append(f"Станок: {current_machine} (по диаметру D={D:g} мм)")
    if user_D1 <= 0 and normalized_type in data.SHEET_PRODUCTS:
        steps.append(f"Припуск на диаметр по S={S:g}: +{allowance:g} мм → "
                     f"диаметр заготовки D1={final_D1:g} мм")
    steps.append("Составляющие машинного времени:")
    shown = False
    for name, minutes in components:
        # Показываем ВСЕ ненулевые строки, в том числе отрицательные: раньше
        # минусовая составляющая молча пропускалась, и было не видно, откуда
        # взялся отрицательный итог.
        if minutes and abs(minutes) > 1e-9:
            mark = "  <-- ОТРИЦАТЕЛЬНАЯ, проверьте диаметры" if minutes < 0 else ""
            steps.append(f"  • {name}: {minutes*60:.2f} сек ({minutes:.3f} мин){mark}")
            shown = True
    if not shown:
        steps.append("  • (нет ненулевых составляющих)")
    steps.append(f"Сумма машинного времени: {total_min:.3f} мин ({total_min*60:.2f} сек)")
    steps.append(f"Коэффициент вспом. работ (D1={final_D1:g}, S={S:g}): ×{awc:g}")
    if insert_ring:
        steps.append("Закладное кольцо: ×2")
    if negative_total:
        steps.append("ВНИМАНИЕ: расчет дал отрицательное время — итог обнулен. "
                     "Проверьте введенные диаметры.")
    steps.append(f"ИТОГО токарная обработка: {final_time_sec:.2f} сек")
    if thread_min > 0:
        steps.append(f"Резьба (отдельно, без коэфф.): {thread_min*60:.2f} сек")

    return {
        "time_sec": final_time_sec,
        "machine": current_machine,
        "rpm": get_rpm_for_diam(D),
        "thread_sec": thread_min * 60,
        "steps": steps,
    }