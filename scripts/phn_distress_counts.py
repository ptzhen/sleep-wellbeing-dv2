"""Estimated number of adults with high/very high psychological distress per PHN,
plus a label point (inside the polygon) for each PHN, for the proportional symbol map.
Usage: python3 phn_distress_counts.py <phidu_data_phn_lga_aust.xlsx> <phn.topojson> <out.csv>"""
import sys, csv, json, re, openpyxl
from shapely.geometry import shape
src, topo, out = sys.argv[1:4]

ws = openpyxl.load_workbook(src, read_only=True, data_only=True)['Estimates_risk_factors_adults']
rows = list(ws.iter_rows(values_only=True))
desc, head = rows[0], rows[4]
col = None
for j, d in enumerate(desc):
    if d and 'psychological distress' in d and 'persons aged' in re.sub(r'\s+', ' ', d):
        col = j
        break
assert head[col] == 'Number', head[col]
counts = {}
for r in rows[5:]:
    if r[0] and str(r[0]).startswith('PHN') and r[0] not in counts and isinstance(r[col], (int, float)):
        counts[r[0]] = round(r[col])

# decode topojson arcs to get polygons for representative points
t = json.load(open(topo))
sc, tr = t['transform']['scale'], t['transform']['translate']
arcs = []
for a in t['arcs']:
    x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy
        pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
    arcs.append(pts)
def ring(ix):
    pts = []
    for i in ix:
        seg = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(seg if not pts else seg[1:])
    return pts
with open(out, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['code', 'name', 'state', 'distressed_adults', 'lon', 'lat'])
    for g in t['objects']['phn']['geometries']:
        p = g['properties']
        if g['type'] == 'Polygon': geo = {'type': 'Polygon', 'coordinates': [ring(r) for r in g['arcs']]}
        else: geo = {'type': 'MultiPolygon', 'coordinates': [[ring(r) for r in poly] for poly in g['arcs']]}
        s = shape(geo).buffer(0)
        if s.geom_type == 'MultiPolygon': s = max(s.geoms, key=lambda q: q.area)
        pt = s.representative_point()
        w.writerow([p['PHN_CODE'], p['PHN_NAME'], p['STATE_NAME'], counts.get(p['PHN_CODE'], ''), round(pt.x, 3), round(pt.y, 3)])
print(len(counts), 'PHNs with counts; column', col, desc[col][:80])
