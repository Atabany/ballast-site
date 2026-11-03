# ballast-site

The public website for **Ballast: Quit PMO**, an iPhone app. Plain HTML, one CSS file, one small script on the tool page. No framework, web fonts, cookies, analytics or third-party requests.

## How it's built

**Don't edit the root `*.html` files.** They're generated.

| Source | What it is |
|---|---|
| `_ops/discovery.json` | App facts, the fact block and **`SITE_URL`, the one place a host is written** |
| `_ops/content/*.html` | Page text. Each starts with a JSON meta block |
| `_ops/llms-product.md` | The plain product summary in `llms-full.txt` |
| `_ops/horizon.py` | The swell artwork, pure SVG |
| `assets/site.css`, `assets/urge-plan.js` | Style; the plan builder |

```sh
python3 _ops/build.py        # regenerate the site
python3 _ops/build.py --og   # also regenerate Open Graph images (headless Chrome, Pillow)
python3 _ops/validate.py     # must print OK before publishing
```

Check locally from a folder where the repo appears at the `SITE_URL` path:

```sh
mkdir -p /tmp/serve && ln -sfn "$PWD" /tmp/serve/ballast-site
python3 -m http.server 8765 -d /tmp/serve
python3 _ops/linkcheck.py http://localhost:8765/ballast-site/ --external
```

Pages keep their names when moved. `privacy.html` and `support.html` are App Store Connect URLs and linked from the app, so never rename them.

## Rules

Copy obeys the app's rules, and `validate.py` enforces what it can:

- A slip is data. No shaming copy, and no claims about dopamine, rewiring or fixed timelines, except inside `<!--quoted:start-->…<!--quoted:end-->` where a page is quoting or explaining a claim it doesn't make.
- "Uses skills from CBT and ACT", never "proven". Ballast is not treatment.
- No prices and no invented ratings, counts or rankings.
- Each page has a single App Store campaign tag in Apple's format, plus the official badge and app icon on every call to action.

Page shortcodes (store, cta, help, facts, slot, plan_table) are listed in `expand()` in `_ops/build.py`. FAQ text goes between `<!--faq:start-->` and `<!--faq:end-->` as `<h3>`/`<p>` pairs; the build generates the JSON-LD from it.

## Ops docs

- `_ops/PUBLISH_CHECKLIST.md`: exact steps for publishing, and which claims wait for the App Store update
- `_ops/QUITTR_RECHECK.md`: facts to recheck on publish day
- `_ops/DOMAIN_MOVE.md`: one-line domain change and the redirect plan
- `_ops/SCREENSHOTS_NEEDED.md`: real app captures to supply; slots use abstract artwork until then

The old flow (`tools/build_site.py` in the app repo, then `_ops/enrich.py`) is retired. Running the app's generator against this repo would overwrite it.
