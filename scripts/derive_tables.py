"""Small derived tables for the page, built from the cleaned CSVs in data/.
Usage: python3 derive_tables.py <data_dir>"""
import sys, csv, math, os
d = sys.argv[1]

# 1. Sleep by life circumstance now comes from extract_abs_tus2024.py (ABS 2024)

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
print('done')
