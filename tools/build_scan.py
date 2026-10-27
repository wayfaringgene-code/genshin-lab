# 聖遺物ビデオスキャナーを、命ノ星座カードの「動画から取り込む」ページ用に組み立てる。
# 使い方: python3 build_scan.py <スキャナーのフォルダ（index.html core.js data.js tess/）> <出力のフォルダ（カードアプリの scan/）>
# 変更点：
#   - core.js の toLab：レベル（+20未満なら lv）、未発動のサブOP（off:true で4つ目に置く）を残す。★4は外して数える（notes）
#   - index.html：?embed=1 で枠の中に置かれたときだけ、カードアプリの見た目に合わせ、
#     「キャラ一覧に入れる」ボタン（親のページへ postMessage）と、高さの通知を足す。単体で開いたときは今までどおり
import os, shutil, sys

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(dst, 'tess'), exist_ok=True)

def patch(name, pairs):
    s = open(os.path.join(src, name), encoding='utf-8').read()
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, (name, old[:80], n)
        s = s.replace(old, new)
    open(os.path.join(dst, name), 'w', encoding='utf-8').write(s)

# ---------- core.js ----------
patch('core.js', [
("""  function toLab(arts, date) {
    const by = new Map();
    for (const a of arts) {
      if (!a.location) continue;
""", """  function toLab(arts, date) {
    const by = new Map(), notes = { low: 0, partial: 0 };
    for (const a of arts) {
      if (!a.location) continue;
      if (a.rarity !== 5) { notes.low++; continue; }   // ラボの計算は★5だけ
"""),
("""        const subs = a.substats.concat(a.unactivatedSubstats || []).map(x => ({ s: LAB_STAT[x.key], v: String(x.value) }));
        while (subs.length < 4) subs.push({ s: '', v: '' });
        pieces[a.slotKey] = { main: LAB_STAT[a.mainStatKey], subs: subs.slice(0, 4) };
""", """        // 未発動のサブOPは off の印を付けて後ろに置く（ラボは数えない）。+20未満なら lv を付ける（ラボはいまの値で評価する）
        const subs = a.substats.map(x => ({ s: LAB_STAT[x.key], v: String(x.value) }))
          .concat((a.unactivatedSubstats || []).map(x => ({ s: LAB_STAT[x.key], v: String(x.value), off: true })));
        while (subs.length < 4) subs.push({ s: '', v: '' });
        const p = { main: LAB_STAT[a.mainStatKey], subs: subs.slice(0, 4) };
        if (a.level < 20) { p.lv = a.level; notes.partial++; }
        pieces[a.slotKey] = p;
"""),
("return { app: 'genshin-lab-chars', v: 1, at: new Date().toISOString(), chars };",
 "return { app: 'genshin-lab-chars', v: 1, at: new Date().toISOString(), chars, notes };"),
])

# ---------- index.html ----------
EMBED_CSS = """
/* ===== 命ノ星座カードの枠の中（?embed=1）：カードアプリの見た目に合わせる ===== */
html:root.embed {
  color-scheme: dark;
  --ground: transparent; --panel: rgba(11,14,34,.78); --panel-2: rgba(17,21,44,.82); --line: rgba(233,211,154,.2);
  --ink: #f3ead6; --ink-2: #9aa6bb; --amber: #e9d39a; --amber-soft: rgba(233,211,154,.14); --star: #f6dc94;
  --ok: #6cc7a0; --warn: #ff9d8f; --warn-soft: rgba(255,157,143,.12); --elx: #b9a3f0; --screen: #05060d;
  --font: "Murecho", "M PLUS 1p", "Hiragino Sans", "Yu Gothic", system-ui, sans-serif;
}
html.embed body { background: transparent; }
html.embed .wrap { padding: 0; max-width: none; }
html.embed header.top h1, html.embed header.top > p { display: none; }
html.embed #save, html.embed #copy, html.embed .export label.note { display: none !important; }
html.embed #toCards { display: inline-flex; }
/* 地の色を文字に使っている所（押した絞り込み・レベルの札・装備キャラの札・主ボタン）は、カードアプリの「透けた金」に */
html.embed .tabs button[aria-pressed="true"], html.embed .l1 .lv { background: rgba(233,211,154,.14); color: #f3e3b4; box-shadow: inset 0 0 0 1px rgba(233,211,154,.7); }
html.embed .l1 .who { color: #08140e; }
html.embed .btn { background: rgba(255,255,255,.04); border-color: rgba(233,211,154,.22); color: var(--ink); }
html.embed .btn.primary, html.embed .btn.onscreen { background: rgba(233,211,154,.14); border-color: rgba(233,211,154,.7); color: #f3e3b4; }
html.embed .btn:disabled { opacity: .45; cursor: default; }
#toCards { display: none; }
</style>"""

patch('index.html', [
# 文字：カードアプリと同じ Murecho も読む
("https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New",
 "https://fonts.googleapis.com/css2?family=Murecho:wght@400;700&family=Zen+Kaku+Gothic+New"),
# 見た目（スキャナーのスタイルの最後に足す）
("textarea.json { width: 100%; height: 120px; font-family: var(--mono); font-size: 12px; background: var(--panel); color: var(--ink); border: 1px solid var(--line); border-radius: 6px; padding: 8px; }\n</style>",
 "textarea.json { width: 100%; height: 120px; font-family: var(--mono); font-size: 12px; background: var(--panel); color: var(--ink); border: 1px solid var(--line); border-radius: 6px; padding: 8px; }" + EMBED_CSS),
# ボタン
('<button class="btn primary" id="save" type="button" disabled hidden>ファイルを保存</button>',
 '<button class="btn primary" id="toCards" type="button" disabled>キャラ一覧に入れる</button>\n        <button class="btn primary" id="save" type="button" disabled hidden>ファイルを保存</button>'),
("$('copy').disabled = $('save').disabled = n === 0;",
 "$('copy').disabled = $('save').disabled = $('toCards').disabled = n === 0;"),
# 枠の中かどうか（最初に決める）
("  const G = window.GSCAN, D = window.GSCAN_DATA, P = G.PANEL;",
 "  const G = window.GSCAN, D = window.GSCAN_DATA, P = G.PANEL;\n"
 "  const EMBED = window.parent !== window && /[?&]embed\\b/.test(location.search);   // 命ノ星座カードの「動画から取り込む」の枠の中\n"
 "  if (EMBED) document.documentElement.classList.add('embed');"),
# 親のページとのやりとり
("  window.__gscan = { S, exportJSON, load };",
 """  if (EMBED) {
    $('exmsg').textContent = '読み終わったら「キャラ一覧に入れる」で、装備中のキャラ（★5の聖遺物）をカードアプリに入れます。';
    $('toCards').addEventListener('click', () => { parent.postMessage({ type: 'gscan:lab', json: exportJSON('lab') }, '*'); $('exmsg').textContent = '送りました…'; });
    window.addEventListener('message', e => { if (e.source !== parent) return; const d = e.data || {}; if (d.type === 'gscan:done') $('exmsg').textContent = d.msg || '入れました。'; });
    const wrap = document.querySelector('.wrap');
    let lastH = 0; const post = () => { const h = Math.ceil(wrap.getBoundingClientRect().height); if (h !== lastH) { lastH = h; parent.postMessage({ type: 'gscan:h', h }, '*'); } };
    new ResizeObserver(post).observe(wrap); post();
  }
  window.__gscan = { S, exportJSON, load };"""),
])

shutil.copy(os.path.join(src, 'data.js'), os.path.join(dst, 'data.js'))
for f in os.listdir(os.path.join(src, 'tess')):
    shutil.copy(os.path.join(src, 'tess', f), os.path.join(dst, 'tess', f))
print('wrote', dst)
