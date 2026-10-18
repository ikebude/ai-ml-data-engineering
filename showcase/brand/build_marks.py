"""Builds every CI / PI logo file. Run: python3 brand/build_marks.py && npm run sheet"""
import math, os, subprocess
W = 11  # stroke / bar width on a 100x100 grid
INK, WHITE, EMERALD = "#0B1220", "#FFFFFF", "#10B981"

def letter(l, fg):
    if l == "P":
        return f'<path d="M24 78 V27.5 H43 A13.5 13.5 0 0 1 43 54.5 H24" fill="none" stroke="{fg}" stroke-width="{W}"/>'
    cx, cy, r, a = 41, 50, 22.5, math.radians(42)
    x, y1, y2 = cx + r*math.cos(a), cy - r*math.sin(a), cy + r*math.sin(a)
    return f'<path d="M{x:.2f} {y1:.2f} A{r} {r} 0 1 0 {x:.2f} {y2:.2f}" fill="none" stroke="{fg}" stroke-width="{W}"/>'

def svg(l, fg, acc, tile=None, size=None):
    t = f'<rect width="100" height="100" rx="22" fill="{tile}"/>' if tile else ''
    i = f'<rect x="{74 - W/2}" y="22" width="{W}" height="56" fill="{acc}"/>'   # capital I, full cap height
    wh = f' width="{size}" height="{size}"' if size else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"{wh}>{t}{letter(l, fg)}{i}</svg>'

d = os.path.dirname(os.path.abspath(__file__))
for l in "CP":
    n = l.lower() + "i"
    files = {f"{n}-mark.svg": svg(l, WHITE, EMERALD, INK), f"{n}-mark-light.svg": svg(l, INK, EMERALD, WHITE),
             f"{n}-glyph-light.svg": svg(l, WHITE, EMERALD), f"{n}-glyph-dark.svg": svg(l, INK, EMERALD)}
    for f, s in files.items(): open(os.path.join(d, f), "w").write(s)
# Round WhatsApp profile pictures (content kept inside the centre so the circle crop is safe)
for name, bg, fg, acc in [("green", EMERALD, INK, WHITE), ("white", WHITE, INK, EMERALD)]:
    html = f'<!doctype html><body style="margin:0;width:640px;height:640px;background:{bg};display:grid;place-items:center">{svg("C", fg, acc, size=400)}</body>'
    p = os.path.join(d, f"_profile-{name}.html"); open(p, "w").write(html)
    subprocess.run(["node", os.path.join(d, "..", "snap.js"), "file://" + p, os.path.join(d, f"profile-ci-{name}-640.png"), "640", "640"], check=True); os.remove(p)
for m in ["ci-mark", "pi-mark", "ci-mark-light", "pi-mark-light"]:
    s = open(os.path.join(d, m + ".svg")).read().replace("<svg ", '<svg width="1024" height="1024" ', 1)
    p = os.path.join(d, "_png.html"); open(p, "w").write('<!doctype html><body style="margin:0;width:1024px;height:1024px;background:transparent">' + s + "</body>")
    subprocess.run(["node", os.path.join(d, "..", "snap.js"), "file://" + p, os.path.join(d, m + "-1024.png"), "1024", "1024"], check=True); os.remove(p)
print("marks built")
