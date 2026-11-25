# Publish checklist

Pages serves `main` from the repo root, on `quitpmo.com`. Publishing, pinging IndexNow and anything in App Store Connect, DNS or Pages settings is public or hard to undo, so each needs the owner's or the coordinator's go-ahead.

## Before publishing

```sh
python3 _ops/build.py --og && python3 _ops/validate.py      # must print OK
python3 -m http.server 8765 &                               # then, and stop it after:
python3 _ops/linkcheck.py http://localhost:8765/ --external
git grep -nE '^(<<<<<<<|>>>>>>>)( |$)'                      # must print nothing
```

- [ ] `curl -s "https://itunes.apple.com/lookup?id=6803731313&country=us"` shows the version in `_ops/discovery.json`, and the same name.
- [ ] `QUITTR_RECHECK.md` was done within the last day. If it can't be redone, keep the dated wording and change no date.
- [ ] Every row in **Claims that follow the app** is true of the shipped build's code.
- [ ] The privacy text matches `docs/PRIVACY_POLICY.md` and `Services/Legal.swift` in the app repo.
- [ ] Icon files match the shipped `AppIcon-1024.png` and the App Store artwork.
- [ ] Every page has been looked at at 320, 390 and 1440 px, with reduced motion, and by keyboard.
- [ ] New first-person statements on the about, comparison and QUITTR pages have been read by the owner.

## After publishing

- [ ] `https://quitpmo.com/`, `/privacy.html`, `/support.html` and the guides return 200 over HTTPS; `/_ops/discovery.json` and `/README.md` return 404; `/does-not-exist` shows the styled 404.
- [ ] Open the home page on a real iPhone: Smart App Banner, badge, film, pause button. Share the URL to yourself to see the Open Graph image.
- [ ] With approval: `python3 _ops/indexnow.py all`.
- [ ] Search Console and Bing: the sitemap reads, and changed pages are re-requested.
- [ ] Update `docs/kb/website.md` in the app repo.

## Claims that follow the app

Checked on 25 November 2026 against the code of 1.4.0 (tag `v1.4.0`; the app code on `main` is the same). On a device, the owner has confirmed that the filter and an added site work; the commitment lock, blocked apps and a Pro lapse have been checked in the code, not on a device.

| Claim | Where | Check in the app |
|---|---|---|
| Five tabs: Home, Progress, Panic, Toolkit, Blocker | All | `App/RootView.swift` |
| Four panic steps; in for four, out for six; ten-minute ride; no plan or signal needed; Home, Panic tab, Control Centre, Siri | Home, guides, llms | `Features/Panic/UrgeFlowLogic.swift`, `Models/Profile.swift`, `Intents/BallastShortcuts.swift` |
| Ten levels by total days free; a level is never taken away | Home, slip page, comparison, llms | `Services/LightLevel.swift` (`_ops/daybreak.py` repeats it) |
| Goal of 7 to 365 days in a row, with its date | Home, llms | `StreakGoal` |
| A slip today restarts the streak and keeps the rest; an earlier day comes off the total | Home, slip page, support, llms | `Features/Slip/SlipEffect.swift`, `SlipCopy.swift` |
| One-tap filter, free; no VPN; turns off Safari Private Browsing; misses some sites; other browsers unknown | Home, guide, support, privacy, comparison, llms | `Services/ShieldCopy.swift` |
| Own sites: 3 free, up to 25 with Pro; stay on the phone; out of backups | Home, guide, support, llms | `Services/FreeTier.swift`, `ShieldSites.swift` |
| Commitment lock: 10 minutes, 1 hour, 24 hours; trusted person's code; 24-hour wait always works; 15-minute window | Home, guide, support, llms | `Services/ShieldPolicy.swift` |
| Blocked apps until a chosen time; open again when Ballast next opens | Home, guide, llms | `ShieldPolicy`, `AppShieldSheet` |
| Locks and blocked apps let go if Pro ends; the filter stays | Home, guide, support, comparison, llms | `ShieldPolicy.reconcile` |
| Free and Pro lists | Home, llms, FAQ | `Services/FreeTier.swift`, `FreeTierTests` |
| 30-day course, week one free; skills from CBT and ACT | Home, llms | `Resources/Course/course.json` |
| Heads-up from an hour before the hardest window, free | Home, llms | `Services/HeadsUp.swift` |
| Widgets on the Home Screen and Lock Screen; Panic in Control Centre; "Ballast panic"; Live Activity | Home, llms | `BallastWidget`, `BallastShortcuts.swift` |
| Restore purchase, Back up to a file, Restore from a backup, Export my data: the labels in Settings | Support | `Features/Settings` |
| "Cut the easy access" in Toolkit, under More; seven jobs | Guide, llms | `PlanTabLogic.swift`, `FrictionChecklist.swift` |
| Setup asks how long since the last time | QUITTR page | `OnboardingCopy.lastTimeTitle` |
| `softwareVersion` | JSON-LD, `discovery.json` | Live version |

## History

The site launched on 5 November 2026 describing 1.0.1, moved to the 1.1 app on 8 November, and to Ballast 2 ("Daybreak", 1.4.0) on the `ballast2` branch on 25 November. The prelaunch sources and their switch are gone.
