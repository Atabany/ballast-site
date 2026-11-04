# Moving from github.io to Ballast's own domain

**`quitpmo.com` was registered on 2026-11-04** at Cloudflare by the owner (1 year, auto-renew on, Cloudflare nameservers). `SITE_URL` and `CNAME` on this branch already point at it. **No DNS records exist yet, and nothing is connected:** connecting waits for the owner's go-ahead, per `PUBLISH_CHECKLIST.md`.

DNS records for GitHub Pages at publish time, all **DNS only** (grey cloud, no proxy): `A @` to 185.199.108.153, 185.199.109.153, 185.199.110.153 and 185.199.111.153; `AAAA @` to 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153 and 2606:50c0:8003::153; `CNAME www` to atabany.github.io. Verify these against GitHub's current docs on the day. Then set the custom domain in the Pages settings, enforce HTTPS, and test redirects.

## The one-line rebuild

1. In `_ops/discovery.json`, set `"SITE_URL": "https://<domain>/"`. That is the only place a host is written.
2. `python3 _ops/build.py --og && python3 _ops/validate.py`. Canonicals, Open Graph, JSON-LD, sitemap, robots, llms files and the 404 page's paths all follow.
3. Add a `CNAME` file containing `<domain>` and commit.

## Redirect plan: old URL to new URL

GitHub Pages redirects a project site's `github.io` address to its custom domain once one is set, keeping the path. Because there's no user site at `atabany.github.io` (checked 2026-11-04), the mapping is:

| Old | New |
|---|---|
| `https://atabany.github.io/ballast-site/` | `https://<domain>/` |
| `.../ballast-site/privacy.html` | `https://<domain>/privacy.html` |
| `.../ballast-site/support.html` | `https://<domain>/support.html` |
| `.../ballast-site/block-porn-iphone-screen-time.html` | `https://<domain>/block-porn-iphone-screen-time.html` |
| every other page | same filename at the root |

File names don't change, so every old URL has an exact match. After connecting, test each one:

```sh
python3 - <<'PY'
import json, re, subprocess
for loc in re.findall(r'<loc>(.*?)</loc>', open('sitemap.xml').read()):
    path = loc.split('/', 3)[3]
    old = 'https://atabany.github.io/ballast-site/' + path
    out = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code} %{redirect_url}', old], capture_output=True, text=True).stdout
    print(out, '<-', old)
PY
```

Each line should read `301 https://<domain>/<same path>`. This has not been tested for this repo, since no domain exists yet. If a redirect is missing, stop and fix it before changing anything that links to the old URL.

Live references to the old URLs, which must keep working throughout:

- The shipped app: `Services/Legal.swift` links `privacy.html` and `support.html` (builds up to and including the one live at that time).
- App Store Connect: Privacy Policy and Support URLs, which are locked while a version is live or in review. Change them in the next editable version; redirects cover the gap.
- `docs/STORE_SETUP.md` in the app repo.

Never delete the `ballast-site` repo or disable Pages. The redirects depend on it, and old app versions keep linking through them.

## What only works after the move

- `robots.txt` becomes authoritative. On a project subpath, crawlers read the host root's policy, which isn't ours.
- IndexNow: its key file must be at the host root (`python3 _ops/indexnow.py init`).
- Search Console Domain property and Bing Webmaster, per `PUBLISH_CHECKLIST.md`.
