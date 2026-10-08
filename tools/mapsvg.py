"""Dotted map of Selangor + Kuala Lumpur.

The source template uses a dotted map of the United States with pins on the
cities it serves. Same device here, but the geography is the actual service
area: Selangor and the Federal Territory, so the five pins land where those
towns really are instead of piling up on one corner of a country map.

The outline is a simplified lon/lat polygon; dots are a grid sampled inside it.
"""

VIEW_W, VIEW_H = 1000, 720

# Rough coastline + inland border, (lon, lat), clockwise from the north-west.
OUTLINE = [
    (101.26, 3.80), (100.98, 3.70), (100.93, 3.46), (101.02, 3.24),
    (101.24, 3.06), (101.30, 2.90), (101.40, 2.79), (101.52, 2.69),
    (101.67, 2.64), (101.82, 2.71), (101.93, 2.88), (101.96, 3.07),
    (101.86, 3.21), (101.92, 3.37), (101.81, 3.52), (101.70, 3.61),
    (101.58, 3.71), (101.44, 3.81),
]

LON0, LON1 = 100.86, 102.03
LAT0, LAT1 = 2.56, 3.88

PAD = 36


def project(lon, lat):
    """lon/lat -> svg user units, north up."""
    x = PAD + (lon - LON0) / (LON1 - LON0) * (VIEW_W - PAD * 2)
    y = PAD + (LAT1 - lat) / (LAT1 - LAT0) * (VIEW_H - PAD * 2)
    return x, y


def percent(lon, lat):
    """lon/lat -> percentage of the svg box, for absolutely positioned pins."""
    x, y = project(lon, lat)
    return round(x / VIEW_W * 100, 2), round(y / VIEW_H * 100, 2)


def _inside(px, py, poly):
    hit = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > py) != (y2 > py):
            xi = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if px < xi:
                hit = not hit
    return hit


def dotted_map(step=17, r=3.1):
    poly = [project(lon, lat) for lon, lat in OUTLINE]
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    dots = []
    y = min(ys)
    row = 0
    while y <= max(ys):
        # offset alternate rows so the grid reads as a texture, not a screen door
        x = min(xs) + (step / 2 if row % 2 else 0)
        while x <= max(xs):
            if _inside(x, y, poly):
                dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
            x += step
        y += step * 0.88
        row += 1
    return (
        f'<svg viewBox="0 0 {VIEW_W} {VIEW_H}" role="img" '
        f'aria-label="Dotted map of Selangor and Kuala Lumpur showing the areas Meranti Works serves">'
        f'<g class="map__dot">{"".join(dots)}</g></svg>'
    )


# Where each place actually is.
PLACES = {
    'kuala-lumpur':  (101.693, 3.139),
    'petaling-jaya': (101.617, 3.107),
    'shah-alam':     (101.532, 3.073),
    'subang-jaya':   (101.588, 3.044),
    'klang':         (101.443, 3.044),
}
