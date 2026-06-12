#!/usr/bin/env python3
"""
Generates assets/photos/case_map.png — a North-Atlantic map of the key
locations in the Epstein case (Palm Beach, New York, USVI, London, Paris)
with connecting routes, drawn in the deck's navy/gold palette.

Land geometry: assets/countries.geo.json (johan/world.geo.json, derived
from Natural Earth public-domain data).
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "countries.geo.json")
OUT = os.path.join(HERE, "assets", "photos", "case_map.png")

# deck palette
NAVY  = (0x0F, 0x2A, 0x43, 255)
ACCENT= (0xC0, 0x8A, 0x2B, 255)
LIGHT = (0xF2, 0xF4, 0xF7, 255)
GREY  = (0x6B, 0x76, 0x82, 255)

# ---- crop & projection (plate carrée, x scaled by cos of mid-latitude) ----
LON0, LON1 = -100.0, 16.0
LAT0, LAT1 = 12.0, 58.0
KLAT = math.cos(math.radians((LAT0 + LAT1) / 2))
W = 2000
H = int(round(W * (LAT1 - LAT0) / ((LON1 - LON0) * KLAT)))
SS = 2  # supersample factor for anti-aliased land/arcs

def proj(lon, lat, w, h):
    x = (lon - LON0) / (LON1 - LON0) * w
    y = (LAT1 - lat) / (LAT1 - LAT0) * h
    return x, y

# ---- Sutherland–Hodgman polygon clipping against the (padded) crop box ----
PAD = 4.0
def clip_poly(pts):
    def clip_edge(pts, inside, intersect):
        out = []
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            ia, ib = inside(a), inside(b)
            if ia:
                out.append(a)
                if not ib: out.append(intersect(a, b))
            elif ib:
                out.append(intersect(a, b))
        return out
    def x_lo(p): return p[0] >= LON0 - PAD
    def x_hi(p): return p[0] <= LON1 + PAD
    def y_lo(p): return p[1] >= LAT0 - PAD
    def y_hi(p): return p[1] <= LAT1 + PAD
    def ix_lo(a, b):
        t = (LON0 - PAD - a[0]) / (b[0] - a[0]); return (LON0 - PAD, a[1] + t * (b[1] - a[1]))
    def ix_hi(a, b):
        t = (LON1 + PAD - a[0]) / (b[0] - a[0]); return (LON1 + PAD, a[1] + t * (b[1] - a[1]))
    def iy_lo(a, b):
        t = (LAT0 - PAD - a[1]) / (b[1] - a[1]); return (a[0] + t * (b[0] - a[0]), LAT0 - PAD)
    def iy_hi(a, b):
        t = (LAT1 + PAD - a[1]) / (b[1] - a[1]); return (a[0] + t * (b[0] - a[0]), LAT1 + PAD)
    for inside, intersect in ((x_lo, ix_lo), (x_hi, ix_hi), (y_lo, iy_lo), (y_hi, iy_hi)):
        pts = clip_edge(pts, inside, intersect)
        if len(pts) < 3: return []
    return pts

# ---- case locations & routes ----
LOCS = {
    "New York":   (-74.01, 40.71),
    "Palm Beach": (-80.04, 26.71),
    "USVI":       (-64.83, 18.30),
    "London":     (-0.13, 51.51),
    "Paris":      (2.35, 48.86),
}
HUBS = {"New York", "USVI"}  # slightly larger markers
# (from, to, control-point offset in degrees from the chord midpoint) —
# offsets chosen so routes bow over open water, clear of land and labels
ARCS = [
    ("New York", "Palm Beach", (4.5, 0.0)),
    ("New York", "USVI",       (3.5, 1.0)),
    ("Palm Beach", "USVI",     (2.0, -1.0)),
    ("London", "New York",     (0.0, -8.0)),
    ("Paris", "New York",      (0.0, -14.0)),
]

def bezier(p0, p1, p2, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts

def main():
    ws, hs = W * SS, H * SS
    img = Image.new("RGBA", (ws, hs), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # land
    gj = json.load(open(SRC))
    for feat in gj["features"]:
        geom = feat["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            ring = poly[0]  # exterior ring only
            lons = [p[0] for p in ring]; lats = [p[1] for p in ring]
            if max(lons) < LON0 - PAD or min(lons) > LON1 + PAD: continue
            if max(lats) < LAT0 - PAD or min(lats) > LAT1 + PAD: continue
            clipped = clip_poly([(p[0], p[1]) for p in ring])
            if len(clipped) < 3: continue
            d.polygon([proj(lo, la, ws, hs) for lo, la in clipped], fill=NAVY)

    # route arcs (gold, bowing over open water)
    for a, b, (dlon, dlat) in ARCS:
        la, lb = LOCS[a], LOCS[b]
        p0 = proj(*la, ws, hs); p2 = proj(*lb, ws, hs)
        ctrl = proj((la[0] + lb[0]) / 2 + dlon, (la[1] + lb[1]) / 2 + dlat, ws, hs)
        d.line(bezier(p0, ctrl, p2), fill=ACCENT, width=5 * SS, joint="curve")

    # location markers (gold dot with light ring)
    for name, (lon, lat) in LOCS.items():
        x, y = proj(lon, lat, ws, hs)
        r = (21 if name in HUBS else 16) * SS
        d.ellipse([x - r - 5 * SS, y - r - 5 * SS, x + r + 5 * SS, y + r + 5 * SS], fill=LIGHT)
        d.ellipse([x - r, y - r, x + r, y + r], fill=ACCENT)

    img = img.resize((W, H), Image.LANCZOS)

    # labels at final resolution for crispness
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", 78)
    anchors = {           # text anchor relative to the marker
        "New York":   ("rm", -34, -42),
        "Palm Beach": ("lm", 38, -2),
        "USVI":       ("lm", 38, 34),
        "London":     ("rm", -38, -34),
        "Paris":      ("rm", -34, 30),
    }
    for name, (lon, lat) in LOCS.items():
        x, y = proj(lon, lat, W, H)
        anc, dx, dy = anchors[name]
        d.text((x + dx, y + dy), name, font=f, fill=NAVY, anchor=anc,
               stroke_width=8, stroke_fill=LIGHT)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print(f"saved {OUT}  ({W}x{H}, aspect {W/H:.3f})")

if __name__ == "__main__":
    main()
