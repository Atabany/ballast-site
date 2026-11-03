# Publish checklist. For the owner's go-ahead only.

Nothing here has been done. `rebuild/next` is local and unpushed. `main` and the live site are
unchanged, no DNS or console has been touched and nothing has been posted. Every step below is
public or irreversible enough to need your approval.

Order matters: **the App Store update comes first.** The site describes Ballast 1.1, which isn't
released. On 2026-11-04 the App Store listing is version 1.0.1, with no filter, no Shield and no
Voyage.

## 1. Before anything goes live

- [ ] Ballast 1.1 is approved and **live** on the App Store. Confirm: `curl -s "https://itunes.apple.com/lookup?id=6803731313&country=us" | python3 -c "import json,sys;r=json.load(sys.stdin)['results'][0];print(r['version'],r['userRatingCount'],r['trackName'])"`
- [ ] The real Shield path has been run on a device. It can't be tested on a simulator, so `FamilyControlsShield` is unverified until then.
- [ ] Every entry in **"Claims that wait for the App Store update"** below is true of the shipped build.
- [ ] Rating count re-read from that command. If there are ratings: the comparison's "No ratings yet" and the about page's and `llms-product.md`'s lines must change. The site still shows no stars; add a rating with its count only as the checklist describes, and only if real.
- [ ] `QUITTR_RECHECK.md` completed on the day. If it can't be, delete that page's source and links for now and publish the rest.
- [ ] `SCREENSHOTS_NEEDED.md` slots filled with real captures, or accept the abstract panels for launch.
- [ ] Privacy policy source in the app repo matches: `docs/PRIVACY_POLICY.md` in `quitPorn-next` still lacks the Shield section. Copy the same wording there so app, tests and site agree. `LegalTests` scans that file.
- [ ] **Retire `tools/build_site.py` in the app repo.** It overwrites `index.html`, `privacy.html`, `support.html`, `robots.txt`, `sitemap.xml` and `llms.txt`, and its old copy would undo this site. Site source is now `_ops/content/` here.
- [ ] Update `docs/kb/website.md` in the app repo: its guide note says Ballast has no filter, and that the generator owns these files.
- [ ] Copy read by you, especially `about.html` (it says you're not a clinician, no clinician reviewed the site, and that AI tools help with research, drafting and building) and the first-person statements on the comparison and QUITTR pages. They're written in your voice. Edit anything you wouldn't sign.
- [ ] Age rating: `privacy.html` says 16+, from the app docs. Apple's iTunes lookup reported `17+` on 2026-11-04, which may just be how that API maps the rating. Confirm in App Store Connect.
- [ ] Optional but recommended: a qualified clinician reads `how-to-stop-watching-porn.html` and `what-to-do-after-a-slip.html`. Then the about page's sentence changes.

## 2. Merge and publish on github.io

```sh
cd ~/indie/ballast-site-next
python3 _ops/build.py --og && python3 _ops/validate.py    # must print OK
git grep -nE '^(<<<<<<<|>>>>>>>)( |$)'                    # must print nothing
git push origin rebuild/next
cd ~/indie/ballast-site && git pull --ff-only && git merge --ff-only rebuild/next && git push origin main
```

GitHub Pages serves `main`. Then check:

- [ ] `curl -sI https://atabany.github.io/ballast-site/privacy.html` and `support.html`, the guide and the home page return 200. The app and App Store Connect link to the first two.
- [ ] `https://atabany.github.io/ballast-site/does-not-exist` shows the styled 404.
- [ ] Open the home page on a real iPhone: Smart App Banner, badge, and an App Store link that opens the right listing.
- [ ] Share the home URL to yourself to see the Open Graph image.

## 3. Domain (optional; you choose, you pay)

Follow `DOMAIN_MOVE.md`. Summary: buy on Cloudflare Registrar, set DNS only (4 x A 185.199.108-111.153, 4 x AAAA 2606:50c0:8000-8003::153, `www` CNAME `atabany.github.io`), change `SITE_URL`, rebuild, validate, add `CNAME`, merge, enforce HTTPS with `gh api -X PUT repos/Atabany/ballast-site/pages -F https_enforced=true` once the certificate is approved, and test each 301.

## 4. Consoles

These work properly only with your own domain.

- [ ] Google Search Console: Domain property `sc-domain:<domain>`, verified by DNS TXT ("Any DNS provider"; never authorise Google into Cloudflare). Submit `https://<domain>/sitemap.xml`. Inspect the home page and each page, then Request indexing. "Couldn't fetch" on day one is normal.
- [ ] Bing Webmaster: add `https://<domain>/`, verify with `BingSiteAuth.xml` at the root (don't use "import from Google"), submit the sitemap.
- [ ] Without a domain, a URL-prefix property for the github.io path is possible with an HTML file. It would need redoing after a move.

## 5. IndexNow (only with your own domain)

```sh
python3 _ops/indexnow.py init        # creates <key>.txt at the root; commit and push it
python3 _ops/indexnow.py all         # after the key file is live
```
It refuses to run on github.io, because the key must be at the host root.

## 6. App Store Connect, next editable version

- [ ] Marketing URL to home. Support URL to `/support.html`. Privacy Policy URL to `/privacy.html`, in every locale. These are locked while a version is live or in review.
- [ ] `Services/Legal.swift`: update URLs for the next build if the domain changed. Old builds keep working through the redirects.
- [ ] App privacy label: re-read it against this policy once Family Controls ships. App Review may ask how the entitlement's data is handled; the policy's Shield section is the answer.

## 7. Afterwards

- [ ] Dated baseline first: App Store impressions, page views, downloads, web referrers. Baseline in `docs/REBUILD.md`: Aug 5 to Nov 2, 2026, 366 impressions, 38 page views, 11 downloads. Note 1.1 itself as a confounder.
- [ ] Campaign results appear in App Analytics once they pass Apple's thresholds. An empty report doesn't mean zero traffic. `ballast_index`, `ballast_support`, `ballast_privacy` and `ballast-guide-block-porn` are existing tags kept for continuity.
- [ ] Off-site (Reddit answers, list-author outreach, video): drafted for your review; you post.
- [ ] Weekly content routine and growth review: not set up. Set them up only once you've approved publishing.

## Claims that wait for the App Store update

All of these are true of the spec in `docs/REBUILD.md`, not of the live 1.0.1. None is verified on a shipped build.

| Claim | Where | Check in the shipped build |
|---|---|---|
| One-tap adult-website filter, free; disables Safari private browsing | Home, guide, support, privacy, comparison, FAQ, llms, fact block | Shield tab, on a device |
| Commitment lock: cool-off 10 min, 1 h, 24 h; trusted-person code; 24-hour wait always works; salted hash only | Home, guide, support, privacy, comparison | Pro on a device, including the 24-hour path |
| App shields until a chosen time; lift when Ballast next opens | Home, guide, privacy | Pro on a device |
| Locks release if Pro ends; filter stays yours | Home, guide, support, comparison | Let a sandbox subscription lapse |
| Tabs named **Shield** and **Plan**; friction checklist under Plan's tools | Guide, support | Actual labels |
| Urge flow: tap what's happening, own card and reason, breathe, ride the wave, or plan | Home, guide, tool page | Actual flow |
| One plan free; unlimited with Pro; free/Pro table | Home, comparison, llms | `Services/FreeTier.swift`; `FreeTierTests` |
| Clear days never reset; waypoints 1, 3, 7, 14, 30, 60, 100, 180, 365; slips as ordinary marks | Home, slip page, comparison, llms | Voyage tab |
| Backup and restore through a file, free; Shield settings stay out of the backup | Home, support, privacy, comparison | Round trip on a device |
| A finished wait opens a 15-minute window | Support | `ShieldPolicy.releaseWindow` |
| After-slip "next hour" support and the day-after card; no offers at that moment | Slip page | Log a slip |
| Setup asks how long since the last time | QUITTR page | Onboarding |
| `softwareVersion` 1.1.0 | JSON-LD, `discovery.json` | Set to the live version |

**Could go live before the update**, if you wanted, after removing or rewording their Ballast sections and calls to action: `how-to-stop-watching-porn.html`, `if-then-urge-plan.html`, `what-to-do-after-a-slip.html`, the QUITTR page. The current guide's statement that Ballast has no filter stays true until 1.1 ships, so `block-porn-iphone-screen-time.html` should only change with the release.
