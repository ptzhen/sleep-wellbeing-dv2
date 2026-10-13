"""Sunrise clock time across Australia on the summer and winter solstices.
Computes a 0.5 degree grid with the NOAA sunrise equation (zenith 90.833 deg),
converts it to each state's legal clock time (incl. daylight saving in summer),
and writes isolines every 30 minutes, clipped to each state.
Usage: python3 sunrise_field.py <states.geojson> <out_grid.csv> <out_isolines.geojson>"""
import sys, csv, json, math
import numpy as np
from shapely.geometry import shape, Point, LineString, mapping
from shapely.prepared import prep
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

src, out_csv, out_geo = sys.argv[1:4]
states = [(f['properties']['STATE_NAME'], shape(f['geometry']).buffer(0)) for f in json.load(open(src))['features']]
prepped = [(n, prep(g), g) for n, g in states]

# UTC offsets in hours: [winter, summer]
TZ = {'Western Australia': (8, 8), 'Northern Territory': (9.5, 9.5), 'South Australia': (9.5, 10.5),
      'Queensland': (10, 10), 'New South Wales': (10, 11), 'Australian Capital Territory': (10, 11),
      'Victoria': (10, 11), 'Tasmania': (10, 11)}
SEASONS = {'Winter (21 June)': (172, 0), 'Summer (21 December)': (355, 1)}

def sunrise_utc(lat, lon, doy):
    """NOAA approximation; returns sunrise in minutes after UTC midnight."""
    g = 2 * math.pi / 365 * (doy - 1)
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                       - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    phi = math.radians(lat)
    ha = math.degrees(math.acos(math.cos(math.radians(90.833)) / (math.cos(phi) * math.cos(decl))
                                - math.tan(phi) * math.tan(decl)))
    return 720 - 4 * (lon + ha) - eqtime

step = 0.5
lons = np.arange(112.75, 154, step)
lats = np.arange(-43.75, -10, step)
rows, iso = [], []
for season, (doy, si) in SEASONS.items():
    for name, pg, geom in prepped:
        z = np.full((len(lats), len(lons)), np.nan)
        # wider evaluation (no mask) so contours extend to the coast, then clip to the state
        for i, la in enumerate(lats):
            for j, lo in enumerate(lons):
                z[i, j] = (sunrise_utc(la, lo, doy) + TZ[name][si] * 60) % 1440
                if pg.contains(Point(lo, la)):
                    rows.append([season, name, lo, la, round(z[i, j], 1)])
        levels = np.arange(240, 540, 30)
        cs = plt.contour(lons, lats, z, levels=levels)
        for lev, segs in zip(cs.levels, cs.allsegs):
            for seg in segs:
                if len(seg) < 2: continue
                clipped = LineString(seg).intersection(geom)
                if clipped.is_empty: continue
                label = f'{int(lev // 60)}:{int(lev % 60):02d}'
                iso.append({'type': 'Feature', 'properties': {'season': season, 'state': name, 'minutes': int(lev), 'label': label},
                            'geometry': json.loads(json.dumps(mapping(clipped.simplify(0.05))))})
        plt.close('all')

with open(out_csv, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['season', 'state', 'lon', 'lat', 'sunrise_min']); w.writerows(rows)
def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 3), round(c[1], 3)]
for f in iso: f['geometry']['coordinates'] = rnd(f['geometry']['coordinates'])
json.dump({'type': 'FeatureCollection', 'features': [f for f in iso if f['geometry']['coordinates']]}, open(out_geo, 'w'))
print(len(rows), 'cells,', len(iso), 'isolines')
