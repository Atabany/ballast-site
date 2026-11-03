"""Validate a small app site's metadata, links, install paths and discovery coverage."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, parse_qs, unquote
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / '_ops/discovery.json').read_text())
errors = []

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.h3 = []
        self.in_h3 = False
        self.in_body = False
        self.title = ''
        self.in_title = False
        self.in_json = False
        self.buffer = ''
        self.schema = []
        self.links = []
        self.images = []
        self.ids = set()
        self.meta = {}
        self.canonical = []
        self.h1 = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:
                errors.append('Duplicate ID: ' + a['id'])
            self.ids.add(a['id'])
        if tag == 'title':
            self.in_title = True
        if tag == 'body':
            self.in_body = True
        if tag == 'h3':
            self.in_h3 = True
            self.h3.append('')
        if tag == 'h1':
            self.h1 += 1
        if tag == 'meta':
            key = a.get('name', a.get('property', ''))
            self.meta.setdefault(key, []).append(a.get('content', ''))
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical.append(a.get('href', ''))
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.in_json = True
            self.buffer = ''
        if tag == 'img':
            self.images.append(a)
        for key in ['href', 'src', 'poster']:
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

pages = {}
for path in ROOT.glob('*.html'):
    p = Page()
    p.feed(path.read_text())
    pages[path.name] = p

urls = {x.text for x in ET.parse(ROOT / 'sitemap.xml').getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
expected = {C['base'] + ('' if name == 'index.html' else name) for name in pages}
if urls != expected:
    errors.append('Sitemap differs from published pages')
if len({p.title for p in pages.values()}) != len(pages):
    errors.append('Duplicate titles')
for name, p in pages.items():
    def require(ok, message):
        if not ok:
            errors.append(name + ': ' + message)
    require(p.h1 == 1, 'needs one H1')
    require(0 < len(p.title) <= 60, 'title length')
    require(len(p.meta.get('description', [])) == 1 and 0 < len(p.meta['description'][0]) <= 155, 'description length/count')
    require(p.canonical == [C['base'] + ('' if name == 'index.html' else name)], 'canonical mismatch')
    require(p.meta.get('apple-itunes-app') == ['app-id=' + str(C['appId'])], 'wrong Smart App Banner')
    require(bool(p.schema), 'missing schema')
    installs = 0
    for raw in p.links:
        u = urlsplit(raw)
        if u.netloc or u.scheme:
            if u.hostname == 'apps.apple.com' and '/app/' in u.path:
                installs += 1
                q = parse_qs(u.query)
                require(str(C['appId']) in u.path, 'wrong App Store destination')
                require(q.get('pt') == ['127826363'] and q.get('mt') == ['8'] and 0 < len(q.get('ct', [''])[0]) <= 40, 'invalid campaign')
            continue
        target = unquote(u.path) or name
        if target.startswith('/'):
            target = target.removeprefix(urlsplit(C['base']).path)
        local = ROOT / target
        require(local.exists(), 'broken link/asset: ' + raw)
        if u.fragment and target in pages:
            require(unquote(u.fragment) in pages[target].ids, 'broken anchor: ' + raw)
    require(installs > 0, 'no install path')
    for img in p.images:
        require(all(x in img for x in ['width', 'height', 'alt']), 'image missing dimensions/alt')
    require(C['base'] + ('' if name == 'index.html' else name) in (ROOT / 'llms.txt').read_text(), 'missing reference coverage')
home = pages['index.html']
app = next((s for s in home.schema if s.get('@type') == 'MobileApplication'), None)
if not app or app.get('downloadUrl') != 'https://apps.apple.com/app/id' + str(C['appId']):
    errors.append('Missing or incorrect application entity')
if 'listing is being prepared' in (ROOT / 'index.html').read_text():
    errors.append('Outdated launch status')
# Guides: hand-written pages listed in discovery.json and re-linked by enrich.py.
guides = C.get('guides', [])
if len({g['campaign'] for g in guides}) != len(guides):
    errors.append('Guide campaign tags must be unique')
norm = lambda x: ' '.join(x.split())
for g in guides:
    name = g['file']
    def require(ok, message):
        if not ok:
            errors.append(name + ': ' + message)
    p = pages.get(name)
    if not p:
        errors.append('Missing guide page: ' + name)
        continue
    require(p.title == g['title'], 'title differs from discovery.json')
    require(0 < len(g['campaign']) <= 30, 'campaign tag must be 1-30 characters')
    tags = [parse_qs(urlsplit(u).query).get('ct', [''])[0] for u in p.links if urlsplit(u).hostname == 'apps.apple.com']
    require(tags and set(tags) == {g['campaign']}, 'App Store links must all use ct=' + g['campaign'])
    require('assets/app-icon.png' in p.links and 'assets/app-store-badge.svg' in p.links, 'CTA needs app icon and App Store badge')
    types = {x.get('@type') for x in p.schema}
    require({'Article', 'BreadcrumbList'} <= types, 'needs Article and BreadcrumbList JSON-LD')
    article = next((x for x in p.schema if x.get('@type') == 'Article'), {})
    require(article.get('dateModified') == g['updated'], 'Article dateModified differs from discovery.json')
    text = norm(''.join(p.text))
    require('Updated ' in text and 'support.html' in p.links, 'needs a visible updated date and support/correction link')
    faq = next((x for x in p.schema if x.get('@type') == 'FAQPage'), None)
    require(bool(faq) == bool(g.get('faq')), 'FAQPage presence differs from discovery.json')
    for q in (faq or {}).get('mainEntity', []):
        require(norm(q['name']) in [norm(h) for h in p.h3], 'FAQ question not visible: ' + q['name'])
        require(norm(q['acceptedAnswer']['text']) in text, 'FAQ answer not visible: ' + q['name'])
    for host in ['index.html', 'support.html']:
        require(name in pages[host].links, 'not linked from ' + host)
    for ref in ['llms.txt', 'llms-full.txt']:
        require(C['base'] + name in (ROOT / ref).read_text(), 'missing from ' + ref)
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print('OK — ' + C['shortName'] + ': ' + str(len(pages)) + ' pages, ' + str(len(guides)) + ' guide(s): metadata, local assets, links, schema, FAQ text, sitemap, llms and App Store campaigns')
