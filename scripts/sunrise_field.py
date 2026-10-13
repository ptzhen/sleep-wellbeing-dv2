"""Sunrise clock time across Australia on the summer and winter solstices, as 30-minute bands.
Computes a 0.1 degree grid with the NOAA sunrise equation (zenith 90.833 deg), converts it to
each state's legal clock time (incl. daylight saving in summer), merges cells into 30-minute
bands and clips each band to the state outline, so the bands fill exactly to the coast.
Usage: python3 sunrise_field.py <states.geojson> <out_bands.geojson>
Then: mapshaper out_bands.geojson name=bands -o sunrise_bands.topojson format=topojson quantization=1e5"""
import sys, csv, json, math
import numpy as np
from shapely.geometry import shape, box, mapping, Polygon, MultiPolygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely.prepared import prep

src, out_geo = sys.argv[1:3]
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

step = 0.1
BREAKS = [270, 300, 330, 360, 390, 420, 450]
def band_label(i):
    t = lambda m: f'{m // 60}:{m % 60:02d}'
    if i == 0: return f'before {t(BREAKS[0])} am'
    if i == len(BREAKS): return f'after {t(BREAKS[-1])} am'
    return f'{t(BREAKS[i - 1])}–{t(BREAKS[i])} am'

feats = []
for season, (doy, si) in SEASONS.items():
    for name, pg, geom in prepped:
        x0, y0, x1, y1 = geom.bounds
        cells = {}
        # integer cell indices so neighbouring cells share exact edges and merge without slivers
        for ix in range(int(math.floor(x0 / step)), int(math.ceil(x1 / step)) + 1):
            for iy in range(int(math.floor(y0 / step)), int(math.ceil(y1 / step)) + 1):
                lo, la = round(ix * step, 6), round(iy * step, 6)
                m = (sunrise_utc(la + step / 2, lo + step / 2, doy) + TZ[name][si] * 60) % 1440
                i = int(np.searchsorted(BREAKS, m, side='right'))
                cells.setdefault(i, []).append(box(lo, la, round(lo + step, 6), round(la + step, 6)))
        for i, boxes in cells.items():
            band = unary_union(boxes).buffer(1e-7).intersection(geom).simplify(0.02)
            if band.is_empty: continue
            # d3-geo (used by Vega) expects clockwise outer rings
            polys = [q for q in getattr(band, 'geoms', [band]) if isinstance(q, Polygon)]
            g = mapping(MultiPolygon([orient(q, sign=-1.0) for q in polys]))
            feats.append({'type': 'Feature', 'properties': {'season': season, 'state': name, 'band': i, 'label': band_label(i)},
                          'geometry': g})

def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 3), round(c[1], 3)]
for f in feats:
    f['geometry'] = {'type': f['geometry']['type'], 'coordinates': rnd(f['geometry']['coordinates'])}
json.dump({'type': 'FeatureCollection', 'features': feats}, open(out_geo, 'w'))
print(len(feats), 'band polygons')
