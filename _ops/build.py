#!/usr/bin/env python3
"""Build the Ballast site: every root *.html, sitemap, robots and llms files.

    python3 _ops/build.py            # write the site into the repo root
    python3 _ops/build.py --og       # also regenerate Open Graph images (uses headless Chrome)
    python3 _ops/build.py --out DIR  # write elsewhere (the validator uses this to check freshness)

SITE_URL in _ops/discovery.json is the single source for every absolute URL. To move domain,
change that one line and rebuild. Page text lives in _ops/content/*.html; nothing in the repo
root is hand-edited. Standard library only, except --og (Chrome).

Icons, Open Graph images and app screenshots live in _ops/live/assets; the build copies them into
assets/ and removes what is no longer there. The light at the top of each page is drawn by
_ops/daybreak.py; the hero film is cut from real recordings by _ops/hero_film.py (not part of the build).
"""
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
import argparse, base64, hashlib, html, json, re, shutil, subprocess, sys, tempfile

OPS = Path(__file__).resolve().parent
ROOT = OPS.parent
sys.path.insert(0, str(OPS))
import daybreak  # noqa: E402

C = json.loads((OPS / 'discovery.json').read_text())
LIVE_ASSETS = OPS / 'live/assets'
SITE = C['SITE_URL']
assert SITE.startswith('https://') and SITE.endswith('/'), 'SITE_URL must be https and end in /'
APP = C['appId']
E = lambda s: html.escape(s, quote=True)
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
BADGE = 'assets/app-store-badge.svg'
ICON = 'assets/icon-112.png'

# Starters adapted from the app's own Services/TriggerPlans.swift. Written to be edited.
TRIGGERS = [
    ('Late night', "If it's late and I'm in bed with my phone,", ["the phone goes on the kitchen charger and the book on my pillow opens.", "lights out and phone off at the same moment."]),
    ('Stress', 'If I notice stress building,', ["I go out the front door for five minutes with no phone in my pocket.", "I write the one thing stressing me on paper and set a ten-minute timer to start on it."]),
    ('Boredom', "If I'm bored with nothing planned,", ["I put my shoes on and walk one lap of the block, then decide what's next.", "I set a kitchen timer for twenty minutes and start the chore I've been dodging."]),
    ('Loneliness', 'If I feel lonely,', ["I text one person a real question, not just 'hey'.", "I take myself somewhere with people in earshot: kitchen table, café, front step."]),
    ('Tired', "If I'm tired and still up,", ["the phone stays on the hallway charger and I go to bed.", "I brush my teeth now, which tells me the day is over."]),
    ('Anxiety', "If I'm anxious,", ["I put my feet flat on the floor and take four long breaths, each exhale slower.", "I write the worry as one sentence on paper."]),
    ('Social media', 'If scrolling starts to turn into something else,', ["I close the app, log out, and put the phone face-down across the room for ten minutes.", "I swap the screen for a kettle: phone down, tea on, back in five."]),
    ('Drinking', "If I've been drinking,", ["the phone stays in my jacket pocket, not on the table, for the rest of the night.", "the phone sleeps in the kitchen when I get home."]),
    ('Argument', "If I've just had an argument,", ["I walk once around the block before I do anything else.", "I type the angry version in Notes, delete it, then decide what actually needs saying."]),
    ('Home alone', "If I'm home alone and restless,", ["I leave the house for twenty minutes: coffee, corner shop, anywhere with other people.", "my laptop and phone stay in the living room and the bedroom stays screen-free."]),
]

HELP = '''<section class="help">
<h2 id="more-help">When to look for more help</h2>
<p>Ballast is a self-tracking and educational tool, not treatment. None of these is a diagnosis, but any one is a fair reason to book a conversation: you've tried to cut back several times and it keeps coming back; it's eating into sleep, work or time with people; it has become the main way you deal with stress or low mood; or you feel low or anxious most days.</p>
<ul>
<li><strong>A therapist.</strong> Look for someone who works with CBT or ACT and is comfortable talking about sex.</li>
<li><strong>Your GP or family doctor.</strong> A good first stop if you're unsure. They can check what else might be going on and refer you on.</li>
<li><strong><a href="https://smartrecovery.org">SMART Recovery</a>.</strong> Free peer meetings, online and in person, built on practical CBT-style tools.</li>
<li><strong><a href="https://saa-recovery.org">SAA</a>.</strong> A twelve-step fellowship with free meetings in many countries and online.</li>
</ul>
<p><strong>If things feel very dark:</strong> if you are having thoughts of harming yourself, contact your local emergency services or a crisis line now. In the US, call or text 988. Elsewhere, <a href="https://findahelpline.com">findahelpline.com</a> lists free lines by country.</p>
</section>'''


# Custom Product Pages (App Store Connect, created 2026-11-08). Until a page is approved, Apple shows the
# default product page for its ppid, so these links are safe before approval. ct keeps the campaign attribution.
CPP_FILTER = '65a3645b-db29-4a09-84a7-61881d998113'
CPP_URGE = 'b72291d5-44bd-4a11-895c-3f4d6c91a870'
CPP_PRIVATE = 'ce9482be-63a2-4d56-bc4c-09aa4fda5504'
PPID_FOR_TAG = {
    'ballast-guide-block-porn': CPP_FILTER,
    'ballast-compare-apps': CPP_FILTER,
    'ballast-tool-urge-plan': CPP_URGE,
    'ballast-guide-how-to-stop': CPP_URGE,
    'ballast-guide-after-slip': CPP_URGE,
    'ballast-guide-quittr': CPP_PRIVATE,
}


def store_url(tag):
    url = f'https://apps.apple.com/app/apple-store/id{APP}?pt={C["providerToken"]}&ct={tag}&mt=8'
    ppid = PPID_FOR_TAG.get(tag)
    return f'{url}&ppid={ppid}' if ppid else url


def store_link(tag, cls='store'):
    return (f'<a class="{cls}" href="{E(store_url(tag))}" aria-label="Download Ballast on the App Store">'
            f'<img class="icon" src="{ICON}" alt="" width="56" height="56">'
            f'<img class="badge" src="{BADGE}" alt="Download on the App Store" width="150" height="50"></a>')


def page_source(name):
    return (OPS / 'content' / name).read_text()


def load_pages():
    pages = []
    for path in sorted((OPS / 'content').glob('*.html')):
        s = page_source(path.name)
        m = re.match(r'<!--meta\s*(\{.*?\})\s*-->\s*', s, re.S)
        assert m, f'{path.name}: missing meta block'
        meta = json.loads(m[1])
        meta['file'] = path.name
        meta['body'] = s[m.end():]
        pages.append(meta)
    return sorted(pages, key=lambda p: p.get('order', 50))


def page_url(name):
    return SITE + ('' if name == 'index.html' else name)


def plain(fragment):
    fragment = re.sub(r'<!--.*?-->', '', fragment, flags=re.S)
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', '', fragment)).split())


def faq_pairs(body):
    m = re.search(r'<!--faq:start-->(.*?)<!--faq:end-->', body, re.S)
    if not m:
        return []
    return [(plain(q), plain(a)) for q, a in re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p>(.*?)</p>', m[1], re.S)]


def slot(name, level, alt, caption=''):
    """A real capture, or the light itself while a capture is missing. Never a drawn interface."""
    for ext in ('.jpg', '.png'):
        f = LIVE_ASSETS / 'screens' / (name + ext)
        if f.exists():
            w, h = image_size(f)
            cap = f'<figcaption>{caption}</figcaption>' if caption else ''
            return f'<figure class="shot"><img src="assets/screens/{name}{ext}" width="{w}" height="{h}" alt="{E(alt)}" loading="lazy" decoding="async">{cap}</figure>'
    return f'<!-- slot:{name} --><div class="panel">{light(level, 200)}</div>'


def light(level, size):
    assert level in daybreak.NAMES, f'no level called {level}'
    lazy = ' loading="lazy"' if size < 168 else ''  # Only the one at the top of a page is in the first view.
    return f'<img class="mast-light" src="assets/light-{level}.svg" alt="" width="{size}" height="{size}"{lazy}>'


def levels_list():
    """The ten levels, from the same data the art is drawn from."""
    def need(days):
        return f'{days} day{"" if days == 1 else "s"} free'
    return '<ol class="levels">' + ''.join(
        f'<li><img src="assets/level-{name.lower()}.svg" alt="" width="84" height="84" loading="lazy" decoding="async"><span><strong>{name}</strong>{need(days)}</span></li>'
        for name, days, *_ in daybreak.LEVELS) + '</ol>'


def image_size(path):
    from struct import unpack
    b = path.read_bytes()
    if b[:8] == b'\x89PNG\r\n\x1a\n':
        return unpack('>II', b[16:24])
    i = 2
    while i < len(b):
        marker, size = b[i + 1], unpack('>H', b[i + 2:i + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = unpack('>HH', b[i + 5:i + 9])
            return w, h
        i += size + 2
    raise ValueError(path)


def plan_table():
    rows = []
    for name, if_text, thens in TRIGGERS:
        then = ''.join(f'<li>{E(t)}</li>' for t in thens)
        rows.append(f'<tr data-trigger="{E(name)}" data-if="{E(if_text)}"><th scope="row">{E(name)}</th><td>{E(if_text)}</td><td data-label="Then, for example"><ul class="plain">{then}</ul></td></tr>')
    return ('<div class="table-wrap"><table class="stack" id="starters"><caption>Ten common triggers and starter plans. Edit them until they sound like you.</caption>'
            '<thead><tr><th scope="col">Trigger</th><th scope="col">If</th><th scope="col">Then, for example</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')


def expand(body, page):
    tag = page['campaign']
    body = body.replace('{{help}}', HELP)
    body = body.replace('{{plan_table}}', plan_table())
    body = body.replace('{{chips}}', ''.join(f'<label class="chip"><input type="radio" name="trigger" value="{i}"><span>{E(t[0])}</span></label>' for i, t in enumerate(TRIGGERS)))
    body = body.replace('{{facts}}', f'<aside class="facts"><h2 id="app-facts">App facts</h2><p>{E(C["facts"])}</p><p class="small">Made by <a href="about.html">{E(C["author"])}</a>. Facts checked {E(C["factsChecked"])}.</p></aside>')
    body = re.sub(r'\{\{store\}\}', lambda _: store_link(tag), body)
    body = re.sub(r'\{\{cta\|(.*?)\|(.*?)\}\}', lambda m: f'<aside class="cta"><h2 class="cta-title">{m[1]}</h2><p>{m[2]}</p>{store_link(tag)}</aside>', body, flags=re.S)
    body = body.replace('{{levels}}', levels_list())
    body = re.sub(r'\{\{slot\|([^|{}]*)\|([^|{}]*)\|([^|{}]*)(?:\|([^|{}]*))?\}\}', lambda m: slot(m[1], m[2], m[3], m[4] or ''), body)
    body = re.sub(r'\{\{light\|(\w+)\|(\d+)\}\}', lambda m: light(m[1], int(m[2])), body)
    return body.strip()


def toc(body):
    items = re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', body, re.S)
    li = ''.join(f'<li><a href="#{i}">' + re.sub(r'^\d+\.\s*', '', t) + '</a></li>' for i, t in items)
    return f'<nav class="toc" aria-label="On this page"><strong>On this page</strong><ol>{li}</ol></nav>'


def schema(page, pages, body):
    url = page_url(page['file'])
    og = SITE + f'assets/og/{Path(page["file"]).stem}.png'
    author = {'@type': 'Person', '@id': SITE + 'about.html#author', 'name': C['author'], 'url': SITE + 'about.html', 'sameAs': [C['authorUrl']]}
    app_ref = {'@id': SITE + '#app'}
    out = []
    kind = page['kind']
    if kind == 'home':
        out.append({'@context': 'https://schema.org', '@type': 'WebSite', '@id': SITE + '#site', 'name': 'Ballast', 'url': SITE, 'inLanguage': 'en', 'description': page['description']})
        out.append({'@context': 'https://schema.org', '@type': 'MobileApplication', '@id': SITE + '#app', 'name': C['storeName'], 'url': SITE,
                    'downloadUrl': f'https://apps.apple.com/app/id{APP}', 'installUrl': f'https://apps.apple.com/app/id{APP}',
                    'operatingSystem': 'iOS ' + C['minimumOS'] + ' or later', 'applicationCategory': C['category'], 'softwareVersion': C['version'],
                    'image': SITE + 'assets/discovery-icon.png', 'description': C['facts'], 'author': author, 'publisher': author})
    elif kind in ('article', 'tool'):
        out.append({'@context': 'https://schema.org', '@type': 'Article', 'headline': page['h1'], 'description': page['description'], 'url': url, 'mainEntityOfPage': url,
                    'datePublished': page['published'], 'dateModified': page['updated'], 'inLanguage': 'en', 'image': og, 'author': author, 'publisher': author, 'about': app_ref if page.get('about_app') else {'@type': 'Thing', 'name': page['topic']}})
        if kind == 'tool':
            out.append({'@context': 'https://schema.org', '@type': 'WebApplication', 'name': page['h1'], 'url': url, 'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any web browser',
                        'browserRequirements': 'Requires JavaScript for the builder. The reference table and blank sheet work without it.', 'isAccessibleForFree': True, 'description': page['description'], 'author': author})
    elif kind == 'about':
        out.append({'@context': 'https://schema.org', '@type': 'AboutPage', 'name': page['title'], 'url': url, 'description': page['description'], 'dateModified': page['updated'], 'mainEntity': {**author, '@context': None, 'jobTitle': 'Independent iOS developer', 'email': 'mailto:' + C['contact']}})
        out[-1]['mainEntity'].pop('@context')
    elif kind == 'legal':
        out.append({'@context': 'https://schema.org', '@type': 'WebPage', 'name': page['title'], 'url': url, 'description': page['description'], 'dateModified': page['updated'], 'author': author})
    if kind not in ('home', '404'):
        out.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Ballast', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': page['crumb'], 'item': url}]})
    faqs = faq_pairs(page['body'])
    if faqs:
        out.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]})
    return json.dumps(out, ensure_ascii=False).replace('</', '<\\/')


def head(page, pages, css_v, body, prefix):
    url = page_url(page['file'])
    og = SITE + f'assets/og/{Path(page["file"]).stem}.png'
    is404 = page['kind'] == '404'
    out = ['<!doctype html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           '''<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'">''',
           f'<title>{E(page["title"])}</title>', f'<meta name="description" content="{E(page["description"])}">']
    if is404:
        out.append('<meta name="robots" content="noindex">')
    else:
        out.append(f'<link rel="canonical" href="{url}">')
    out += [f'<meta name="apple-itunes-app" content="app-id={APP}">', '<meta name="color-scheme" content="dark">', '<meta name="theme-color" content="#08080D">',
            f'<meta property="og:type" content="{"article" if page["kind"] in ("article", "tool") else "website"}">', '<meta property="og:site_name" content="Ballast">',
            f'<meta property="og:title" content="{E(page["title"])}">', f'<meta property="og:description" content="{E(page["description"])}">',
            f'<meta property="og:url" content="{url}">', f'<meta property="og:image" content="{og}">', '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
            f'<meta property="og:image:alt" content="{E(page.get("og_alt", "The words: " + plain(page["h1"]) + " Beside them, a screen from the Ballast app on an iPhone."))}">',
            '<meta name="twitter:card" content="summary_large_image">', f'<meta name="twitter:title" content="{E(page["title"])}">', f'<meta name="twitter:description" content="{E(page["description"])}">', f'<meta name="twitter:image" content="{og}">',
            f'<link rel="icon" type="image/png" sizes="64x64" href="{prefix}assets/icon-64.png">', f'<link rel="apple-touch-icon" href="{prefix}assets/icon-180.png">',
            f'<link rel="stylesheet" href="{prefix}assets/site.css?v={css_v}">']
    if not is404:
        out.append('<script type="application/ld+json">' + schema(page, pages, body) + '</script>')
    out.append('</head>')
    return '\n'.join(out)


def site_header(page):
    tag = page['campaign']
    nav = [('if-then-urge-plan.html', 'Plan tool'), ('index.html#guides', 'Guides'), ('best-apps-to-quit-porn-compared.html', 'Compare'), ('about.html', 'About')]
    links = ''.join(f'<a href="{h}"' + (' aria-current="page"' if h == page['file'] else '') + f'>{t}</a>' for h, t in nav)
    return (f'<header class="site-head"><div class="wrap head-row"><a class="brand" href="index.html"><img src="assets/icon-64.png" alt="" width="34" height="34"><span>Ballast</span></a>'
            f'<nav class="site-nav" aria-label="Main">{links}</nav>'
            f'<a class="head-badge" href="{E(store_url(tag))}" aria-label="Download Ballast on the App Store"><img src="{BADGE}" alt="Download on the App Store" width="120" height="40"></a></div></header>')


def site_footer(page, pages):
    guides = ''.join(f'<li><a href="{p["file"]}">{E(p["linkText"])}</a></li>' for p in pages if p.get('linkText'))
    return (f'<footer class="site-foot"><div class="wrap foot-grid"><div><p class="foot-title">Guides and tools</p><ul class="plain">{guides}</ul></div>'
            f'<div><p class="foot-title">Ballast</p><ul class="plain"><li><a href="index.html">Home</a></li><li><a href="about.html">About and method</a></li><li><a href="support.html">Support</a></li><li><a href="privacy.html">Privacy</a></li><li><a href="support.html#more-help">Getting more help</a></li></ul></div>'
            f'<div class="foot-note"><p>{E(C["facts"])}</p><p>Made by <a href="about.html">{E(C["author"])}</a>. This site sets no cookies and runs no analytics. <a href="mailto:{C["contact"]}">Send a correction</a>.</p>'
            f'<p class="small">Apple, the Apple logo, iPhone and App Store are trademarks of Apple Inc., registered in the U.S. and other countries.</p></div></div></footer>')


def human_date(iso):
    d = date.fromisoformat(iso)
    return f'{d.day} {d.strftime("%B %Y")}'


def render(page, pages, css_v):
    body = expand(page['body'], page)
    prefix = urlsplit(SITE).path if page['kind'] == '404' else ''
    tint = page.get('tint', 'ember')
    glow = '<div class="glow' + ('' if tint == 'ember' else f' glow-{tint}') + '"></div>'
    parts = [head(page, pages, css_v, body, prefix), '<body>', '<a class="skip" href="#main">Skip to content</a>', glow, site_header(page)]
    if page['kind'] == 'home':
        parts.append(f'<main id="main">{body}</main>')
    else:
        crumbs = f'<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Ballast</a> <span aria-hidden="true">/</span> <span>{E(page["crumb"])}</span></nav>' if page['kind'] != '404' else ''
        byline = ''
        if page['kind'] in ('article', 'tool'):
            byline = f'<p class="byline">By <a href="about.html">{E(C["author"])}</a>, developer of Ballast · Updated {human_date(page["updated"])}</p>'
        elif page['kind'] in ('legal', 'about'):
            byline = f'<p class="byline">Updated {human_date(page["updated"])}</p>'
        intro = []
        if page.get('disclosure'):
            intro.append(f'<p class="disclosure"><strong>Conflict of interest:</strong> {page["disclosure"]}</p>')
        if page.get('answer'):
            intro.append(f'<p class="answer">{page["answer"]}</p>')
        if page.get('toc'):
            intro.append(toc(body))
        parts.append(f'<main id="main"><div class="wrap mast">{light(page.get("light", "ember"), 168)}<div>{crumbs}<h1>{page["h1"]}</h1>{byline}</div></div>'
                     '<div class="wrap prose">' + ''.join(intro) + body + '</div></main>')
    parts.append(site_footer(page, pages))
    if page.get('script'):
        parts.append(f'<script src="assets/{page["script"]}" defer></script>')
    parts += ['</body>', '</html>', '']
    html_out = '\n'.join(parts)
    if page['kind'] == '404':
        base = urlsplit(SITE).path
        html_out = re.sub(r'(href|src)="(?!https?:|mailto:|/|#)([^"]+)"', lambda m: f'{m[1]}="{base}{m[2]}"', html_out)
    return html_out


ROBOT_AGENTS = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot', 'Applebot-Extended', 'Bingbot', 'Googlebot']


def write_support_files(pages, out):
    listed = [p for p in pages if p['kind'] != '404']
    urls = ''.join(f'  <url>\n    <loc>{page_url(p["file"])}</loc>\n    <lastmod>{p["updated"]}</lastmod>\n  </url>\n' for p in listed)
    (out / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    robots = '# A project subpath does not control the host-root robots.txt. This file becomes\n# authoritative once SITE_URL is the root of Ballast\'s own domain. See _ops/DOMAIN_MOVE.md.\nUser-agent: *\nAllow: /\n\n'
    robots += ''.join(f'User-agent: {a}\nAllow: /\n\n' for a in ROBOT_AGENTS) + f'Sitemap: {SITE}sitemap.xml\n'
    (out / 'robots.txt').write_text(robots)
    store = f'https://apps.apple.com/app/id{APP}'
    lines = lambda items, summary: '\n'.join(f'- [{p.get("linkText") or p["title"]}]({page_url(p["file"])})' + (f': {p["summary"]} Updated {p["updated"]}.' if summary and p.get('summary') else '') for p in items)
    guides = [p for p in listed if p.get('linkText')]
    core = [p for p in listed if not p.get('linkText')]
    head_txt = f'# {C["storeName"]}\n\n> {C["promise"]} Official website by {C["author"]}.\n\n{C["facts"]}\n\nApp Store listing: {store}\nFacts checked: {C["factsChecked"]}\n'
    tail = '\nThis file is a plain reference for readers and assistants. It does not establish search ranking or AI recommendations.\n'
    (out / 'llms.txt').write_text(head_txt + '\n## Pages\n\n' + lines(core, False) + '\n\n## Guides and tools\n\n' + lines(guides, False) + '\n' + tail)
    full = (OPS / 'llms-product.md').read_text().strip()
    (out / 'llms-full.txt').write_text(head_txt + '\n' + full + '\n\n## Pages\n\n' + lines(core, True) + '\n\n## Guides and tools\n\n' + lines(guides, True) + '\n' + tail)


def write_art(pages, out):
    art = out / 'assets'
    art.mkdir(exist_ok=True)
    for i, name in enumerate(daybreak.NAMES):
        (art / f'level-{name}.svg').write_text(daybreak.light(i, side=96))
    used = {p.get('light', 'ember') for p in pages if p['kind'] != 'home'} | set(re.findall(r'\{\{light\|(\w+)\|', ''.join(p['body'] for p in pages)))
    for name in used:
        i = daybreak.NAMES.index(name)
        (art / f'light-{name}.svg').write_text(daybreak.light(i, progress=(i + 1) / len(daybreak.NAMES) if i + 1 < len(daybreak.NAMES) else 0.96))
    for f in art.glob('light-*.svg'):
        if f.stem.removeprefix('light-') not in used:
            f.unlink()


def install_assets(out):
    """Put the icons, Open Graph images and screenshots in assets/, and drop any no longer supplied."""
    for name in ('screens', 'og'):
        folder = out / 'assets' / name
        if folder.is_dir():
            shutil.rmtree(folder)
    for f in LIVE_ASSETS.rglob('*'):
        if f.is_file() and f.name != '.DS_Store':
            target = out / 'assets' / f.relative_to(LIVE_ASSETS)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, target)


OG_CSS = """html,body{margin:0;background:#08080D}*{box-sizing:border-box}
.w{position:relative;width:1200px;height:630px;overflow:hidden;background:radial-gradient(620px 420px at 4% 0,rgba(255,138,76,.3),transparent 70%),radial-gradient(560px 560px at 82% 60%,rgba(44,201,174,.26),transparent 70%),#08080D}
.t{position:absolute;left:68px;top:40px;height:440px;width:716px;display:flex;align-items:center;color:#F6F7FB;font:800 72px/1.12 ui-rounded,"SF Pro Rounded",system-ui,sans-serif;letter-spacing:-.022em}
.t p{margin:0;text-wrap:balance}.t.short{font-size:96px;line-height:1.06}.t.long{font-size:60px}
.hl{display:inline-block;color:#08080D;background:linear-gradient(100deg,#FF6A48,#FF8A4C 45%,#FFCB5C);padding:.02em .22em .1em;margin-left:-.06em;border-radius:.22em;transform:rotate(-2deg);box-shadow:0 14px 60px rgba(255,120,70,.45)}
.b{position:absolute;left:68px;bottom:54px;color:#F6F7FB;font:700 30px ui-rounded,"SF Pro Rounded",system-ui,sans-serif;display:flex;align-items:center;gap:16px}
.b img{width:64px;height:64px;border-radius:15px}.b span{color:#B4B8CB;font-weight:600}
.p{position:absolute;right:74px;top:58px;width:318px;border-radius:46px;box-shadow:0 0 0 1px #2A2D3B,0 0 0 9px #050508,0 0 0 11px #33364A,0 40px 90px rgba(0,0,0,.6)}"""


def make_og(pages):
    """1200x630 images: the page's title and a real capture of the app."""
    target = LIVE_ASSETS / 'og'
    target.mkdir(parents=True, exist_ok=True)
    data = lambda f, kind: f'data:image/{kind};base64,' + base64.b64encode(f.read_bytes()).decode()
    icon = data(LIVE_ASSETS / 'icon-112.png', 'png')
    with tempfile.TemporaryDirectory() as tmp:
        for p in pages:
            stem = Path(p['file']).stem
            title = E(p.get('og_title', plain(p['h1'])))
            mark = E(p.get('og_hl', ''))
            assert not mark or mark in title, f'{stem}: og_hl is not in the title'
            if mark:
                title = title.replace(mark, f'<span class="hl">{mark}</span>')
            shot = LIVE_ASSETS / 'screens' / (p['og_shot'] + '.jpg') if p.get('og_shot') else ROOT / 'assets/ballast-panic-hero-poster.jpg'
            words = len(plain(title))
            size = ' short' if words <= 28 else ' long' if words > 44 else ''
            doc = (f'<!doctype html><meta charset="utf-8"><style>{OG_CSS}</style><div class="w"><img class="p" src="{data(shot, "jpeg")}" alt="">'
                   f'<div class="t{size}"><p>{title}</p></div><div class="b"><img src="{icon}" alt="">Ballast <span>{urlsplit(SITE).netloc}</span></div></div>')
            f = Path(tmp) / f'{stem}.html'
            f.write_text(doc)
            png = target / f'{stem}.png'
            # Chrome can write the file and still exit non-zero in teardown, so the file is the test.
            png.unlink(missing_ok=True)
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--user-data-dir={tmp}/profile', '--window-size=1200,630', '--force-device-scale-factor=1', f'--screenshot={png}', f.as_uri()], capture_output=True, timeout=120)
            assert png.exists(), f'Chrome wrote no image for {stem}'
            try:
                from PIL import Image
                im = Image.open(png).convert('RGB')
                if im.size != (1200, 630):
                    im = im.crop((0, 0, 1200, 630))
                im.save(png, optimize=True)  # True colour: a palette posterises the light.
            except ImportError:
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(ROOT))
    ap.add_argument('--og', action='store_true')
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pages = load_pages()
    css_v = hashlib.sha256((ROOT / 'assets/site.css').read_bytes()).hexdigest()[:8]
    for p in pages:
        (out / p['file']).write_text(render(p, pages, css_v))
    write_support_files(pages, out)
    write_art(pages, out)
    if a.og:
        make_og(pages)
    install_assets(out)
    print(f'Built {len(pages)} pages for {SITE} into {out}')


if __name__ == '__main__':
    main()
