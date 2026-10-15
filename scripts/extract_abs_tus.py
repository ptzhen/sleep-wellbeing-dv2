"""Extract sleep-related tables from ABS How Australians Use Their Time 2020-21.
Usage: python3 extract_abs_tus.py <raw_dir> <out_dir>"""
import sys, csv, openpyxl
raw, out = sys.argv[1], sys.argv[2]

def hm(v):  # 'h:mm' -> minutes
    if v in (None, '', 'np', '..'): return ''
    h, m = str(v).split(':')[:2]
    return int(h) * 60 + int(m)

def sheet(f, s):
    return list(openpyxl.load_workbook(f'{raw}/{f}', read_only=True, data_only=True)[s].iter_rows(values_only=True))

# 1) Proportion asleep / doing activity by hour of day (Tables 13.1-17.1)
acts = {'13.1': 'Sleep', '14.1': 'Work', '15.1': 'Domestic', '16.1': 'Child care', '17.1': 'Free time'}
with open(f'{out}/tus_activity_by_hour.csv', 'w', newline='') as fo:
    w = csv.writer(fo); w.writerow(['activity', 'hour_start', 'time_label', 'day_type', 'sex', 'pct'])
    for t, act in acts.items():
        rows = sheet('ABS_TUS_T13-17.xlsx', f'Table {t}')
        groups = [(d, s) for d in ['Weekday', 'Weekend', 'All days'] for s in ['Males', 'Females', 'Persons']]
        if t == '17.1':
            # Table 17.1 is laid out differently: a WEEKDAY block then a WEEKEND DAY block,
            # with columns for two sub-groups and then 'Total Free time' (columns 7-9)
            day, h = None, 0
            for r in rows:
                if r[0] is None and r[1] in ('WEEKDAY', 'WEEKEND DAY'):
                    day, h = ('Weekday' if r[1] == 'WEEKDAY' else 'Weekend'), 0
                elif day and r[0] and ('AM–' in str(r[0]) or 'PM–' in str(r[0])):
                    for k, sx in enumerate(['Males', 'Females', 'Persons']):
                        w.writerow([act, h, str(r[0]), day, sx, r[7 + k]])
                    h += 1
            continue
        h = 0
        for r in rows:
            if r[0] and ('AM–' in str(r[0]) or 'PM–' in str(r[0])):
                for k, (d, s) in enumerate(groups):
                    v = r[1 + k]
                    w.writerow([act, h, str(r[0]), d, s, '' if v is None else v])
                h += 1

# 2) Sleep and sleeplessness: average time and participation (T1.1 all, T2.1 weekday/weekend, T5.1 15-24)
with open(f'{out}/tus_sleep_summary.csv', 'w', newline='') as fo:
    w = csv.writer(fo)
    w.writerow(['group', 'day_type', 'sex', 'activity', 'pct_participated', 'mins_participants', 'mins_total_pop'])
    sexes = ['Males', 'Females', 'Persons']
    for f, s, grp in [('ABS_TUS_T1.xlsx', 'Table 1.1', 'All 15+'), ('ABS_TUS_T5.xlsx', 'Table 5.1', '15 to 24')]:
        for r in sheet(f, s):
            if r[0] in ('Sleeping', 'Sleeplessness'):
                for k, sx in enumerate(sexes):
                    w.writerow([grp, 'All days', sx, r[0], r[1 + k], hm(r[4 + k]), hm(r[7 + k])])
    for r in sheet('ABS_TUS_T2.xlsx', 'Table 2.1'):
        if r[0] in ('Sleeping', 'Sleeplessness'):
            for di, d in enumerate(['Weekday', 'Weekend']):
                for k, sx in enumerate(sexes):
                    c = di * 3 + k
                    w.writerow(['All 15+', d, sx, r[0], r[1 + c], hm(r[7 + c]), hm(r[13 + c])])

# 3) Personal care time (mostly sleep) of total population by demographics (T4.5)
rows = sheet('ABS_TUS_T4.xlsx', 'Table 4.5')
cats = [c for c in rows[6]]  # activity headers
with open(f'{out}/tus_time_by_demographic.csv', 'w', newline='') as fo:
    w = csv.writer(fo)
    w.writerow(['sex', 'dimension', 'group', 'personal_care_mins', 'paid_work_mins', 'free_time_mins', 'pop_000'])
    sex = dim = None
    for r in rows[8:]:
        if r[0] is None and str(r[1]).strip() in ('MALES', 'FEMALES', 'PERSONS'):
            sex = str(r[1]).strip().title(); continue
        lab = r[0]
        if not lab: continue
        lab = str(lab).strip()
        if all(v is None for v in r[1:5]): dim = lab; continue
        if sex is None or lab.startswith(('Total', '©')): continue
        def col(name):
            return hm(r[cats.index(name)]) if name in cats else ''
        w.writerow([sex, dim, lab, col('Personal care activities'), col('Employment related activities'),
                    col('Total Free time'), r[13] if isinstance(r[13], (int, float)) else ''])
print('done')
