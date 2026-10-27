// 命ノ星座カード用の Enka.Network 中継（Cloudflare Workers）
// ・GET /uid/{UID} を受けて、https://enka.network/api/uid/{UID}/ に問い合わせ、結果をそのまま返す
// ・呼び出しを受け付けるのは ALLOW のページだけ（ブラウザが付ける Origin で見分ける）
// ・Enka の決まりに合わせて、独自の User-Agent を付け、応答の ttl の間は同じUIDを取り直さない（使える環境ならキャッシュ）
// 置き方は proxy/README.md を参照
const ALLOW = [
  'https://wayfaringgene-code.github.io', // GitHub Pages
  'http://localhost:8000',                // 手元で試すとき（python3 -m http.server 8000）
];
const UA = 'meinoseiza-card/1.0 (+https://github.com/wayfaringgene-code/genshin-lab)';

export default {
  async fetch(req, env, ctx) {
    const origin = req.headers.get('Origin') || '';
    const cors = {
      'Access-Control-Allow-Origin': ALLOW.includes(origin) ? origin : ALLOW[0],
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Accept',
      'Access-Control-Max-Age': '86400',
      'Vary': 'Origin',
    };
    const reply = (status, text) => new Response(text, { status, headers: { ...cors, 'Content-Type': 'text/plain; charset=utf-8' } });
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (req.method !== 'GET') return reply(405, 'GET only');
    if (origin && !ALLOW.includes(origin)) return reply(403, 'This proxy is only for the 命ノ星座カード pages');
    const m = new URL(req.url).pathname.match(/^\/uid\/(\d{9,10})\/?$/);
    if (!m) return reply(404, 'Use /uid/{UID}');
    const uid = m[1];

    const cache = (typeof caches !== 'undefined' && caches.default) || null;
    const key = new Request('https://enka-proxy.cache/uid/' + uid);
    let res = cache ? await cache.match(key) : null;
    if (!res) {
      let up;
      try {
        up = await fetch(`https://enka.network/api/uid/${uid}/`, { headers: { 'User-Agent': UA, 'Accept': 'application/json' } });
      } catch (e) {
        return reply(502, 'Could not reach Enka.Network');
      }
      const body = await up.text();
      let ttl = 60;
      if (up.ok) { try { const j = JSON.parse(body); if (+j.ttl > 0) ttl = Math.min(+j.ttl, 600); } catch (e) {} }
      res = new Response(body, {
        status: up.status,
        headers: { 'Content-Type': up.ok ? 'application/json; charset=utf-8' : 'text/plain; charset=utf-8', 'Cache-Control': `public, max-age=${up.ok ? ttl : 30}` },
      });
      if (cache && (up.ok || up.status === 404)) ctx.waitUntil(cache.put(key, res.clone()));
    }
    const out = new Response(res.body, res);
    for (const [k, v] of Object.entries(cors)) out.headers.set(k, v);
    return out;
  },
};
