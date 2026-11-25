# ballast-site

The public website for **Ballast: Quit PMO & Blocker**, an iPhone app. Plain HTML, one CSS file, two small scripts (the hero film's pause control and the plan builder). No framework, web fonts, cookies, analytics or third-party requests.

## How it's built

**Don't edit the root `*.html` files.** They're generated.

| Source | What it is |
|---|---|
| `_ops/discovery.json` | App facts, the version, the fact block and **`SITE_URL`, the one place a host is written** |
| `_ops/content/*.html` | Page text. Each starts with a JSON meta block: `light` picks the light at the top of the page, `tint` its glow, `og_shot` and `og_hl` the Open Graph image |
| `_ops/llms-product.md` | The plain product summary in `llms-full.txt` |
| `_ops/daybreak.py` | The light, pure SVG, from the app's ten levels |
| `_ops/hero_film.py` | Cuts the hero film from real recordings. Run by hand, not by the build |
| `assets/site.css`, `assets/urge-plan.js`, `assets/hero-video.js` | Style; the plan builder; the hero's pause control |
| `_ops/live/assets` | Icons, Open Graph images and screenshots. The build copies them into `assets/` |

The look is the app's: "Daybreak". The tokens in `site.css` are the ones in the app's `DesignSystem/Theme.swift`: a night-black ground, one light per page, the sunrise gradient for the idea, mint for calm and free, slate for slips, violet for Pro, rounded system type. Dark only, like the app. One question per section on the home page, and one main button: the App Store badge.

```sh
python3 _ops/build.py        # regenerate the site
python3 _ops/build.py --og   # also regenerate Open Graph images (headless Chrome, Pillow)
python3 _ops/validate.py     # must print OK before publishing
```

Check locally:

```sh
python3 -m http.server 8765
python3 _ops/linkcheck.py http://localhost:8765/ --external
```

GitHub Pages' Jekyll build keeps `_ops` private on the site, so never add a `.nojekyll` file. Pages keep their names when moved. `privacy.html` and `support.html` are App Store Connect URLs and linked from the app, so never rename them.

## Rules

Copy obeys the app's rules, and `validate.py` enforces what it can:

- A slip is data. No shaming copy, and no claims about dopamine, rewiring or fixed timelines, except inside `<!--quoted:start-->…<!--quoted:end-->` where a page is quoting or explaining a claim it doesn't make.
- "Uses skills from CBT and ACT", never "proven". Ballast is not treatment.
- No prices, no ratings or statements about ratings, no invented counts or rankings.
- The app's words: streak, total days free, level, goal, slip, urge, Panic, Progress, Toolkit, Blocker. The 1.x words and versions fail the build, except inside `<!--earlier:start-->…<!--earlier:end-->`, where a page tells someone upgrading what a thing used to be called, and on the privacy page, which covers every version.
- The free/Pro line and the ten levels are checked on the home page and in `llms-full.txt`.
- Real captures only, and a Blocker shot with the filter on only from a real device (`_ops/SCREENSHOTS_NEEDED.md`).
- Each page has a single App Store campaign tag in Apple's format, plus the official badge and app icon on every call to action.
- The home page, with all its media, stays under 2 MB, and the film under 1.5 MB.

Page shortcodes (store, cta, help, facts, slot, light, levels, plan_table) are listed in `expand()` in `_ops/build.py`. FAQ text goes between `<!--faq:start-->` and `<!--faq:end-->` as `<h3>`/`<p>` pairs; the build generates the JSON-LD from it.

## Ops docs

- `_ops/PUBLISH_CHECKLIST.md`: what to check before and after publishing, and which claims follow the app
- `_ops/QUITTR_RECHECK.md`: facts to recheck on publish day
- `_ops/DOMAIN_MOVE.md`: how the site moved to its own domain, and why the old addresses must keep working
- `_ops/SCREENSHOTS_NEEDED.md`: the real app captures and where each is used

The old flow (`tools/build_site.py` in the app repo, then `_ops/enrich.py`) is retired. Running the app's generator against this repo would overwrite it.
