# Recheck the QUITTR page on publish day

`quittr-left-the-app-store.html` makes dated claims about a real company. **Before publishing, and
at each later edit, recheck everything below and update the date.** If it can't be rechecked, hold
the page back and publish the rest.

Rules: the cause is stated as unknown. Make no accusation. Attribute every claim. Keep the conflict
of interest at the top. Do not imply a link between the 404 Media reporting and the listing.

## Last recheck: 5 November 2026

| Item | Result |
|---|---|
| Lookup and listing, six storefronts | `resultCount` 0 and HTTP 404 in US, GB, CA, AU, DE, AE |
| quittrapp.com | Online. Home and support pages carry no statement about the listing, and the home page still links to the App Store listings and a Google Play page |
| News | Google News RSS for "QUITTR app App Store removed" and "Quittr" over 45 days: no coverage of the listing going away |
| Social accounts | **Not read.** They need a login or block automated reading, and the page says so |
| 404 Media, March and April 2026 | Both still up. Public parts match the page's summary. **The paid parts are still unread**, and the page says only the public part was read. Someone with a membership should read the rest |
| AppsHunter | **Couldn't be confirmed:** its bot wall returned 403, including to headless Chrome. Row removed |
| AppGoblin | Read directly: "This app was removed from the US App Store and is no longer live", last crawled 2026-11-01. Row added, and the page notes it doesn't say who removed it or why |
| Pledgely | Read directly, updated 30 October. Its status note matches the page |
| Apple cancel and refund guides | Steps still match |
| Google Play help | Resolves. It says that when an app is removed from Google Play "your future subscription will be cancelled". The page links to the help article and doesn't quote this |

Also changed: several sentences tracked Pledgely's wording closely, so they're rewritten in the page's own words. It's a competitor's text, and the page already credits it as a source.

## Commands

```sh
# Listing: resultCount 0 and HTTP 404 mean still gone. Any result means update or pull the page.
for c in us gb ca au de ae; do
  printf "$c "; curl -s -o /dev/null -w '%{http_code} ' "https://apps.apple.com/$c/app/id6532588521"
  curl -s "https://itunes.apple.com/lookup?id=6532588521&country=$c" | python3 -c "import json,sys;print(json.load(sys.stdin)['resultCount'])"
done
```

## Checklist

1. Listing state in all six storefronts (above). If it has returned, rewrite the page or pull it.
2. Any statement from QUITTR or Apple: check https://quittrapp.com, its support page, its social accounts and news search. If there is a stated cause, say who stated it and quote it. The FAQ answer and the "what isn't known" section will need to change.
3. 404 Media's March and April 2026 reports: are they still up, corrected or updated? Only the public parts were read on 2026-11-04. Someone with a membership should read the rest before publication, because the page summarises them.
4. Third-party rows: reread Pledgely and AppGoblin. Add a row only for a page you actually read.
5. Apple's cancel and refund steps at https://support.apple.com/en-us/118428 and https://support.apple.com/en-us/118223 still match.
6. Google Play help link still resolves and says what the page implies.
7. Update `updated` in `_ops/content/quittr-left-the-app-store.html`, the "Facts checked" line and the table's last row. Rebuild and validate.

## Claims not used

The research memo notes SEVER (a competitor) saying the app was live 10-24 and gone by 10-31. That page wasn't re-read, so it isn't on the page. AppsHunter's "last seen 26 Oct 2026" couldn't be read either. Add them with links only if they can be read and add something.

Wet Ink's coverage came up in search and isn't linked: 404 Media is the primary source, and that outlet isn't suitable for an age-appropriate page.
