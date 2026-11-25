# Real app screenshots

Every screen on the site is a real capture of Ballast. **Never put mock UI in a slot.** While a file
is missing, its slot shows the light (`_ops/daybreak.py`): decoration, `alt=""`, no interface.

**A Blocker shot with the filter on only from a real device.** On the simulator the filter can't be
granted, so "Filter on" there is a debug state and is not used here, even though the filter works on a
phone. `validate.py` refuses a file whose name says the filter is on.

To supply or replace one: save it as `_ops/live/assets/screens/<filename>`, run
`python3 _ops/build.py`, then `python3 _ops/validate.py`. The build picks up the file, its size and the
alt text by itself, and removes files no longer supplied.

Recommended export, from a 6.9" capture (1320 x 2868 pixels):
`sips -s format jpeg -s formatOptions 82 -Z 1560 capture.png --out _ops/live/assets/screens/<filename>.jpg`

Use `-seed-demo` data, which contains no real person's data. Avoid anything explicit in shot content.
Launch arguments are in `CLAUDE.md` and `docs/kb/simulator-and-debug.md` of the app repo.

The set below was exported on 25 November 2026 from `marketing/app-store-2026-11-v2/raw/` in the app
repo: Ballast 1.4.0's App Store captures (iPhone 17 Pro Max simulator, iOS 26.5, sample data). They all
show the same person: 44 total days free, a 13-day streak, level 6, 32 urges beaten.

| File (`.jpg` or `.png`) | Source | Page | What it must show |
|---|---|---|---|
| `ballast-panic-step-1-breathe-iphone.jpg` | `panic-breathe` | Home | Panic step 1: the light, "Breathe out", the person's reason |
| `ballast-panic-step-2-your-if-then-plan-iphone.jpg` | `panic-plan` | Home; plan builder | Panic step 2: "Do this now" with their own if-then card |
| `ballast-panic-step-3-ride-it-out-timer-iphone.jpg` | `panic-ride` | Home | Panic step 3: the ring and the time left |
| `ballast-panic-step-4-urge-beaten-iphone.jpg` | `panic-passed` | Home | After "It passed": urges beaten |
| `ballast-progress-total-days-free-and-levels-iphone.jpg` | `progress` | Home | Total days free, level, streak, the row of levels |
| `ballast-after-a-slip-what-changes-what-stays-iphone.jpg` | `afterslip` | Home; after a slip | "What changes, what stays", one thing for the next hour |
| `ballast-blocker-tab-filter-off-iphone.jpg` | `blocker-off` | Home; Screen Time guide | The Blocker before it is turned on |
| `ballast-toolkit-lesson-and-tools-iphone.jpg` | `toolkit-pro` | Home | Today's lesson (day 12, Pro, and the caption says so) and the six tools |
| `ballast-insights-when-it-is-hardest-iphone.jpg` | `insights` | Home, beside a PRO tag | The short version and the map of the week |

The home hero is a film cut from real recordings in `marketing/app-preview-2026-11-v2/captures/` of the
app repo by `_ops/hero_film.py` (`assets/ballast-panic-hero-film.mp4`, poster beside it), with
`assets/hero-video.js` for the pause control. Under `prefers-reduced-motion` and Save-Data, or with no
JavaScript, it stays on the poster and nothing is downloaded.
