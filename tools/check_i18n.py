#!/usr/bin/env python3
"""Fail when any page on this site is missing a language.

The site has two kinds of multilingual content, and both fail silently:

1. Generated pages (apps.json -> generate.py -> {en,zh-hant,zh-hans}/...). A field filled in one
   locale only, an English string left in Chinese, or a zh-hans string that is still Traditional
   all render without an error.
2. Hand-written sub-sites (tinyaquarium/...) that carry `const I18N = {'zh-Hant':{}, 'zh-Hans':{},
   'en-US':{}}` and a `t()` that falls back to zh-Hant when a key is missing. A key added to zh-Hant
   only shows Chinese on the English page; Chinese typed straight into the HTML never goes through
   `t()` at all.

What it checks
  apps.json      every app has every site locale with the same fields; en has no Chinese; zh-hans
                 is not Traditional; privacy page and screenshot count match across locales.
  locale dirs    the same pages exist under every locale; visible en text has no Chinese; visible
                 zh-hans text is not Traditional.
  I18N pages     every key exists in every language; en-US values have no Chinese; zh-Hans values
                 are not Traditional; every data-i18n* key in the HTML and every literal t('key') in the
                 script exists; no Chinese in visible
                 HTML text or alt/title/placeholder/aria-label outside an element with data-i18n*.
  other pages    under a sub-site (no I18N, not noindex): lang="en", "zh-Hant", "zh-Hans" blocks exist.

What it cannot see (check these by hand, e.g. switch the live page to English and look)
  - Text built at runtime from JS or from assets/data/*.json (species names, SVG labels, category
    names). Chinese string literals in <script> outside I18N are listed as WARN only, because the
    script may branch on currentLang.
  - Wrong or stale translations. It checks that a language is present, not that it says the same.
  - zh-hant text that is accidentally Simplified.

Usage: python3 tools/check_i18n.py [--root DIR]    exit 1 on any FAIL
"""
import argparse, glob, html.parser, json, os, re, shutil, subprocess, sys

CJK = re.compile(r"[㐀-鿿]")
LANG_LABELS = {"繁中", "简中", "簡中", "繁體中文", "简体中文", "簡體中文", "中文", "繁體", "简体", "簡體"}
SKIP_DIRS = {".git", ".scratch", "assets", "tools", "node_modules", ".githooks"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
ATTRS = ("alt", "title", "placeholder", "aria-label")

fails, warns = [], []
def fail(where, msg, examples=()):
    ex = list(examples)
    fails.append(f"FAIL {where}: {msg}" + (f" — e.g. {', '.join(ex[:5])}" + (f" (+{len(ex) - 5})" if len(ex) > 5 else "") if ex else ""))
def warn(where, msg): warns.append(f"WARN {where}: {msg}")

OPENCC = shutil.which("opencc")
def traditional_left(texts):
    """Return the texts that opencc t2s would change, i.e. that still contain Traditional characters."""
    texts = [t for t in texts if CJK.search(t)]
    if not texts: return []
    if not OPENCC:
        warn("-", "opencc not installed; zh-Hans Traditional check skipped (brew install opencc)")
        return []
    sep = "\n⁣SEP⁣\n"
    out = subprocess.run([OPENCC, "-c", "t2s"], input=sep.join(texts), capture_output=True, text=True).stdout
    conv = out.split(sep)
    if len(conv) != len(texts): return []
    def still_traditional(a, b):
        b = b.rstrip("\n")
        if a == b: return False
        if len(a) != len(b): return True
        # A conversion into a character outside the BMP (e.g. 魟 -> 𫚉) is a rare form fonts do not
        # render; the BMP character is the one Simplified text actually uses.
        return any(x != y and ord(y) <= 0xFFFF for x, y in zip(a, b))
    return [a for a, b in zip(texts, conv) if still_traditional(a, b)]

def strip_tags(s): return re.sub(r"<[^>]+>", " ", s)

class Visible(html.parser.HTMLParser):
    """Collects visible text and user-facing attributes, noting whether an i18n attribute covers them."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.found, self.keys, self.langs, self.noindex = [], [], set(), set(), False
    def covered(self): return any(c for _, c, _, _ in self.stack)
    def hidden(self): return any(t in ("script", "style", "template", "noscript", "head") for t, _, _, _ in self.stack)
    def ids(self): return [h for _, _, _, hs in self.stack for h in hs]
    @staticmethod
    def hooks(a):  # the id and classes a script could use to find this element
        return ([a["id"]] if a.get("id") else []) + (a.get("class") or "").split()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        has_i18n = any(k.startswith("data-i18n") for k in a)
        for k, v in a.items():
            if k.startswith("data-i18n") and v: self.keys.add(v)
        if "lang" in a and a["lang"]: self.langs.add(a["lang"])
        if tag == "meta" and a.get("name") == "robots" and "noindex" in (a.get("content") or ""): self.noindex = True
        if not self.hidden():
            for k in ATTRS:
                if a.get(k) and CJK.search(a[k]) and not has_i18n and not self.covered():
                    self.found.append((f'{k}="{a[k][:30]}"', self.ids() + self.hooks(a)))
        if tag not in VOID:
            # <html lang> is the page default, not a per-block language marker; counting it would
            # exempt every text node on the page.
            self.stack.append((tag, has_i18n, bool(a.get("lang")) and tag != "html", self.hooks(a)))
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]; break
    def handle_data(self, data):
        s = data.strip()
        if not s or not CJK.search(s) or self.hidden() or self.covered(): return
        if s in LANG_LABELS or any(l for _, _, l, _ in self.stack): return
        self.found.append((s[:30], self.ids()))

def visible_text(src):
    p = Visible(); p.feed(src); return p

NODE_EXTRACT = r"""
const fs = require('fs'); const s = fs.readFileSync(process.argv[1], 'utf8');
function span(name) {
  const i = s.indexOf('const ' + name); if (i < 0) return null;
  let j = s.indexOf('=', i) + 1; while (/\s/.test(s[j])) j++;
  const open = s[j], close = open === '{' ? '}' : ']'; let d = 0, q = null, k = j;
  for (; k < s.length; k++) {
    const c = s[k];
    if (q) { if (c === '\\') { k++; continue; } if (c === q) q = null; continue; }
    if (c === "'" || c === '"' || c === '`') { q = c; continue; }
    if (c === '/' && s[k + 1] === '/') { k = s.indexOf('\n', k); continue; }
    if (c === '/' && s[k + 1] === '*') { k = s.indexOf('*/', k) + 1; continue; }
    if (c === open) d++; else if (c === close) { d--; if (d === 0) break; }
  }
  return s.slice(j, k + 1);
}
const src = span('I18N'), langs = span('LANGS');
const I18N = Function('return (' + src + ')')();
const LANGS = langs ? Function('return (' + langs + ')')() : Object.keys(I18N);
console.log(JSON.stringify({ I18N, LANGS, src }));
"""

def check_i18n_page(root, rel, src):
    r = subprocess.run(["node", "-e", NODE_EXTRACT, os.path.join(root, rel)], capture_output=True, text=True)
    if r.returncode != 0:
        fail(rel, "cannot evaluate const I18N (node): " + r.stderr.strip().splitlines()[-1][:120]); return
    d = json.loads(r.stdout); I18N, LANGS = d["I18N"], d["LANGS"]
    for lang in LANGS:
        if lang not in I18N: fail(rel, f"LANGS lists {lang} but I18N has no {lang} table")
    langs = [l for l in LANGS if l in I18N]
    allkeys = set().union(*(I18N[l].keys() for l in langs))
    for lang in langs:
        miss = sorted(allkeys - set(I18N[lang]))
        if miss: fail(rel, f"{len(miss)} key(s) missing in {lang} (t() falls back to another language)", miss)
    en = next((l for l in langs if l.lower().startswith("en")), None)
    if en:
        bad = [k for k, v in I18N[en].items() if isinstance(v, str) and CJK.search(strip_tags(v))]
        if bad: fail(rel, f"{len(bad)} {en} value(s) contain Chinese", bad)
    hans = next((l for l in langs if l.lower() == "zh-hans"), None)
    if hans:
        items = [(k, strip_tags(v)) for k, v in I18N[hans].items() if isinstance(v, str)]
        left = set(traditional_left([v for _, v in items]))
        bad = [k for k, v in items if v in left]
        if bad: fail(rel, f"{len(bad)} {hans} value(s) still Traditional", bad)
    p = visible_text(src)
    undefined = sorted(k for k in p.keys if k not in allkeys)
    if undefined: fail(rel, f"{len(undefined)} data-i18n key(s) not in I18N", undefined)
    body = src.replace(d["src"], "")
    script = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", body, re.S))
    # an id or class the page script actually selects: getElementById('x'), '#x', querySelector('.x'), getElementsByClassName('x')
    touched = lambda hooks: any(re.search(r"""getElementById\(\s*['"]%s['"]|['"][^'"]*#%s(?![\w-])|querySelector(?:All)?\(\s*['"][^'"]*\.%s(?![\w-])|getElementsByClassName\(\s*['"]%s['"]""" % ((re.escape(h),) * 4), script) for h in hooks)
    literal = sorted({k for k in re.findall(r"""\bt\(\s*['"]([\w.-]+)['"]\s*\)""", script) if k not in allkeys})
    if literal: fail(rel, f"{len(literal)} t('key') call(s) use a key no language defines (the page shows the key name)", literal)
    hard = [txt for txt, ids in p.found if not touched(ids)]
    soft = [txt for txt, ids in p.found if touched(ids)]
    if hard: fail(rel, f"{len(hard)} Chinese text(s) in HTML without data-i18n", hard)
    if soft: warn(rel, f"{len(soft)} Chinese placeholder text(s) in elements the script writes to (confirm the script localizes them): " + ", ".join(soft[:4]))
    lits = [m for m in re.findall(r"""(['"`])((?:\\.|(?!\1).)*?[㐀-鿿](?:\\.|(?!\1).)*?)\1""", "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", body, re.S)))]
    if lits: warn(rel, f"{len(lits)} Chinese string literal(s) in <script> outside I18N (check they branch on currentLang)")

def check_other_subsite_page(rel, src):
    p = visible_text(src)
    if p.noindex: return
    have = {l.lower().split("-")[0] if l.lower().startswith("en") else l.lower() for l in p.langs}
    miss = [l for l in ("en", "zh-hant", "zh-hans") if l not in have]
    if miss: fail(rel, "page has no I18N table and no lang block for " + ", ".join(miss))

def check_generated(root):
    path = os.path.join(root, "apps.json")
    if not os.path.exists(path): return []
    d = json.load(open(path, encoding="utf-8")); L = d["site"]["locales"]
    def strings(o, pre=""):
        if isinstance(o, dict):
            for k, v in o.items(): yield from strings(v, f"{pre}.{k}" if pre else k)
        elif isinstance(o, list):
            for i, v in enumerate(o): yield from strings(v, f"{pre}[{i}]")
        elif isinstance(o, str): yield pre, o
    for a in d["apps"]:
        i, loc = a["id"], a.get("locales", {})
        where = f"apps.json {i}"
        miss = [l for l in L if l not in loc]
        if miss: fail(where, "missing locale(s) " + ", ".join(miss)); continue
        shapes = {l: {p.split("[")[0] for p, _ in strings(loc[l])} for l in L}
        allf = set().union(*shapes.values())
        for l in L:
            m = sorted(allf - shapes[l])
            if m: fail(where, f"field(s) missing in {l}", m)
        qa = {l: len(loc[l].get("qa") or []) for l in L}
        if len(set(qa.values())) > 1: fail(where, f"qa count differs by locale {qa}")
        if "en" in loc:
            bad = [p for p, s in strings(loc["en"]) if CJK.search(s)]
            if bad: fail(where, "en field(s) contain Chinese", bad)
        if "zh-hans" in loc:
            items = list(strings(loc["zh-hans"]))
            left = set(traditional_left([s for _, s in items]))
            bad = [p for p, s in items if s in left]
            if bad: fail(where, "zh-hans field(s) still Traditional", bad)
        pv = {l: os.path.isfile(os.path.join(root, l, i, "privacy", "index.html")) for l in L}
        if len(set(pv.values())) > 1: fail(where, f"privacy page exists in some locales only {pv}")
        sh = {l: len(glob.glob(os.path.join(root, "assets", i, l, "*.png"))) for l in L}
        if len(set(sh.values())) > 1: fail(where, f"screenshot count differs by locale {sh} (copy zh-hant when a locale has none)")
    pages = {l: {os.path.relpath(os.path.join(r, f), os.path.join(root, l))
                 for r, _, fs in os.walk(os.path.join(root, l)) for f in fs if f.endswith(".html")} for l in L}
    for p in sorted(set().union(*pages.values())):
        m = [l for l in L if p not in pages[l]]
        if m: fail(f"{p}", "page missing under " + ", ".join(m))
    en_hits, hans_texts = [], {}
    for l in L:
        for p in pages[l]:
            src = open(os.path.join(root, l, p), encoding="utf-8").read()
            v = visible_text(src)
            if l == "en" and v.found: en_hits.append(f"en/{p}: {v.found[0][0]}")
            if l == "zh-hans":
                txt = strip_tags(re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", src, flags=re.S))
                hans_texts[f"zh-hans/{p}"] = re.sub(r"\s+", " ", txt.replace("繁體中文", ""))
    if en_hits: fail("en/", f"{len(en_hits)} page(s) show Chinese", en_hits)
    left = set(traditional_left(list(hans_texts.values())))
    bad = [p for p, t in hans_texts.items() if t in left]
    if bad: fail("zh-hans/", f"{len(bad)} page(s) still contain Traditional text", bad)
    return L

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    root = ap.parse_args().root
    locales = check_generated(root) or []
    for dirpath, dirs, files in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        top = rel_dir.split(os.sep)[0]
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        if top in locales or rel_dir == ".": continue
        for f in files:
            if not f.endswith(".html"): continue
            rel = os.path.join(rel_dir, f); src = open(os.path.join(root, rel), encoding="utf-8").read()
            if "const I18N" in src: check_i18n_page(root, rel, src)
            else: check_other_subsite_page(rel, src)
    for line in warns: print(line)
    for line in fails: print(line)
    print(f"i18n check: {len(fails)} FAIL, {len(warns)} WARN")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
