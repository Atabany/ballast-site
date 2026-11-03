# Moving from github.io to Ballast's own domain

No domain has been bought. Candidates and evidence are in the app repo's
`docs/RESEARCH_2026-11.md`; `urgeplan.com` had no RDAP record on 2026-11-04, which isn't proof of
availability, price or trademark clearance. The owner decides.

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
