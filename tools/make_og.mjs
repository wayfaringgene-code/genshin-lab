// X などにURLを貼ったときの画像（src/og.png、1200×630）を、トップの見本カードから作る。
// 使い方：
//   python3 tools/build_pages.py
//   python3 -m http.server 8000 --directory _site   （別の画面で動かしたまま）
//   node tools/make_og.mjs                           （Playwright が要る：npm i playwright）
// 見本のキャラや同梱の立ち絵を変えたら、作り直して commit する。
// 文字は src/fonts のカード用フォント（Murecho、足りない字は M PLUS 1p）を埋め込んで描く。
import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import fs from 'fs';
import path from 'path';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const OUT = path.join(ROOT, 'src', 'og.png');
const URL = process.env.OG_URL || 'http://localhost:8000/';

let css = '';
for (const [file, fam, w] of [['murecho-400', 'Murecho', 400], ['murecho-700', 'Murecho', 700], ['mplus1p-400', 'M PLUS 1p', 400], ['mplus1p-700', 'M PLUS 1p', 700]]) {
  const pk = JSON.parse(fs.readFileSync(path.join(ROOT, 'src', 'fonts', file + '.json'), 'utf8'));
  for (const sb of pk.subsets) css += `@font-face{font-family:"${fam}";font-weight:${w};src:url(data:font/woff2;base64,${sb.d}) format("woff2");unicode-range:${sb.r};}\n`;
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
await page.goto(URL);
await page.waitForSelector('#homeSample svg');
await page.waitForTimeout(2500); // 立ち絵の切り出し待ち
const svg = await page.$eval('#homeSample svg', (e) => e.outerHTML);

// 1200×630 の台に、カード（16:9）を真ん中に置く
const og = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
await og.goto(URL); // 立ち絵（portraits/…）を同じ場所から読めるように
await og.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${css}
html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:radial-gradient(900px 500px at 30% 20%,#191a40,#05060d 70%)}
.c{position:absolute;left:40px;top:0;width:1120px;height:630px}.c svg{width:100%;height:100%;display:block}</style></head>
<body><div class="c">${svg}</div></body></html>`);
await og.evaluate(() => document.fonts.ready);
await og.waitForTimeout(1500);
await og.screenshot({ path: OUT });
await browser.close();
console.log('wrote', OUT);
