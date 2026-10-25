"""Draw the rooftop skylines used at the chapter breaks (decoration only, no data).
Usage: python3 scripts/make_skyline.py img"""
import random, sys

def skyline(fill, windows, seed=7, W=1440, H=140):
    r = random.Random(seed)  # fixed seed, so both skylines are the same street
    parts, wins, x = [], [], 0
    while x < W:
        kind = r.random()
        if kind < 0.18:  # tree
            cx = x + 18; rr = r.randint(14, 22); top = H - r.randint(40, 60)
            parts.append(f'<rect x="{cx-2}" y="{top+rr}" width="4" height="{H-top-rr}"/>')
            parts.append(f'<circle cx="{cx}" cy="{top+rr}" r="{rr}"/><circle cx="{cx-rr*0.6:.0f}" cy="{top+rr*1.5:.0f}" r="{rr*0.75:.0f}"/>'
                         f'<circle cx="{cx+rr*0.6:.0f}" cy="{top+rr*1.5:.0f}" r="{rr*0.75:.0f}"/>')
            x += rr * 2 + r.randint(4, 14); continue
        w = r.randint(46, 92); h = r.randint(34, 70) if kind < 0.8 else r.randint(80, 112)
        y = H - h
        if kind < 0.6:  # house with a gable roof
            roof = r.randint(14, 24)
            parts.append(f'<path d="M{x} {H}V{y+roof}L{x+w/2:.0f} {y}L{x+w} {y+roof}V{H}Z"/>')
            if r.random() < 0.4: parts.append(f'<rect x="{x+w*0.7:.0f}" y="{y+2}" width="7" height="{roof}"/>')
            top = y + roof
        else:  # flats
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>'); top = y
        if windows:
            for wy in range(top + 10, H - 14, 18):
                for wx in range(x + 8, x + w - 14, 16):
                    if r.random() < 0.16: wins.append(f'<rect x="{wx}" y="{wy}" width="7" height="9" rx="1"/>')
        x += w + r.randint(0, 10)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice"><g fill="{fill}">{"".join(parts)}</g>'
    if windows: svg += f'<g fill="#f3b64e" opacity=".85">{"".join(wins)}</g>'
    return svg + '</svg>'

out = sys.argv[1]
open(f"{out}/skyline-night.svg", "w").write(skyline("#0b0f2a", True))   # darker than the sky, so the rooftops read as a silhouette
open(f"{out}/skyline-dawn.svg", "w").write(skyline("#3b2550", False))
