"""Тест: 50 случайных изделий, сравнение Python-программы с формулами Excel."""
import math, sys, random
sys.path.insert(0, '/home/user/Composit-Calculator')
import core.data as data
import core.calculations as calc

random.seed(42)

def machine_by_D(D):
    for name, (lo, hi) in data.RANGES_DATA.items():
        if lo <= D <= hi: return name
    return 'CK5126'

def rpm(machine, dia):
    diams, rpms = data.TURNING_DATA[machine]
    nd = min(diams, key=lambda x: abs(x - dia))
    return rpms[diams.index(nd)]

def mceil(x, s):
    """Excel: IF(ROUNDUP(x/s)=1, ROUNDUP+1, ROUNDUP)"""
    r = math.ceil(x / s)
    return 2 if r == 1 else r

def excel_thread(p, internal):
    L = p.get('L', 0); M = p.get('M', 0); H = p.get('H', 0)
    if L <= 0 or H <= 0: return 0
    passes = math.ceil(((H / 2) * 1.1) / 0.2)
    rpm_t = (12 if M < 36 else 100) if internal else (10 if M < 16 else 15)
    return (L * passes) / (rpm_t * H) * 60

def excel_total(ptype, p):
    D = p.get('D', 0); d = p.get('d', 0); t = p.get('t', 0)
    D1 = p.get('D1', 0); D2 = p.get('D2', 0); S = p.get('S', 0)
    DM = p.get('DM', 0); a = p.get('a', 0); Dw = p.get('Dw', p.get('DW', 0)); b = p.get('b', 0); c = p.get('c', 0)
    DM1 = p.get('Dm1', 0); dM2 = p.get('dm2', 0); K = p.get('K', 0); E = p.get('E', 0)
    m = machine_by_D(D)
    sl, st, fl, ff, chs = data.FEEDRATE_DATA[m]
    B1 = D1 - D; B2 = S - t; B3 = D1 - D2; B4 = (d - D2) / 2 if d else 0
    B80 = mceil((B1 / 2), sl) if B1 > 0 else 0
    B81 = mceil((B2 / 2), st) if B2 > 0 else 0
    B82 = mceil(B4, st) if B4 > 0 else 0
    B55 = fl * rpm(m, (D1 + D) / 2)
    B54 = ff * rpm(m, (D1 + D2) / 2 if D2 > 0 else D1)
    ops = (S * B80) / B55                                   # B111 нар. точение
    ops += (t * B82) / B55 if d else 0                      # B112 внутр. точение
    ops += (B3 * B81) / B54                                 # B115 торцовка
    # B116 фаски
    chl = sum(p.get(f'ch{i}', 0) / math.cos(p.get(f'angle_ch{i}', 0)) for i in range(1, 11) if p.get(f'ch{i}', 0) > 0)
    ops += chl / chs
    # B113: 1-я внутр. проточка
    B6 = a + E
    B5 = (DM - d) / 2 if DM else 0
    B83 = mceil((B6 / 2), st) if B6 > 0 else 0
    if B5 > 0 and B83 > 0 and ptype not in ('компенсатор', 'втулка', 'штифт'):
        ops += (B5 * B83) / (ff * rpm(m, (DM + d) / 2))
    # B114: 2-я внутр. проточка
    B27 = (Dw - d) / 2 if Dw else 0
    B84 = mceil(t - b, st) if (ptype in ('кольцо', 'приварной') and t - b > 0) else 0
    B85 = mceil(c / 2, st) if (ptype == 'формующий' and c > 0) else 0
    if B27 > 0 and (B84 + B85) > 0:
        ops += (B27 * (B84 + B85)) / (ff * rpm(m, (Dw + d) / 2))
    # B117/B118 компенсатор
    if ptype == 'компенсатор':
        B62 = (DM1 - d) / 2
        if B62 > 0 and B83 > 0: ops += (B62 * B83) / (ff * rpm(m, (DM1 + d) / 2))
        gw = data.GROOVE_INSERT_WIDTH[m]
        B86 = math.ceil(((DM1 - dM2) / 2) / gw) + 1
        if K - E > 0: ops += ((K - E) * B86) / (data.GROOVE_FEED * rpm(m, (D1 + D) / 2))
    # B120/B121 переходной
    if ptype == 'переходной':
        F11 = (D - DM) / 2; F12 = p.get('ch5', 0)
        B87 = mceil(F12, st) if F12 > 0 else 0
        if F11 > 0 and B87 > 0: ops += (F11 * B87) / (ff * rpm(m, (D + DM) / 2))
        P = p.get('P', 0); n = p.get('n', 0); Dk = p.get('Dk', 0)
        if P * n > 0: ops += (P * n) / (ff * rpm(m, Dk))
    # B119 сферический
    if ptype == 'сферический':
        RS = p.get('RS', 0); RA = p.get('RA', 0); A1 = p.get('A1', 0); ash = p.get('as', 0)
        if RS > 0 and RA > 0:
            b5 = (DM - d) / 2
            f1 = 2 * RS * math.sin((RA / 2) * math.pi / 180)
            f2 = math.sqrt(max(0, f1**2 - ash**2))
            f3 = (RS**2 * ((math.pi * RA / 90) - math.sin(2 * RA * math.pi / 180))) / 4
            f4 = ash * (b5 - f2)
            f5 = ((b5 - f2) * ((b5 - f2) * math.tan(A1 * math.pi / 180))) / 2
            f7 = math.ceil(sl); f8 = (f3 + f4 + f5) / f7
            f9 = 2 * math.pi * A1 * RA / 360
            f10 = (b5 - f2) / math.cos(A1 * math.pi / 180)
            ops += (f8 + f9 + f10) / (ff * rpm(m, (DM + d) / 2))
    # B125 канава внешняя (Втулка)
    if ptype == 'втулка':
        Dk_v = p.get('Dk', 0); X = p.get('a', 0)  # в программе ширина = 'a'
        F21 = (Dw - Dk_v) / 2
        if F21 > 0 and X > 0:
            B89 = mceil(X, sl)
            ops += (F21 * B89) / (ff * rpm(m, (D1 + D) / 2))
    # B122/B123 штифт
    if ptype == 'штифт':
        Dc = p.get('Dc', 0)
        ops += (t * B80) / B55
        B88 = mceil((D - Dc) / 2, sl) if D - Dc > 0 else 0
        if a > 0 and B88 > 0: ops += (a * B88) / B55
    total = ops * 60 * calc.get_AWC_coeff(D1, S)
    if p.get('insert_ring', 0) == 1: total *= 2
    # резьба отдельной строкой (E3)
    thr = 0
    if ptype == 'втулка резьбовая': thr = excel_thread(p, internal=True)
    if ptype == 'втулка': thr = excel_thread(p, internal=False)
    return m, total + thr


def rnd(lo, hi, step=1):
    return round(random.uniform(lo, hi) / step) * step

def gen_case():
    ptype, itype = random.choice([
        ('поворотный', 'swivel'), ('круг', 'circle'), ('обечайка', 'shell'),
        ('кольцо', 'weldring'), ('приварной', 'welding_flange'), ('ТНФ', 'welding_tnf'),
        ('компенсатор', 'compensator'), ('формующий', 'forming'), ('переходной', 'adapter'),
        ('сферический', 'rotspher'), ('втулка резьбовая', 'threaded_bushing'),
        ('втулка', 'bushing'), ('штифт', 'pin'),
    ])
    D = rnd(60, 1800, 10)
    t = rnd(15, 80, 5)
    S = t + rnd(4, 12, 2)
    D1 = D + rnd(6, 14, 2)
    d = max(20, D - rnd(40, 160, 10))
    D2 = max(10, d - rnd(6, 14, 2))
    p = {'D': D, 't': t, 'S': S, 'D1': D1,
         'ch1': rnd(1, 3), 'angle_ch1': round(random.uniform(0.2, 0.8), 2),
         'ch2': rnd(0, 2), 'angle_ch2': round(random.uniform(0.2, 0.8), 2)}
    if ptype not in ('круг', 'втулка', 'штифт'):
        p.update({'d': d, 'D2': D2})
    if ptype == 'поворотный' and random.random() < 0.3:
        p['insert_ring'] = 1
    if ptype in ('кольцо', 'приварной'):
        p.update({'DM': d + rnd(10, 40, 5), 'a': rnd(4, 12), 'Dw': d + rnd(5, 30, 5), 'b': rnd(5, t - 5)})
    if ptype == 'ТНФ':
        p.update({'DM': d + rnd(10, 40, 5), 'a': rnd(4, 12)})
    if ptype == 'компенсатор':
        dm2 = d + rnd(10, 30, 5)
        p.update({'Dm1': dm2 + rnd(10, 40, 5), 'dm2': dm2, 'E': rnd(4, 10), 'K': rnd(12, 25)})
    if ptype == 'формующий':
        p.update({'DM': d + rnd(10, 40, 5), 'a': rnd(4, 12), 'DW': d + rnd(5, 30, 5), 'c': rnd(4, 14)})
    if ptype == 'переходной':
        p.update({'DM': D - rnd(10, 40, 5), 'ch5': rnd(2, 8),
                  'Dk': d + rnd(5, 25, 5), 'P': rnd(2, 6), 'n': rnd(2, 8)})
    if ptype == 'сферический':
        p.update({'DM': d + rnd(20, 60, 5), 'as': rnd(8, 25), 'RS': rnd(60, 150, 10),
                  'RA': rnd(30, 80, 5), 'A1': rnd(5, 25, 5)})
    if ptype == 'втулка резьбовая':
        p.update({'M': rnd(20, 70, 5), 'H': random.choice([1.5, 2, 2.5, 3]), 'L': rnd(10, 40, 5)})
    if ptype == 'втулка':
        Dk_v = D - rnd(10, 30, 5)
        p.update({'Dw': Dk_v + rnd(4, 16, 2), 'Dk': Dk_v, 'a': rnd(3, 12),
                  'M': rnd(20, 70, 5), 'H': random.choice([1.5, 2, 2.5]), 'L': rnd(10, 40, 5),
                  'ch3': rnd(0, 2), 'angle_ch3': round(random.uniform(0.2, 0.8), 2)})
    if ptype == 'штифт':
        p.update({'Dc': max(10, D - rnd(20, 60, 10)), 'a': rnd(5, 30, 5)})
    return ptype, itype, p


fails = 0
print(f"{'#':>3} {'тип':<18} {'станок':<14} {'Excel,с':>10} {'Python,с':>10} {'Δ%':>8}")
for i in range(1, 51):
    ptype, itype, p = gen_case()
    m_x, t_x = excel_total(ptype, dict(p))
    res = calc.calculate_lathe_time(itype, dict(p))
    t_p = res['time_sec'] + res.get('thread_sec', 0)
    dpc = (t_p - t_x) / t_x * 100 if t_x else float('nan')
    flag = '' if abs(dpc) < 3 else '  <-- РАСХОЖДЕНИЕ > 3%'
    if abs(dpc) >= 3: fails += 1
    print(f"{i:>3} {ptype:<18} {m_x:<14} {t_x:>10.2f} {t_p:>10.2f} {dpc:>7.3f}%{flag}")
print(f"\nИтого случаев с расхождением >= 3%: {fails} из 50")
