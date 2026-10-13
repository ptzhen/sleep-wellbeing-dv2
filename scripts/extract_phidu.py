"""Extract PHIDU Social Health Atlas indicators (ASR per 100) to tidy CSVs.
Usage: python3 extract_phidu.py <phidu_data_phn_lga_aust.xlsx> <out_dir>"""
import sys, csv, re, openpyxl
src, out = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(src, read_only=True, data_only=True)

def blocks(ws):
    rows = list(ws.iter_rows(values_only=True))
    desc, head = rows[0], rows[4]
    res = []
    for j, h in enumerate(head):
        if h == 'ASR per 100':
            k = j
            while k >= 0 and not (desc[k] and k >= 2): k -= 1
            res.append((j, re.sub(r'\s+', ' ', desc[k]).strip()))
    return rows, res

def short(d):
    m = {'psychological distress': 'k10_high', 'fair or poor self-assessed': 'fair_poor_health',
         'physical activity': 'inactive', 'current smokers': 'smoker', '5 or more standard': 'risky_drinking',
         'who were obese': 'obese', 'high blood pressure': 'high_bp'}
    for k, v in m.items():
        if k in d:
            sex = 'male' if 'males aged' in d and 'females' not in d else 'female' if 'females aged' in d else 'persons'
            return f'{v}_{sex}'
    return None

recs = {}  # (level, code, name) -> {indicator: value}
for sheet in ['Estimates_risk_factors_adults', 'Estimates_self_assessed_health']:
    rows, bl = blocks(wb[sheet])
    level = 'PHN'
    seen_phn = set()
    for r in rows[5:]:
        code, name = r[0], r[1]
        if not name: continue
        name = str(name).strip()
        if code is None:
            if name.startswith(('+', '*', 'For more', '++')): continue
            lvl, key = 'STATE', name
        else:
            code = str(code).strip()
            if code.startswith('PHN'):
                if code in seen_phn: lvl = 'PHN_REPEAT'
                else: seen_phn.add(code); lvl = 'PHN'
            else: lvl = 'LGA'
            key = code
        if lvl == 'PHN_REPEAT': continue
        d = recs.setdefault((lvl, key, name), {})
        for j, desc in bl:
            ind = short(desc)
            if ind and r[j] not in (None, '', '..', '#', '~'):
                try: d[ind] = round(float(r[j]), 2)
                except ValueError: pass

cols = sorted({k for d in recs.values() for k in d})
for lvl in ['PHN', 'LGA', 'STATE']:
    with open(f'{out}/phidu_{lvl.lower()}_2022.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['code', 'name'] + cols)
        for (l, key, name), d in recs.items():
            if l == lvl and d: w.writerow([key if lvl != 'STATE' else '', name] + [d.get(c, '') for c in cols])
print(cols)
