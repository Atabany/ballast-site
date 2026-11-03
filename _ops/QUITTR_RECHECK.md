# Recheck the QUITTR page on publish day

`quittr-left-the-app-store.html` makes dated claims about a real company. **Before publishing, and
at each later edit, recheck everything below and update the date.** If it can't be rechecked, hold
the page back and publish the rest.

Rules: the cause is stated as unknown. Make no accusation. Attribute every claim. Keep the conflict
of interest at the top. Do not imply a link between the 404 Media reporting and the listing.

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
4. Third-party rows: AppsHunter "last seen 26 Oct 2026" was read from a search-result excerpt, not the rendered page. Open it in a browser and confirm. Pledgely's 30 October note was read directly.
5. Apple's cancel and refund steps at https://support.apple.com/en-us/118428 and https://support.apple.com/en-us/118223 still match.
6. Google Play help link still resolves and says what the page implies.
7. Update `updated` in `_ops/content/quittr-left-the-app-store.html`, the "Facts checked" line and the table's last row. Rebuild and validate.

## Claims not used

The research memo notes SEVER (a competitor) saying the app was live 10-24 and gone by 10-31, and AppGoblin reporting removal. Neither source page could be re-read on 2026-11-04, so neither is on the page. Add them with links only if they can be read and add something.

Wet Ink's coverage came up in search and isn't linked: 404 Media is the primary source, and that outlet isn't suitable for an age-appropriate page.
