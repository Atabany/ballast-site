# Publish checklist

Two stages. `RELEASE_STATE` in `_ops/discovery.json` is the one switch between them.

- **`prelaunch`** (until 8 November 2026): the site said only what was true of Ballast 1.0.1.
- **`live`** (now): the full 1.1 site. Ballast 1.1.0 went live on 7 November 2026, the site flipped on 8 November (`379cb32`), and the prelaunch sources, `prelaunch_edits.py`, the `prelaunch` block and `test_states.py` were removed. The stage 1 commands that use them no longer apply.

Every step below is public or hard to undo, so each needs the owner's or the coordinator's go-ahead.

## Stage 1: prelaunch (history)

Status on 2026-11-05: built and validated on branch `prelaunch`. Nothing pushed, and no DNS or GitHub setting changed.

### Check before pushing

```sh
cd ~/indie/bs-pre
python3 _ops/build.py --og && python3 _ops/validate.py --both   # both must print OK
python3 _ops/test_states.py rebuild/next                        # must print OK
git grep -nE '^(<<<<<<<|>>>>>>>)( |$)'                          # must print nothing
```

- [ ] `QUITTR_RECHECK.md` was done within the last day. If it can't be redone, pull that page and its links rather than publish stale facts.
- [ ] `curl -s "https://itunes.apple.com/lookup?id=6803731313&country=us"` still shows version 1.0.1. If 1.1.0 is live, go to stage 2.
- [ ] The owner has read `about.html` and the first-person statements on the comparison and QUITTR pages. They're written in his voice.

### Connect the domain, in this order

**DNS comes first.** Once Pages has a custom domain, `atabany.github.io/ballast-site/*` redirects to `quitpmo.com`. That address is the Privacy Policy and Support URL of the live app. If `quitpmo.com` doesn't resolve at that moment, those URLs break for users and for App Review.

1. [ ] **Owner login, Cloudflare:** add the records in `DOMAIN_MOVE.md`, all DNS only. Check with `dig +short quitpmo.com` and `dig +short www.quitpmo.com`.
2. [ ] Push. Pages serves `main` from the repo root, and `main` is an ancestor of `prelaunch`, so a fast-forward works:
   ```sh
   git -C ~/indie/bs-pre push origin prelaunch:main
   ```
3. [ ] Confirm the custom domain was picked up, or set it: `gh api -X PUT repos/Atabany/ballast-site/pages -f cname=quitpmo.com`.
4. [ ] Enforce HTTPS once the certificate is approved: `gh api -X PUT repos/Atabany/ballast-site/pages -F https_enforced=true`. If the certificate sticks, remove and re-add the custom domain.

### Check after pushing

- [ ] `https://quitpmo.com/`, `/privacy.html`, `/support.html` and the guides return 200 over HTTPS.
- [ ] `https://quitpmo.com/_ops/discovery.json` and `/README.md` return 404.
- [ ] `https://quitpmo.com/does-not-exist` shows the styled 404.
- [ ] Each old URL returns a 301 to the same path on `quitpmo.com`. The test is in `DOMAIN_MOVE.md`.
- [ ] Open the home page on a real iPhone: Smart App Banner, badge, and a link that opens the right listing. Share the URL to yourself to see the Open Graph image.

### Search engines and assistants

These need a login, so the site carries no verification tokens.

- [ ] **Owner login, Google Search Console:** Domain property `sc-domain:quitpmo.com`, verified with a DNS TXT record ("Any DNS provider"; don't authorise Google into Cloudflare). Submit `https://quitpmo.com/sitemap.xml`. Inspect the home page and each guide, then Request indexing. "Couldn't fetch" on day one is normal.
- [ ] **Owner login, Bing Webmaster:** add `https://quitpmo.com/`, download `BingSiteAuth.xml`, put it at the repo root, build, push and verify. Don't use "import from Google". Submit the sitemap.
- [ ] IndexNow: the key file `16bdd4cc417b5f9865b1f568f9965089.txt` is already at the root. After the site is live over HTTPS, run `python3 _ops/indexnow.py all`. No ping has been sent.
- [ ] `robots.txt` allows AI crawlers and is authoritative at the domain root. `llms.txt` and `llms-full.txt` are at the root.

### Next editable version in App Store Connect

**Owner login.** These are locked while a version is in review, and redirects cover the gap.

- [ ] Marketing URL to `https://quitpmo.com/`, Support URL to `/support.html`, Privacy Policy URL to `/privacy.html`, in every locale.
- [ ] Retire `tools/build_site.py` in the app repo. It overwrites this site's files with old copy.

### Known gaps in the live app to fix in 1.1

- The in-app privacy text in 1.0.1 (`Services/Legal.swift` on `main`) says the export is "a complete JSON file of everything Ballast holds". The export leaves out plans, course progress, steps, weekly reviews and the picture. This site states what the export really contains. The `quitPorn-next` policy already has the correct wording.
- `quitPorn-next/docs/PRIVACY_POLICY.md` doesn't mention **Sites you add** yet. The site's 1.1 section does, using the wording on `rebuild/next`. Bring the app's policy and `Services/Legal.swift` in line before submitting 1.1.

## Stage 2: the day 1.1.0 is live

Done on 8 November 2026, apart from the items marked open. Do these only once the App Store shows it: `curl -s "https://itunes.apple.com/lookup?id=6803731313&country=us" | python3 -c "import json,sys;r=json.load(sys.stdin)['results'][0];print(r['version'],r['userRatingCount'],r['trackName'])"`.

### Before flipping

- [x] The real Shield path has been run on a device: the owner confirmed on an iPhone (2026-11-05) that the one-tap filter and an added site work. The commitment lock, its 24-hour path, app shields, a Pro lapse and a backup round trip have been checked in the v1.1.0 code only, not on a device.
- [x] **Reshoot Shield from a real device.** The mock shot was deleted on 8 November, so the slot shows the abstract panel. Add a real-device capture whenever there is one.
- [x] Every other shot in `SCREENSHOTS_NEEDED.md` still matches the shipped build. Replace any that don't in `_ops/live/assets/screens/`.
- [x] `_ops/live/assets/` holds the icon that shipped (byte-identical to the v1.1.0 `AppIcon-1024.png`; matches the App Store artwork). If it isn't what's on the App Store, regenerate the icon files there.
- [x] Every row in **Claims that wait for the App Store update** below is true of the shipped build's code.
- [x] Rating count re-read: 0 on 8 November 2026. If there are ratings, the comparison's "No ratings yet", the about page and `llms-product.md` must change. The site still shows no stars unless the count and rating are real.
- [x] `QUITTR_RECHECK.md` done again that day. Update `_ops/content/quittr-left-the-app-store.html`.
- [x] Privacy text in `_ops/content/privacy.html` still matches `docs/PRIVACY_POLICY.md` and `Services/Legal.swift` in the app repo.

### Flip

```sh
# 1. In _ops/discovery.json set "RELEASE_STATE": "live", and update factsChecked
python3 _ops/build.py --og      # regenerates Open Graph images with the new icon
python3 _ops/validate.py        # must print OK
git grep -nE '^(<<<<<<<|>>>>>>>)( |$)'
git add -A && git commit        # then push to main
python3 _ops/indexnow.py all    # after the new pages are live
```

The flip swaps icons and screenshots by itself: `build.py` installs `_ops/live/assets` into `assets/` and removes the prelaunch set.

### After flipping

- [ ] App Store Connect, in the next version: confirm the listing's Marketing, Support and Privacy Policy URLs are on `quitpmo.com`, and remove any `atabany.github.io` URL from the description. `Services/Legal.swift` also moves to the new URLs for the next build. Old builds keep working through the redirects.
- [ ] Re-read the App Privacy label against the policy, now Family Controls has shipped.
- [ ] Update `docs/kb/website.md` in the app repo.
- [x] Clean up: delete `_ops/prelaunch/`, `_ops/prelaunch_edits.py` and the `prelaunch` block in `discovery.json`. In `_ops/content/privacy.html`, the note about earlier versions stays.
- [ ] Dated baseline: App Store impressions, page views, downloads, web referrers. Baseline in `docs/REBUILD.md`: Aug 5 to Nov 2, 2026, 366 impressions, 38 page views, 11 downloads. Note 1.1 as a confounder.
- [ ] Off-site (Reddit answers, list-author outreach, video): drafted for review; the owner posts. Weekly content routine and growth review: set up only once approved.
- [ ] Optional: a qualified clinician reads `how-to-stop-watching-porn.html` and `what-to-do-after-a-slip.html`. Then the about page's sentence changes.

## Claims that wait for the App Store update

Checked on 8 November 2026 against the v1.1.0 source in `quitPorn-next` (tag `v1.1.0`): none is contradicted. On a device, only the filter and an added site have been seen working (owner, 2026-11-05).

| Claim | Where (live state) | Check in the shipped build |
|---|---|---|
| One-tap adult-website filter, free; disables Safari private browsing | Home, guide, support, privacy, comparison, FAQ, llms, fact block | Shield tab, on a device |
| Sites you add: 3 free, up to 25 with Pro; stay on the phone; out of backups | Home, guide, support, privacy, comparison, llms | Shield tab, on a device |
| Commitment lock: cool-off 10 min, 1 h, 24 h; trusted-person code; 24-hour wait always works; salted hash only | Home, guide, support, privacy, comparison | Pro on a device, including the 24-hour path |
| App shields until a chosen time; lift when Ballast next opens | Home, guide, privacy | Pro on a device |
| Locks release if Pro ends; filter stays yours | Home, guide, support, comparison | Let a sandbox subscription lapse |
| Tabs named **Shield** and **Plan**; friction checklist under Plan's tools | Guide, support | Actual labels |
| Urge flow: tap what's happening, own card and reason, breathe, ride the wave, or plan | Home, guide, tool page | Actual flow |
| One plan free; unlimited with Pro; free/Pro table | Home, comparison, llms | `Services/FreeTier.swift`; `FreeTierTests` |
| Clear days never reset; waypoints 1, 3, 7, 14, 30, 60, 100, 180, 365; slips as ordinary marks | Home, slip page, comparison, llms | Voyage tab |
| Backup and restore through a file, free; Shield settings stay out of the backup | Home, support, privacy, comparison | Round trip on a device |
| A finished wait opens a 15-minute window | Support | `ShieldPolicy.releaseWindow` |
| Setup asks how long since the last time | QUITTR page | Onboarding |
| Privacy page: RevenueCat asked at each launch and foreground; export leaves out plans, course answers, steps, reviews and the picture | Privacy, support, llms | `Store.refresh`, `DataExport`, same wording as `docs/PRIVACY_POLICY.md` |
| `softwareVersion` 1.1.0 | JSON-LD, `discovery.json` | Set to the live version |
