# certaindaniel.github.io

Static landing page hub for Daniel Lu's apps. Data-driven — `apps.json` is the
single source of truth, `generate.py` renders it to static HTML committed into
this repo (no build step on GitHub Pages).

## Generate the site

Install the image dependency once with `python3 -m pip install -r requirements.txt`,
then run `python3 generate.py`. The generator keeps the original PNG icons and
creates WebP copies at 112px for Hub cards and 192px for app-page icons (2× their
display size). Hub cards below the first row use native lazy loading.
Commit the generated HTML and WebP files together so GitHub Pages can serve them.

## TinyAquarium website assets

The handwritten homepage and Fish Vault use prebuilt Tailwind CSS instead of
compiling styles in the browser. After changing their classes, run
`sh tools/build_tinyaquarium_css.sh` (Node.js/npm required) and commit
`tinyaquarium/assets/site.css` with the HTML. Font CSS loads without blocking the
initial render. The homepage starts its UI at DOM ready and pauses the interactive
tank while it is offscreen or the tab is hidden.

To rebuild the localized codex screenshots, favicon, and Apple touch icon, run
`python3 tools/optimize_tinyaquarium_images.py /path/to/TinyAquarium/screenshots`.
English uses `en-US/02.png`, Traditional Chinese uses `raw/zh-Hant/02_dex.png`,
and Simplified Chinese uses `zh-Hans/02.png`. Screenshots are served as WebP at up
to 760px wide; URL language, saved language, and in-page switches select the same
language for both the text and the image.

## Add a new app

1. Add an entry to `apps.json` under `apps` (icon path, App Store URL, per-locale
   name/tagline/features, screenshots). Set `"flagship": true` to get a full
   landing page (`/{locale}/{id}/`); omit it to only show a Hub card that links
   straight to the App Store.
2. Drop the icon + localized marketing screenshots under `assets/{id}/`.
3. Run `python3 generate.py` and commit the generated HTML.

## Locales

`en`, `zh-hant`, `zh-hans` — configured in `apps.json` → `site.locales`.
