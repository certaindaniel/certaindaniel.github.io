#!/usr/bin/env python3
"""Generate the static site from apps.json. Re-run after editing apps.json or adding an app."""
import json
import html
import os
import glob
import urllib.parse

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


def asset_url(path):
    full_path = os.path.join(ROOT, path.lstrip("/"))
    if os.path.exists(full_path):
        mtime = int(os.path.getmtime(full_path))
        return f"/{path.lstrip('/')}?v={mtime}"
    return f"/{path.lstrip('/')}"


def hub_html(locale):
    hub = SITE["hub"][locale]
    cards = []
    for app in APPS:
        loc = app["locales"][locale]
        coming_soon = app.get("comingSoon")
        tag = COMING_SOON_LABEL.get(locale, "Coming Soon") if coming_soon else app["platform"]
        icon_src = asset_url(app['icon'])
        inner = f"""
      <span class="platform-tag">{e(tag)}</span>
      <img class="icon" src="{e(icon_src)}" alt="">
      <h3>{e(loc['name'])}</h3>
      <p>{e(loc['tagline'])}</p>"""
        if app.get("flagship"):
            href = f'/{locale}/{app["id"]}/'
        elif not coming_soon:
            href = app["appStoreUrl"]
        else:
            href = None
        if href:
            soon_cls = " app-card--soon" if coming_soon else ""
            cards.append(f'\n    <a class="app-card{soon_cls}" href="{e(href)}">{inner}\n    </a>')
        else:
            cards.append(f'\n    <div class="app-card app-card--soon">{inner}\n    </div>')
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

# Apple rejects a Support URL that is only a marketing page (Guideline 1.5 — TrailPop
# 1.1 was rejected for exactly this). Every app page carries a real support block with
# a working contact address, so any page can be used as the Support URL.
SUPPORT = {
    "en": {
        "heading": "Support",
        "body": "Questions, bug reports, or feature requests — email us and we will get back to you. Please mention your device model and OS version so we can reproduce the problem.",
        "cta": "Email support",
    },
    "zh-hant": {
        "heading": "支援與聯絡",
        "body": "使用問題、錯誤回報或功能建議，都歡迎寄信給我們，我們會回覆你。請一併說明你的裝置型號與系統版本，方便我們重現問題。",
        "cta": "寄信給支援",
    },
    "zh-hans": {
        "heading": "支持与联系",
        "body": "使用问题、错误报告或功能建议，都欢迎发邮件给我们，我们会回复你。请一并说明你的设备型号与系统版本，方便我们重现问题。",
        "cta": "发邮件给支持",
    },
}


def support_html(app, locale):
    email = SITE.get("supportEmail")
    if not email:
        return ""
    s = SUPPORT.get(locale, SUPPORT["en"])
    subject = urllib.parse.quote(f"{app['locales'][locale]['name']} support")
    return f"""<section class="support" id="support">
    <h2>{e(s['heading'])}</h2>
    <p>{e(s['body'])}</p>
    <p><a class="support-link" href="mailto:{e(email)}?subject={subject}">{e(s['cta'])}: {e(email)}</a></p>
  </section>"""


def app_html(app, locale):
    loc = app["locales"][locale]
    hub = SITE["hub"][locale]
    shot_files = sorted(glob.glob(os.path.join(ROOT, "assets", app["id"], locale, "*.png")))
    shots = "".join(
        f'<img src="{e(asset_url(f"assets/{app["id"]}/{locale}/{os.path.basename(f)}"))}" alt="{e(loc["name"])} screenshot">'
        for f in shot_files
    )
    features = "".join(f"<li>{e(feat)}</li>" for feat in loc["features"])
    qa_items = loc.get("qa") or []
    qa_html = (
        '<div class="qa" id="faq">' + "".join(
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
    has_live_demo = os.path.isfile(os.path.join(ROOT, app["id"], "live", "index.html")) or app.get("liveDemoUrl")
    live_demo_link = ""
    if has_live_demo:
        demo_url = app.get("liveDemoUrl") or f"/{app['id']}/live/"
        demo_labels = {
            "en": "Try Web Demo",
            "zh-hant": "在線試玩魚缸",
            "zh-hans": "在线试玩鱼缸"
        }
        demo_label = demo_labels.get(locale, demo_labels["en"])
        live_demo_link = f'\n      <a class="cta cta--secondary" href="{e(demo_url)}">{e(demo_label)} ↗</a>'

    # 玩法攻略手冊：產生頁原本完全連不到它，使用者只能從官網首頁繞過去。
    guide_link = ""
    if app.get("guideUrl"):
        guide_labels = {
            "en": "Player Guide",
            "zh-hant": "玩法攻略",
            "zh-hans": "玩法攻略",
        }
        guide_link = f'\n      <a class="cta cta--secondary" href="{e(app["guideUrl"])}">{e(guide_labels.get(locale, guide_labels["en"]))} ↗</a>'

    cta = (
        f'<a class="cta" href="{e(app["appStoreUrl"])}">{e(loc["cta"])}</a>'
        if app.get("appStoreUrl") and not app.get("comingSoon") else
        f'<span class="cta cta--disabled">{e(loc["cta"])}</span>'
    )

    icon_src = asset_url(app['icon'])

    body = f"""<div class="wrap">
  {lang_switch(locale, app_id=app['id'])}
  <section class="hero">
    <img class="icon" src="{e(icon_src)}" alt="">
    <h1>{e(loc['name'])}</h1>
    <p class="tagline">{e(loc['tagline'])}</p>
    <p class="promo">{e(loc['promo'])}</p>
    <div class="hero-actions">
      {cta}{live_demo_link}{guide_link}
    </div>
    {privacy_link}
  </section>
  <div class="screenshots">{shots}</div>
  <ul class="features">{features}</ul>
  {qa_html}
  {support_html(app, locale)}
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
