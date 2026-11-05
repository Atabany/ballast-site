# ballast-site

The public website for **Ballast: Quit PMO**, an iPhone app. Plain HTML, one CSS file, one small script on the tool page. No framework, web fonts, cookies, analytics or third-party requests.

## How it's built

**Don't edit the root `*.html` files.** They're generated.

| Source | What it is |
|---|---|
| `_ops/discovery.json` | App facts, the fact block, **`SITE_URL`, the one place a host is written**, and **`RELEASE_STATE`** |
| `_ops/content/*.html` | Page text. Each starts with a JSON meta block |
| `_ops/llms-product.md` | The plain product summary in `llms-full.txt` |
| `_ops/horizon.py` | The swell artwork, pure SVG |
| `assets/site.css`, `assets/urge-plan.js` | Style; the plan builder |
| `_ops/live/assets`, `_ops/prelaunch/assets` | Icons, Open Graph images and screenshots for each state. The build copies the current state's set into `assets/` |
| `_ops/prelaunch/pages`, `_ops/prelaunch_edits.py`, `_ops/prelaunch/llms-product.md` | What differs before 1.1.0 is on the App Store |

## Release state

`"RELEASE_STATE": "prelaunch"` publishes only what's true of the version on the App Store today. `"live"` publishes the full 1.1 site, with no other edits. Change that line, rebuild, validate. In `prelaunch` the validator fails on any claim of an unshipped feature, except in the labelled coming note. A failed edit in `prelaunch_edits.py` stops the build, so if the live copy changes the prelaunch page can't drift unnoticed.

```sh
python3 _ops/build.py        # regenerate the site
python3 _ops/build.py --og   # also regenerate Open Graph images (headless Chrome, Pillow)
python3 _ops/validate.py     # must print OK before publishing
python3 _ops/validate.py --both        # both states, in temporary copies
python3 _ops/test_states.py rebuild/next  # flip both ways against a baseline; plant claims and check they're caught
```

Check locally:

```sh
python3 -m http.server 8765
python3 _ops/linkcheck.py http://localhost:8765/ --external
```

GitHub Pages' Jekyll build keeps `_ops` private, so never add a `.nojekyll` file. Pages keep their names when moved. `privacy.html` and `support.html` are App Store Connect URLs and linked from the app, so never rename them.

## Rules

Copy obeys the app's rules, and `validate.py` enforces what it can:

- A slip is data. No shaming copy, and no claims about dopamine, rewiring or fixed timelines, except inside `<!--quoted:start-->…<!--quoted:end-->` where a page is quoting or explaining a claim it doesn't make.
- "Uses skills from CBT and ACT", never "proven". Ballast is not treatment.
- No prices and no invented ratings, counts or rankings.
- Each page has a single App Store campaign tag in Apple's format, plus the official badge and app icon on every call to action.

Page shortcodes (store, cta, help, facts, slot, plan_table) are listed in `expand()` in `_ops/build.py`. FAQ text goes between `<!--faq:start-->` and `<!--faq:end-->` as `<h3>`/`<p>` pairs; the build generates the JSON-LD from it.

## Ops docs

- `_ops/PUBLISH_CHECKLIST.md`: two stages, prelaunch now and the day 1.1.0 is live, and which claims wait for the update
- `_ops/QUITTR_RECHECK.md`: facts to recheck on publish day
- `_ops/DOMAIN_MOVE.md`: one-line domain change and the redirect plan
- `_ops/SCREENSHOTS_NEEDED.md`: real app captures to supply; slots use abstract artwork until then

The old flow (`tools/build_site.py` in the app repo, then `_ops/enrich.py`) is retired. Running the app's generator against this repo would overwrite it.
