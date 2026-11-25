#!/usr/bin/env python3
"""Validate the Ballast site. Must print OK before anything is published.

Metadata, links, install paths, JSON-LD, FAQ text, sitemap and llms coverage, plus the product's
rules: no prices, no ratings, no banned claims, no third-party requests, one SITE_URL, and nothing
left of the 1.x app (its tabs, words, versions or artwork). Stdlib only, no network. See
_ops/linkcheck.py for live and external link checks.

    python3 _ops/validate.py
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs, unquote
import filecmp, html, json, re, struct, subprocess, sys, tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OPS = ROOT / '_ops'


sys.path.insert(0, str(OPS))
import build  # noqa: E402
import daybreak  # noqa: E402

C = build.C
SITE = C['SITE_URL']
APP = str(C['appId'])
errors = []
norm = lambda x: ' '.join(x.split())

# Word-boundary, case-insensitive. Mentions are only allowed inside <!--quoted:start/end--> in
# the source, where a page is quoting or explaining a claim it does not make.
BANNED = [r'dopamine', r'rewir\w*', r'neural', r'neuro\w*', r'detox\w*', r'prefrontal', r'receptors?', r'brain chemistry',
          r'proven', r'science-based', r'scientifically', r'clinically', r'guarantee\w*', r'#1', r'number one', r'clean streak',
          r'90[- ]days?', r'relapse\w*', r'fail\w*', r'shame\w*', r'be strong', r'cure[sd]?', r'miracle', r'porn star\w*', r'nofap']
BANNED_RE = re.compile(r'(?<![\w-])(?:' + '|'.join(BANNED) + r')(?![\w])', re.I)
PRICE_RE = re.compile(r'(?:[$€£¥]\s?\d|\b\d+(?:\.\d\d)?\s?(?:USD|EUR|GBP|AED)\b|\b\d+\.99\b)')
RATING_RE = re.compile(r'★|☆|\b\d(?:\.\d)?\s?(?:stars?|out of 5)\b|\baggregateRating\b|\bratingValue\b', re.I)
HELP_LINKS = ['https://smartrecovery.org', 'https://saa-recovery.org', 'https://findahelpline.com']
REQUIRED_URLS = ['privacy.html', 'support.html', 'block-porn-iphone-screen-time.html', 'index.html']
MUST_STATE = {
    'quittr-left-the-app-store.html': ['The cause is unknown', 'Conflict of interest', 'I have no evidence connecting'],
    'best-apps-to-quit-porn-compared.html': ['Conflict of interest', 'Where other apps are better than Ballast', 'Community'],
    'about.html': ['Mohamed Elatabany', 'Ballast is not treatment', 'I am not a clinician'],
    'privacy.html': ['Family Controls', 'stays on your phone', 'No browsing data reaches Ballast', 'No app data reaches Ballast', 'The Blocker and Apple'],
    'block-porn-iphone-screen-time.html': ['Limit Adult Websites', 'disables Safari private browsing', "a phone's owner can undo it in Settings", 'Blocker tab', 'There\'s no VPN', 'Cut the easy access'],
    'how-to-stop-watching-porn.html': ['risk of bias', 'Not tested on pornography'],
    'what-to-do-after-a-slip.html': ['A slip is data', 'Total days free never reset', 'a slip never takes away'],
    'support.html': ['Restore purchase', 'Back up to a file', 'Export my data', 'a 24-hour wait always works', 'Turn off the filter', 'not treatment'],
    'index.html': ['Your plan for the next urge', 'Private. Secular. No brain myths.', 'Panic', 'Progress', 'Toolkit', 'Blocker', 'uses skills from CBT and ACT',
                   'Your streak restarts. Your level doesn\'t.', 'A slip is data, not a verdict', 'friction, not a wall', 'a 24-hour wait always works',
                   "never asked to buy during an urge or after a slip", 'No account', 'no server'],
}
# The free/Pro line, as the app draws it (Services/FreeTier.swift). Home and llms-full.txt must both carry it.
FREE_FACTS = ['3 sites of your own', 'up to 25', 'One if-then plan', 'one habit', 'week one', 'weeks 2 to 4', 'a week of journal', 'backup and restore', 'the heads-up', 'Unlimited if-then plans', 'weekly review', 'commitment lock', 'blocked apps', 'insights']
# The 1.x app: its tabs, words, versions and look. Allowed only inside <!--earlier:start-->...<!--earlier:end-->,
# on the privacy page (which covers every version), and where a page quotes someone else.
OLD = [r'voyages?', r'shield\w*', r'clear[- ]days?', r'waypoints?', r'sail(?:ed|ing|s)?', r'horizon\w*', r'swells?', r"today's watch", r'today tab', r'plan tab', r'urge tab', r'current run',
       r'on your route', r'friction checklist', r'(?:ballast|version) 1\.[0-3](?:\.\d+)?', r'1\.[0-3]\.\d+', r'app shields?']
OLD_RE = re.compile(r'(?<![\w-])(?:' + '|'.join(OLD) + r')(?![\w])', re.I)
EARLIER_RE = re.compile(r'<!--earlier:start-->.*?<!--earlier:end-->', re.S)
RATING_STATE_RE = re.compile(r'\b(?:no|one|its first|only) (?:App Store |US )?ratings? (?:yet|so far)\b|\b(?:has|have) no (?:App Store )?ratings\b|\bNo ratings\b|\bfive[- ]star\b', re.I)
HOME_BUDGET = 2_000_000
FILM_BUDGET = 1_500_000


def json_strings(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        value = list(value.values())
    return [s for v in value for s in json_strings(v)] if isinstance(value, list) else []


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text, self.h3, self.schema, self.links, self.images, self.scripts, self.styles, self.heads = [], [], [], [], [], [], [], []
        self.in_h3 = self.in_body = self.in_title = self.in_json = False
        self.title = self.buffer = ''
        self.ids, self.meta, self.canonical, self.h1, self.lang = set(), {}, [], 0, None
        self.frames = 0
        self.videos = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:
                errors.append('Duplicate ID: ' + a['id'])
            self.ids.add(a['id'])
        if tag == 'html':
            self.lang = a.get('lang')
        if tag == 'title':
            self.in_title = True
        if tag == 'body':
            self.in_body = True
        if tag == 'h3':
            self.in_h3 = True
            self.h3.append('')
        if tag == 'h1':
            self.h1 += 1
        if tag == 'video':
            self.videos.append(a)
        if tag in ('iframe', 'embed', 'object', 'audio'):
            self.frames += 1
        if tag == 'meta':
            key = a.get('name', a.get('property', a.get('http-equiv', '')))
            self.meta.setdefault(key, []).append(a.get('content', ''))
        if tag == 'link':
            if a.get('rel') == 'canonical':
                self.canonical.append(a.get('href', ''))
            if a.get('rel') == 'stylesheet':
                self.styles.append(a.get('href', ''))
        if tag == 'script':
            if a.get('type') == 'application/ld+json':
                self.in_json = True
                self.buffer = ''
            else:
                self.scripts.append(a.get('src', 'INLINE'))
        if tag == 'img':
            self.images.append(a)
        for key in ['href', 'src', 'poster', 'data-src']:
            if a.get(key):
                self.links.append(a[key])

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'h3':
            self.in_h3 = False
        if tag == 'script' and self.in_json:
            try:
                data = json.loads(self.buffer)
                self.schema.extend(data if isinstance(data, list) else [data])
            except ValueError:
                errors.append('Invalid JSON-LD')
            self.in_json = False

    def handle_data(self, value):
        if self.in_title:
            self.title += value
        if self.in_json:
            self.buffer += value
        elif self.in_body:
            self.text.append(value)
        if self.in_h3:
            self.h3[-1] += value


def png_size(path):
    b = path.read_bytes()[:24]
    return struct.unpack('>II', b[16:24]) if b[:8] == b'\x89PNG\r\n\x1a\n' else (0, 0)


def url_for(name):
    return SITE + ('' if name == 'index.html' else name)


def source_scan_text(name):
    """Source text with quoted sections and tags removed, for the vocabulary rules."""
    src = build.page_source(name)
    def meta_text(m):
        d = json.loads(m[0][8:-3])
        return ' '.join(d.get(k, '') for k in ('title', 'h1', 'description', 'answer', 'summary', 'disclosure'))
    src = re.sub(r'<!--meta.*?-->', meta_text, src, count=1, flags=re.S)
    src = re.sub(r'<!--quoted:start-->.*?<!--quoted:end-->', ' ', src, flags=re.S)
    src = re.sub(r'<a\b[^>]*>', ' ', src)
    return re.sub(r'<[^>]+>', ' ', src)


pages = {}
for path in ROOT.glob('*.html'):
    p = Page()
    p.feed(path.read_text())
    pages[path.name] = p
    if str(path.name) not in [f.name for f in (OPS / 'content').glob('*.html')]:
        errors.append(path.name + ': no source in _ops/content (hand-edited page?)')

metas = {}
for f in (OPS / 'content').glob('*.html'):
    metas[f.name] = json.loads(re.match(r'<!--meta\s*(\{.*?\})\s*-->', build.page_source(f.name), re.S)[1])
indexable = [n for n in pages if metas.get(n, {}).get('kind') != '404']

# 1. Single SITE_URL: nothing may hard-code a host, and the built output must be fresh.
if not (SITE.startswith('https://') and SITE.endswith('/')):
    errors.append('SITE_URL must be https and end in /')
host = urlsplit(SITE).netloc
for f in list((OPS / 'content').glob('*.html')) + [OPS / 'build.py', OPS / 'llms-product.md']:
    if 'github.io' in f.read_text():
        errors.append(f.name + ': hard-codes a github.io URL; use relative links or SITE_URL')
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable, str(OPS / 'build.py'), '--out', tmp], check=True, capture_output=True)
    for f in Path(tmp).rglob('*'):
        if f.is_file():
            target = ROOT / f.relative_to(tmp)
            if not target.exists() or not filecmp.cmp(f, target, shallow=False):
                errors.append(str(f.relative_to(tmp)) + ': stale. Run python3 _ops/build.py')

# 1b. Hosting. GitHub Pages' Jekyll build is what keeps _ops private, so it must stay on.
if (ROOT / '.nojekyll').exists():
    errors.append('.nojekyll would publish _ops: remove it')
cname = ROOT / 'CNAME'
if not cname.exists() or cname.read_text().strip() != host:
    errors.append('CNAME must contain ' + host)
for f in ROOT.glob('*.txt'):
    if re.fullmatch(r'[0-9a-f]{32}', f.stem) and f.read_text().strip() != f.stem:
        errors.append(f.name + ': IndexNow key file must contain its own key')

# 2. Sitemap, robots, llms.
urls = {x.text for x in ET.parse(ROOT / 'sitemap.xml').getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
if urls != {url_for(n) for n in indexable}:
    errors.append('Sitemap differs from published pages')
robots = (ROOT / 'robots.txt').read_text()
for agent in ['OAI-SearchBot', 'ChatGPT-User', 'GPTBot', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Google-Extended', 'Applebot', 'Applebot-Extended', 'Bingbot']:
    if not re.search(r'User-agent: ' + re.escape(agent) + r'\nAllow: /', robots):
        errors.append('robots.txt: does not allow ' + agent)
if 'Disallow' in robots or 'Sitemap: ' + SITE + 'sitemap.xml' not in robots:
    errors.append('robots.txt: wrong policy or sitemap')
llms, llms_full = (ROOT / 'llms.txt').read_text(), (ROOT / 'llms-full.txt').read_text()
for ref_name, ref in [('llms.txt', llms), ('llms-full.txt', llms_full)]:
    if C['facts'] not in ref:
        errors.append(ref_name + ': missing the fact block')
    for bad in (PRICE_RE.search(ref), RATING_RE.search(ref), RATING_STATE_RE.search(ref)):
        if bad:
            errors.append(ref_name + ': price or rating text: ' + bad[0])
    for m in OLD_RE.finditer(ref):
        errors.append(f'{ref_name}: 1.x word: "{m[0]}" in ...{norm(ref[max(0, m.start() - 40):m.end() + 30])}...')
    for n in indexable:
        if '(' + url_for(n) + ')' not in ref:
            errors.append(ref_name + ': missing ' + n)

# 3. Every page.
for name in REQUIRED_URLS:
    if name not in pages:
        errors.append('Existing URL must be preserved: ' + name)
if len({p.title for p in pages.values()}) != len(pages):
    errors.append('Duplicate titles')
if len({p.meta['description'][0] for p in pages.values()}) != len(pages):
    errors.append('Duplicate descriptions')
tags_seen = {}
slots_used = set()
needed = (OPS / 'SCREENSHOTS_NEEDED.md').read_text() if (OPS / 'SCREENSHOTS_NEEDED.md').exists() else ''
for name, p in pages.items():
    def require(ok, message):
        if not ok:
            errors.append(name + ': ' + message)
    meta = metas.get(name, {})
    kind = meta.get('kind')
    raw = (ROOT / name).read_text()
    text = norm(''.join(p.text))
    require(p.lang == 'en', 'needs lang=en')
    require(p.h1 == 1, 'needs one H1')
    require(0 < len(p.title) <= 60, f'title length {len(p.title)}')
    require(len(p.meta.get('description', [])) == 1 and 0 < len(p.meta['description'][0]) <= 155, 'description length/count: ' + str(len(p.meta.get('description', [''])[0])))
    require(p.meta.get('apple-itunes-app') == ['app-id=' + APP], 'wrong Smart App Banner')
    require(p.meta.get('viewport') == ['width=device-width, initial-scale=1'], 'wrong viewport')
    require("connect-src 'none'" in ''.join(p.meta.get('Content-Security-Policy', [])), 'missing security policy')
    require('og:image' in p.meta and p.meta['og:image'][0].startswith(SITE), 'needs OG image on SITE_URL')
    og_file = ROOT / p.meta['og:image'][0].removeprefix(SITE) if p.meta.get('og:image') else None
    require(bool(og_file and og_file.exists() and png_size(og_file) == (1200, 630)), 'OG image must exist at 1200x630 (run build.py --og)')
    require(p.meta.get('twitter:card') == ['summary_large_image'], 'needs large Twitter card')
    require(p.frames == 0, 'no embedded frames or media')
    require(not p.videos or name == 'index.html', 'video only in the home hero')
    for v in p.videos:
        require(all(x in v for x in ['autoplay', 'muted', 'loop', 'playsinline', 'poster', 'width', 'height']), 'hero video needs autoplay muted loop playsinline poster width height')
        require('hero-toggle' in raw and 'hero-video.js' in raw, 'hero video needs its pause control')
    require(len(raw.encode()) < 110_000, 'HTML over 110 KB')
    if kind == '404':
        require(p.meta.get('robots') == ['noindex'] and not p.canonical and not p.schema, '404 must be noindex with no canonical or schema')
    else:
        require(p.canonical == [url_for(name)], 'canonical mismatch')
        require(p.meta.get('og:url') == [url_for(name)], 'og:url mismatch')
        require(bool(p.schema), 'missing schema')
    # No third parties: every script, stylesheet and image is ours.
    for src in p.scripts + p.styles + [i.get('src', '') for i in p.images]:
        u = urlsplit(src)
        require(src != 'INLINE', 'inline script')
        require(not u.netloc, 'third-party resource: ' + src)
    # Install paths: our own App Store links carry a campaign, one tag per page.
    tags = set()
    for link in p.links:
        u = urlsplit(link)
        if u.scheme or u.netloc:
            if u.hostname == 'apps.apple.com' and APP in u.path:
                q = parse_qs(u.query)
                require(u.path == f'/app/apple-store/id{APP}', 'App Store link not in campaign format: ' + link)
                require(q.get('pt') == [C['providerToken']] and q.get('mt') == ['8'] and 0 < len(q.get('ct', [''])[0]) <= 30, 'invalid campaign: ' + link)
                tags.add(q.get('ct', [''])[0])
            elif u.hostname == 'apps.apple.com':
                require('rel="nofollow"' in raw, 'competitor links must be nofollow')
            continue
        target = unquote(u.path) or name
        if kind == '404' and target.startswith('/'):
            target = target.removeprefix(urlsplit(SITE).path)
        require(not target.startswith('/'), 'root-absolute link breaks on a project site: ' + link)
        require((ROOT / target).exists(), 'broken link/asset: ' + link)
        if u.fragment and target in pages:
            pass
        if u.fragment:
            other = pages.get(target)
            if other:
                require(unquote(u.fragment) in other.ids, 'broken anchor: ' + link)
    require(len(tags) == 1, 'needs exactly one campaign tag, found ' + str(sorted(tags)))
    for t in tags:
        if t in tags_seen:
            errors.append(f'Campaign tag {t} used by {tags_seen[t]} and {name}')
        tags_seen[t] = name
    home_path = urlsplit(SITE).path
    icon_badge = any(l.endswith('assets/icon-112.png') for l in p.links) and any(l.endswith('assets/app-store-badge.svg') for l in p.links)
    require(icon_badge, 'CTA needs app icon and official badge')
    for img in p.images:
        require(all(x in img for x in ['width', 'height', 'alt']), 'image missing dimensions/alt: ' + img.get('src', ''))
        if 'app-store-badge' in img.get('src', ''):
            require(int(img['height']) >= 40, 'App Store badge under 40 px')
    # Product rules.
    source = source_scan_text(name)
    for m in BANNED_RE.finditer(source):
        errors.append(f'{name}: banned word outside a quoted section: "{m[0]}" in ...{norm(source[max(0, m.start() - 40):m.end() + 30])}...')
    combined = text + ' ' + p.title + ' ' + ' '.join(p.meta.get('description', []))
    for rx, why in [(PRICE_RE, 'price'), (RATING_RE, 'star rating'), (RATING_STATE_RE, 'rating statement')]:
        m = rx.search(combined)
        if m:
            errors.append(f'{name}: {why} text: {m[0]}')
    if 'aggregateRating' in raw or 'ratingValue' in raw:
        errors.append(name + ': rating schema is not allowed')
    for phrase in MUST_STATE.get(name, []):
        require(norm(phrase) in text.replace('’', "'"), 'must state: ' + phrase)
    for slot in re.findall(r'<!-- slot:([\w-]+) -->', raw):
        slots_used.add(slot)
    if name != 'privacy.html':
        kept = EARLIER_RE.sub(' ', re.sub(r'(?s)<!--quoted:start-->.*?<!--quoted:end-->', ' ', raw))
        seen = html.unescape(re.sub(r'(?s)<script.*?</script>|<!--.*?-->|<[^>]+>', ' ', kept)) + ' ' + ' '.join(i.get('alt', '') for i in p.images)
        extras = ' '.join(json_strings(p.schema) + [v for vs in p.meta.values() for v in vs] + [p.title])
        for m in OLD_RE.finditer(seen + ' ' + extras):
            around = (seen + ' ' + extras)[max(0, m.start() - 40):m.end() + 30]
            errors.append(f'{name}: 1.x word outside an earlier section: "{m[0]}" in ...{norm(around)}...')
    require('horizon' not in raw.lower() or name == 'privacy.html', 'old artwork or words: horizon')
    for img in p.images:
        if 'assets/screens/' in img.get('src', ''):
            slots_used.add(Path(img['src']).stem)
            require(len(img.get('alt', '')) > 60, 'real screenshot needs descriptive alt')
            require(img.get('loading') == 'lazy', 'screenshots load lazily')
            require('filter-on' not in img['src'] and 'blocker-on' not in img['src'], 'a Blocker shot with the filter on must come from a real device (SCREENSHOTS_NEEDED.md)')
    # Schema.
    types = {x.get('@type') for x in p.schema}
    faq = next((x for x in p.schema if x.get('@type') == 'FAQPage'), None)
    for q in (faq or {}).get('mainEntity', []):
        require(norm(q['name']) in [norm(h) for h in p.h3], 'FAQ question not visible: ' + q['name'])
        require(norm(q['acceptedAnswer']['text']) in text, 'FAQ answer not visible: ' + q['name'])
    if kind in ('article', 'tool'):
        require({'Article', 'BreadcrumbList', 'FAQPage'} <= types, 'needs Article, BreadcrumbList and FAQ JSON-LD')
        article = next(x for x in p.schema if x.get('@type') == 'Article')
        require(article.get('dateModified') == meta.get('updated'), 'Article dateModified differs')
        require('Updated ' in text, 'needs a visible updated date')
        require(article['author']['url'] == SITE + 'about.html' and 'about.html' in p.links, 'needs a real author link to about.html')
        for h in HELP_LINKS:
            require(h in p.links, 'needs help link ' + h)
        require('call or text 988' in text, 'needs the crisis line')
        require(meta.get('linkText') and meta.get('summary'), 'guide needs linkText and summary')
        require(len(text.split()) >= 500, 'thin page: ' + str(len(text.split())) + ' words')
    if kind in ('article', 'tool', 'about', 'legal'):
        require('BreadcrumbList' in types, 'needs BreadcrumbList')
        require(any(m in text for m in ['not treatment', 'not medical advice']), 'needs a not-treatment statement')
    if kind != '404':
        require(p.meta.get('og:title') == [p.title], 'og:title differs')
    require('{{' not in raw, 'unexpanded placeholder')
    require(len(re.findall(r'^(<<<<<<<|>>>>>>>)( |$)', raw, re.M)) == 0, 'conflict marker')

# 4. Site-wide wiring.
home = pages['index.html']
app = next((s for s in home.schema if s.get('@type') == 'MobileApplication'), None)
if not app or app.get('downloadUrl') != 'https://apps.apple.com/app/id' + APP or 'aggregateRating' in app:
    errors.append('Missing or incorrect MobileApplication entity')
if app and app.get('softwareVersion') != C['version']:
    errors.append('MobileApplication softwareVersion differs from discovery.json')
for n, m in metas.items():
    if m.get('linkText'):
        if n not in home.links:
            errors.append(n + ': not linked from the home page')
        if n not in pages['support.html'].links:
            errors.append(n + ': not linked from the support page')
for slot in slots_used:
    if slot not in needed:
        errors.append(f'Screenshot slot {slot} is not listed in _ops/SCREENSHOTS_NEEDED.md')
for n in re.findall(r'`(ballast-[\w-]+-iphone)\.(?:jpg|png)`', needed):
    if n not in slots_used:
        errors.append(f'SCREENSHOTS_NEEDED.md lists {n}, which no page uses')
for f in (ROOT / 'assets/screens').glob('*'):
    if f.stem not in slots_used:
        errors.append(f'assets/screens/{f.name} is used by no page')
# The levels on the page are the levels the art is drawn from, and llms-full.txt says the same.
home_text = norm(''.join(home.text)).replace('’', "'")
for level, days, *_ in daybreak.LEVELS:
    said = level + ('where everyone starts' if days == 0 else f'{days} day{"" if days == 1 else "s"} free')
    if said not in home_text:
        errors.append(f'index.html: level {level} at {days} days free is missing')
    if not re.search(rf'{level} \({days}\b', llms_full):
        errors.append(f'llms-full.txt: level {level} ({days}) is missing')
for fact in FREE_FACTS:
    for where, body in [('index.html', home_text), ('llms-full.txt', llms_full)]:
        if fact.lower() not in body.lower():
            errors.append(f'{where}: free/Pro fact missing: {fact}')
if C['version'] not in llms_full:
    errors.append('llms-full.txt: does not name version ' + C['version'])
if f"Version {'.'.join(C['version'].split('.')[:2])}," not in home_text:
    errors.append("index.html: the what's-new section does not name version " + C['version'])
# What the home page can load, in all: every image, the film, the poster, the style and the script.
weight = sum((ROOT / unquote(urlsplit(l).path)).stat().st_size for l in {x.split('?')[0] for x in home.links} | {'index.html'}
             if not urlsplit(l).scheme and (l.startswith('assets/') or l == 'index.html') and (ROOT / l).exists())
if weight > HOME_BUDGET:
    errors.append(f'index.html: {weight} bytes with media, over {HOME_BUDGET}')
for v in home.videos:
    if (ROOT / v.get('data-src', '')).stat().st_size > FILM_BUDGET:
        errors.append('hero film over 1.5 MB')
for doc in ['PUBLISH_CHECKLIST.md', 'SCREENSHOTS_NEEDED.md', 'QUITTR_RECHECK.md', 'DOMAIN_MOVE.md']:
    if not (OPS / doc).exists():
        errors.append('_ops/' + doc + ' is missing')
css = (ROOT / 'assets/site.css').read_text()
if len(css.encode()) > 20_000:
    errors.append('site.css over 20 KB')
for need in ['--gutter: 16px', 'prefers-reduced-motion', '#08080D', '#14151D', '#FF8A4C', '#FFCB5C', '#6EE7CF', '#A3A8C2', '#9B8CFF', 'ui-rounded']:
    if need not in css:
        errors.append('site.css: Daybreak token missing: ' + need)
for old in ['serif;', 'ui-serif', 'Georgia', '#120E17', '#FF9D6C', 'horizon', 'swell', '@font-face', '@import']:
    if old in css.replace('sans-serif;', ''):
        errors.append('site.css: old look or a web font: ' + old)

if errors:
    print('\n'.join(errors))
    print(f'\nFAILED with {len(errors)} problem(s)')
    raise SystemExit(1)
print(f'OK: {C["shortName"]} (version {C["version"]}): {len(pages)} pages on {SITE}, home {weight / 1000:.0f} KB with all media. Metadata, assets, links, schema, FAQ text, sitemap, robots, llms, campaigns, single SITE_URL, freshness, free/Pro facts, levels, no prices, no ratings, no banned claims, nothing left of 1.x, no third parties.')
