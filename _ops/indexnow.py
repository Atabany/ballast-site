#!/usr/bin/env python3
"""Tell IndexNow about changed URLs. Only works on Ballast's own domain.

    python3 _ops/indexnow.py init                 # create the key file at the repo root, once
    python3 _ops/indexnow.py all                  # ping every URL in sitemap.xml
    python3 _ops/indexnow.py <url> [<url> ...]    # ping specific URLs

Refuses to run on github.io: the key must be served from the host root. Publishing a ping is a
public action, so only run it after the owner has approved publication.
"""
from pathlib import Path
from urllib.parse import urlsplit
import json, re, secrets, sys, urllib.request

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / '_ops/discovery.json').read_text())
host = urlsplit(C['SITE_URL']).netloc
if host.endswith('github.io'):
    sys.exit('Refusing: IndexNow needs a key at the host root. Connect the domain first (_ops/DOMAIN_MOVE.md).')
args = sys.argv[1:]
keys = [p.stem for p in ROOT.glob('*.txt') if re.fullmatch(r'[0-9a-f]{32}', p.stem)]
if args == ['init']:
    if keys:
        sys.exit('Key already exists: ' + keys[0])
    key = secrets.token_hex(16)
    (ROOT / f'{key}.txt').write_text(key)
    sys.exit(f'Created {key}.txt. Commit and deploy it, then run: python3 _ops/indexnow.py all')
if not keys or not args:
    sys.exit(__doc__)
urls = re.findall(r'<loc>(.*?)</loc>', (ROOT / 'sitemap.xml').read_text()) if args == ['all'] else args
body = json.dumps({'host': host, 'key': keys[0], 'keyLocation': f'https://{host}/{keys[0]}.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
with urllib.request.urlopen(req) as r:
    print('IndexNow HTTP', r.status, 'for', len(urls), 'URLs')
