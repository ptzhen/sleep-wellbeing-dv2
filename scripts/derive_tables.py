"""Small derived tables for the page, built from the cleaned CSVs in data/.
Usage: python3 derive_tables.py <data_dir>"""
import sys, csv, math, os
d = sys.argv[1]

# 1. Sleep minutes (participants, primary activity) by life circumstance, ABS TUS 2020-21 Tables 8-11
pick = {
    ('Table 8.3', 'Has disability'): 'Has a disability',
    ('Table 8.3', 'Has no disability'): 'No disability',
    ('Table 9.3', 'Provided care to another person'): 'Carer',
    ('Table 9.3', 'Did not provide care to another person'): 'Not a carer',
    ('Table 10.3', 'Did unpaid voluntary work in last 12 months'): 'Volunteer',
    ('Table 10.3', 'Did not do unpaid voluntary work in last 12 months'): 'Not a volunteer',
    ('Table 11.3', 'Youngest child in household 0 to 4 years'): 'Parent, youngest child 0–4',
    ('Table 11.3', 'Youngest child in household 5 to 14 years'): 'Parent, youngest child 5–14',
    ('Table 11.3', 'Non-parents'): 'No child under 15',
}
sexmap = {'Males': 'Men', 'Male parents': 'Men', 'Females': 'Women', 'Female parents': 'Women',
          'Persons': 'All', 'Total parents': 'All', 'Total': 'All'}
out, seen = [], set()
for r in csv.DictReader(open(f'{d}/abs_tus_sleep_extra_tables.csv')):
    if r['activity'] != 'Sleeping' or r['activity_scope'] != 'Primary Activity': continue
    g = pick.get((r['sheet'], r['group']))
    s = sexmap.get(r['subgroup'].strip())
    if g and s and (g, s) not in seen:
        seen.add((g, s)); out.append([g, s, float(r['value']), r['table']])
with open(f'{d}/sleep_by_circumstance.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['group', 'sex', 'sleep_min', 'source_table']); w.writerows(out)

# 2. Capital city vs rest of state, high/very high distress (PHIDU 2022)
rows = {r['name'].strip(): r for r in csv.DictReader(open(f'{d}/phidu_state_2022.csv'))}
pairs = [('New South Wales', 'Greater Sydney', 'Rest of New South Wales'),
         ('Victoria', 'Greater Melbourne', 'Rest of Victoria'),
         ('Queensland', 'Greater Brisbane', 'Rest of Queensland'),
         ('South Australia', 'Greater Adelaide', 'Rest of South Australia'),
         ('Western Australia', 'Greater Perth', 'Rest of Western Australia'),
         ('Tasmania', 'Greater Hobart', 'Rest of Tasmania'),
         ('Northern Territory', 'Greater Darwin', 'Rest of Northern Territory')]
with open(f'{d}/capital_vs_rest.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['state', 'area', 'area_name', 'k10_high_persons'])
    for st, cap, rest in pairs:
        w.writerow([st, 'Capital city', cap, rows[cap]['k10_high_persons']])
        w.writerow([st, 'Rest of state', rest, rows[rest]['k10_high_persons']])

# 3. Sunrise clock time for capital cities (same NOAA equation as sunrise_field.py)
sys.path.insert(0, os.path.dirname(__file__))
src = open(os.path.join(os.path.dirname(__file__), 'sunrise_field.py')).read()
ns = {'math': math}; exec(src[src.index('def sunrise_utc'):src.index('step = 0.5')], ns)
cities = [('Perth', -31.95, 115.86, 8, 8), ('Darwin', -12.46, 130.84, 9.5, 9.5), ('Adelaide', -34.93, 138.6, 9.5, 10.5),
          ('Brisbane', -27.47, 153.03, 10, 10), ('Sydney', -33.87, 151.21, 10, 11), ('Canberra', -35.28, 149.13, 10, 11),
          ('Melbourne', -37.81, 144.96, 10, 11), ('Hobart', -42.88, 147.33, 10, 11)]
with open(f'{d}/sunrise_cities.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['season', 'city', 'lon', 'lat', 'sunrise_min', 'sunrise_label'])
    for season, doy, k in [('Winter (21 June)', 172, 0), ('Summer (21 December)', 355, 1)]:
        for c, la, lo, tw, ts in cities:
            m = ns['sunrise_utc'](la, lo, doy) + (tw, ts)[k] * 60
            w.writerow([season, c, lo, la, round(m, 1), f'{int(m // 60)}:{int(m % 60):02d} am'])
print(len(out), 'circumstance rows')
