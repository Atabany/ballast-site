# ballast-site

The public pages for **Ballast**, an iPhone app for quitting porn.

- `privacy.html` — App Store Connect *Privacy Policy URL*
- `support.html` — App Store Connect *Support URL*

These files are **generated**, not hand-edited. The source of the privacy policy is
`docs/PRIVACY_POLICY.md` in the app repo; run `python3 tools/build_site.py <this-dir>` there
and commit the result, so the hosted copy can never drift from the one shipped in the app.

No cookies, no analytics, no external requests.
