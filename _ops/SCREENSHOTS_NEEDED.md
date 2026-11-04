# Real app screenshots needed

Pages reserve these slots. Until a file exists, the page shows an abstract Horizon panel: decorative
artwork, `alt=""`, with no fake interface. **Never put mock UI in these slots.** Screens must be
captured from Ballast 1.1 itself, on a device or simulator. Don't use `MockShield` output as evidence
of the real Shield path unless the real path has been run on a device first.

To supply one: save it as `assets/screens/<filename>`, run `python3 _ops/build.py`, then
`python3 _ops/validate.py`. The build picks up the file, its dimensions and the alt text by itself.

Recommended export, from a 6.3" capture (1206 x 2622 pixels):
`sips -s format jpeg -s formatOptions 82 -Z 1560 capture.png --out assets/screens/<filename>.jpg`

Use `-seed-demo` data, which contains no real person's data. Avoid anything explicit in shot content.
Launch arguments are in `CLAUDE.md` and `docs/kb/simulator-and-debug.md` of the app repo.

| File (`.jpg` or `.png`) | Page | What it must show |
|---|---|---|
| `ballast-shield-filter-and-commitment-lock-iphone.jpg` | Home; Screen Time guide | Shield tab: status hero, filter on, commitment lock settings, and the honest-limits text if it fits |
| `ballast-urge-flow-if-then-plan-card-iphone.jpg` | Home | Urge flow with the user's own if-then card and reason, plus the choice: breathe, ride the wave, do the plan |
| `ballast-voyage-route-clear-days-waypoints-iphone.jpg` | Home | Voyage: clear days, route, waypoints, a slip as an ordinary mark |
| `ballast-after-slip-next-hour-support-iphone.jpg` | After a slip | After-slip screen, "The next hour" |
| `ballast-plan-tab-my-urge-plans-iphone.jpg` | Plan builder | Plan tab, list of urge plans by trigger |

All five are installed, from `quitPorn-next/marketing/site-screens`. **The Shield screen is mock output** (`MockShield`, on a simulator): `PUBLISH_CHECKLIST.md` has the step that clears it. The Plan screen is the Urge plans page, one tap from the Plan tab, because that's where the list by trigger is.

The home hero is the loop from the same folder (`assets/ballast-horizon-hero-loop.mp4`, poster beside it), with `assets/hero-video.js` for the pause control. Under `prefers-reduced-motion` and Save-Data it stays on the poster.
