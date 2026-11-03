# ballast-site

The public pages for **Ballast**, an iPhone app for quitting porn.

- `privacy.html` — App Store Connect *Privacy Policy URL*
- `support.html` — App Store Connect *Support URL*
- `index.html` — the homepage (also generated)
- `block-porn-iphone-screen-time.html` — a hand-written guide (see below)

The privacy, support and index files are **generated**, not hand-edited. The source of the privacy policy is
`docs/PRIVACY_POLICY.md` in the app repo; run `python3 tools/build_site.py <this-dir>` there
and commit the result, so the hosted copy can never drift from the one shipped in the app.

No cookies, no analytics, no external requests.

## Discovery and install links (18 October 2026)

After regenerating policy/support pages, run `python3 _ops/enrich.py`. It restores the verified metadata, App Store badges and campaign links from `_ops/discovery.json` without changing legal body text. Keep app-specific facts in sync with the current listing and app source. Privacy remains authored in the app repository. This project subpath does not control the host-root robots.txt. `llms.txt` is an optional reference, not an AI ranking mechanism.

## Guides (added 4 November 2026)

Guides are **hand-written files in this repo**, listed under `guides` in `_ops/discovery.json`. The app's generator (`tools/build_site.py`) writes only `index.html`, `privacy.html`, `support.html`, `robots.txt`, `sitemap.xml`, `llms.txt` and two assets, so it leaves guide files alone. It does overwrite the homepage, support page, sitemap and llms file, so `_ops/enrich.py` re-adds the guide links to all of them, regenerates `llms-full.txt`, and re-applies each guide's App Store campaign tag. This was tested on 4 November 2026: generator plus enrich reproduced this repo byte for byte, with both the committed generator and the owner's uncommitted one (which calls enrich itself). The committed generator does not, so run `python3 _ops/enrich.py` afterwards.

To add a guide: write the HTML (it carries its own copy of the site CSS, so restyle it if the generator's CSS changes), add an entry to `guides` with a unique `campaign` of 30 characters or fewer, run `_ops/enrich.py`, then `_ops/validate.py`. The validator checks Article and BreadcrumbList JSON-LD, that FAQ markup matches visible text, the campaign tag on every App Store link, and links from home, support and both llms files.

### 2026-11-04: block porn on iPhone guide

`block-porn-iphone-screen-time.html`, campaign `ballast-guide-block-porn`. Choosing the topic is editorial judgment based on the app's real features (the free Friction checklist and urge flow), not measured search volume; no query data was available. Ballast does not block anything (no FamilyControls or NetworkExtension code), and the guide says so.

Sources checked 4 November 2026: Apple's iPhone User Guide for iOS 26 (block websites; Screen Time passcode), its iOS 27 page, which does not describe a web filter for your own iPhone, and Apple's parental controls article 105121. **Recheck the iOS 27 paragraph when Apple documents the own-device path.** App labels were checked in the Swift source at the commit that shipped 1.0.1 (`FrictionChecklist`, `MoreView`, `TodayView`, `RootView`, `PanicFlowView`, `FreeTier`). The App Store listing was checked through the iTunes lookup API: 1.0.1, iOS 26.0, 0 ratings, so no social proof is shown.

IndexNow is skipped because it needs a key file at the host root, which a `github.io` project site cannot provide. Search Console indexing and rankings were not measured.
