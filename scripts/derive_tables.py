"""Small derived tables for the page, built from the cleaned CSVs in data/.
Usage: python3 derive_tables.py <data_dir>"""
import sys, csv, math, os
d = sys.argv[1]

# 1. Sleep by life circumstance now comes from extract_abs_tus2024.py (ABS 2024)

# 2. Capital city vs rest of state, high/very high distress (PHIDU 2022), with tile-grid positions
rows = {r['name'].strip(): r for r in csv.DictReader(open(f'{d}/phidu_state_2022.csv'))}
tiles = [('NT', 'Northern Territory', 'Greater Darwin', 'Rest of Northern Territory', 1, 0),
         ('QLD', 'Queensland', 'Greater Brisbane', 'Rest of Queensland', 2, 0),
         ('WA', 'Western Australia', 'Greater Perth', 'Rest of Western Australia', 0, 1),
         ('SA', 'South Australia', 'Greater Adelaide', 'Rest of South Australia', 1, 1),
         ('NSW', 'New South Wales', 'Greater Sydney', 'Rest of New South Wales', 2, 1),
         ('ACT', 'Australian Capital Territory', 'Australian Capital Territory (Canberra)', None, 3, 1),
         ('VIC', 'Victoria', 'Greater Melbourne', 'Rest of Victoria', 2, 2),
         ('TAS', 'Tasmania', 'Greater Hobart', 'Rest of Tasmania', 2, 3)]
with open(f'{d}/capital_vs_rest.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['abbr', 'state', 'area', 'area_name', 'col', 'row', 'k10_high_persons', 'k10_high_female', 'k10_high_male'])
    for ab, st, cap, rest, c, r in tiles:
        for area, name in [('Capital city', cap), ('Rest of state', rest)]:
            if name is None: continue
            x = rows[name]
            w.writerow([ab, st, area, name.replace(' (Canberra)', ''), c, r,
                        x['k10_high_persons'], x['k10_high_female'], x['k10_high_male']])

# 3. Sunrise clock time for capital cities (same NOAA equation as sunrise_field.py)
sys.path.insert(0, os.path.dirname(__file__))
src = open(os.path.join(os.path.dirname(__file__), 'sunrise_field.py')).read()
ns = {'math': math}; exec(src[src.index('def sunrise_utc'):src.index('step = 0.1')], ns)
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
