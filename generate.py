#!/usr/bin/env python3
"""Generate the static site from apps.json. Re-run after editing apps.json or adding an app."""
import json
import html
import os
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "apps.json"), encoding="utf-8") as f:
    data = json.load(f)

SITE = data["site"]
LOCALES = SITE["locales"]
APPS = data["apps"]


def e(s):
    return html.escape(s, quote=True)


def lang_switch(locale, app_id=None):
    links = []
    for loc in LOCALES:
        cls = ' class="current"' if loc == locale else ""
        href = f"/{loc}/{app_id}/" if app_id else f"/{loc}/"
        links.append(f'<a href="{href}"{cls}>{e(SITE["localeLabels"][loc])}</a>')
    return '<nav class="lang-switch">' + "".join(links) + "</nav>"


def page(title, body, locale):
    return f"""<!doctype html>
<html lang="{locale}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<link rel="stylesheet" href="/style.css">
</head>
<body>
{body}
</body>
</html>
"""


COMING_SOON_LABEL = {"en": "Coming Soon", "zh-hant": "即將推出", "zh-hans": "即将推出"}


def hub_html(locale):
    hub = SITE["hub"][locale]
    cards = []
    for app in APPS:
        loc = app["locales"][locale]
        coming_soon = app.get("comingSoon")
        tag = COMING_SOON_LABEL.get(locale, "Coming Soon") if coming_soon else app["platform"]
        inner = f"""
      <span class="platform-tag">{e(tag)}</span>
      <img class="icon" src="/{e(app['icon'])}" alt="">
      <h3>{e(loc['name'])}</h3>
      <p>{e(loc['tagline'])}</p>"""
        if coming_soon:
            cards.append(f'\n    <div class="app-card app-card--soon">{inner}\n    </div>')
        else:
            href = f'/{locale}/{app["id"]}/' if app.get("flagship") else app["appStoreUrl"]
            cards.append(f'\n    <a class="app-card" href="{e(href)}">{inner}\n    </a>')
    body = f"""<div class="wrap">
  <header class="site">
    <h1>{e(hub['title'])}</h1>
    <p>{e(hub['subtitle'])}</p>
    {lang_switch(locale)}
  </header>
  <div class="app-grid">{"".join(cards)}
  </div>
  <footer class="site">© {e(SITE['owner'])} · <a href="https://github.com/{e(SITE['githubUser'])}">GitHub</a></footer>
</div>"""
    return page(hub["title"], body, locale)


PRIVACY_LABEL = {
    "en": "Privacy Policy", "zh-hant": "隱私權政策", "zh-hans": "隐私政策",
}


def app_html(app, locale):
    loc = app["locales"][locale]
    hub = SITE["hub"][locale]
    shot_files = sorted(glob.glob(os.path.join(ROOT, "assets", app["id"], locale, "*.png")))
    shots = "".join(
        f'<img src="/assets/{app["id"]}/{locale}/{e(os.path.basename(f))}" alt="{e(loc["name"])} screenshot">'
        for f in shot_files
    )
    features = "".join(f"<li>{e(feat)}</li>" for feat in loc["features"])
    qa_items = loc.get("qa") or []
    qa_html = (
        '<div class="qa">' + "".join(
            f'<div class="qa-item"><h3>{e(item["q"])}</h3><p>{e(item["a"])}</p></div>'
            for item in qa_items
        ) + "</div>"
        if qa_items else ""
    )
    # Privacy page discovered by convention (like screenshots) rather than listed in
    # apps.json, so the link can never drift out of sync with what's actually on disk.
    privacy_href = f"/{locale}/{app['id']}/privacy/"
    has_privacy = os.path.isfile(os.path.join(ROOT, locale, app["id"], "privacy", "index.html"))
    privacy_link = (
        f'<a class="legal-link" href="{e(privacy_href)}">{e(PRIVACY_LABEL.get(locale, "Privacy Policy"))}</a>'
        if has_privacy else ""
    )
    body = f"""<div class="wrap">
  {lang_switch(locale, app_id=app['id'])}
  <section class="hero">
    <img class="icon" src="/{e(app['icon'])}" alt="">
    <h1>{e(loc['name'])}</h1>
    <p class="tagline">{e(loc['tagline'])}</p>
    <p class="promo">{e(loc['promo'])}</p>
    <a class="cta" href="{e(app['appStoreUrl'])}">{e(loc['cta'])}</a>
    {privacy_link}
  </section>
  <div class="screenshots">{shots}</div>
  <ul class="features">{features}</ul>
  {qa_html}
  <a class="back-link" href="/{locale}/">← {e(hub['title'])}</a>
</div>"""
    return page(f"{loc['name']} — {loc['tagline']}", body, locale)


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


for locale in LOCALES:
    hub_content = hub_html(locale)
    write(f"{locale}/index.html", hub_content)
    if locale == SITE["defaultLocale"]:
        write("index.html", hub_content)
    for app in APPS:
        if app.get("flagship"):
            write(f"{locale}/{app['id']}/index.html", app_html(app, locale))

print(f"Generated {len(LOCALES)} hub(s) + {sum(1 for a in APPS if a.get('flagship')) * len(LOCALES)} app page(s).")
