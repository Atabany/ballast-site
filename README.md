# ballast-site

The public pages for **Ballast**, an iPhone app for quitting porn.

- `privacy.html` — App Store Connect *Privacy Policy URL*
- `support.html` — App Store Connect *Support URL*

These files are **generated**, not hand-edited. The source of the privacy policy is
`docs/PRIVACY_POLICY.md` in the app repo; run `python3 tools/build_site.py <this-dir>` there
and commit the result, so the hosted copy can never drift from the one shipped in the app.

No cookies, no analytics, no external requests.

## Discovery and install links (18 October 2026)

After regenerating policy/support pages, run `python3 _ops/enrich.py`. It restores the verified metadata, App Store badges and campaign links from `_ops/discovery.json` without changing legal body text. Keep app-specific facts in sync with the current listing and app source. Privacy remains authored in the app repository. This project subpath does not control the host-root robots.txt. `llms.txt` is an optional reference, not an AI ranking mechanism.
