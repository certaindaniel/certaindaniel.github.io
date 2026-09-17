// Resolve the language before the hero image starts downloading.
const LANGS = ['zh-Hant', 'zh-Hans', 'en-US'];
const URL_LANG_ALIASES = { en: 'en-US', 'en-us': 'en-US', 'zh-hans': 'zh-Hans', 'zh-hant': 'zh-Hant' };
let currentLang = 'zh-Hant';
const queryLang = new URLSearchParams(location.search).get('lang');
const urlLang = queryLang && URL_LANG_ALIASES[queryLang.toLowerCase()];
try {
    const stored = localStorage.getItem('ta_lang');
    if (LANGS.includes(stored)) currentLang = stored;
    if (urlLang) localStorage.setItem('ta_lang', urlLang);
} catch (e) { /* Storage can be unavailable in private browsing. */ }
if (urlLang) currentLang = urlLang;

function updateLocalizedScreenshot() {
    const image = document.getElementById('dex-screenshot');
    if (!image) return;
    const source = image.getAttribute('data-' + currentLang.toLowerCase());
    if (image.getAttribute('src') !== source) image.src = source;
}
