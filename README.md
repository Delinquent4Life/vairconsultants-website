# vairconsultants.com

Website of V.A.I.R Consultants B.V., Philipsburg, Sint Maarten.

Published automatically by Netlify whenever this repository changes.

- `index.html` — the whole site (pages, text, news posts, styles)
- `logo.png` — logo, also used in email signatures (https://vairconsultants.com/logo.png)

Last published by Claude: 2026-09-27

## Pages and addresses (Oct 2026)
Each page has its own address (e.g. /work-residence-permits-sint-maarten/) for search engines.
`index.html` is the source and the home page. After any change to it or to `routes.json`, run
`python3 build.py`, which regenerates the per-page folders, news post pages, sitemap.xml and robots.txt.
Commit the generated files too. Future-dated news posts get their own page on the first build after their date.
