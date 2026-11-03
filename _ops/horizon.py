"""The Horizon artwork: layered flat swells under a banded sky, in pure SVG.

Deterministic (no randomness), so rebuilding never changes a file by accident. Used for the
home hero (inline, so CSS can move the layers), the article band, the screenshot fallback
panels and the Open Graph images.
"""
import math

THEMES = {
    'dawn': {
        'sky': ['#120E17', '#1A1320', '#241829', '#342033', '#4F2A3D', '#7A3A45', '#B4574D', '#E57F59', '#FF9D6C'],
        'swell': ['#6B3A4C', '#46293F', '#2E2033', '#1E1824', '#120E17'],
        'rim': '#FFD08A', 'sun': '#FFD08A',
    },
    'night': {
        'sky': ['#120E17', '#151119', '#19141E', '#1E1824', '#241D2B', '#2A2232', '#30283A', '#352C3D', '#3E3448'],
        'swell': ['#4A4056', '#352C3D', '#2A2232', '#1E1824', '#120E17'],
        'rim': '#BFD9D3', 'sun': None,
    },
    'day': {
        'sky': ['#3E3448', '#6F5A6E', '#A77F7C', '#D6A184', '#F0BC8A', '#FFD08A', '#FFDDA6', '#FFE8C4', '#F6EFE9'],
        'swell': ['#A79BB3', '#6F6180', '#463A52', '#2A2232', '#120E17'],
        'rim': '#F6EFE9', 'sun': '#FFF3DC',
    },
}


def ridge(width, base, amp, wavelength, phase, step=64):
    """A closed swell silhouette: long rounded rollers, one slower swell on top."""
    pad = 96
    points = []
    x = -pad
    while x <= width + pad:
        t = 2 * math.pi * (x / wavelength) + phase
        roller = (1 - abs(math.sin(t / 2))) ** 1.35
        drift = math.sin(t * 0.37 + phase * 1.7)
        points.append((x, base - amp * roller - amp * 0.28 * drift))
        x += step
    d = f'M{points[0][0]} {points[0][1]:.0f}'
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f'C{c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} {p2[0]} {p2[1]:.0f}'
    return d


def scene(width=1600, height=560, theme='dawn', horizon=0.42, sun_x=0.70, sun_rise=0.0, inner_only=False, classes=False, standalone=True, layered=False):
    t = THEMES[theme]
    hy = height * horizon
    band = hy / len(t['sky'])
    parts = []
    # Woodblock sky: flat bands, no smooth gradient.
    for i, colour in enumerate(t['sky']):
        parts.append(f'<rect x="0" y="{i * band:.1f}" width="{width}" height="{band + 1:.1f}" fill="{colour}"/>')
    # Sea behind the swells, then the low sun and its reflection.
    parts.append(f'<rect x="0" y="{hy:.1f}" width="{width}" height="{height - hy:.1f}" fill="{t["swell"][0]}"/>')
    if t['sun'] and sun_x is not None:
        r = height * 0.075
        cx = width * sun_x
        cy = hy - r * 0.32 - sun_rise * height
        parts.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{t["sun"]}"/>')
        parts.append(f'<rect x="0" y="{hy:.1f}" width="{width}" height="{height - hy:.1f}" fill="{t["swell"][0]}"/>')
        for i, w in enumerate([1.5, 1.05, 0.7, 0.42]):
            bw = r * 2 * w
            parts.append(f'<rect x="{cx - bw / 2:.0f}" y="{hy + 9 + i * 13:.0f}" width="{bw:.0f}" height="3" fill="{t["rim"]}" opacity="{0.7 - i * 0.12:.2f}"/>')
    # Swells, far to near. The far crest catches a thin rim of light.
    layers = [
        (0.56, 0.050, 560, 0.4), (0.70, 0.105, 860, 1.9), (0.84, 0.135, 1120, 3.1), (0.98, 0.150, 1400, 4.4),
    ]
    for i, (b, a, wl, ph) in enumerate(layers):
        scale = width / 1600
        d = ridge(width, height * b, height * a, wl * scale, ph)
        closed = d + f'L{width + 96} {height + 4}L-96 {height + 4}Z'
        rim = f'<path d="{d}" fill="none" stroke="{t["rim"]}" stroke-width="1.5" opacity="0.55"/>' if i == 0 else ''
        cls = f' class="swell swell-{i}"' if classes else ''
        parts.append(f'<g{cls}><path d="{closed}" fill="{t["swell"][i + 1]}"/>{rim}</g>')
    if layered:
        # The home hero: a static sky and sea, then each swell in its own element, so moving it is
        # compositor-only and costs no repaint. Layers are wider than the frame to hide their edges.
        wrap = lambda inner, cls: f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" preserveAspectRatio="xMidYMax slice" class="{cls}" aria-hidden="true" focusable="false">{inner}</svg>'
        n = len(layers)
        return wrap(''.join(parts[:-n]), 'horizon') + ''.join(wrap(x, f'swell swell-{i}') for i, x in enumerate(parts[-n:]))
    inner = ''.join(parts)
    if inner_only:
        return inner
    head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" preserveAspectRatio="xMidYMax slice"'
    if standalone:
        return head + '>' + inner + '</svg>\n'
    return head + ' class="horizon" aria-hidden="true" focusable="false">' + inner + '</svg>'
