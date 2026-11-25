"""The light: Ballast's one signature, as SVG.

The same ten levels, colours and bezel as the app's own light (Services/LightLevel.swift and
DesignSystem/LightOrb.swift). Deterministic, so rebuilding never changes a file by accident.
Used large and alone at the top of a page, and small in the list of levels. It is decoration:
every figure it stands for is written in text beside it. Never a drawn interface.
"""
import math

# (name, total days free, darkest, middle, brightest, energy). Change only when the app changes.
LEVELS = [
    ('Spark', 0, '#9A4A2E', '#E8703A', '#FFA060', 0.30),
    ('Ember', 1, '#C8502E', '#FF7240', '#FFAA5C', 0.40),
    ('Flame', 3, '#FF5A3C', '#FF8A4C', '#FFC857', 0.50),
    ('Torch', 7, '#FF6A3D', '#FFA94D', '#FFE08A', 0.58),
    ('Lantern', 14, '#FF8F3D', '#FFCB5C', '#FFF0B8', 0.66),
    ('Beacon', 30, '#2CC9AE', '#6EE7CF', '#FFE08A', 0.74),
    ('Star', 60, '#4F7CFF', '#6FD3FF', '#DDF6FF', 0.82),
    ('Sun', 100, '#FF5E7E', '#FF9D4D', '#FFE27A', 0.90),
    ('Nova', 180, '#8B5CFF', '#FF6AD5', '#FFD36E', 0.96),
    ('Polaris', 365, '#7CA8FF', '#B8A6FF', '#F2FBFF', 1.0),
]
NAMES = [level[0].lower() for level in LEVELS]


def mix(a, b, t):
    pa, pb = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (a, b))
    return '#' + ''.join(f'{round(x + (y - x) * t):02X}' for x, y in zip(pa, pb))


def orb(index, r, cx, cy, halo):
    """The sphere: halo, body in the level's three colours, hot core, highlight, rim."""
    _, _, dark, mid, light, energy = LEVELS[index]
    core = mix(light, '#FFFFFF', 0.25 + 0.45 * energy)
    # gradientUnits stay objectBoundingBox, so the same definitions serve any size.
    edge = r / halo
    deep = mix(dark, '#000000', 0.25)
    stops = [(edge * 0.94, 0.95 * (0.35 + 0.65 * energy)), (edge + (1 - edge) * 0.18, 0.5 * energy), (edge + (1 - edge) * 0.45, 0.17 * energy), (1, 0)]
    halo_stops = ''.join(f'<stop offset="{o:.2f}" stop-color="{mid}" stop-opacity="{v:.2f}"/>' for o, v in stops)
    defs = (
        f'<radialGradient id="h">{halo_stops}</radialGradient>'
        f'<radialGradient id="b" cx=".5" cy=".48" r=".56"><stop offset="0" stop-color="{core}"/><stop offset=".42" stop-color="{mid}"/><stop offset="1" stop-color="{mix(dark, mid, .15)}"/></radialGradient>'
        f'<linearGradient id="s" x1=".86" y1=".04" x2=".2" y2="1"><stop offset="0" stop-color="{mix(light, dark, .18)}" stop-opacity=".9"/><stop offset=".34" stop-color="{light}" stop-opacity="0"/><stop offset=".6" stop-color="{dark}" stop-opacity="0"/><stop offset="1" stop-color="{deep}" stop-opacity=".75"/></linearGradient>'
        f'<radialGradient id="c" cx=".42" cy=".4" r=".4"><stop offset="0" stop-color="#fff" stop-opacity="{0.35 + 0.65 * energy:.2f}"/><stop offset=".45" stop-color="#fff" stop-opacity="{0.3 + 0.6 * energy:.2f}"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="r" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".65"/><stop offset="1" stop-color="#fff" stop-opacity=".08"/></linearGradient>'
    )
    body = (f'<circle cx="{cx}" cy="{cy}" r="{halo}" fill="url(#h)"/>'
            + ''.join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{i})"/>' for i in 'bsc')
            + f'<circle cx="{cx}" cy="{cy}" r="{r - 0.75}" fill="none" stroke="url(#r)" stroke-width="1.5"/>')
    return defs, body


def bezel(index, progress, side):
    """Seventy-two ticks filling clockwise from the top, with one bright point at the head."""
    _, _, _, mid, light, _ = LEVELS[index]
    c = side / 2
    lit = math.floor(progress * 72)
    groups = {}
    for i in range(72):
        a = i / 72 * 2 * math.pi - math.pi / 2
        major = i % 6 == 0
        outer, inner = side * 0.485, side * (0.435 if major else 0.452)
        d = f'M{c + math.cos(a) * inner:.1f} {c + math.sin(a) * inner:.1f}L{c + math.cos(a) * outer:.1f} {c + math.sin(a) * outer:.1f}'
        if i < lit:
            key = (mix(mid, light, round(i / 72 * 6) / 6), 1, major)
        else:
            key = ('#fff', 0.2 if major else 0.11, major)
        groups.setdefault(key, []).append(d)
    out = ''.join(f'<path d="{"".join(ds)}" stroke="{colour}" stroke-opacity="{op}" stroke-width="{side * (0.011 if major else 0.008):.1f}" stroke-linecap="round"/>'
                  for (colour, op, major), ds in groups.items())
    if 0 < progress < 1:
        a = progress * 2 * math.pi - math.pi / 2
        x, y, dot = c + math.cos(a) * side * 0.468, c + math.sin(a) * side * 0.468, side * 0.022
        out += (f'<radialGradient id="p"><stop offset=".3" stop-color="{light}" stop-opacity=".7"/><stop offset="1" stop-color="{light}" stop-opacity="0"/></radialGradient>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{side * 0.015 + dot * 1.6:.1f}" fill="url(#p)"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{dot:.1f}" fill="#fff"/>')
    return out


def light(index, progress=None, side=320):
    """One light. With `progress` it sits inside the bezel, without it is the small form for lists."""
    c = side / 2
    if progress is None:
        defs, body = orb(index, side * 0.3, c, c, side * 0.5)
        ticks = ''
    else:
        defs, body = orb(index, side * 0.28, c, c, side * 0.47)
        ticks = bezel(index, progress, side)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side} {side}" width="{side}" height="{side}" fill="none">'
            f'<defs>{defs}</defs>{body}{ticks}</svg>\n')
