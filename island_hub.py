"""Render the localized app archipelago from the site's app catalog."""
import html
import re


def esc(value):
    return html.escape(str(value), quote=True)


UI = {
    "en": {
        "eyebrow": "A LITTLE WORLD OF APPS", "headline": "One island.<br>One app.",
        "explore": "Explore the islands", "count": "islands", "filter": "Explore by type",
        "all": "All", "game": "Games", "tool": "Tools", "list": "Island index",
        "close": "Close", "visit": "Explore this app", "map_label": "App archipelago",
        "groups": {
            "game": ("01 / PLAY & UNWIND", "Games & cozy escapes", "Little worlds to play in and unwind."),
            "reading": ("02 / READING & SOUND", "Reading & sound", "Stories, books and voices close together."),
            "creative": ("03 / CREATE & CAPTURE", "Create & capture", "Ideas, pictures and journeys take shape here."),
            "utility": ("04 / EVERYDAY TOOLS", "Everyday & developer tools", "Useful companions for work and making things."),
        },
    },
    "zh-hant": {
        "eyebrow": "WELCOME TO THE APP ARCHIPELAGO", "headline": "一座島，<br>一個 App。",
        "explore": "開始探索", "count": "座島", "filter": "依類型探索",
        "all": "全部", "game": "遊戲", "tool": "工具", "list": "島嶼清單",
        "close": "關閉", "visit": "前往 App 介紹", "map_label": "App 群島地圖",
        "groups": {
            "game": ("01 / PLAY & UNWIND", "遊戲與療癒", "來這裡走走，玩一下、放鬆一下。"),
            "reading": ("02 / READING & SOUND", "閱讀與聲音", "書、故事與聲音，在這片海域相遇。"),
            "creative": ("03 / CREATE & CAPTURE", "影像與創作", "記錄風景、整理靈感，讓想法成形。"),
            "utility": ("04 / EVERYDAY TOOLS", "日常與開發工具", "為工作與開發準備的實用小幫手。"),
        },
    },
    "zh-hans": {
        "eyebrow": "WELCOME TO THE APP ARCHIPELAGO", "headline": "一座岛，<br>一个 App。",
        "explore": "开始探索", "count": "座岛", "filter": "按类型探索",
        "all": "全部", "game": "游戏", "tool": "工具", "list": "岛屿清单",
        "close": "关闭", "visit": "前往 App 介绍", "map_label": "App 群岛地图",
        "groups": {
            "game": ("01 / PLAY & UNWIND", "游戏与治愈", "来这里走走，玩一下、放松一下。"),
            "reading": ("02 / READING & SOUND", "阅读与声音", "书、故事与声音，在这片海域相遇。"),
            "creative": ("03 / CREATE & CAPTURE", "影像与创作", "记录风景、整理灵感，让想法成形。"),
            "utility": ("04 / EVERYDAY TOOLS", "日常与开发工具", "为工作与开发准备的实用小帮手。"),
        },
    },
}

# Each scene is a small landmark. The app's own accent colors its landscape.
SCENES = {
    "aquarium": '''<ellipse cx="120" cy="103" rx="58" ry="19" fill="#a9e2dc"/><ellipse cx="120" cy="100" rx="48" ry="13" fill="var(--accent)" opacity=".55"/><path d="M91 99q8-8 16 0-8 8-16 0l-6-5v10Zm39 5q7-7 14 0-7 7-14 0l-6-4v8Z" fill="#f5a07b"/><path d="M91 80V62a29 29 0 0 1 58 0v18" fill="#fdf9e9" stroke="#709b8d" stroke-width="2"/><path d="M91 62a29 29 0 0 1 58 0Z" fill="var(--accent)" opacity=".75"/><path d="M62 104V83m0 12-9-10m9 15 8-10m98 15V84m0 12-8-10m8 14 8-10" stroke="#db8c70" stroke-width="4" stroke-linecap="round"/>''',
    "fruit": '''<path d="M105 105V61" stroke="#987055" stroke-width="8" stroke-linecap="round"/><circle cx="105" cy="60" r="27" fill="#6ba67e"/><circle cx="83" cy="68" r="19" fill="#83ba88"/><circle cx="127" cy="67" r="20" fill="#86b987"/><circle cx="91" cy="58" r="8" fill="var(--accent)"/><circle cx="116" cy="73" r="9" fill="var(--accent)"/><circle cx="133" cy="57" r="7" fill="var(--accent)"/><path d="M146 98h33v17h-33z" fill="#f8e6bf" stroke="#b98e69" stroke-width="2"/><path d="M151 104h23m-23 5h23" stroke="var(--accent)" stroke-width="2"/>''',
    "book": '''<path d="M57 99 66 45h26l9 54Z" fill="#fff9e8" stroke="#709487" stroke-width="2"/><path d="M64 48h31l-5-12H69Z" fill="var(--accent)"/><path d="M70 36V27h19v9" fill="#f8eed9" stroke="#709487" stroke-width="2"/><path d="m67 27 12-9 13 9Z" fill="#547f72"/><rect x="74" y="59" width="10" height="13" rx="5" fill="#a8d6c9"/><path d="M112 98V68l30-15 31 15v30Z" fill="#fff7e5" stroke="#77998b" stroke-width="2"/><path d="m106 70 36-21 37 21-5 4-32-16-31 16Z" fill="var(--accent)"/><path d="M105 106q20-9 37 0 17-9 37 0v12q-20-7-37 1-17-8-37-1Z" fill="#fffdf0" stroke="#b99879" stroke-width="2"/><path d="M142 106v13" stroke="#c6b49a" stroke-width="2"/>''',
    "books": '''<path d="M72 104h104v12H72z" fill="#f5e9ce" stroke="#b99a76" stroke-width="2"/><path d="M82 87h78v17H82z" fill="var(--accent)"/><path d="M91 69h79v18H91z" fill="#f9f5e5" stroke="#aa9780" stroke-width="2"/><path d="M80 52h80v17H80z" fill="var(--accent)" opacity=".72"/><path d="M112 76h43m-43 5h43" stroke="var(--accent)" stroke-width="2"/><path d="M170 90h17v25h-17z" fill="#fdf7e4" stroke="#8b9c85" stroke-width="2"/><path d="M174 94v17m3-17v17m4-17v17m3-17v17" stroke="#536e64" stroke-width="1.4"/>''',
    "audio": '''<path d="M76 91V72a43 43 0 0 1 86 0v19" fill="none" stroke="var(--accent)" stroke-width="11" stroke-linecap="round"/><rect x="67" y="78" width="22" height="34" rx="9" fill="#fff8e5" stroke="var(--accent)" stroke-width="4"/><rect x="149" y="78" width="22" height="34" rx="9" fill="#fff8e5" stroke="var(--accent)" stroke-width="4"/><path d="M104 96v-9m10 16V80m10 29V73m10 27V83" stroke="var(--accent)" stroke-width="4" stroke-linecap="round"/>''',
    "voice": '''<rect x="103" y="42" width="34" height="55" rx="17" fill="var(--accent)"/><path d="M91 80v4a29 29 0 0 0 58 0v-4M120 113v10m-17 0h34" fill="none" stroke="#6b9285" stroke-width="4" stroke-linecap="round"/><path d="M111 60h18m-18 8h18m-18 8h18" stroke="#e6f8ed" stroke-width="2" stroke-linecap="round"/><path d="M66 91q-12-13 0-26m107 26q12-13 0-26" fill="none" stroke="var(--accent)" stroke-width="3" opacity=".65"/>''',
    "slides": '''<path d="M59 105V48h121v57Z" fill="#fff9e8" stroke="#799b8b" stroke-width="3"/><path d="M53 45h133v9H53z" fill="var(--accent)"/><path d="M120 105v18m-22 0 22-18 22 18" fill="none" stroke="#819a87" stroke-width="3" stroke-linecap="round"/><path d="M74 89h18V73H74zm26 0h17V62h-17zm25 0h17V76h-17zm25 0h16V69h-16z" fill="var(--accent)" opacity=".8"/>''',
    "mobile": '''<path d="M57 102V48h116v54Z" fill="#fff9e8" stroke="#799b8b" stroke-width="3"/><path d="M52 45h126v9H52z" fill="var(--accent)"/><path d="M71 86h15V72H71zm23 0h15V62H94zm23 0h15V75h-15z" fill="var(--accent)" opacity=".75"/><rect x="145" y="70" width="35" height="54" rx="6" fill="#fff9e8" stroke="#688b80" stroke-width="3"/><rect x="150" y="78" width="25" height="36" rx="2" fill="var(--accent)" opacity=".65"/><circle cx="162.5" cy="119" r="2" fill="#688b80"/>''',
    "camera": '''<path d="m53 100 38-44 30 35 21-25 44 38Z" fill="#8aac8c"/><path d="m76 73 15-17 15 17-7-3-8 5-7-4Z" fill="#eff3df"/><rect x="83" y="72" width="95" height="49" rx="8" fill="#fff9e8" stroke="#6d9385" stroke-width="3"/><path d="m101 72 7-10h25l7 10Z" fill="var(--accent)"/><circle cx="130" cy="96" r="19" fill="var(--accent)"/><circle cx="130" cy="96" r="11" fill="#d5ece0"/><path d="M183 105V73" stroke="#8d7659" stroke-width="3"/><path d="M183 75c-10-11-8-21 0-21s10 10 0 21Z" fill="var(--accent)"/><circle cx="183" cy="64" r="3" fill="#fff"/>''',
    "focus": '''<rect x="67" y="69" width="111" height="53" rx="9" fill="#fff9e8" stroke="#799b8b" stroke-width="3"/><path d="m85 69 9-12h31l9 12Z" fill="var(--accent)"/><circle cx="124" cy="96" r="23" fill="var(--accent)"/><circle cx="124" cy="96" r="14" fill="#e4f1df"/><path d="M124 86v20m-10-10h20" stroke="#719488" stroke-width="2"/><circle cx="91" cy="81" r="4" fill="#da997c"/>''',
    "sunrise": '''<path d="M62 105h119V57H62Z" fill="#fdf8e8" stroke="#87a18e" stroke-width="3"/><circle cx="121" cy="75" r="14" fill="var(--accent)"/><path d="m67 100 35-27 22 20 20-16 32 23Z" fill="#7eaf8e"/><path d="M55 110h133v9H55z" fill="#e9d3a2"/><path d="M83 45h12m55 0h12m-43-15v9" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>''',
    "route": '''<path d="M54 103q25-32 53-10t75-16" fill="none" stroke="#fff8e5" stroke-width="13" stroke-linecap="round"/><path d="M54 103q25-32 53-10t75-16" fill="none" stroke="var(--accent)" stroke-width="3" stroke-dasharray="3 6" stroke-linecap="round"/><path d="M177 78c-13-15-10-28 0-28s13 13 0 28Z" fill="var(--accent)"/><circle cx="177" cy="63" r="4" fill="#fff9e8"/><circle cx="53" cy="103" r="6" fill="#e7a37c"/>''',
    "mail": '''<rect x="65" y="60" width="110" height="63" rx="8" fill="#fff9e8" stroke="#799a91" stroke-width="3"/><path d="m67 64 53 37 53-37" fill="none" stroke="var(--accent)" stroke-width="5" stroke-linejoin="round"/><path d="m68 118 37-28m67 28-37-28" fill="none" stroke="#b5c6bf" stroke-width="2"/><circle cx="177" cy="59" r="11" fill="var(--accent)"/><path d="M172 59h10m-5-5v10" stroke="#fff" stroke-width="2"/>''',
    "folder": '''<path d="M59 69V57h43l9 10h67v48H59Z" fill="var(--accent)" opacity=".8"/><path d="M59 77h126l-10 41H69Z" fill="#fff9e8" stroke="#71958a" stroke-width="3"/><path d="M78 86h87m-87 9h62m-62 9h74" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>''',
    "walk": '''<path d="M59 108q22-25 48-10t69-15" fill="none" stroke="#f8f0d6" stroke-width="15" stroke-linecap="round"/><path d="M59 108q22-25 48-10t69-15" fill="none" stroke="var(--accent)" stroke-width="3" stroke-dasharray="3 7" stroke-linecap="round"/><path d="M113 63c8 0 12 6 12 14v11h-19V75c0-7 3-12 7-12Zm18 25c-6 0-10 5-10 11v8h17v-9c0-6-3-10-7-10Z" fill="var(--accent)"/><circle cx="111" cy="55" r="4" fill="var(--accent)"/><circle cx="119" cy="55" r="4" fill="var(--accent)"/>''',
    "network": '''<path d="M120 70 102 117m18-47 18 47m-29-15h22m-26 10h30" fill="none" stroke="#698f81" stroke-width="4" stroke-linecap="round"/><circle cx="120" cy="67" r="7" fill="var(--accent)"/><path d="M105 61q-9 8 0 16m30-16q9 8 0 16M96 53q-18 16 0 32m48-32q18 16 0 32" fill="none" stroke="var(--accent)" stroke-width="4" stroke-linecap="round"/>''',
}

SPRITE_ATLASES = {
    "creative-atlas.webp": (1774, 887, 510, 420),
    "play-reading-atlas.webp": (1774, 887, 520, 420),
    "utility-atlas.webp": (1774, 887, 550, 420),
}
SPRITE_ART = {
    "aquarium": ("play-reading-atlas.webp", 316.5, 233), "fruit": ("play-reading-atlas.webp", 889.5, 233),
    "book": ("play-reading-atlas.webp", 1454.5, 233), "books": ("play-reading-atlas.webp", 317, 673),
    "audio": ("play-reading-atlas.webp", 891, 673), "voice": ("play-reading-atlas.webp", 1459, 673),
    "slides": ("creative-atlas.webp", 265, 233), "mobile": ("creative-atlas.webp", 722, 233),
    "camera": ("creative-atlas.webp", 1183.5, 233), "focus": ("creative-atlas.webp", 264, 673),
    "route": ("creative-atlas.webp", 741.5, 673), "sunrise": ("creative-atlas.webp", 1205, 673),
    "mail": ("utility-atlas.webp", 322, 233), "folder": ("utility-atlas.webp", 889.5, 233),
    "network": ("utility-atlas.webp", 1462.5, 233), "walk": ("utility-atlas.webp", 331, 673),
}


def blended(accent, base="#d5dfc4", weight=0.32):
    return "#" + "".join(f"{round(int(accent[i:i+2], 16)*weight + int(base[i:i+2], 16)*(1-weight)):02x}" for i in (1, 3, 5))


def island_art(scene, asset_url):
    if scene in SPRITE_ART:
        atlas, center_x, center_y = SPRITE_ART[scene]
        image_width, image_height, crop_width, crop_height = SPRITE_ATLASES[atlas]
        x = (center_x - crop_width / 2) / (image_width - crop_width) * 100
        y = (center_y - crop_height / 2) / (image_height - crop_height) * 100
        size_x = image_width / crop_width * 100
        size_y = image_height / crop_height * 100
        url = esc(asset_url(f"assets/island-hub/{atlas}"))
        return f'<span class="island-landmark island-landmark--generated" aria-hidden="true" style="--art-url:url({url});--art-position:{x:.3f}% {y:.3f}%;--art-size:{size_x:.3f}% {size_y:.3f}%"></span>'
    return f'''<svg viewBox="0 0 240 160" aria-hidden="true" focusable="false">
      <ellipse cx="120" cy="132" rx="101" ry="19" fill="#65a99c" opacity=".18"/>
      <path d="M20 100C35 75 71 68 119 71c49-8 86 1 101 25v19c-19 24-56 34-100 33-43-1-81-10-100-31Z" fill="var(--island-side)"/>
      <path d="M20 100C35 75 71 68 119 71c49-8 86 1 101 25-18 25-56 36-100 35-43-1-81-10-100-31Z" fill="#ead4a1"/>
      <path d="M29 98c18-18 51-23 90-21 42-7 73 1 91 19-20 19-51 27-90 27-38 0-72-8-91-25Z" fill="var(--island-ground)"/>
      <path d="M35 109c25 11 55 14 86 14 34 0 63-6 84-17" fill="none" stroke="#fff3d1" stroke-width="2" stroke-linecap="round" opacity=".65"/>
      {SCENES[scene]}
    </svg>'''


def render_hub(locale, site, apps, asset_url, icon_path, lang_switch, seo_meta, page, coming_soon_label):
    ui = UI[locale]
    hub = site["hub"][locale]
    groups = {group: [] for group in ("game", "reading", "creative", "utility")}
    visible_apps = [app for app in apps if app.get("showOnHub", True)]
    for app in visible_apps:
        island = app.get("island", {})
        group = island.get("group", "utility")
        scene = island.get("scene", "folder")
        accent = island.get("accent", "#4b9a8b")
        if group not in groups or scene not in SCENES or not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
            raise ValueError(f"Invalid island metadata for {app['id']}")
        groups[group].append(app)
    for entries in groups.values():
        entries.sort(key=lambda app: app.get("island", {}).get("order", 999))

    sections, index_groups = [], []
    for group, entries in groups.items():
        if not entries:
            continue
        kind = "game" if group == "game" else "tool"
        kicker, heading, description = ui["groups"][group]
        nodes, index_links = [], []
        for app in entries:
            loc = app["locales"][locale]
            island = app.get("island", {})
            accent = island.get("accent", "#4b9a8b")
            scene = island.get("scene", "folder")
            icon = asset_url(icon_path(app["icon"], 112))
            status = coming_soon_label.get(locale, "Coming Soon") if app.get("comingSoon") else app["platform"]
            href = f'/{locale}/{app["id"]}/' if app.get("flagship") else (app.get("appStoreUrl") if not app.get("comingSoon") else None)
            attrs = f'data-name="{esc(loc["name"])}" data-description="{esc(loc["tagline"])}" data-status="{esc(status)}" data-icon="{esc(icon)}"'
            ground, side = blended(accent), blended(accent, "#897c6a", 0.12)
            label = f'<span class="island-nameplate"><img src="{esc(icon)}" alt="" width="40" height="40" loading="lazy" decoding="async"><span><strong>{esc(loc["name"])}</strong><small>{esc(status)}</small></span></span>'
            summary = f'<span class="island-summary">{esc(loc["tagline"])}</span>'
            art = island_art(scene, asset_url)
            style = f'--accent:{accent};--island-ground:{ground};--island-side:{side}'
            if href:
                link_attrs = f'href="{esc(href)}" {attrs}'
                nodes.append(f'<a class="map-island island-detail-trigger" {link_attrs} style="{style}">{art}{label}{summary}</a>')
                index_links.append(f'<a class="island-detail-trigger index-link" {link_attrs} aria-label="{esc(loc["name"])}"><img src="{esc(icon)}" alt="" width="30" height="30" loading="lazy"><span>{esc(loc["name"])}</span></a>')
            else:
                nodes.append(f'<div class="map-island" style="{style}">{art}{label}{summary}</div>')
                index_links.append(f'<span class="index-link"><img src="{esc(icon)}" alt="" width="30" height="30" loading="lazy"><span>{esc(loc["name"])} · {esc(status)}</span></span>')
        sections.append(f'''<section class="sea-region sea-region--{group}" data-region="{kind}" aria-labelledby="region-{group}">
          <div class="region-heading"><div><p>{esc(kicker)}</p><h2 id="region-{group}">{esc(heading)}</h2></div><span>{esc(description)}</span></div>
          <div class="island-cluster">{"".join(nodes)}</div>
        </section>''')
        index_groups.append(f'<div class="index-group" data-index-region="{kind}"><h3>{esc(heading)}</h3>{"".join(index_links)}</div>')

    css = f'<link rel="stylesheet" href="{esc(asset_url("island-hub.css"))}">\n'
    hero_art_url = esc(asset_url("assets/island-hub/hero-compass.webp"))
    body = f'''<div class="archipelago">
      <header class="map-topbar">
        <a class="map-brand" href="/{locale}/"><span class="brand-emblem" aria-hidden="true">DL</span><span><strong>Daniel Lu</strong><small>THE APP ARCHIPELAGO</small></span></a>
        <div class="map-navigation">
          <nav class="map-filters" aria-label="{esc(ui['filter'])}" hidden><button type="button" data-filter="all" aria-pressed="true">{esc(ui["all"])}</button><button type="button" data-filter="game" aria-pressed="false">{esc(ui["game"])}</button><button type="button" data-filter="tool" aria-pressed="false">{esc(ui["tool"])}</button></nav>
          <details class="map-index"><summary>☰ {esc(ui["list"])}</summary><div class="index-panel">{"".join(index_groups)}</div></details>
          {lang_switch(locale)}
        </div>
      </header>
      <main>
        <section class="map-intro" aria-labelledby="map-title">
          <div><p class="map-eyebrow">{esc(ui["eyebrow"])}</p><h1 id="map-title">{ui["headline"]}</h1><p class="map-intro-copy">{esc(hub["subtitle"])}</p><a class="explore-link" href="#islands">{esc(ui["explore"])} <span aria-hidden="true">↓</span></a></div>
          <div class="intro-compass" aria-hidden="true"><span class="compass-north">N</span><img src="{hero_art_url}" alt="" width="256" height="256" fetchpriority="high" decoding="async"><span class="compass-count"><strong>{len(visible_apps):02}</strong><small>{esc(ui["count"])}</small></span></div>
        </section>
        <div id="islands" class="archipelago-map" aria-label="{esc(ui["map_label"])}">{"".join(sections)}</div>
      </main>
      <footer class="map-footer">© {esc(site["owner"])} · <a href="https://github.com/{esc(site["githubUser"])}">GitHub</a></footer>
      <dialog class="island-dialog" aria-labelledby="dialog-title"><div class="dialog-content"><div class="dialog-top"><span class="dialog-kicker">THE APP ARCHIPELAGO</span><form method="dialog"><button class="dialog-close" aria-label="{esc(ui["close"])}">×</button></form></div><div class="dialog-heading"><img id="dialog-icon" alt="" width="64" height="64"><div><h2 id="dialog-title"></h2><span id="dialog-status"></span></div></div><p id="dialog-description"></p><a id="dialog-link" class="dialog-link" href="/">{esc(ui["visit"])} <span aria-hidden="true">↗</span></a></div></dialog>
    </div>
    <script src="{esc(asset_url("island-hub.js"))}" defer></script>'''
    return page(hub["title"], body, locale, seo_meta(hub["title"], locale, f"/{locale}/", description=hub.get("subtitle")) + css, body_class="archipelago-page")
