/* 聖遺物パネルの画像解析と OCR 結果の解釈。DOM に依存しない純粋な関数だけを置く。 */
(function (g) {
  'use strict';
  const D = g.GSCAN_DATA;

  // 1920x1080 基準での詳細パネルの位置（コントローラー操作時のレイアウト）
  const PANEL = { x: 1350, y: 130, w: 410, h: 820 };
  const BODY_H = 530;       // ステータスとセット名までが収まる高さ

  const SLOTS = { flower: '生の花', plume: '死の羽', sands: '時の砂', goblet: '空の杯', circlet: '理の冠' };
  const MAIN_BY_SLOT = {
    flower: ['hp'], plume: ['atk'],
    sands: ['hp_', 'def_', 'atk_', 'eleMas', 'enerRech_'],
    goblet: ['hp_', 'def_', 'atk_', 'eleMas', 'physical_dmg_', 'anemo_dmg_', 'geo_dmg_', 'electro_dmg_', 'hydro_dmg_', 'pyro_dmg_', 'cryo_dmg_', 'dendro_dmg_'],
    circlet: ['hp_', 'def_', 'atk_', 'eleMas', 'critRate_', 'critDMG_', 'heal_'],
  };
  const SUB_KEYS = ['hp', 'hp_', 'atk', 'atk_', 'def', 'def_', 'eleMas', 'enerRech_', 'critRate_', 'critDMG_'];
  const PCT = k => k.endsWith('_');

  /* ---------- 画像処理 ---------- */

  function lumAt(d, i) { return 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2]; }

  function percentile(arr, p) {
    const a = Float32Array.from(arr).sort();
    return a[Math.min(a.length - 1, Math.max(0, Math.floor(p * (a.length - 1))))];
  }

  // 領域を「白地に黒文字」のグレースケールに正規化して、文字の外接矩形で切り出す
  function extract(d, W, x0, y0, x1, y1, mode) {
    const w = x1 - x0, h = y1 - y0;
    const v = new Float32Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = ((y0 + y) * W + (x0 + x)) * 4;
      v[y * w + x] = mode === 'white' ? Math.min(d[i], d[i + 1], d[i + 2]) : lumAt(d, i);
    }
    let bg, ink;
    if (mode === 'white') { bg = percentile(v, 0.5); ink = percentile(v, 0.995); }
    else { bg = percentile(v, 0.6); ink = percentile(v, 0.005); }
    const span = ink - bg;
    if (Math.abs(span) < 30) return null;
    const out = new Uint8Array(w * h);
    let bx0 = w, bx1 = -1, by0 = h, by1 = -1;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      let t = (v[y * w + x] - bg) / span;           // 0=背景, 1=文字
      t = t < 0.15 ? 0 : t > 0.85 ? 1 : (t - 0.15) / 0.7;
      out[y * w + x] = 255 - Math.round(t * 255);
      if (t > 0.5) { if (x < bx0) bx0 = x; if (x > bx1) bx1 = x; if (y < by0) by0 = y; if (y > by1) by1 = y; }
    }
    if (bx1 < 0) return null;
    bx0 = Math.max(0, bx0 - 2); by0 = Math.max(0, by0 - 2); bx1 = Math.min(w - 1, bx1 + 2); by1 = Math.min(h - 1, by1 + 2);
    const cw = bx1 - bx0 + 1, ch = by1 - by0 + 1, c = new Uint8Array(cw * ch);
    for (let y = 0; y < ch; y++) c.set(out.subarray((by0 + y) * w + bx0, (by0 + y) * w + bx0 + cw), y * cw);
    return { w: cw, h: ch, px: c };
  }

  function scaleGray(src, s) {
    const w = Math.max(1, Math.round(src.w * s)), h = Math.max(1, Math.round(src.h * s)), o = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) {
      const fy = Math.min(src.h - 1, (y + 0.5) / s - 0.5), y0 = Math.max(0, Math.floor(fy)), y1 = Math.min(src.h - 1, y0 + 1), wy = Math.max(0, fy - y0);
      for (let x = 0; x < w; x++) {
        const fx = Math.min(src.w - 1, (x + 0.5) / s - 0.5), x0 = Math.max(0, Math.floor(fx)), x1 = Math.min(src.w - 1, x0 + 1), wx = Math.max(0, fx - x0);
        const a = src.px[y0 * src.w + x0], b = src.px[y0 * src.w + x1], c = src.px[y1 * src.w + x0], e = src.px[y1 * src.w + x1];
        o[y * w + x] = (a * (1 - wx) + b * wx) * (1 - wy) + (c * (1 - wx) + e * wx) * wy;
      }
    }
    return { w, h, px: o };
  }

  // 文字と文字の間の空白列を広げる。「11」のように細い同じ字が続くと 1 字に潰れて読まれるのを防ぐ
  function spread(im, extra) {
    const blank = new Uint8Array(im.w);
    for (let x = 0; x < im.w; x++) { let b = 1; for (let y = 0; y < im.h; y++) if (im.px[y * im.w + x] < 150) { b = 0; break; } blank[x] = b; }
    const map = [];
    for (let x = 0; x < im.w; x++) {
      map.push(x);
      if (blank[x] && x + 1 < im.w && !blank[x + 1] && map.length > 1) for (let k = 0; k < extra; k++) map.push(-1);
    }
    const w = map.length, o = new Uint8Array(w * im.h).fill(255);
    for (let y = 0; y < im.h; y++) for (let x = 0; x < w; x++) if (map[x] >= 0) o[y * w + x] = im.px[y * im.w + map[x]];
    return { w, h: im.h, px: o };
  }

  // 1 行ぶんの画像を、余白つきの PGM (P5) にする
  function toPGM(line, targetH, gap) {
    const s = Math.min(3, targetH / line.h), im = scaleGray(gap ? spread(line, gap) : line, s), pad = 16;
    const W = im.w + pad * 2, H = im.h + pad * 2, body = new Uint8Array(W * H).fill(255);
    for (let y = 0; y < im.h; y++) body.set(im.px.subarray(y * im.w, (y + 1) * im.w), (y + pad) * W + pad);
    const head = `P5\n${W} ${H}\n255\n`, out = new Uint8Array(head.length + body.length);
    for (let i = 0; i < head.length; i++) out[i] = head.charCodeAt(i);
    out.set(body, head.length);
    return out;
  }

  /**
   * パネル画像 (410x530 RGBA) から OCR にかける行を切り出す。
   * 聖遺物パネルでなければ null。
   */
  function analyzePanel(d, W, H) {
    W = W || PANEL.w; H = H || PANEL.h;
    if (H <= BODY_H) return analyzeBody(d, W, H);
    // エリクシル産は、星の下に紫の帯「祈聖のエリクシルで生成」が入り、以降の表示が下にずれる。帯を抜いて通常の配置に戻す
    const band = [];
    for (let y = 225; y < 300; y++) {
      let c = 0;
      for (let x = 0; x < W; x += 2) { const i = (y * W + x) * 4; if (d[i + 2] > 200 && d[i + 2] > d[i] + 8 && d[i + 2] > d[i + 1] + 25) c++; }
      if (c > W / 2 * 0.6) band.push(y);
    }
    const elixir = band.length >= 20;
    let body = d;
    if (elixir) {
      const y0 = band[0], y1 = band[band.length - 1] + 1;
      body = new Uint8ClampedArray(W * BODY_H * 4);
      body.set(d.subarray(0, y0 * W * 4), 0);
      body.set(d.subarray(y1 * W * 4, (BODY_H + y1 - y0) * W * 4), y0 * W * 4);
    }
    const meta = analyzeBody(body, W, BODY_H);
    if (!meta) return null;
    meta.elixir = elixir;
    // 装備中は、パネル下端に淡い黄色の帯「（キャラ名）装備済」が出る
    let yellow = 0;
    for (let y = 765; y < 818 && y < H; y++) {
      let c = 0;
      for (let x = 60; x < 400; x += 2) { const i = (y * W + x) * 4; if (d[i] > 235 && d[i + 1] > 220 && d[i + 2] < 215 && d[i + 2] > 150) c++; }
      if (c > 170 * 0.5) yellow++;
    }
    meta.equipped = yellow >= 30;
    if (meta.equipped) { const im = extract(d, W, 62, 774, 400, 812, 'dark'); if (im) meta.lines.push({ kind: 'equip', im }); }
    return meta;
  }

  function analyzeBody(d, W, H) {
    // 本文エリアがベージュ地か
    let beige = 0, n = 0;
    for (let y = 300; y < 520; y += 4) for (let x = 200; x < 400; x += 4) {
      const i = (y * W + x) * 4; n++;
      if (d[i] > 205 && d[i + 1] > 195 && d[i + 2] > 175 && d[i] - d[i + 2] > 5 && d[i] - d[i + 2] < 60) beige++;
    }
    if (beige / n < 0.5) return null;

    // レア度: 星の数
    let stars = 0, run = 0;
    for (let x = 16; x < 200; x++) {
      let c = 0;
      for (let y = 198; y < 228; y++) { const i = (y * W + x) * 4; if (d[i] > 215 && d[i + 1] > 160 && d[i + 2] < 120) c++; }
      if (c >= 3) run++; else { if (run >= 8) stars++; run = 0; }
    }
    if (run >= 8) stars++;

    // ロック状態: アイコンの地色が暗い
    let lr = 0, ln = 0;
    for (let y = 253; y < 289; y++) for (let x = 262; x < 298; x++) { lr += d[(y * W + x) * 4]; ln++; }
    const lockVal = lr / ln, lock = lockVal < 175;

    const lines = [];
    const add = (kind, im, extra) => { lines.push(Object.assign({ kind, im }, extra)); };
    add('title', extract(d, W, 12, 6, 398, 46, 'white'));
    add('slot', extract(d, W, 18, 56, 240, 88, 'white'));
    add('mainLabel', extract(d, W, 18, 124, 250, 153, 'white'));
    add('mainValue', extract(d, W, 18, 152, 250, 196, 'white'));
    // レベル表示は濃紺地に白文字
    add('level', extract(d, W, 28, 262, 70, 280, 'white'));

    // 本文: 行の帯を検出
    const X0 = 16, X1 = 404, Y0 = 292;
    const samples = [];
    for (let y = Y0; y < H; y += 3) for (let x = 300; x < X1; x += 3) samples.push(lumAt(d, (y * W + x) * 4));
    const bgL = percentile(samples, 0.8);
    const rows = new Uint16Array(H);
    for (let y = Y0; y < H; y++) { let c = 0; for (let x = X0; x < X1; x++) if (bgL - lumAt(d, (y * W + x) * 4) > 30) c++; rows[y] = c; }
    const bands = [];
    let s = -1;
    for (let y = Y0; y <= H; y++) {
      const on = y < H && rows[y] >= 2;
      if (on && s < 0) s = y;
      if (!on && s >= 0) { if (bands.length && s - bands[bands.length - 1][1] <= 3) bands[bands.length - 1][1] = y; else bands.push([s, y]); s = -1; }
    }
    let foundSet = false;
    for (const [a, b] of bands) {
      if (b - a < 9 || b - a > 34) continue;
      let ink = 0, green = 0, dark = 0;
      for (let y = a; y < b; y++) for (let x = X0; x < X1; x++) {
        const i = (y * W + x) * 4, dl = bgL - lumAt(d, i);
        if (dl > 30) { ink++; dark += dl; if (d[i + 1] > d[i] + 18 && d[i + 1] > d[i + 2] + 18) green++; }
      }
      if (!ink) continue;
      const im = extract(d, W, X0, Math.max(Y0, a - 3), X1, Math.min(H, b + 3), 'dark');
      if (green / ink > 0.4) { add('set', im); foundSet = true; break; }
      add('sub', im, { darkness: dark / ink });
      if (lines.length > 12) break;
    }
    if (!foundSet) return null;
    return { stars, lock, lockVal, lines: lines.filter(l => l.im), missing: lines.filter(l => !l.im).map(l => l.kind) };
  }

  /* ---------- 文字列の照合 ---------- */

  function norm(s) {
    return (s || '').normalize('NFKC').replace(/\s+/g, '');
  }
  function lev(a, b) {
    const m = a.length, n = b.length;
    if (!m) return n; if (!n) return m;
    let prev = Array.from({ length: n + 1 }, (_, i) => i);
    for (let i = 1; i <= m; i++) {
      const cur = [i];
      for (let j = 1; j <= n; j++) cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      prev = cur;
    }
    return prev[n];
  }
  const dist = (a, b) => lev(a, b) / Math.max(a.length, b.length, 1);
  function best(text, cands) {      // cands: [[key, label]]
    let bk = null, bd = 9, second = 9;
    for (const [k, label] of cands) {
      const dd = dist(text, label);
      if (dd < bd) { second = bd; bd = dd; bk = k; } else if (dd < second) second = dd;
    }
    return { key: bk, d: bd, margin: second - bd };
  }

  // 行の最後（first=true なら最初）の数値を取り出す。小数点があれば % 表記とみなす（実数値はすべて整数表示のため）
  function parseNumber(s, first) {
    const t = s.replace(/[oOＯ]/g, '0').replace(/[lI|]/g, '1');
    const all = [...t.matchAll(/\d[\d,.]*/g)];
    if (!all.length) return null;
    const m = first ? all[0] : all[all.length - 1];
    let num = m[0].replace(/[.,]+$/, '');
    const pct = /[.,]\d$/.test(num) || /%/.test(t.slice(m.index));
    // % 表記の小数は 1 桁しかない。「%」を数字に読み違えた余分な桁は落とす
    num = pct ? num.replace(/,/g, '.').replace(/^(\d+\.\d)\d+$/, '$1') : num.replace(/[.,]/g, '');
    const v = parseFloat(num);
    return isNaN(v) ? null : { value: v, pct, index: m.index, raw: num };
  }

  // 「1」が潰れて読まれた場合の候補: 各「1」を「11」にした値
  function doubledOnes(raw) {
    const out = [];
    for (let i = 0; i < raw.length; i++) if (raw[i] === '1') out.push(parseFloat(raw.slice(0, i) + '1' + raw.slice(i)));
    return [...new Set(out)];
  }

  const mainDisplay = (key, v) => PCT(key) ? Math.round(v * 1000) / 10 : Math.round(v);
  const clean = s => (s || '').replace(/[^A-Za-z0-9぀-ヿ一-鿿]/g, '');

  const SUB_LABELS = [['hp', 'HP'], ['atk', '攻撃力'], ['def', '防御力'], ['eleMas', '元素熟知'], ['enerRech_', '元素チャージ効率'], ['critRate_', '会心率'], ['critDMG_', '会心ダメージ']];
  const SET_LIST = Object.entries(D.sets).map(([k, v]) => [k, v.n]);
  // 旅人は元素違いをまとめて 1 人として扱う（GOOD 形式でのキーは Traveler）
  const CHAR_LIST = Object.entries(D.chars || {}).filter(([k]) => !k.startsWith('Traveler')).concat([['Traveler', '旅人']]);
  const CHAR_NAME = Object.fromEntries(CHAR_LIST);

  // サブステータス値が取り得る値か。戻り値は最小の強化回数（不正なら 0）
  function rollsOf(rarity, key, value) {
    const list = (D.subs[rarity] || {})[key];
    if (!list) return -1;                         // 検証データなし
    const hit = list.find(e => Math.abs(e[0] - value) < 0.051);
    return hit ? hit[1] : 0;
  }

  // サブステータス 1 行を解釈する。single=true なら 1 回ぶんの値しか認めない
  function readSub(text, rarity, single) {
    let t = text.replace(/^[^A-Za-z0-9぀-ヿ一-鿿]+/, '');
    let pending = false;
    const paren = t.search(/[(（《〈]/);
    if (paren > 0) { pending = true; t = t.slice(0, paren); }
    const num = parseNumber(t);
    if (!num) return null;
    const pre = t.slice(0, num.index), hasPlus = /[+＋]$/.test(pre);
    const m = best(clean(pre.replace(/[十tT†ユ]+$/, '')), SUB_LABELS);
    let key = m.key;
    if (key === 'hp' || key === 'atk' || key === 'def') key = num.pct ? key + '_' : key;
    // 候補値: 「+」を「1」と読み違えた場合と、小数点を落とした場合を含める
    const cands = [num.value];
    if (/^1\d/.test(num.raw)) { const v = parseFloat(num.raw.slice(1)); if (hasPlus) cands.push(v); else cands.unshift(v); }
    if (PCT(key) && !/\./.test(num.raw)) cands.push(num.value / 10);
    cands.push(...doubledOnes(num.raw));
    const one = single || pending;
    let value = null, rolls = 0;
    for (const c of cands) {
      const r = rollsOf(rarity, key, c);
      if (r === -1 || (r > 0 && (!one || r === 1))) { value = c; rolls = r; break; }
    }
    return { key, value: value === null ? num.value : value, valid: value !== null, repaired: value !== null && value !== num.value, rolls, pending, nameDist: m.d };
  }

  /**
   * analyzePanel の行情報と、各行の OCR 文字列から聖遺物 1 個を組み立てる。
   * texts[i] は文字列、文字列の配列（読み直しを含む候補）、または未読なら undefined。
   * 戻り値: { art, issues, want, retry } または null（聖遺物として解釈できない）
   *   want  … 追加で読むべき行の種類（'title' / 'level'）
   *   retry … 値が不正で読み直すべきサブステータス行の番号
   */
  function parseArtifact(meta, texts) {
    const issues = [], want = [], retry = [];
    const by = {}; const subs = [];
    meta.lines.forEach((l, i) => {
      const alts = (Array.isArray(texts[i]) ? texts[i] : [texts[i]]).filter(x => x !== undefined).map(norm);
      if (l.kind === 'sub') subs.push({ alts, darkness: l.darkness, i });
      else if (alts.length) { by[l.kind] = alts[0]; if (l.kind === 'mainValue') by.mainAlts = alts; }
    });
    const has = k => meta.lines.some(l => l.kind === k);

    // 部位
    const slot = best(clean(by.slot), Object.entries(SLOTS));
    if (slot.d > 0.67) return null;
    const slotKey = slot.key;

    // セット: セット名の行と、部位名（タイトル）で照合
    const setText = clean(by.set);
    let setKey = null, sd = 9, second = 9;
    for (const [k, name] of SET_LIST) {
      const piece = D.sets[k].p[slotKey];
      if (!piece) continue;
      const score = dist(setText, clean(name)) + (by.title !== undefined ? 0.5 * dist(clean(by.title), clean(piece)) : 0);
      if (score < sd) { second = sd; sd = score; setKey = k; } else if (score < second) second = score;
    }
    if (setKey === null || sd > 1.0) return null;
    if (sd > 0.34 || second - sd < 0.2) {
      if (by.title === undefined && has('title')) want.push('title');
      else if (sd > 0.9 || second - sd < 0.15) issues.push('セット名の読み取りが不確か');
    }

    let rarity = meta.stars;
    if (!(rarity >= 1 && rarity <= 5)) { rarity = 5; issues.push('レア度を判定できず★5と仮定'); }

    // メインステータス
    const mainAlts = (by.mainAlts || []).map(t => parseNumber(t, true)).filter(Boolean);
    let mv = mainAlts[0] || null;
    let mainStatKey;
    if (slotKey === 'flower' || slotKey === 'plume') mainStatKey = MAIN_BY_SLOT[slotKey][0];
    else {
      const all = MAIN_BY_SLOT[slotKey].map(k => [k, D.stat[k]]);
      const cands = mv ? all.filter(([k]) => (k === 'eleMas') !== mv.pct) : all;
      const m = best(clean(by.mainLabel), cands.length ? cands : all);
      mainStatKey = m.key;
      if (m.d > 0.5 || (m.margin < 0.12 && cands.length > 1)) issues.push('メインステータスの読み取りが不確か');
    }

    // レベル: メインステータスの数値（レベルごとに決まっている）と、レベル表示の両方で決める
    const table = (D.main[rarity] || {})[mainStatKey] || [];
    const shown = table.map(v => PCT(mainStatKey) ? mainDisplay(mainStatKey, v).toFixed(1) : String(mainDisplay(mainStatKey, v)));
    const lm = (by.level || '').replace(/[oOＯ]/g, '0').match(/(\d{1,2})/);
    const badge = lm && +lm[1] <= 20 ? +lm[1] : null;
    let level = null, exact = false;
    for (const alt of mainAlts) {
      const raw = alt.raw;
      const hits = shown.map((t, L) => t === raw ? L : -1).filter(L => L >= 0);
      if (hits.length === 1) { level = hits[0]; exact = true; break; }
      if (hits.length > 1 && hits.includes(badge)) { level = badge; exact = true; break; }
    }
    if (!exact) {
      if (mainAlts.length < 2 && has('mainValue')) want.push('mainValue');      // 字間を変えて読み直す
      else {
        // 1 文字違いまでなら表の値に寄せる
        const near = shown.map((t, L) => [L, Math.min(...mainAlts.map(a => lev(a.raw, t)), 9)]).filter(x => x[1] <= 1).map(x => x[0]);
        // 字が落ちただけ（「311」→「3」）なら、レベル表示のほうを信じる
        const sub = (a, b) => { let i = 0; for (const c of b) if (c === a[i]) i++; return a.length > 0 && i === a.length; };
        const partial = badge !== null && shown[badge] !== undefined && mainAlts.some(a => sub(a.raw, shown[badge]));
        if (badge !== null && (near.includes(badge) || partial || !shown.length)) level = badge;
        else if (near.length === 1 && badge === null) level = near[0];
        else { level = badge !== null ? badge : (near.length ? near[0] : 0); issues.push('レベルを確定できず'); }
      }
    } else if (badge !== null && badge !== level) issues.push('レベル表示とメインステータス値が合わない');

    // サブステータス
    const substats = [];
    const single = level === 0;
    for (const s of subs) {
      if (!s.alts.length) continue;
      const first = s.alts[0];
      if (!/\d/.test(first) && /[待化アブ]/.test(first)) { // 折り返した「（アクティブ化待ち）」
        if (substats.length) substats[substats.length - 1].pending = true;
        continue;
      }
      const pendingByColor = s.darkness < 90;
      const reads = s.alts.map(a => readSub(a, rarity, single || pendingByColor)).filter(Boolean);
      const good = reads.filter(x => x.valid);
      let r = good[0] || reads[0] || null;
      if (good.length > 1 && good.some(x => x.value !== good[0].value)) {
        // 字が潰れると桁が減るので、桁の多い読みを採る
        r = good.reduce((m, x) => String(x.value).length > String(m.value).length ? x : m, good[0]);
        issues.push(`${D.stat[r.key]} の値が読み方によって違う（${[...new Set(good.map(x => x.value))].join(' / ')}）`);
      }
      if (!r) { if (s.alts.length < 2) retry.push(s.i); else issues.push(`サブステータスを読めず: ${first}`); continue; }
      // 「1」を含む値は潰れやすいので、字間を広げた読み直しで確かめる
      if (s.alts.length < 2 && (!r.valid || /1/.test(String(r.value)) || r.repaired)) retry.push(s.i);
      if (pendingByColor) r.pending = true;
      if (!r.valid && s.alts.length >= 2) {
        issues.push(`${D.stat[r.key]}+${r.value}${PCT(r.key) ? '%' : ''} はあり得ない値`);
      }
      if (r.nameDist > 0.5) issues.push(`サブステータス名が不確か: ${first}`);
      substats.push(r);
    }
    if (!substats.length) return null;
    if (substats.length > 4) issues.push('サブステータスが5行以上');
    const keys = substats.map(s => s.key);
    if (new Set(keys).size !== keys.length) issues.push('サブステータスが重複');
    if (keys.includes(mainStatKey)) issues.push('メインとサブが同じステータス');
    const active = substats.filter(s => !s.pending);
    if (rarity === 5 && substats.length < 4 && !want.length) issues.push('サブステータスの行数が不足');
    const used = active.reduce((n, s) => n + Math.max(1, s.rolls), 0);
    if (used > (rarity - 1) + Math.floor(level / 4) && !retry.length) issues.push('強化回数とサブステータス値が合わない');

    // 装備キャラ
    let location = '';
    if (meta.equipped) {
      const t = clean((by.equip || '').replace(/装.{0,2}済.*$/, '').replace(/[装備済]+$/, ''));
      const m = best(t, CHAR_LIST);
      if (t && m.d <= 0.5) location = m.key; else issues.push('装備キャラの名前を読めず: ' + (by.equip || ''));
      if (location && m.d > 0.34 && m.margin < 0.15) issues.push('装備キャラの名前が不確か');
    }

    const art = {
      setKey, slotKey, level, rarity, mainStatKey, location, lock: !!meta.lock,
      substats: active.map(({ key, value }) => ({ key, value })),
    };
    const un = substats.filter(s => s.pending).map(({ key, value }) => ({ key, value }));
    if (un.length) art.unactivatedSubstats = un;
    if (meta.elixir) art.elixirCrafted = true;
    return { art, issues, want, retry };
  }

  /**
   * 1 個ぶんの読み取り手順。ocr(行画像, 目標の高さ) は文字列を返す非同期関数。
   * まず必要最小限の行を読み、照合が不確かなときだけ追加の行や読み直しを行う。
   */
  /**
   * 1 個ぶんの読み取り手順。ocr(行画像, 目標の高さ, 字間の広げ幅) は文字列を返す非同期関数。
   * まず全行を 1 回ずつ読み、照合が不確かな行だけ条件を変えて読み直す。
   */
  async function readArtifact(meta, ocr) {
    const texts = new Array(meta.lines.length);
    const H = k => k === 'mainValue' ? 48 : 44;
    for (let i = 0; i < meta.lines.length; i++) {
      const k = meta.lines[i].kind;
      if (k !== 'title') texts[i] = await ocr(meta.lines[i].im, k === 'mainValue' ? 30 : H(k), k === 'mainValue' ? 4 : 0);
    }
    let p = parseArtifact(meta, texts);
    for (let round = 0; p && round < 2 && (p.want.length || p.retry.length); round++) {
      for (let i = 0; i < meta.lines.length; i++) {
        const k = meta.lines[i].kind;
        if (!p.want.includes(k)) continue;
        if (k === 'mainValue') texts[i] = [texts[i], await ocr(meta.lines[i].im, 48, 0), await ocr(meta.lines[i].im, 40, 8)];
        else texts[i] = await ocr(meta.lines[i].im, H(k), 0);
      }
      for (const i of p.retry) texts[i] = [texts[i], await ocr(meta.lines[i].im, 44, 3)];
      p = parseArtifact(meta, texts);
    }
    return p ? { art: p.art, issues: p.issues, texts } : { art: null, issues: [], texts };
  }

  const artKey = a => [a.setKey, a.slotKey, a.level, a.rarity, a.mainStatKey,
    a.substats.map(s => s.key + s.value).join(','), (a.unactivatedSubstats || []).map(s => s.key + s.value).join(',')].join('|');

  // 評価アプリ「聖遺物ラボ：キャラ」の引っ越しデータ形式で、装備中のキャラごとにまとめる
  const LAB_STAT = { hp: 'HP', atk: 'ATK', def: 'DEF', hp_: 'HP%', atk_: 'ATK%', def_: 'DEF%', enerRech_: 'ER', eleMas: 'EM', critRate_: 'CR', critDMG_: 'CD', heal_: 'HEAL', physical_dmg_: 'PHYS',
    pyro_dmg_: 'DMG_炎', hydro_dmg_: 'DMG_水', cryo_dmg_: 'DMG_氷', electro_dmg_: 'DMG_雷', anemo_dmg_: 'DMG_風', geo_dmg_: 'DMG_岩', dendro_dmg_: 'DMG_草' };
  function toLab(arts, date) {
    const by = new Map();
    for (const a of arts) {
      if (!a.location) continue;
      if (!by.has(a.location)) by.set(a.location, []);
      by.get(a.location).push(a);
    }
    const chars = [];
    for (const [key, list] of by) {
      const pieces = {}, count = {};
      for (const a of list) {
        const subs = a.substats.concat(a.unactivatedSubstats || []).map(x => ({ s: LAB_STAT[x.key], v: String(x.value) }));
        while (subs.length < 4) subs.push({ s: '', v: '' });
        pieces[a.slotKey] = { main: LAB_STAT[a.mainStatKey], subs: subs.slice(0, 4) };
        count[a.setKey] = (count[a.setKey] || 0) + 1;
      }
      const set = Object.entries(count).sort((x, y) => y[1] - x[1]).filter(e => e[1] >= 2).map(e => D.sets[e[0]].n + (e[1] >= 4 ? '4' : '2')).join('＋');
      chars.push({ id: 'scan-' + key, name: CHAR_NAME[key] || key, set, pieces, date });
    }
    return { app: 'genshin-lab-chars', v: 1, at: new Date().toISOString(), chars };
  }

  /**
   * 並び順の番号を決める。cols[i] は i 番目に映った聖遺物のときのカーソルの列（0〜9、不明なら -1）。
   * 右へ 1 つずつ送る前提で、列のずれが次の聖遺物でも続いたときだけ「飛ばした」「同じ枠をもう一度映した」とみなす。
   * 1 回きりのずれは、カーソルの検出ミスとして無視する。
   */
  function numberCells(cols) {
    const n = cols.length, no = new Array(n).fill(0), missed = [];
    const f = cols.findIndex(c => c >= 0);
    if (f < 0) return { no, missed, known: false };
    let offset = ((cols[f] - f) % 10 + 10) % 10;                 // 番号 = 映った順 + offset + 1
    for (let i = 0; i < n; i++) {
      const c = cols[i];
      if (c >= 0) {
        const e = (i + offset) % 10;
        if (c !== e) {
          let d = ((c - e) % 10 + 10) % 10; if (d > 5) d -= 10;
          let j = i + 1; while (j < n && cols[j] < 0) j++;
          if (j < n && cols[j] === (((j + offset + d) % 10) + 10) % 10) {
            for (let k = 0; k < d; k++) missed.push(i + offset + 1 + k);
            offset += d;
          }
        }
      }
      no[i] = i + offset + 1;
    }
    return { no, missed, known: true };
  }

  /**
   * 並び順の番号を決める（拾い直しの結果を使う版）。
   * fix[i] は i 番目と i+1 番目の境目を 1 コマずつ確かめた結果: { mids: 間にあった個数 } か { same: true }（同じ枠のまま）。
   * 確かめていない境目は 1 つ進んだものとする。
   */
  function numberSeq(cols, fix) {
    const n = cols.length, no = new Array(n).fill(0);
    const f = cols.findIndex(c => c >= 0);
    if (f < 0) return { no, known: false };
    const colOf = v => ((v - 1) % 10 + 10) % 10;
    const step = i => { const x = fix[i]; return x ? (x.same ? 0 : 1 + x.mids) : 1; };
    // 最初に列が分かったところで、番号と列の対応を決める
    let before = 0; for (let i = 0; i < f; i++) before += step(i);
    no[0] = ((cols[f] - before) % 10 + 10) % 10 + 1;
    for (let i = 1; i < n; i++) {
      const x = fix[i - 1];
      no[i] = no[i - 1] + (x ? (x.same ? 0 : 1 + x.mids) : 1);
    }
    return { no, known: true };
  }

  function toGOOD(arts) {
    return { format: 'GOOD', version: 3, source: 'Seiibutsu Video Scanner', artifacts: arts };
  }

  g.GSCAN = { PANEL, numberCells, numberSeq, CHAR_NAME, toLab, SLOTS, SUB_KEYS, analyzePanel, parseArtifact, readArtifact, toPGM, artKey, toGOOD, norm, PCT };
})(typeof self !== 'undefined' ? self : globalThis);
