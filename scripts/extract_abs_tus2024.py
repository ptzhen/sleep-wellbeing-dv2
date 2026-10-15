"""Sleep minutes from ABS How Australians Use Their Time, 2024 (TUSDC tables).
Usage: python3 extract_abs_tus2024.py <folder with TUSDC*.xlsx> <data_dir>
In 2024 everyone recorded some sleep, so participant and whole-population averages are the same."""
import sys, csv, datetime, openpyxl
src, out = sys.argv[1], sys.argv[2]

def sleeping_row(table, sheet):
    rows = list(openpyxl.load_workbook(f'{src}/{table}.xlsx', read_only=True)[sheet]
                .iter_rows(max_col=60, values_only=True))
    head, sub = rows[4], rows[5]
    if table == 'TUSDC04': head, sub = rows[5], rows[6]   # extra header row (measure, then day type)
    sleep = next(r for r in rows if r[0] == 'Sleeping')
    cols, cur = [], None
    for i in range(1, len(sleep)):
        if head[i]: cur = str(head[i]).strip()
        if isinstance(sleep[i], datetime.timedelta):
            cols.append((cur, str(sub[i]).replace('\n', ' ').strip(), round(sleep[i].total_seconds() / 60)))
    return cols

SEX = {'Males': 'Men', 'Male parents': 'Men', 'Females': 'Women', 'Female parents': 'Women',
       'Persons(b)': 'All', 'Persons(c)': 'All', 'Persons(d)': 'All', 'Total parents(b)': 'All'}

# Weekday vs weekend (Table 4.1): the first block of time columns is participants
with open(f'{out}/tus2024_sleep_summary.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['day_type', 'sex', 'sleep_min', 'source'])
    for day in ['All days']:
        for sex, m in zip(['Men', 'Women', 'All'], [r[2] for r in sleeping_row('TUSDC01', 'Table 1.1')[:3]]):
            w.writerow([day, sex, m, 'ABS TUS 2024 Table 1.1'])
    for day, sex, m in sleeping_row('TUSDC04', 'Table 4.1')[:6]:
        w.writerow([day, SEX[sex], m, 'ABS TUS 2024 Table 4.1'])

# Life circumstances (Tables 5.3, 11.3, 12.3, 13.3)
NAMES = {
    'Youngest child in household aged under 1 year': 'Parent, youngest child under 1',
    'Youngest child in household aged 1 year': 'Parent, youngest child aged 1',
    'Youngest child in household aged 2 to 4 years': 'Parent, youngest child 2–4',
    'Youngest child in household aged 5 to 11 years': 'Parent, youngest child 5–11',
    'Youngest child in household aged 12 to 14 years': 'Parent, youngest child 12–14',
    'Non-parents': 'No child under 15 at home',
    'Has disability(b)': 'Has a disability', 'Has no disability': 'No disability',
    'Provided care to another person(b)': 'Carer', 'Did not provide care to another person(c)': 'Not a carer',
    'Did unpaid voluntary work in last 12 months(b)': 'Volunteer',
    'Did not do unpaid voluntary work in last 12 months(c)': 'Not a volunteer'}
with open(f'{out}/sleep_by_circumstance.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['group', 'sex', 'sleep_min', 'source_table'])
    for t, s in [('TUSDC05', 'Table 5.3'), ('TUSDC12', 'Table 12.3'), ('TUSDC13', 'Table 13.3'), ('TUSDC11', 'Table 11.3')]:
        for g, sex, m in sleeping_row(t, s):
            if g in NAMES and sex in SEX:
                w.writerow([NAMES[g], SEX[sex], m, 'ABS TUS 2024 ' + s])
