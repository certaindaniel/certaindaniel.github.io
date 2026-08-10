# certaindaniel.github.io

Static landing page hub for Daniel Lu's apps. Data-driven — `apps.json` is the
single source of truth, `generate.py` renders it to static HTML committed into
this repo (no build step on GitHub Pages).

## Add a new app

1. Add an entry to `apps.json` under `apps` (icon path, App Store URL, per-locale
   name/tagline/features, screenshots). Set `"flagship": true` to get a full
   landing page (`/{locale}/{id}/`); omit it to only show a Hub card that links
   straight to the App Store.
2. Drop the icon + localized marketing screenshots under `assets/{id}/`.
3. Run `python3 generate.py` and commit the generated HTML.

## Locales

`en`, `zh-hant`, `zh-hans` — configured in `apps.json` → `site.locales`.
