#!/usr/bin/env python3
"""Check links against a running local server, including anchors, and optionally external links.

    python3 _ops/linkcheck.py http://localhost:8765/ballast-site/ [--external]

Serve a folder where this repo appears at the SITE_URL path, so the 404 page's absolute paths work.
A 403 or 429 from an external host usually means bot blocking, not a dead page; those are listed
separately and should be opened in a browser.
"""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urldefrag
import json, pathlib, subprocess, sys, urllib.error, urllib.request

start = sys.argv[1]
SITE = json.loads((pathlib.Path(__file__).resolve().parent / 'discovery.json').read_text())['SITE_URL']
external = '--external' in sys.argv
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        for k in ('href', 'src'):
            if a.get(k):
                self.links.append(a[k])


seen, ids, anchors, out_links, broken = {}, {}, [], {}, []
queue = [start, urljoin(start, '404.html')]
while queue:
    url = queue.pop()
    if url in seen:
        continue
    try:
        with urllib.request.urlopen(url) as r:
            body = r.read()
            seen[url] = r.status
            ctype = r.headers.get('Content-Type', '')
    except urllib.error.HTTPError as e:
        seen[url] = e.code
        broken.append((url, e.code))
        continue
    if 'html' not in ctype:
        continue
    p = Links()
    p.feed(body.decode())
    ids[url] = p.ids
    for link in p.links:
        full = urljoin(url, link)
        u = urlsplit(full)
        if u.scheme == 'mailto':
            continue
        if full.startswith(start.rsplit('/', 2)[0]):
            base, frag = urldefrag(full)
            if frag:
                anchors.append((url, base, frag))
            queue.append(base)
        elif not full.startswith(SITE):  # Canonical URLs aren't live until publication.
            out_links.setdefault(full, url)
for src, base, frag in anchors:
    if frag not in ids.get(base, set()):
        broken.append((f'{src} -> {base}#{frag}', 'missing anchor'))
print(f'Internal: {len(seen)} URLs, {len(anchors)} anchors, {len(broken)} broken')
for b in broken:
    print('  BROKEN', b)
blocked = []
if external:
    bad = []
    for link in sorted(out_links):
        code = subprocess.run(['curl', '-sL', '-o', '/dev/null', '-m', '25', '-A', UA, '-w', '%{http_code}', link], capture_output=True, text=True).stdout
        if code.startswith('2') or code.startswith('3'):
            continue
        (blocked if code in ('403', '429', '000') else bad).append((code, link))
    print(f'External: {len(out_links)} URLs, {len(bad)} dead, {len(blocked)} refused automated checks')
    for b in bad:
        print('  DEAD', b)
    for b in blocked:
        print('  REFUSED', b)
    broken += bad
sys.exit(1 if broken else 0)
