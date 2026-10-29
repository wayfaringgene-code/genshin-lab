# 命ノ星座カード（単品アプリ）を、聖遺物厳選ラボの最新版から組み立てる。
# 使い方: python3 build_card.py <ラボのHTML> <出力のHTML>
# 方針：計算・取り込み・カード描画はラボのコードをそのまま使い（LAB_MODE='card'）、
#       画面だけをページ切り替え（キャラ一覧／カード／動画から取り込む／設定）に組み替える。
#       v1.1：動画から取り込む（scan/ に置いたビデオスキャナーを枠で動かす。scan/ は build_scan.py で作る）、育成途中の聖遺物（lv・未発動OP）。
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (old[:80], n)
    s = s.replace(old, new)

# --- 題名とモード ---
rep('<title>聖遺物厳選ラボ</title>', '<title>命ノ星座カード</title>')
rep("<script>\n(function(){", "<script>window.LAB_MODE='card';</script>\n<script>\n(function(){")
rep("const $=id=>document.getElementById(id);",
    "const $=id=>document.getElementById(id);\nconst CARD_APP=window.LAB_MODE==='card'; // 単品のカードアプリとして動かす")

# --- 単位：カードアプリでは英語（DAYS／MONTHS／YEARS）だけ ---
rep("function fmtWait(d,L){ L=WAIT_UNITS[L]?L:'jp';",
    "function fmtWait(d,L){ L=WAIT_UNITS[L]?L:(CARD_APP?'en3c':'jp');")

# --- 一覧の行を押したら、カードのページへ ---
rep("if(CH_OPEN) $('chList').scrollIntoView({behavior:'smooth',block:'nearest'}); };",
    "if(CH_OPEN){ if(CARD_APP) cardShowPage('card'); else $('chList').scrollIntoView({behavior:'smooth',block:'nearest'}); } };")
rep("const go=()=>{ CH_OPEN=CH_OPEN===b.dataset.open?null:b.dataset.open;",
    "const go=()=>{ CH_OPEN=(CH_OPEN===b.dataset.open&&!CARD_APP)?null:b.dataset.open;")

# --- 一覧の並び：高い順・低い順・追加した順を切り替え（記憶）。カードのページの ◀▶・プルダウンも同じ並び（v1.3） ---
rep("$('chTimeline').innerHTML=rows.length?tlf(rows.slice().sort((a,b)=>(a.st.age||0)-(b.st.age||0))):",
    "$('chTimeline').innerHTML=rows.length?tlf(CARD_APP?cardListSort(rows):rows.slice().sort((a,b)=>(a.st.age||0)-(b.st.age||0))):")

# --- カードアプリでは見えない部分の計算を飛ばす（山の全景・天球図・キャラの詳細のグラフ・有効OPの見直しの表）（v1.3） ---
rep("{ const sk=$('chSky'); if(sk) sk.innerHTML=", "if(!CARD_APP){ const sk=$('chSky'); if(sk) sk.innerHTML=")
rep("$('chPano').innerHTML=rows.some(", "if(!CARD_APP) $('chPano').innerHTML=rows.some(")
rep("${charDetailHTML(c,st)}", "${CARD_APP?'':charDetailHTML(c,st)}")
rep("{ const er=$('effRev'); if(er){", "{ const er=$('effRev'); if(er&&!CARD_APP){")

# --- 保存場所の共有：GitHub Pages ではキャラ版（ルート）とカードアプリ（/card/）が同じ保存場所を使う（v1.5） ---
#     キャラのデータは共有したいが、見た目の設定は書き換えない：カードアプリは cardVar・tlStyle を保存せず、決まった値で描く
assert s.count("store.get('cardVar','X3G')") == 5
s = s.replace("store.get('cardVar','X3G')", "(CARD_APP?'SK':store.get('cardVar','X3G'))")
rep("const tls=store.get('tlStyle','score')", "const tls=CARD_APP?'score':store.get('tlStyle','score')")

# --- 描画のたびに、カードをカードのページへ移す（描画の前に前回のカードを外し、idの重複を防ぐ） ---
rep("function renderChars(){\n  const rows=CHARS.map(c=>({c,st:charStats(c)}));", "function renderChars(){\n  if(CARD_APP&&$('cardHost')) $('cardHost').innerHTML='';\n  const rows=CHARS.map(c=>({c,st:charStats(c)}));")
rep("$('evCompare').value=''; showTab('eval'); }));\n}\n/* ---------- 目標から逆算", "$('evCompare').value=''; showTab('eval'); }));\n  if(CARD_APP) cardAfterRender();\n}\n/* ---------- 目標から逆算")

# --- 立ち絵を端末に保存する（選んだとき・大きさ・位置を変えたとき） ---
rep("const id=CH_OPEN; CARD_IMG[id]=rd.result; delete CARD_FIT[id]; delete CARD_POS[id];",
    "const id=CH_OPEN; CARD_IMG[id]=rd.result; delete CARD_FIT[id]; delete CARD_POS[id]; portraitSave(id);")
rep("CARD_ZOOM[id]=+cz.value; fitCardArt(", "CARD_ZOOM[id]=+cz.value; portraitSave(id); fitCardArt(")
rep("const end=()=>{ drag=null; svg.style.cursor='grab'; };",
    "const end=()=>{ if(drag) portraitSave(id); drag=null; svg.style.cursor='grab'; };")
rep("svg.addEventListener('dblclick',e=>{ CARD_POS[id]={dx:0,dy:0};",
    "svg.addEventListener('dblclick',e=>{ CARD_POS[id]={dx:0,dy:0}; portraitSave(id);")

# --- 貼り付けで取り込み：キャラの画面が隠れていても受け付ける ---
rep("if($('view-chars').hidden) return;", "if(!CARD_APP&&$('view-chars').hidden) return;")

# --- 育成途中の聖遺物（v1.1）：部位に lv（0〜20、省略は+20）、未発動のサブOPに off:true ---
#     いまの値で評価する（見込みは足さない）。ロール数の逆算は「1個を評価」タブと同じ仮説の立て方。
_i = s.find('function estPiece(main,subs){'); _j = s.find('\nfunction charMainKeys', _i)
assert _i > 0 and _j > _i
s = s[:_i] + r"""function estPiece(main,subs,lv){ // 1個：表示値からロール数を逆算 → {ok, four, det:[{s,n,u}], lv, up, pend}（uは10%単位の推定）
  // lv＝レベル（省略は+20）。subs[i].off＝まだ付いていないサブOP（+0の3OPの4つ目）：種類だけ持ち、数えない
  lv=(lv==null||lv==='')?20:Math.max(0,Math.min(20,Math.floor(+lv/4)*4)); const k=lv/4;
  if(!main||subs.length!==4) return {ok:false,msg:'未入力'};
  const act=subs.filter(x=>!x.off), pend=4-act.length;
  if(pend>1||(pend&&lv>0)) return {ok:false,msg:'未発動のサブOPは、+0のときの4つ目だけです'};
  if(act.some(x=>x.v===''||isNaN(parseFloat(x.v)))) return {ok:false,msg:'サブOPの値が未入力'};
  if(new Set(subs.map(x=>x.s)).size<4||subs.some(x=>x.s===main)) return {ok:false,msg:'サブOPが重複'};
  const nS=act.length, MA=act.map(x=>matches(x.s,x.v)); let best=null;
  // 仮説：[初期4OPか, 付いているサブOPに入ったロールの合計, 事前確率]。+0で4つ付いていれば4OP、未発動があれば3OP
  const hyps=pend?[[false,3,1]]:lv===0?[[true,4,1]]:[[true,4+k,S.p4],[false,3+k,1-S.p4]];
  for(const [four,R,pw] of hyps){ const U=R-nS;
    (function rec(i,left,ns){
      if(i===nS){ if(left!==0) return; let fact=1; for(let q=1;q<=U;q++) fact*=q; let den=1; for(const n of ns) for(let q=1;q<=n-1;q++) den*=q;
        let sc=fact/den/Math.pow(4,U)*pw; for(let q=0;q<nS;q++) sc*=MA[q][ns[q]].L; if(!best||sc>best.sc) best={sc,ns:ns.slice(),four,R}; return; }
      for(let n=1;n<=Math.min(6,left-(nS-1-i));n++){ if(!MA[i][n].cnt) continue; ns.push(n); rec(i+1,left-n,ns); ns.pop(); }
    })(0,R,[]); }
  if(!best) return {ok:false,msg:lv<20?`+${lv}でこの値になる伸び方がない（レベルを確かめてください）`:'この値になる伸び方がない'};
  const det=act.map((x,i)=>{ const m=MA[i][best.ns[i]]; let eu=0,c=0; for(const [uu,cc] of m.rv){ eu+=uu*cc; c+=cc; } return {s:x.s,n:best.ns[i],u:eu/c}; });
  return {ok:true,four:best.four,det,lv,up:best.R-nS,pend:pend>0};
}
function exactPiece(p){ // ロールの内訳が分かっている1個（Enka から取り込んだもの）：p.rolls={OP:[段,…]}（段0〜3＝70〜100%）。合わなければ null（推定に戻す）
  const R=p&&p.rolls; if(!R||!p.subs) return null; const lv=p.lv==null?20:+p.lv;
  const act=p.subs.filter(x=>x.s&&!x.off), det=act.map(x=>{ const t=R[x.s]||[]; return {s:x.s,n:t.length,u:t.reduce((a,v)=>a+7+v,0)}; });
  if(!act.length||det.some(d=>!d.n)) return null;
  const tot=det.reduce((a,d)=>a+d.n,0), init=tot-Math.floor(lv/4);
  return {ok:true,four:init>=4,det,lv,up:tot-act.length,pend:p.subs.some(x=>x.off),exact:true};
}""" + s[_j:]
rep("est=estPiece(p.main,p.subs); if(est.ok) rv=", "est=exactPiece(p)||estPiece(p.main,p.subs,p.lv); if(est.ok) rv=")
rep("for(const x of p.subs){ const v=parseFloat(x.v); if(isNaN(v)) continue;",
    "for(const x of p.subs){ if(x.off) continue; const v=parseFloat(x.v); if(isNaN(v)) continue;")
rep(".filter(q=>q.s==='CR'||q.s==='CD').length", ".filter(q=>!q.off&&(q.s==='CR'||q.s==='CD')).length")
# カード：部位の見出しに「+8」の印。未発動のサブOPは薄く、点線の丸と「未発動」。強化回数の分母はそのレベルまでの回数
rep("${eq?esc(MAIN_SHORT(p.main)):'未装備'}</tspan></text>",
    "${eq?esc(MAIN_SHORT(p.main)):'未装備'}</tspan>${eq&&p.lv!=null&&+p.lv<20?`<tspan dx=\"8\" font-family='${mono}' font-size=\"12\" font-weight=\"700\" fill=\"#e8a15a\">+${+p.lv}</tspan>`:''}</text>")
rep("subs.forEach((q,i)=>{ const on=effS.has(q.s), lab=SUBS_SHORT[q.s]||q.s",
    "subs.forEach((q,i)=>{ const g0=g.length, on=effS.has(q.s), lab=SUBS_SHORT[q.s]||q.s")
rep("g+=`</g>`; } });\n      if(det){ const U=x.est.four?5:4,",
    "g+=`</g>`; }\n        if(q.off) g=g.slice(0,g0)+`<g opacity=\".5\"><title>${JP[q.s]||lab}：まだ付いていないサブOP（+4で付く）。数えていません</title>`+g.slice(g0)+`<circle cx=\"${cx+13}\" cy=\"${y1+20.5}\" r=\"5.9\" fill=\"none\" stroke=\"${bc}\" stroke-width=\".9\" stroke-dasharray=\"2 1.6\"/></g><text x=\"${cx+4}\" y=\"${y1+60}\" font-family='${sans}' font-size=\"9\" fill=\"#8a93a6\">未発動</text>`; });\n      if(det){ const U=x.est.up!=null?x.est.up:(x.est.four?5:4),")
# 編集：部位ごとにレベル、+0なら4つ目の「未発動」
rep('<span class="note" id="ceR_${slot}"></span></div>`',
    '<select data-lv="${slot}" aria-label="${SLOT_JP[slot]}のレベル" style="padding:3px 6px">${[20,16,12,8,4,0].map(l=>`<option value="${l}"${l===(p.lv==null?20:+p.lv)?\' selected\':\'\'}>+${l}</option>`).join(\'\')}</select><span class="note" id="ceR_${slot}"></span></div>`')
rep('aria-label="${SLOT_JP[slot]}のサブOP${i+1}の値"></div>`',
    'aria-label="${SLOT_JP[slot]}のサブOP${i+1}の値">${i===3&&(p.lv!=null&&+p.lv===0)?`<label class="note" style="grid-column:1/-1;display:flex;gap:6px;align-items:center"><input type="checkbox" data-off="${slot}"${x.off?\' checked\':\'\'}>4つ目はまだ付いていない（未発動）</label>`:\'\'}</div>`')
rep("c.pieces[slot]={main,subs}; } }",
    "const lvEl=q(`[data-lv=\"${slot}\"]`), lv=lvEl?+lvEl.value:20, offEl=q(`[data-off=\"${slot}\"]`); if(lv===0&&offEl&&offEl.checked) subs[3].off=true;\n    const old=c.pieces[slot], np=lv<20?{main,subs,lv}:{main,subs}; if(old&&old.rolls&&old.main===main&&(old.lv==null?20:+old.lv)===lv&&JSON.stringify(old.subs.filter(x=>x.s).map(x=>[x.s,x.v]))===JSON.stringify(subs.map(x=>[x.s,x.v]))) np.rolls=old.rolls;\n    c.pieces[slot]=np; } }")
rep("const mainChanged=el.dataset.main;", "const mainChanged=el.dataset.main||el.dataset.lv;")
rep("const e=estPiece(p.main,p.subs); el.innerHTML=", "const e=exactPiece(p)||estPiece(p.main,p.subs,p.lv); el.innerHTML=")
rep('<p class="note">+20の聖遺物の表示値をそのまま入れます（%系は小数第1位）。',
    '<p class="note">ゲームの表示値をそのまま入れます（%系は小数第1位）。+20になっていない部位はレベルを選びます（いまの値で評価し、カードに「+8」などの印が付きます）。')

# --- 空の部位（サブOPの値が1つもない部位）は「まだなし」：保存するときに外し、計算でもメインOPを使わない（v1.3） ---
#     以前は、編集で保存すると空の冠が「会心率の冠」として残り、狙いのメインOP（会心率 or 会心ダメージ）の条件が変わって秘境レベルがずれていた
rep("function charMainKeys(c,slot){ const p=c.pieces[slot]; if(p&&p.main) return [p.main];",
    "function charMainKeys(c,slot){ const p=c.pieces[slot]; if(p&&p.main&&(p.subs||[]).some(x=>x.v!=='')) return [p.main];")
rep("$('ceSave').addEventListener('click',()=>{ editorRead(); delete CH_EDIT.effGuess;",
    "$('ceSave').addEventListener('click',()=>{ editorRead(); for(const k of SLOTS){ const q=CH_EDIT.pieces[k]; if(q&&!(q.subs||[]).some(x=>x.v!=='')) delete CH_EDIT.pieces[k]; } delete CH_EDIT.effGuess;")

# --- カード画像：まとめて保存のために、保存せずに中身だけ返す呼び方（opt.blobOnly） ---
rep("async function cardExport(fmt,msg){", "async function cardExport(fmt,msg,opt){ opt=opt||{};")
rep("const r=await saveBlob(`命ノ星座_${nm}_${ds}.${ext}`,blob);", "const fname=`命ノ星座_${nm}_${ds}.${ext}`; if(opt.blobOnly) return {blob,name:fname,fontOk}; const r=await saveBlob(fname,blob);")

# --- カードの下に、サイトの名前とURL（共有された画像から来られるように）（v2.0） ---
# 定義の文はカードアプリでは短くし、日付・アプリ名・URLは右下に右寄せで別に置く（長いと枠からはみ出すため）
rep("＝このキャラ（メインOP・有効OP）の条件で、この有効RV（${Math.round(st.tot)}%）を秘境だけで揃えるのにかかる日数。強さではなく「聖遺物の珍しさ」の物差し<tspan fill=\"#6f7a8e\" font-size=\"10\" dx=\"12\">聖遺物ラボ ${c.date||''}</tspan></text>`;",
    "${CARD_APP?`＝この有効RV（${Math.round(st.tot)}%）を秘境だけで揃えるのにかかる日数。強さではなく「珍しさ」の物差し</text><text x=\"${W-40}\" y=\"${H-23}\" text-anchor=\"end\" font-family='${sans}' font-size=\"10.5\" fill=\"#8a93a6\" letter-spacing=\".02em\">${esc(c.date||'')}<tspan dx=\"10\" fill=\"#e9d39a\" font-weight=\"700\">命ノ星座カード</tspan><tspan dx=\"8\">wayfaringgene-code.github.io/genshin-lab</tspan></text>`:`＝このキャラ（メインOP・有効OP）の条件で、この有効RV（${Math.round(st.tot)}%）を秘境だけで揃えるのにかかる日数。強さではなく「聖遺物の珍しさ」の物差し<tspan fill=\"#6f7a8e\" font-size=\"10\" dx=\"12\">聖遺物ラボ ${c.date||''}</tspan></text>`}`;")

# --- 起動 ---
rep("showTab(CHARS_ONLY?'chars':TABS.includes(h0)?h0:'sim');",
    "showTab((CHARS_ONLY||CARD_APP)?'chars':TABS.includes(h0)?h0:'sim');\nif(CARD_APP) cardAppInit();")

CSS = r"""
<style>
/* ===== 命ノ星座カード（単品アプリ） ===== */
.mode-card header.top .tabs:not(.cnav), .mode-card section.settings, .mode-card #view-chars{display:none!important}
.mode-card #cardHost .chdetail{border-top:0!important; padding:0!important; animation:none}
.mode-card #cardHost .chdetail > .row, .mode-card #cardHost .chdetail > p.note{display:none}
.mode-card .wrap > p.note{display:none}
.cnav button[disabled]{opacity:.45; cursor:default}
.cnav button small{font-size:10px; margin-left:4px; color:var(--muted)}
.cpage[hidden]{display:none!important}
/* 動画のページは、隠しても画面の外で描画を続ける（読み取り中にほかのページを見ても止まらないように） */
#pg-scan.cpage[hidden]{display:block!important; position:absolute; left:-20000px; top:0; width:1100px}
.ctool{display:flex; flex-wrap:wrap; gap:8px; align-items:center; justify-content:space-between}
.ctool .grp2{display:flex; flex-wrap:wrap; gap:8px; align-items:center}
.ctool select{min-width:11em}
.cthumbs{display:grid; grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:10px}
.cthumb{border:1px solid var(--line); border-radius:8px; padding:8px; background:var(--inset); display:grid; gap:6px; justify-items:center; font-size:12px}
.cthumb img{height:110px; width:100%; object-fit:contain}
.ckv{display:grid; grid-template-columns:max-content 1fr; gap:6px 18px; font-size:14px; margin:0}
.ckv dt{color:var(--muted)} .ckv dd{margin:0}
.chero{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.3fr); gap:24px 32px; align-items:center; margin-top:18px}
.chero-copy{min-width:0}
.ceyebrow{font-size:12px; letter-spacing:.2em; color:var(--gold)}
.chero-q{display:block; font-size:clamp(24px,3.4vw,36px); line-height:1.35; margin:8px 0 12px; text-wrap:balance; letter-spacing:.04em}
.chero-q::before{display:none}
.chero-q .nw{display:inline-block}
.chero-lead{color:var(--ink2); font-size:15px; max-width:34em}
.chero-form{display:flex; flex-wrap:wrap; gap:8px; margin-top:16px}
.chero-form input{font-size:18px; padding:9px 12px; width:11em; letter-spacing:.06em; font-variant-numeric:tabular-nums}
.ctrust{font-size:12px; color:var(--muted); margin-top:10px}
#homeMsg{margin-top:8px}
.chero-card{margin:0; min-width:0}
.chero-card svg{display:block; width:100%; height:auto; border-radius:6px; box-shadow:0 18px 48px rgba(0,0,0,.55), 0 0 0 1px rgba(233,211,154,.18)}
.chero-card figcaption{font-size:11px; color:var(--muted); text-align:right; margin-top:6px; letter-spacing:.08em}
.chome-links{margin-top:14px} .chome-links a{color:var(--gold-hi)}
.sr{position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap}
@media (max-width:860px){ .chero{grid-template-columns:minmax(0,1fr)} .chero-card{order:-1} }
.csteps{margin:8px 0 0; padding-left:1.4em; display:grid; gap:2px}
#enkaOpen[aria-disabled="true"]{opacity:.45; cursor:default}
a.btn{text-decoration:none; display:inline-block}
.clock{font-size:11px; color:var(--muted); border:1px solid var(--line); border-radius:999px; padding:0 8px; margin-left:6px; letter-spacing:0}
@media (max-width:760px){ .ckv{grid-template-columns:1fr} .ckv dt{margin-top:6px} .cnav button{padding:6px 10px; font-size:13px} }
/* ===== カードの登場の演出（v2.1 試作）：縦長（9:16）のキャンバスに描く。あとで縦動画に書き出すのも同じ描き方 ===== */
.rv-ov{position:fixed; inset:0; z-index:9000; background:#020309; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:12px; padding:12px; animation:rvIn .3s ease-out}
@keyframes rvIn{from{opacity:0}}
.rv-cv{display:block; width:min(calc(100vw - 24px), calc((100dvh - 92px)*9/16)); aspect-ratio:9/16; height:auto; border-radius:14px; box-shadow:0 0 0 1px rgba(233,211,154,.14), 0 20px 60px rgba(0,0,0,.7)}
@media (max-width:520px){ .rv-cv{border-radius:0; box-shadow:none} .rv-ov{padding:0 0 10px} }
.rv-skip{position:fixed; top:12px; right:12px; z-index:2; background:rgba(255,255,255,.08); color:#e6dfcf; border:1px solid rgba(233,211,154,.35); border-radius:999px; padding:6px 16px; font-size:13px; cursor:pointer}
.rv-bar{display:flex; gap:8px; justify-content:center; min-height:40px; align-items:center}
.rv-bar[hidden]{display:flex!important; visibility:hidden}
.rv-hint{font-size:12px; color:rgba(185,178,163,.6); letter-spacing:.08em}
.rv-ov.rv-ovl{justify-content:flex-start; overflow:auto; padding:0}
.rv-list{position:relative; z-index:1; width:min(100%,1000px); padding:24px 16px 40px; margin:0 auto}
.rv-list .th{display:block; position:relative; transform-origin:50% 50%; will-change:transform}
.rv-list .rv-lh,.rv-list .m,.rv-list .rv-lf{transition:opacity .5s ease}
.rv-list.spread .rv-lh,.rv-list.spread .m,.rv-list.spread .rv-lf{opacity:0}
.rv-list.spread .th canvas{transition:none}
.rv-lh{display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:16px}
.rv-lh h2{font-family:"Shippori Mincho B1","Hiragino Mincho ProN",serif; font-size:clamp(20px,3.4vw,26px); letter-spacing:.14em; color:#e9d39a; margin:0}
.rv-lh h2::before{display:none} .rv-lh h2 small{font-family:"Murecho",sans-serif; font-size:13px; letter-spacing:.06em; color:#b9b2a3; margin-left:10px}
.rv-x{background:rgba(255,255,255,.08); color:#e6dfcf; border:1px solid rgba(233,211,154,.35); border-radius:999px; width:36px; height:36px; font-size:18px; cursor:pointer; flex:none}
.rv-lg{display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:18px 16px}
.rv-lc{display:grid; gap:8px; background:none; border:0; padding:0; text-align:left; color:inherit; cursor:pointer; font:inherit}
.rv-lc .th canvas{display:block; width:100%; height:auto; border-radius:6px; box-shadow:0 0 0 1px rgba(233,211,154,.2), 0 8px 24px rgba(0,0,0,.5); transition:transform .2s}
.rv-lc:hover .th canvas{transform:translateY(-2px)}
.rv-lc.best .th canvas{box-shadow:0 0 0 2px #e9d39a, 0 0 28px rgba(233,211,154,.35)}
.rv-lc .m{display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 10px; font-size:13px}
.rv-lc .m b{font-family:"Shippori Mincho B1","Hiragino Mincho ProN",serif; font-size:16px; letter-spacing:.08em; color:#f4ecd6}
.rv-lc .m i{font-style:normal; font-size:11px; color:#14110a; background:#e9d39a; border-radius:999px; padding:1px 8px; letter-spacing:.1em}
.rv-lc .m .st{letter-spacing:.06em} .rv-lc .m .st.myth{background:linear-gradient(90deg,#ff9cbc,#ffd27a,#8ff0c4,#8fbaff,#d59bff); -webkit-background-clip:text; background-clip:text; color:transparent!important}
.rv-lc .m .a{color:#b9b2a3; margin-left:auto; font-variant-numeric:tabular-nums}
.rv-lf{display:flex; flex-wrap:wrap; gap:10px 14px; justify-content:center; align-items:center; margin-top:24px}
.rv-off{background:none; border:0; color:#8f8a7c; font-size:12px; text-decoration:underline; cursor:pointer; font:inherit; font-size:12px}
.rv-off:disabled{text-decoration:none; cursor:default}
.rv-demo{position:fixed; left:50%; bottom:12px; transform:translateX(-50%); z-index:8000; background:rgba(10,12,28,.94); border:1px solid rgba(233,211,154,.4); border-radius:10px; padding:10px 12px; display:grid; gap:6px; font-size:12px; width:min(calc(100% - 24px),560px); box-shadow:0 10px 30px rgba(0,0,0,.5)}
.rv-demo .row{gap:6px; flex-wrap:wrap; align-items:center}
.rv-demo button[aria-pressed="true"]{border-color:var(--gold); color:var(--gold-hi)}
@media (prefers-reduced-motion: reduce){ .rv-ov{animation:none} }
</style>
"""
s = s.replace("<div class=\"wrap\">", CSS + "<div class=\"wrap\">", 1)

JS = r"""
/* ================= 命ノ星座カード（単品アプリ）の画面 ================= */
var CARD_PAGE='list', CARD_DB=null, CARD_FITTING={};
function cardEl(tag,attrs,html){ const e=document.createElement(tag); if(attrs) for(const k in attrs) e.setAttribute(k,attrs[k]); if(html!=null) e.innerHTML=html; return e; }
function cardShowPage(p){ CARD_PAGE=p; document.querySelectorAll('.cpage').forEach(x=>{ x.hidden=x.id!=='pg-'+p; if(x.hidden) x.setAttribute('inert',''); else x.removeAttribute('inert'); });
  document.querySelectorAll('.cnav [data-page]').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.page===p)));
  try{ store.set('cardPage',p); }catch(e){}
  if(p==='home') homeRender(); else if($('homeSample')) $('homeSample').innerHTML='';
  if(p==='set') cardRenderSettings(); if(p==='card') cardAfterRender(); window.scrollTo({top:0}); }
const LIST_SORTS={desc:'高い順',asc:'低い順',added:'追加した順'};
function listSortMode(){ const m=store.get('listSort','desc'); return LIST_SORTS[m]?m:'desc'; }
function cardListSort(rows){ const m=listSortMode(), r=rows.slice(); // 秘境レベルの高い順・低い順（「上限」は最後尾の扱い）、追加した順（新しく入ったキャラが上）
  if(m==='added'){ const ix=new Map(CHARS.map((c,i)=>[c.id,i])); return r.sort((a,b)=>ix.get(b.c.id)-ix.get(a.c.id)); }
  const v=x=>{ const a=x.st.age||0; return isFinite(a)?a:1e15; }; return r.sort((a,b)=>m==='asc'?v(a)-v(b):v(b)-v(a)); }
function cardSorted(){ return cardListSort(CHARS.map(c=>({c,st:charStats(c)}))); }
function cardAfterRender(){ document.querySelectorAll('[data-lsort]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lsort===listSortMode()))); const host=$('cardHost'); if(!host) return;
  if(!CH_OPEN&&CHARS.length){ CH_OPEN=cardSorted()[0].c.id; renderChars(); return; }
  const det=$('cardBox')&&$('cardBox').closest('.chdetail');
  host.innerHTML=''; if(det) host.appendChild(det);
  if(!CH_OPEN||!det) host.innerHTML=`<div class="empty">${CHARS.length?'キャラを選ぶと、ここにカードが出ます。':'まだキャラがいません。「動画から取り込む」で録画を読み取るか、「キャラ一覧」でスクショを取り込む・手入力で追加してください。'}</div>`;
  const sel=$('cSel'); if(sel){ const rows=cardSorted(); sel.innerHTML=rows.map(({c})=>`<option value="${c.id}"${c.id===CH_OPEN?' selected':''}>${esc(c.name||'（名前なし）')}</option>`).join('')||'<option value="">—</option>'; }
  const z=$('cZoom'); if(z) z.value=String(CARD_ZOOM[CH_OPEN]||100);
  const has=!!(CH_OPEN&&CARD_IMG[CH_OPEN]), own=has&&!/^portraits\//.test(CARD_IMG[CH_OPEN]); if($('cZoomWrap')) $('cZoomWrap').hidden=!has; if($('cArtDel')) $('cArtDel').hidden=!own;
  // 保存してある立ち絵（なければ同梱の立ち絵）は、開いたときに切り出し直す。切り出せない画像（背景つき）は、そのまま貼る
  const id=CH_OPEN; applyBundled(CHARS.find(x=>x.id===id)); if(id&&CARD_IMG[id]&&!(id in CARD_FIT)&&!CARD_FITTING[id]){ CARD_FITTING[id]=1; fitCardArt(CARD_IMG[id],CARD_ZOOM[id]).then(u=>{ delete CARD_FITTING[id]; CARD_FIT[id]=u||''; renderChars(); }); }
}
/* ---- 立ち絵の保存（この端末のIndexedDB。ほかの人には見えない） ---- */
function cardDB(){ if(CARD_DB) return CARD_DB; CARD_DB=new Promise((res)=>{ try{ const r=indexedDB.open('meinoseiza-card',1); r.onupgradeneeded=()=>{ r.result.createObjectStore('portraits',{keyPath:'id'}); }; r.onsuccess=()=>res(r.result); r.onerror=()=>res(null); }catch(e){ res(null); } }); return CARD_DB; }
async function portraitTx(mode,fn){ const db=await cardDB(); if(!db) return null; return new Promise(res=>{ try{ const tx=db.transaction('portraits',mode), st=tx.objectStore('portraits'); const r=fn(st); tx.oncomplete=()=>res(r&&r.result); tx.onerror=()=>res(null); }catch(e){ res(null); } }); }
function portraitSave(id){ if(!CARD_APP||!id||!CARD_IMG[id]) return; const c=CHARS.find(x=>x.id===id);
  portraitTx('readwrite',st=>st.put({id,name:c?c.name:'',src:CARD_IMG[id],pos:CARD_POS[id]||null,zoom:CARD_ZOOM[id]||100,at:Date.now()})); }
async function portraitDelete(id){ await portraitTx('readwrite',st=>st.delete(id)); delete CARD_IMG[id]; delete CARD_FIT[id]; delete CARD_POS[id]; delete CARD_ZOOM[id]; renderChars(); if(CARD_PAGE==='set') cardRenderSettings(); }
async function portraitLoadAll(){ const all=await portraitTx('readonly',st=>st.getAll()); (all||[]).forEach(p=>{ CARD_IMG[p.id]=p.src; if(p.pos) CARD_POS[p.id]=p.pos; if(p.zoom) CARD_ZOOM[p.id]=p.zoom; });
  // 以前の版で元の大きさのまま保存したものは、縮めて保存し直す（見た目は変わらない）
  for(const p of all||[]){ if((p.src||'').length<PORTRAIT_SHRINK_OVER) continue; const s2=await portraitShrink(p.src); if(s2!==p.src&&CARD_IMG[p.id]===p.src){ CARD_IMG[p.id]=s2; portraitSave(p.id); } }
  return all||[]; }
/* 立ち絵の縮小：カードの切り出しは長い辺1600pxで処理するので、それより大きい画像は1600pxに縮めて保存する。
   透明を含む画像はPNG、不透明ならJPEG（品質0.92）。縮めても小さくならなければ元のまま */
var PORTRAIT_MAX=1600, PORTRAIT_SHRINK_OVER=600000;
function portraitShrink(src){ return new Promise(res=>{ const im=new Image(); im.onload=()=>{ try{
    const k=Math.min(1,PORTRAIT_MAX/Math.max(im.width,im.height)); if(k>=1&&src.length<PORTRAIT_SHRINK_OVER) return res(src);
    const w=Math.round(im.width*k), h=Math.round(im.height*k), cv=document.createElement('canvas'); cv.width=w; cv.height=h; const cx=cv.getContext('2d'); cx.drawImage(im,0,0,w,h);
    const a=cx.getImageData(0,0,w,h).data; let alpha=false; for(let i=3;i<a.length;i+=16) if(a[i]<250){ alpha=true; break; }
    const out=alpha?cv.toDataURL('image/png'):cv.toDataURL('image/jpeg',.92); res(out.length<src.length?out:src); }catch(e){ res(src); } }; im.onerror=()=>res(src); im.src=src; }); }
/* ---- 設定のページ ---- */
async function cardRenderSettings(){ { const rc=$('cRevealOn'); if(rc) rc.checked=!store.get('revealOff',0); } const box=$('cPortraits'); if(!box) return; const all=(await portraitTx('readonly',st=>st.getAll()))||[];
  box.innerHTML=all.length?`<div class="cthumbs">${all.map(p=>{ const c=CHARS.find(x=>x.id===p.id); return `<div class="cthumb"><img src="${p.src}" alt=""><b>${esc((c&&c.name)||p.name||'（削除したキャラ）')}</b><button class="btn" style="padding:3px 10px;font-size:12px" data-pdel="${p.id}">削除</button></div>`; }).join('')}</div>`:'<div class="empty">まだ保存した立ち絵はありません。カードのページの「立ち絵を選ぶ」で選ぶと、ここに並びます。</div>';
  box.querySelectorAll('[data-pdel]').forEach(b=>b.addEventListener('click',()=>portraitDelete(b.dataset.pdel))); }
/* ---- 組み立て ---- */
function cardAppInit(){
  document.body.classList.add('mode-card');
  // 見た目は決定済みの値に固定（試作用の切り替えは出さない）
  CC_LABEL='glass'; CC_FONT='murecho'; CC_FRAME='gold'; CC_LINE='star'; CC_MYTH='m1'; CC_MYTHLANG='en'; CC_UNITS='en3c'; CC_SLOTID='badge';
  const head=document.querySelector('header.top'); head.querySelector('h1').innerHTML='<small>秘境で何日回ると、どこまで行く？</small>命ノ星座カード';
  const nav=cardEl('div',{class:'tabs cnav',role:'tablist','aria-label':'ページ'},
    '<button role="tab" data-page="home">ホーム</button><button role="tab" data-page="list">キャラ一覧</button><button role="tab" data-page="card">カード</button><button role="tab" data-page="scan">取り込む</button><button role="tab" data-page="set">設定</button>');
  head.appendChild(nav); nav.querySelectorAll('[data-page]').forEach(b=>b.addEventListener('click',()=>cardShowPage(b.dataset.page)));
  { const h1=head.querySelector('h1'); h1.style.cursor='pointer'; h1.addEventListener('click',()=>cardShowPage('home')); }
  const wrap=document.querySelector('.wrap'), view=$('view-chars');
  const pHome=cardEl('section',{id:'pg-home',class:'cpage'}), pList=cardEl('section',{id:'pg-list',class:'cpage',hidden:''}), pCard=cardEl('section',{id:'pg-card',class:'cpage',hidden:''}), pSet=cardEl('section',{id:'pg-set',class:'cpage',hidden:''}), pScan=cardEl('section',{id:'pg-scan',class:'cpage',hidden:''});
  view.parentNode.insertBefore(pHome,view); view.parentNode.insertBefore(pList,view); view.parentNode.insertBefore(pCard,view); view.parentNode.insertBefore(pScan,view); view.parentNode.insertBefore(pSet,view);
  // キャラ一覧：横棒の一覧＋取り込みの入口（取り込みの確認と手入力は、この上に出る）
  const tl=$('chTimeline').closest('.panel');
  pList.appendChild($('chEditor')); pList.appendChild($('chImport')); pList.appendChild(tl);
  tl.style.marginTop='14px';
  const h=tl.querySelector('.row'); h.querySelector('h2').textContent='手持ちのキャラ';
  const ctrl=h.querySelector('.row'); ctrl.innerHTML=''; const shots=$('chShots').closest('label'); const so=cardEl('div',{class:'seg',role:'group','aria-label':'並び順'},Object.entries(LIST_SORTS).map(([k,v])=>`<button data-lsort="${k}">${v}</button>`).join('')); ctrl.appendChild(so); ctrl.appendChild(shots); ctrl.appendChild($('chAdd'));
  so.querySelectorAll('[data-lsort]').forEach(b=>b.addEventListener('click',()=>{ store.set('listSort',b.dataset.lsort); renderChars(); }));
  const tln=tl.querySelector('p.note'); if(tln) tln.innerHTML='行を押すと、そのキャラのカードが開きます。並び順は右上で切り替えられます（カードのページの ◀ ▶ も同じ順）。スクショは端末の中で読み取り、どこにも送りません（このページへのドラッグや貼り付けでも取り込めます）。棒の長さ＝部位ごとの秘境レベル、右の数字＝5部位の合計の秘境レベル。色はランク（<span id="tierLegend"></span>）。';
  // カード
  pCard.innerHTML=`<div class="panel" style="margin-top:14px"><div class="ctool"><div class="grp2"><button class="btn" id="cPrev" aria-label="前のキャラ">◀</button><select id="cSel" aria-label="キャラ"></select><button class="btn" id="cNext" aria-label="次のキャラ">▶</button><button class="btn" id="cEdit">編集</button><span id="cDelBox"><button class="btn" id="cDel">削除</button></span></div>
    <div class="grp2"><label class="btn" style="cursor:pointer">立ち絵を選ぶ<input type="file" id="cArt" accept="image/*" hidden></label><label id="cZoomWrap" class="row" style="gap:6px;font-size:12px;color:var(--muted)" hidden>大きさ<input type="range" id="cZoom" min="60" max="170" step="5" value="100" style="width:110px"></label><button class="btn" id="cArtDel" hidden>立ち絵を外す</button><button class="btn primary" id="cShare">共有</button><button class="btn" id="cPng">PNGで保存</button><button class="btn" id="cWebp">WebP</button></div></div>
    <p class="note" id="cMsg" aria-live="polite" style="margin-top:6px"></p><div id="cardHost" style="margin-top:6px"></div>
    <p class="note" style="margin-top:8px">立ち絵はこの端末（このブラウザ）に保存され、ほかの人には見えません。絵はドラッグで位置を動かせます（ダブルクリックで元の位置）。保存した画像は2400×1350です。PNGはどこに上げても確実、WebPは軽いかわりに受け付けないサービスもあります。</p></div>`;
  const step=d=>{ const rows=cardSorted(); if(!rows.length) return; let i=rows.findIndex(r=>r.c.id===CH_OPEN); i=(i+d+rows.length)%rows.length; CH_OPEN=rows[i].c.id; renderChars(); };
  $('cPrev').addEventListener('click',()=>step(-1)); $('cNext').addEventListener('click',()=>step(1));
  $('cSel').addEventListener('change',e=>{ CH_OPEN=e.target.value||null; renderChars(); });
  $('cEdit').addEventListener('click',()=>{ if(!CH_OPEN) return; cardShowPage('list'); openEditor(CH_OPEN); $('chEditor').scrollIntoView({behavior:'smooth',block:'start'}); });
  cardAppBindDel();
  $('cArt').addEventListener('change',e=>{ const f=e.target.files[0]; e.target.value=''; if(!f||!CH_OPEN) return; const rd=new FileReader(); rd.onload=async()=>{ const id=CH_OPEN; CARD_IMG[id]=await portraitShrink(rd.result); delete CARD_FIT[id]; delete CARD_POS[id]; portraitSave(id); renderChars(); }; rd.readAsDataURL(f); });
  $('cZoom').addEventListener('change',e=>{ const id=CH_OPEN, src=CARD_IMG[id]; if(!src) return; CARD_ZOOM[id]=+e.target.value; portraitSave(id); fitCardArt(src,CARD_ZOOM[id]).then(u=>{ if(u&&CARD_IMG[id]===src){ CARD_FIT[id]=u; renderChars(); } }); });
  $('cArtDel').addEventListener('click',()=>{ if(CH_OPEN) portraitDelete(CH_OPEN); });
  $('cShare').addEventListener('click',cardShare); $('cPng').addEventListener('click',()=>cardExport('png',$('cMsg'))); $('cWebp').addEventListener('click',()=>cardExport('webp',$('cMsg')));
  // 取り込む：UID（Enka.Network のJSONを受け渡し）と、動画（聖遺物ビデオスキャナーを scan/ に置き、枠の中で動かす）。どちらもキャラ一覧へ直接入れる
  pScan.innerHTML=`<div class="panel" style="margin-top:14px"><h2>UIDから取り込む</h2>
    <p class="note">ゲームのショーケースに並べたキャラの聖遺物を、Enka.Network から取り込みます（ゲームのプロフィールで、キャラの詳細を見られるようにしておいてください）。UIDを入れて「UIDで取得」を押します。</p>
    <div class="row" style="margin-top:10px"><label class="f" for="enkaUid">UID<input type="text" id="enkaUid" inputmode="numeric" autocomplete="off" maxlength="10" placeholder="例：800123456" style="width:9em"></label><button class="btn primary" id="enkaGet">UIDで取得</button></div>
    <div class="note" id="enkaMsg" aria-live="polite" style="margin-top:8px"></div>
    <details class="more" id="enkaManual" style="margin-top:10px"><summary>「UIDで取得」がうまくいかないとき（手で受け渡す）</summary>
    <ol class="note csteps"><li>UIDを入れて「Enkaで開く」を押す（別のタブで文字だらけのページが開きます）</li><li>開いたページの文字を全部選んでコピーする（Firefoxは「生データ」のタブで）。または、そのページを保存する</li><li>下の欄に貼り付けて「読み込む」を押す（保存したときは「ファイルから読み込む」）</li></ol>
    <div class="btns"><a class="btn" id="enkaOpen" target="_blank" rel="noopener" aria-disabled="true">Enkaで開く</a></div>
    <textarea id="enkaText" rows="3" aria-label="Enka のページの文字" placeholder="Enka のページの文字を、ここに貼り付けます" style="width:100%;margin-top:10px;font:12px/1.4 ui-monospace,monospace;color:var(--ink);background:var(--inset);border:1px solid var(--line);border-radius:8px;padding:8px"></textarea>
    <div class="btns"><button class="btn primary" id="enkaIn">読み込む</button><label class="btn" style="cursor:pointer">ファイルから読み込む<input type="file" id="enkaFile" accept=".json,.txt,application/json,text/plain" hidden></label></div></details>
    <p class="note" style="margin-top:8px">★5の聖遺物だけを取り込みます。Enka のデータにはサブOPが伸びた1回ごとの幅が入っているので、有効RVは推定ではなく実際の値で計算します。同じUIDをすぐ開き直しても、しばらくは同じ内容が返ります。データ：Enka.Network</p></div>
    <div class="panel" style="margin-top:14px"><h2>動画から取り込む</h2><p class="note">ゲームの所持品画面（聖遺物）を録画した動画から、聖遺物を読み取ります。読み終わったら「キャラ一覧に入れる」で、装備中のキャラがキャラ一覧に入ります。+20になっていない聖遺物はいまの値で評価し、カードに「+8」などの印が付きます。★4の聖遺物は外します。動画はこの端末の中だけで処理し、どこにも送りません。</p>
    <div class="btns" id="scanStartBox"><button class="btn primary" id="scanStart">動画の読み取りを始める</button><span class="note" style="align-self:center">読み取りの道具（約15MB）を読み込みます</span></div>
    <div class="note" id="scanMsg" aria-live="polite" style="margin-top:6px"></div></div>
    <iframe id="scanFrame" title="聖遺物ビデオスキャナー" hidden style="display:block;width:100%;height:900px;border:0;margin-top:14px;background:transparent;color-scheme:dark"></iframe>`;
  $('scanStart').addEventListener('click',scanOpen);
  { const u=$('enkaUid'), a=$('enkaOpen'), sync=()=>{ const v=u.value.replace(/\D/g,''); if(v!==u.value) u.value=v; const ok=/^\d{9,10}$/.test(v); a.setAttribute('aria-disabled',String(!ok)); if(ok) a.href=`https://enka.network/api/uid/${v}/`; else a.removeAttribute('href'); try{ if(ok) store.set('enkaUid',v); }catch(e){} };
    u.value=store.get('enkaUid','')||''; u.addEventListener('input',sync); sync();
    a.addEventListener('click',e=>{ if(a.getAttribute('aria-disabled')==='true'){ e.preventDefault(); $('enkaMsg').textContent='UIDは9けたか10けたの数字です。'; } }); }
  $('enkaIn').addEventListener('click',()=>enkaImport($('enkaText').value));
  $('enkaGet').addEventListener('click',enkaFetch); $('enkaUid').addEventListener('keydown',e=>{ if(e.key==='Enter'){ e.preventDefault(); enkaFetch(); } });
  $('enkaFile').addEventListener('change',async e=>{ const f=e.target.files[0]; e.target.value=''; if(f) enkaImport(await f.text()); });
  window.addEventListener('message',scanOnMessage);
  // 設定
  const mv=$('mvOut').closest('.panel'); const det=mv.querySelector('details'); if(det){ det.open=true; const sm=det.querySelector('summary'); if(sm) sm.remove(); }
  pSet.innerHTML=`<div class="panel" style="margin-top:14px"><h2>計算の前提 <span class="clock">固定</span></h2><dl class="ckv">
    <dt>1日の周回数</dt><dd>${S.runsPerDay}周（樹脂${S.runsPerDay*20}）</dd><dt>初期4OPの確率</dt><dd>${Math.round(S.p4*100)}%（秘境）</dd><dt>1周の★5ドロップ</dt><dd>平均${DROP5}個</dd><dt>狙いのセット</dt><dd>2択の片方（${Math.round(SET_SHARE*100)}%）</dd>
    <dt>秘境レベル</dt><dd>そのキャラ（メインOP・有効OP）の条件で、いまの有効RVを秘境だけで揃えるのにかかる、平均的な人の日数</dd><dt>ランクの境目</dt><dd>★1 〜1週／★2 〜1か月／★3 〜3か月／★4 〜1年／★5 〜3年／★5+ 3年〜（100年以上は ONCE IN A CENTURY、5000年以上は SINCE THE DAWN OF TIME）</dd>
    <dt>確率の出典</dt><dd>KQM「Genshin Impact Artifacts Guide」、Genshin Impact Wiki（Fandom）「Artifact/Distribution」（草元素追加後の値）</dd></dl></div>
    <div class="panel" style="margin-top:14px"><h2>保存した立ち絵</h2><p class="note" style="margin-bottom:8px">この端末（このブラウザ）にだけ保存されています。ほかの人には見えません。大きい画像は、長い辺1600pxに縮めて保存します（カードの見た目は変わりません）。</p><div id="cPortraits"></div></div>
    <div class="panel" style="margin-top:14px"><h2>カードの登場の演出</h2><label class="row" style="gap:8px;align-items:center"><input type="checkbox" id="cRevealOn">UIDで取り込んだあと、カードが机に落ちてくる演出を出す</label><p class="note" style="margin-top:6px">演出の途中で画面を押す（Enter・スペースでも）と次のカードへ進み、右上の「スキップ」で最後まで飛べます。</p></div>
    <div class="panel" style="margin-top:14px" id="cMoveHost"><h2>データの引っ越し</h2></div>
    <div class="panel" style="margin-top:14px"><h2>このアプリについて</h2><p class="note">命ノ星座カード v2.0。計算は聖遺物厳選ラボと共通です。原神のキャラクター名・画像などの権利は HoYoverse に帰属します。UIDからの取り込みには Enka.Network のデータを、動画からの取り込みには聖遺物ビデオスキャナー（読み取りエンジン：Tesseract.js）を使っています。キャラのデータはこの端末（このブラウザ）に保存され、ラボ本体や別の端末とのやりとりは「データの引っ越し」のJSONで行います（ラボ本体で書き出したものもそのまま読めます）。HoYoverseとは関係のない非公式のファンツールです。</p></div>`;
  const mh=$('cMoveHost'); [...(det||mv).childNodes].forEach(n=>mh.appendChild(n)); mv.remove();
  { const cb=$('cRevealOn'); cb.checked=!store.get('revealOff',0); cb.addEventListener('change',()=>store.set('revealOff',cb.checked?0:1)); }
  // ドラッグで取り込み（どのページでも）
  document.addEventListener('dragover',e=>{ if(e.dataTransfer&&[...e.dataTransfer.types].includes('Files')) e.preventDefault(); });
  document.addEventListener('drop',e=>{ if(e.target.closest&&e.target.closest('#cardHost')) return; const fs=e.dataTransfer?[...e.dataTransfer.files]:[]; if(fs.length){ e.preventDefault(); if(CARD_PAGE==='scan'||fs.every(f=>/^video\//.test(f.type))){ cardShowPage('scan'); scanOpen(); $('scanMsg').textContent='動画は、下の枠（録画ファイルをここにドロップ）に落としてください。'; return; } cardShowPage('list'); importShots(fs); } });
  // 取り込み・手入力を始めたら一覧のページへ
  $('chAdd').addEventListener('click',()=>cardShowPage('list'));
  if(!CH_OPEN&&CHARS.length) CH_OPEN=cardSorted()[0].c.id;
  portraitLoadAll().then(()=>{ renderChars(); });
  homeInit(pHome); cardShowPage('home');
  renderChars();
  if(h0==='reveal'||window.REVEAL_DEMO) revealDemoPanel(); // showTab が先に # を書き換えるので、開いたときの値（h0）で見る
  if(location.hash) try{ history.replaceState(null,'',location.pathname+location.search); }catch(e){}
}
/* ---- 動画から取り込む：枠（scan/index.html?embed=1）とのやりとり ---- */
var SCAN_LOADED=false, SCAN_HELLO=false;
function scanOpen(){ const fr=$('scanFrame'); if(!fr||SCAN_LOADED) return; SCAN_LOADED=true; fr.hidden=false; if($('scanStartBox')) $('scanStartBox').hidden=true; fr.src='scan/index.html?embed=1';
  setTimeout(()=>{ if(!SCAN_HELLO&&$('scanMsg')&&!$('scanMsg').textContent) $('scanMsg').innerHTML='読み取りの画面がまだ出ない場合は、少し待つか、ページを開き直してください。'; },20000); }
function scanOnMessage(e){ const fr=$('scanFrame'); if(!fr||e.source!==fr.contentWindow) return; const d=e.data||{};
  if(d.type==='gscan:h'){ SCAN_HELLO=true; fr.style.height=Math.max(480,Math.ceil(+d.h||0)+4)+'px'; return; }
  if(d.type==='gscan:lab'){ let r, n=0; try{ const j=JSON.parse(d.json); n=(j.chars||[]).length; const nt=j.notes||{};
      r=n?moveImport(d.json):'装備中のキャラが見つかりませんでした（キャラが装備している聖遺物だけを取り込みます）。';
      const ex=[]; if(nt.partial) ex.push(`+20になっていない聖遺物 ${nt.partial}個は、いまの値で評価しています`); if(nt.low) ex.push(`★4の聖遺物 ${nt.low}個は外しました`); if(ex.length) r+='。'+ex.join('。')+'。'; }
    catch(err){ r='読み取り結果を受け取れませんでした（'+(err&&err.message||err)+'）'; }
    let names=[]; try{ names=(JSON.parse(d.json).chars||[]).map(c=>c.name); }catch(err){} importDone($('scanMsg'),r,names);
    try{ fr.contentWindow.postMessage({type:'gscan:done',msg:r},'*'); }catch(err){} } }
/* ---- 取り込みのあと：一覧へ・まとめて保存 ---- */
function importDone(box,msg,names){ const ids=[...new Set(names.map(n=>(CHARS.find(c=>c.name===n)||{}).id).filter(Boolean))];
  box.innerHTML=`<p>${esc(msg)}</p>`+(ids.length?`<div class="btns" style="margin-top:6px"><button class="btn" data-go>キャラ一覧を見る</button><button class="btn primary" data-zip>この${ids.length}人のカードをまとめて保存（ZIP）</button></div><p class="note" data-zmsg aria-live="polite"></p>`:'');
  const g=box.querySelector('[data-go]'); if(g) g.addEventListener('click',()=>cardShowPage('list'));
  const z=box.querySelector('[data-zip]'); if(z) z.addEventListener('click',()=>cardExportMany(ids,box.querySelector('[data-zmsg]'),z)); }
/* ---- まとめて保存：1人ずつカードを描いて画像にし、ZIP（無圧縮）にまとめて1回で保存 ---- */
async function cardExportMany(ids,msg,btn){ const say=t=>{ if(msg) msg.textContent=t; }; ids=ids.filter(id=>CHARS.some(c=>c.id===id)); if(!ids.length) return;
  if(btn) btn.disabled=true; const back=CARD_PAGE, keep=CH_OPEN, files=[]; let fontBad=false;
  try{ cardShowPage('card');
    for(let i=0;i<ids.length;i++){ const id=ids[i], c=CHARS.find(x=>x.id===id); say(`${i+1}/${ids.length}人目（${c.name||''}）を描いています…`);
      applyBundled(c); if(CARD_IMG[id]&&!(id in CARD_FIT)){ const u=await fitCardArt(CARD_IMG[id],CARD_ZOOM[id]); CARD_FIT[id]=u||''; }
      CH_OPEN=id; renderChars(); await new Promise(r=>setTimeout(r,60));
      const r=await cardExport('png',null,{blobOnly:true}); if(!r||!r.blob) throw new Error('image');
      if(!r.fontOk) fontBad=true; files.push({name:`${String(i+1).padStart(2,'0')}_${r.name}`,data:new Uint8Array(await r.blob.arrayBuffer())}); }
    const d=new Date(), ds=`${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}`;
    say('ZIPにまとめています…'); const res=await saveBlob(`命ノ星座_${ids.length}人_${ds}.zip`,zipStore(files));
    say(res==='saved'?`${ids.length}人ぶんのカード（PNG・2400×1350）をZIPで保存しました${fontBad?'。フォントを埋め込めなかったものがあり、文字の形が画面と少し違うかもしれません':''}`:res==='declined'?'保存を取りやめました':/extension/.test(res)?'この画面ではZIPを保存できません。カードのページから1人ずつ保存してください':'保存できませんでした');
  }catch(e){ say('画像を作れませんでした。カードのページから1人ずつ保存してください'); }
  finally{ CH_OPEN=keep; renderChars(); cardShowPage(back); if(btn) btn.disabled=false; } }
function zipStore(files){ // [{name, data:Uint8Array}] → ZIP（無圧縮・ファイル名はUTF-8）
  const T=new Uint32Array(256); for(let n=0;n<256;n++){ let c=n; for(let k=0;k<8;k++) c=c&1?0xEDB88320^(c>>>1):c>>>1; T[n]=c>>>0; }
  const crc=b=>{ let c=0xFFFFFFFF; for(let i=0;i<b.length;i++) c=T[(c^b[i])&255]^(c>>>8); return (c^0xFFFFFFFF)>>>0; };
  const enc=new TextEncoder(), d=new Date(), tm=(d.getHours()<<11)|(d.getMinutes()<<5)|(d.getSeconds()>>1), dt=((d.getFullYear()-1980)<<9)|((d.getMonth()+1)<<5)|d.getDate(), parts=[], cen=[]; let off=0, cs=0;
  for(const f of files){ const nm=enc.encode(f.name), c=crc(f.data), n=f.data.length, h=new DataView(new ArrayBuffer(30)), e=new DataView(new ArrayBuffer(46));
    [[0,0x04034b50,4],[4,20,2],[6,0x0800,2],[8,0,2],[10,tm,2],[12,dt,2],[14,c,4],[18,n,4],[22,n,4],[26,nm.length,2],[28,0,2]].forEach(([o,v,w])=>w===4?h.setUint32(o,v,true):h.setUint16(o,v,true));
    [[0,0x02014b50,4],[4,20,2],[6,20,2],[8,0x0800,2],[10,0,2],[12,tm,2],[14,dt,2],[16,c,4],[20,n,4],[24,n,4],[28,nm.length,2],[30,0,2],[32,0,2],[34,0,2],[36,0,2],[38,0,4],[42,off,4]].forEach(([o,v,w])=>w===4?e.setUint32(o,v,true):e.setUint16(o,v,true));
    parts.push(h.buffer,nm,f.data); cen.push(e.buffer,nm); off+=30+nm.length+n; cs+=46+nm.length; }
  const z=new DataView(new ArrayBuffer(22)); z.setUint32(0,0x06054b50,true); z.setUint16(8,files.length,true); z.setUint16(10,files.length,true); z.setUint32(12,cs,true); z.setUint32(16,off,true);
  return new Blob([...parts,...cen,z.buffer],{type:'application/zip'}); }
/* ---- UIDから取り込む：Enka.Network の応答（JSON）→ ラボのキャラの形 ---- */
const ENKA=__ENKA_TABLES__; // build_enka_tables.py で作る対応表（avatar：キャラ名、set：セット名、affix：★5のサブOP1回ぶん→[OP, 段]）
const ENKA_PROP={FIGHT_PROP_HP:'HP',FIGHT_PROP_ATTACK:'ATK',FIGHT_PROP_DEFENSE:'DEF',FIGHT_PROP_HP_PERCENT:'HP%',FIGHT_PROP_ATTACK_PERCENT:'ATK%',FIGHT_PROP_DEFENSE_PERCENT:'DEF%',FIGHT_PROP_CHARGE_EFFICIENCY:'ER',FIGHT_PROP_ELEMENT_MASTERY:'EM',FIGHT_PROP_CRITICAL:'CR',FIGHT_PROP_CRITICAL_HURT:'CD',FIGHT_PROP_HEAL_ADD:'HEAL',FIGHT_PROP_PHYSICAL_ADD_HURT:'PHYS',FIGHT_PROP_FIRE_ADD_HURT:'DMG_炎',FIGHT_PROP_WATER_ADD_HURT:'DMG_水',FIGHT_PROP_ICE_ADD_HURT:'DMG_氷',FIGHT_PROP_ELEC_ADD_HURT:'DMG_雷',FIGHT_PROP_WIND_ADD_HURT:'DMG_風',FIGHT_PROP_ROCK_ADD_HURT:'DMG_岩',FIGHT_PROP_GRASS_ADD_HURT:'DMG_草'};
const ENKA_SLOT={EQUIP_BRACER:'flower',EQUIP_NECKLACE:'plume',EQUIP_SHOES:'sands',EQUIP_RING:'goblet',EQUIP_DRESS:'circlet'};
function enkaParse(txt){ txt=String(txt||'').trim(); if(!txt) throw new Error('empty');
  try{ return JSON.parse(txt); }catch(e){ const a=txt.indexOf('{'), b=txt.lastIndexOf('}'); if(a>=0&&b>a) return JSON.parse(txt.slice(a,b+1)); throw e; } }
function enkaToLab(d){ const out=[], notes={low:0,partial:0,unknown:0,odd:0};
  for(const av of (d&&d.avatarInfoList)||[]){ const pieces={}, cnt={};
    for(const e of av.equipList||[]){ const f=e.flat||{}, r=e.reliquary; if(f.itemType!=='ITEM_RELIQUARY'||!r) continue;
      if(f.rankLevel!==5){ notes.low++; continue; } const slot=ENKA_SLOT[f.equipType], main=ENKA_PROP[(f.reliquaryMainstat||{}).mainPropId]; if(!slot||!main){ notes.odd++; continue; }
      const lv=Math.max(0,Math.min(20,(+r.level||1)-1)), rolls={}; let bad=false;
      for(const id of r.appendPropIdList||[]){ const x=ENKA.affix[String(id)]; if(!x){ bad=true; continue; } (rolls[x[0]]=rolls[x[0]]||[]).push(x[1]); }
      const subs=(f.reliquarySubstats||[]).map(q=>{ const s=ENKA_PROP[q.appendPropId], v=+q.statValue; return {s,v:FLAT.has(s)?String(Math.round(v)):v.toFixed(1)}; }).filter(q=>q.s);
      if(subs.length<3||subs.length>4){ notes.odd++; continue; }
      if(subs.length===3) subs.push({s:'',v:'',off:true}); // +0の3OP：4つ目は Enka には出てこない（種類も分からない）
      const p={main,subs}; if(lv<20){ p.lv=lv; notes.partial++; } if(!bad) p.rolls=rolls; pieces[slot]=p;
      if(f.setId) cnt[f.setId]=(cnt[f.setId]||0)+1; }
    if(!Object.keys(pieces).length) continue;
    const nm=ENKA.avatar[String(av.avatarId)]; if(!nm) notes.unknown++;
    const set=Object.entries(cnt).sort((a,b)=>b[1]-a[1]).filter(x=>x[1]>=2).map(([k,n])=>(ENKA.set[k]||'セット'+k)+(n>=4?'4':'2')).join('＋');
    out.push({id:'enka-'+av.avatarId,name:nm||`不明なキャラ（${av.avatarId}）`,set,pieces,date:today()}); }
  return {chars:out,notes}; }
/* UIDで取得：Enka に問い合わせる（中継の設定があれば中継、なければ直接）。
   Enka の決まり：応答の ttl（秒）が切れるまでは同じUIDを取り直さない → この端末に応答を取っておき、ttl の間はそれを使う。
   つながらないとき（このページからの通信が許されていない・CORS・ネットワーク）は、手で受け渡す手順を開いて案内する */
const ENKA_PROXY=(location.hostname==='wayfaringgene-code.github.io'||location.hostname==='localhost')?'https://enka-proxy.wayfaringgene.workers.dev/uid/':''; // 中継（proxy/enka-proxy.js を Cloudflare Workers に置いたもの）。中継が受け付けるページのときだけ使い、それ以外は直接
var ENKA_BUSY=false;
async function enkaFetch(){ const box=$('enkaMsg'), uid=$('enkaUid').value.replace(/\D/g,''), btn=$('enkaGet');
  if(!/^\d{9,10}$/.test(uid)){ box.textContent='UIDは9けたか10けたの数字です。'; return; } if(ENKA_BUSY) return;
  let cache=null; try{ cache=JSON.parse(localStorage.getItem('lab:enkaCache:'+uid)||'null'); }catch(e){}
  if(cache&&cache.until>Date.now()&&cache.text){ const nm=enkaImport(cache.text); box.insertAdjacentHTML('afterbegin',`<p class="note">（さっき取った内容を使いました。Enka が新しい内容を返すまで、あと約${Math.ceil((cache.until-Date.now())/1000)}秒です）</p>`); return nm; }
  ENKA_BUSY=true; btn.disabled=true; box.textContent='Enka に問い合わせています…';
  let csp=false; const onCsp=e=>{ if(/enka|workers|proxy/i.test(e.blockedURI||'')||ENKA_PROXY&&(e.blockedURI||'').startsWith(ENKA_PROXY)) csp=true; }; document.addEventListener('securitypolicyviolation',onCsp);
  const url=ENKA_PROXY?ENKA_PROXY+uid:`https://enka.network/api/uid/${uid}/`, ac=new AbortController(), tm=setTimeout(()=>ac.abort(),20000);
  try{ const r=await fetch(url,{signal:ac.signal,headers:{'Accept':'application/json'}});
    if(!r.ok){ const why={400:'UIDの形が正しくないようです',404:'このUIDのプレイヤーが見つかりませんでした',424:'ゲームのメンテナンス中か、更新の直後で Enka が情報を取れない状態です。しばらくしてからもう一度',429:'問い合わせが混み合っています。少し時間をおいてからもう一度',500:'Enka 側で問題が起きています。しばらくしてからもう一度',503:'Enka 側で問題が起きています。しばらくしてからもう一度'}[r.status]; box.textContent=(why||`Enka から取得できませんでした（${r.status}）`)+'。'; return; }
    const text=await r.text(); let ttl=60; try{ const j=JSON.parse(text); if(j&&+j.ttl>0) ttl=Math.min(+j.ttl,600); }catch(e){}
    try{ localStorage.setItem('lab:enkaCache:'+uid,JSON.stringify({until:Date.now()+ttl*1000,text})); }catch(e){}
    return enkaImport(text); }
  catch(e){ await new Promise(r=>setTimeout(r,50)); const det=$('enkaManual'); if(det) det.open=true;
    box.textContent=(e&&e.name==='AbortError')?'Enka から返事がありませんでした。少し待ってもう一度押すか、下の「うまくいかないとき」の手順で取り込んでください。'
      :csp?'この画面（claude.ai の中）からは Enka に直接つなげません。下の「うまくいかないとき」の手順で取り込んでください（GitHub 版のページなら、このボタンで取れる場合があります）。'
      :'このページからは Enka に直接つなげませんでした。下の「うまくいかないとき」の手順で取り込んでください。（理由：通信が許されていない〈CORS〉か、ネットワークの問題）'; }
  finally{ clearTimeout(tm); document.removeEventListener('securitypolicyviolation',onCsp); ENKA_BUSY=false; btn.disabled=false; } }
function enkaImport(txt){ const box=$('enkaMsg'); let d;
  try{ d=enkaParse(txt); }catch(e){ box.textContent='読み込めませんでした。Enka で開いたページの文字を、最初から最後まで全部コピーして貼り付けてください（Firefoxでは「生データ」のタブで全選択します）。'; return; }
  if(!d||typeof d!=='object'||(!d.playerInfo&&!d.avatarInfoList)){ box.textContent='Enka のデータではないようです。「Enkaで開く」で開いたページの文字を貼り付けてください。'; return; }
  if(!Array.isArray(d.avatarInfoList)||!d.avatarInfoList.length){ box.textContent='このUIDでは、キャラの詳細が見られませんでした。ゲームのプロフィールで、ショーケースにキャラを並べ、詳細を見られるようにしてから、もう一度「Enkaで開く」からやり直してください（反映まで少しかかることがあります）。'; return; }
  const {chars,notes}=enkaToLab(d); if(!chars.length){ box.textContent='★5の聖遺物を付けたキャラが見つかりませんでした。'; return; }
  let r=moveImport(JSON.stringify({chars})); const ex=[];
  if(notes.partial) ex.push(`+20になっていない聖遺物 ${notes.partial}個は、いまの値で評価しています`); if(notes.low) ex.push(`★4以下の聖遺物 ${notes.low}個は外しました`);
  if(notes.unknown) ex.push(`名前の分からないキャラが ${notes.unknown}人います（アプリの更新待ち。名前は編集で直せます）`); if(notes.odd) ex.push(`読めなかった聖遺物が ${notes.odd}個ありました`);
  if(ex.length) r+='。'+ex.join('。')+'。'; if(d.uid&&/^\d{9,10}$/.test(String(d.uid))){ $('enkaUid').value=String(d.uid); try{ store.set('enkaUid',String(d.uid)); }catch(e){} }
  $('enkaText').value=''; importDone(box,r,chars.map(c=>c.name)); return chars.map(c=>c.name); }
/* ================= ホーム（v2.0）：見本のカード → UID → いちばんすごいカード ================= */
const SITE_URL='https://wayfaringgene-code.github.io/genshin-lab/';
const ON_SITE=/(^|\.)github\.io$/.test(location.hostname)||location.hostname==='localhost'; // GitHub Pages（と手元の確認）で開いているか
const LAB_URL=ON_SITE?'lab/':'https://claude.ai/artifact/CyumpKAACPGCbSeY8sFpFA';
/* ---- 同梱の立ち絵：portraits/{avatarId}.webp（tools/build_portraits.py で作る）。自分で選んだ立ち絵があれば、そちらが優先 ---- */
const PORTRAITS=__PORTRAITS__; // {avatarId:{file, name, zoom?, pos?}}
let _N2A=null; function name2aid(n){ if(!_N2A){ _N2A={}; for(const [k,v] of Object.entries(ENKA.avatar)) if(!(v in _N2A)) _N2A[v]=k; } return _N2A[n]; }
function bundledPortrait(c){ if(!ON_SITE||!c) return null; const a=((/^(?:enka|sample)-(\d+)$/.exec(c.id||''))||[])[1]||name2aid(c.name); const q=a&&PORTRAITS[a]; return q?{src:'portraits/'+q.file,zoom:q.zoom||0,pos:q.pos||null}:null; }
function applyBundled(c){ if(!c||CARD_IMG[c.id]) return; const b=bundledPortrait(c); if(!b) return; CARD_IMG[c.id]=b.src; if(b.zoom&&!CARD_ZOOM[c.id]) CARD_ZOOM[c.id]=b.zoom; if(b.pos&&!CARD_POS[c.id]) CARD_POS[c.id]=b.pos; }
/* ---- 見本のキャラ（実在のプレイヤーのデータではなく、伸び方を決めて作った例） ---- */
function homeSampleChar(){
  const P=(main,lines)=>{ const rolls={}, subs=lines.map(([k,t])=>{ rolls[k]=t; const v=t.reduce((a,x)=>a+ROLL[k][x],0); return {s:k,v:FLAT.has(k)?String(Math.round(v+1e-9)):(Math.round((v+1e-9)*10)/10).toFixed(1)}; }); return {main,subs,rolls}; };
  return {id:'sample-10000089',name:'フリーナ',set:'黄金の劇団4',eff:['HP%','CR','CD','ER'],date:'見本',pieces:{
    flower:P('HP',[['CR',[3,3,2]],['CD',[3,2]],['HP%',[3,2]],['ER',[2]]]),
    plume:P('ATK',[['CR',[3,3]],['CD',[3,2,2]],['HP%',[2]],['ER',[1]]]),
    sands:P('HP%',[['CR',[3,2]],['CD',[3,3,3]],['ER',[2]],['ATK',[1]]]),
    goblet:P('DMG_水',[['CR',[3,3]],['CD',[3,2,2]],['HP%',[2]],['EM',[1]]]),
    circlet:P('CR',[['CD',[3,3,2,2]],['HP%',[3]],['ER',[2]],['ATK%',[0]]])}}; }
var HOME_SAMPLE=null;
function homeInit(box){
  box.innerHTML=`<section class="chero">
    <div class="chero-copy"><p class="ceyebrow">原神・聖遺物の「珍しさ」を測る</p>
      <h2 class="chero-q"><span class="nw">あなたの聖遺物は、</span><span class="nw">秘境を何日回った</span><span class="nw">人のレベル？</span></h2>
      <p class="chero-lead">UIDを入れるだけで、ショーケースに並べたキャラの聖遺物を「秘境レベル」で測って、カードにします。</p>
      <form id="homeForm" class="chero-form" novalidate><label class="sr" for="homeUid">UID</label><input type="text" id="homeUid" inputmode="numeric" autocomplete="off" maxlength="10" placeholder="UID（9〜10けた）"><button class="btn primary big" id="homeGo" type="submit">カードを作る</button></form>
      <div class="note" id="homeMsg" aria-live="polite"></div>
      <p class="ctrust">ログイン不要・入れるのはUIDだけ・データはこの端末の中だけに保存</p></div>
    <figure class="chero-card"><div id="homeSample" aria-label="カードの見本"></div><figcaption>見本：こんなカードができます</figcaption></figure></section>
    <div id="homeBack"></div>
    <div class="panel" style="margin-top:14px"><details class="more"><summary>「秘境レベル」って？</summary><dl class="ckv" style="margin-top:6px">
      <dt>秘境レベル</dt><dd>そのキャラ（メインOP・有効OP）の条件で、いまの聖遺物と同じだけの有効RVを、秘境だけで揃えるのにかかる平均の日数です（1日9周＝樹脂180）。強さではなく「どれだけ珍しいか」の物差しです。</dd>
      <dt>ランク</dt><dd>★1 〜1週／★2 〜1か月／★3 〜3か月／★4 〜1年／★5 〜3年／★5+ 3年〜。100年以上は ONCE IN A CENTURY、5000年以上は SINCE THE DAWN OF TIME。</dd>
      <dt>有効RV</dt><dd>有効なサブOP（そのキャラに役立つもの）が伸びた量の合計です。1回でいちばん大きく伸びたときを100%として数えます。</dd>
      <dt>使い方のヒント</dt><dd>部位ごとの秘境レベルが、これから秘境を回るつもりの日数より長ければ、その期間にその部位を更新できる見込みは五分以下です。</dd></dl></details></div>
    <p class="note chome-links">ほかの取り込み方：<a href="#" data-hgo="scan">動画・スクショから取り込む</a>　／　くわしく分析：<a href="${LAB_URL}"${ON_SITE?'':' target="_blank" rel="noopener"'}>聖遺物ラボ</a>　／　非公式のファンツールです（HoYoverse とは関係ありません）</p>`;
  box.querySelector('#homeForm').addEventListener('submit',homeGo);
  box.querySelectorAll('[data-hgo]').forEach(a=>a.addEventListener('click',e=>{ e.preventDefault(); cardShowPage(a.dataset.hgo); }));
  const u=$('homeUid'); u.addEventListener('input',()=>{ const v=u.value.replace(/\D/g,''); if(v!==u.value) u.value=v; }); }
function homeRender(){
  const uid=store.get('enkaUid','')||''; if(uid&&!$('homeUid').value) $('homeUid').value=uid; $('homeGo').textContent=uid?'最新のカードを作る':'カードを作る';
  // 見本のカード
  const sm=HOME_SAMPLE||(HOME_SAMPLE=homeSampleChar()); applyBundled(sm);
  const draw=()=>{ const b=$('homeSample'); if(b&&CARD_PAGE==='home') b.innerHTML=cardSVG(sm,charStats(sm),'SK'); }; draw();
  if(CARD_IMG[sm.id]&&!(sm.id in CARD_FIT)&&!CARD_FITTING[sm.id]){ CARD_FITTING[sm.id]=1; fitCardArt(CARD_IMG[sm.id],CARD_ZOOM[sm.id]).then(u=>{ delete CARD_FITTING[sm.id]; CARD_FIT[sm.id]=u||''; draw(); }); }
  // 前回の続き
  const back=$('homeBack'); if(!CHARS.length){ back.innerHTML=''; return; }
  const best=homeBest(CHARS);
  back.innerHTML=`<div class="panel chome-back" style="margin-top:14px"><h2>前回の続き</h2><p class="note">この端末に ${CHARS.length}人のキャラが保存されています。いちばん秘境レベルが高いのは <b class="gold">${esc(best.c.name||'（名前なし）')}</b>（${esc(fmtAge(best.a))}・${esc(tierOf(best.a)[1])}）です。${uid?'上の「最新のカードを作る」で取り直すと、前回からの変化も残ります。':''}</p>
    <div class="btns"><button class="btn primary" data-hb="card">カードを見る</button><button class="btn" data-hb="list">キャラ一覧</button></div></div>`;
  back.querySelector('[data-hb="card"]').addEventListener('click',()=>{ CH_OPEN=best.c.id; renderChars(); cardShowPage('card'); });
  back.querySelector('[data-hb="list"]').addEventListener('click',()=>cardShowPage('list')); }
function homeBest(cs){ const v=a=>isFinite(a)?a:1e15; return cs.map(c=>({c,a:charStats(c).age||0})).sort((x,y)=>v(y.a)-v(x.a))[0]; }
async function homeGo(e){ if(e) e.preventDefault(); const msg=$('homeMsg'), btn=$('homeGo'), uid=$('homeUid').value.replace(/\D/g,'');
  if(!/^\d{9,10}$/.test(uid)){ msg.textContent='UIDは9けたか10けたの数字です（ゲームのメニュー画面の右下などに出ています）。'; return; }
  $('enkaUid').value=uid; try{ store.set('enkaUid',uid); }catch(err){}
  btn.disabled=true; msg.textContent='Enka に問い合わせています…'; let names=null;
  try{ names=await enkaFetch(); }catch(err){} finally{ btn.disabled=false; }
  if(names&&names.length){ msg.textContent=''; homeReveal(names); return; }
  const why=($('enkaMsg').querySelector('p')||$('enkaMsg')).innerText.trim();
  msg.innerHTML=`<p class="err">${esc(why||'取得できませんでした。')}</p><p style="margin-top:4px"><a href="#" id="homeAlt">ほかの方法で取り込む（動画・スクショ・手で受け渡す）</a></p>`;
  $('homeAlt').addEventListener('click',ev=>{ ev.preventDefault(); cardShowPage('scan'); }); }
/* いちばん秘境レベルが高いキャラのカードを出す。下にカードのページを用意してから、上に演出を重ねる */
function homeReveal(names){ const cs=[...new Set(names)].map(n=>CHARS.find(c=>c.name===n)).filter(Boolean); if(!cs.length) return;
  const best=homeBest(cs); CH_OPEN=best.c.id; renderChars(); cardShowPage('card');
  $('cMsg').innerHTML=`${cs.length}人を取り込みました。いちばん秘境レベルが高いのは <b class="gold">${esc(best.c.name)}</b> でした。◀ ▶ でほかのキャラも見られます。`;
  if(!store.get('revealOff',0)) revealPlay(cs,revealVar()); } // 設定で演出をオフにしていれば、カードのページをそのまま見せる
/* ================= カードの登場の演出（v2.1 試作。3案を見比べてから1つに絞る） =================
   思想：お気に入りのキャラのカードが、自分のものとして形になる瞬間を祝う。全員を同じ儀式で迎え、ランクの差は色と★の数で静かに見せる。
         いちばんのカードだけ、溜めを少し長く、光を少し強く。見せ場は縦動画（SNS）。アプリの中ではスキップされる前提
   案：drop ＝落ちるカード：厚みのある重いカードが机に落ち、光の風圧が机の星屑を押し流す。全員のときは机に重なっていく
       photo＝舞い降りる写真：白い縁の写真が、ヒラっと一度だけ揺れて舞い降りる。風圧は軽く
       foil ＝箔押し：紙送りで入った無地のカードに、型押し → 色 → 名前と数字に金の箔 → ★を印のように押す
   描き方：1080×1920 のキャンバスに、時刻 t（ミリ秒）だけから1コマを描く（rvDraw）。スキップは最後の時刻に飛ぶだけ。縦動画の書き出しも同じ関数でコマを作る
   試作の見比べ：URLの末尾に #reveal で操作盤が出る。?reveal=drop|photo|foil で、UIDで取り込んだときの案を切り替え */
const REVEAL_VARS={drop:'案2 落ちるカード',photo:"案2' 舞い降りる写真",foil:'案3 箔押し'};
function revealVar(){ const q=(new URLSearchParams(location.search).get('reveal')||'').toLowerCase(); return REVEAL_VARS[q]?q:'drop'; }
function rvStill(){ try{ return matchMedia('(prefers-reduced-motion: reduce)').matches; }catch(e){ return false; } }
const RVW=1080, RVH=1920, RV_CX=540, RV_CY=800;
const RV_MINCHO='"Shippori Mincho B1","Hiragino Mincho ProN","Yu Mincho",serif', RV_SANS='"Murecho","M PLUS 1p","Hiragino Sans",sans-serif', RV_RB=['#ff9cbc','#ffd27a','#8ff0c4','#8fbaff','#d59bff','#ffc7ea'];
const rvCl=v=>v<0?0:v>1?1:v, rvOC=p=>1-Math.pow(1-p,3), rvIC=p=>p*p*p, rvOB=p=>{ const c1=1.9, c3=c1+1; return 1+c3*Math.pow(p-1,3)+c1*Math.pow(p-1,2); };
const rvRnd=(k,j)=>{ const v=Math.sin(k*127.1+j*311.7)*43758.5453; return v-Math.floor(v); };
// ランク：★の数（★1〜★5）、★5+ は★5に「＋」、100年以上（上限も）は虹
function rvRank(a){ const t=a>0?tierOf(a):TIERS[0], i=Math.max(0,TIERS.indexOf(t)); return {t,i,col:t[2],stars:a>0?Math.min(5,i+1):0,plus:a>0&&i>=5,myth:a>0&&(!isFinite(a)||a>=36500),dawn:a>0&&(!isFinite(a)||a>=1825000)}; }
function rvRR(x,X,Y,w,h,r){ r=Math.min(r,w/2,h/2); x.beginPath(); x.moveTo(X+r,Y); x.arcTo(X+w,Y,X+w,Y+h,r); x.arcTo(X+w,Y+h,X,Y+h,r); x.arcTo(X,Y+h,X,Y,r); x.arcTo(X,Y,X+w,Y,r); x.closePath(); }
function rvCanvas(w,h){ const c=document.createElement('canvas'); c.width=Math.ceil(w); c.height=Math.ceil(h); return c; }
/* ---- カードを1枚の画像にする（保存のときと同じ作り方：書体を埋め込んだSVG → キャンバス）。毎コマSVGを描くと重いので、先に絵にしておく ---- */
async function rvCardImg(c){ applyBundled(c); if(CARD_IMG[c.id]&&!(c.id in CARD_FIT)){ const u=await fitCardArt(CARD_IMG[c.id],CARD_ZOOM[c.id]); CARD_FIT[c.id]=u||''; }
  const NS='http://www.w3.org/2000/svg', W=1960, H=1102, box=document.createElement('div'); box.innerHTML=cardSVG(c,charStats(c),'SK'); const el=box.querySelector('svg'); if(!el) return null;
  el.setAttribute('xmlns',NS); el.setAttribute('xmlns:xlink','http://www.w3.org/1999/xlink'); el.setAttribute('width',W); el.setAttribute('height',H); el.removeAttribute('style');
  try{ const css=await cardFontCSS([...new Set([...el.textContent].map(ch=>ch.codePointAt(0)))]); const st=document.createElementNS(NS,'style'); st.textContent=css; el.insertBefore(st,el.firstChild); }catch(e){}
  const url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(el)],{type:'image/svg+xml'}));
  try{ const im=new Image(); await new Promise((res,rej)=>{ im.onload=res; im.onerror=rej; im.src=url; }); try{ await im.decode(); }catch(e){} await new Promise(r=>setTimeout(r,200));
    const cv=rvCanvas(W,H); cv.getContext('2d').drawImage(im,0,0,W,H); return cv; }catch(e){ return null; } finally{ URL.revokeObjectURL(url); } }
function rvScaled(src,w,h){ const o=rvCanvas(w,h); if(src) o.getContext('2d').drawImage(src,0,0,w,h); return o; }
// 型押しの版：カードの明るさの差から凹凸を作る（読めないとき〈画像が汚染扱い〉は、暗く沈めた絵で代わりにする）
function rvEmboss(src,w,h){ const o=rvScaled(src,w,h), x=o.getContext('2d');
  try{ const d=x.getImageData(0,0,w,h), a=d.data, L=new Float32Array(w*h); for(let i=0;i<w*h;i++) L[i]=a[i*4]*.3+a[i*4+1]*.59+a[i*4+2]*.11;
    for(let y=0;y<h;y++) for(let X=0;X<w;X++){ const i=y*w+X, j=Math.max(0,y-2)*w+Math.max(0,X-2), e=(L[i]-L[j])*1.3, g=Math.max(0,Math.min(255,30+e+L[i]*.1)); a[i*4]=g*.86; a[i*4+1]=g*.88; a[i*4+2]=Math.min(255,g+14); a[i*4+3]=255; }
    x.putImageData(d,0,0); }catch(e){ x.fillStyle='rgba(12,14,30,.78)'; x.fillRect(0,0,w,h); } return o; }
/* ---- 先に作っておく絵：机・星屑・無地のカード・影・光 ---- */
var RV_ASSETS=null;
function rvAssets(){ if(RV_ASSETS) return RV_ASSETS; const desk=rvCanvas(RVW,RVH), x=desk.getContext('2d');
  // 机：夜空を映した黒い漆の天板を、真上から見下ろす。紺の地に、左上からの照り返しと斜めのつや、映り込んだ星、隅から流れ込む金粉（蒔絵）
  let g=x.createRadialGradient(540,820,0,540,820,1400); g.addColorStop(0,'#1f2452'); g.addColorStop(.45,'#0f1234'); g.addColorStop(1,'#05061a'); x.fillStyle=g; x.fillRect(0,0,RVW,RVH);
  g=x.createRadialGradient(240,330,0,240,330,760); g.addColorStop(0,'rgba(165,180,255,.13)'); g.addColorStop(1,'rgba(165,180,255,0)'); x.fillStyle=g; x.fillRect(0,0,RVW,RVH);
  for(const [y0,y1,a] of [[180,1580,.09],[520,1920,.04]]){ g=x.createLinearGradient(0,y0,RVW,y1); g.addColorStop(0,'rgba(210,220,255,0)'); g.addColorStop(.46,'rgba(210,220,255,0)'); g.addColorStop(.5,`rgba(215,225,255,${a})`); g.addColorStop(.54,'rgba(210,220,255,0)'); g.addColorStop(1,'rgba(210,220,255,0)'); x.fillStyle=g; x.fillRect(0,0,RVW,RVH); }
  for(let i=0;i<340;i++){ const r=rvRnd(i,1), big=r<.06; x.globalAlpha=(big?.45:.12)+rvRnd(i,2)*.35; x.fillStyle=rvRnd(i,3)<.2?'#ffe8b8':'#dfe6ff'; x.beginPath(); x.arc(rvRnd(i,4)*RVW,rvRnd(i,5)*RVH,big?1.7:.5+rvRnd(i,6)*.9,0,6.283); x.fill(); }
  // 金粉：左下と右上の隅から、帯になって流れ込む。真ん中（カードと文字の後ろ）はまばら
  const seg=(px,py,ax,ay,bx,by)=>{ const vx=bx-ax, vy=by-ay, t=Math.max(0,Math.min(1,((px-ax)*vx+(py-ay)*vy)/(vx*vx+vy*vy))); return Math.hypot(px-ax-t*vx,py-ay-t*vy); };
  const GOLD=['#e8c877','#f6e2a8','#c9a24f','#ffefc4'];
  for(const [ax,ay,bx,by,r0] of [[-120,1380,620,2040,260],[560,-80,1200,520,220]]) for(let k=0;k<=6;k++){ const cx=ax+(bx-ax)*k/6, cy=ay+(by-ay)*k/6; g=x.createRadialGradient(cx,cy,0,cx,cy,r0); g.addColorStop(0,'rgba(226,190,110,.07)'); g.addColorStop(1,'rgba(226,190,110,0)'); x.fillStyle=g; x.fillRect(cx-r0,cy-r0,r0*2,r0*2); } // 金粉の帯に沿った淡い金のもや
  for(let i=0;i<11000;i++){ const px=rvRnd(i,21)*RVW, py=rvRnd(i,22)*RVH, d1=seg(px,py,-120,1380,620,2040), d2=seg(px,py,560,-80,1200,520), d=Math.min(d1/230,d2/190), dens=Math.exp(-d*d)*.95+.035;
    if(rvRnd(i,23)>dens) continue; const big=rvRnd(i,24)<.02; x.globalAlpha=.28+rvRnd(i,25)*.55; x.fillStyle=GOLD[(rvRnd(i,26)*4)|0];
    if(big){ const r=1.6+rvRnd(i,27)*1.2; x.shadowColor='#ffe2a0'; x.shadowBlur=6; x.beginPath(); for(let k=0;k<8;k++){ const an=k*Math.PI/4, rr=k%2?r*.35:r*2.2; x.lineTo(px+Math.cos(an)*rr,py+Math.sin(an)*rr); } x.closePath(); x.fill(); x.shadowBlur=0; }
    else{ const w=1+rvRnd(i,28)*1.8, h=.8+rvRnd(i,29)*1.2; x.save(); x.translate(px,py); x.rotate(rvRnd(i,30)*3.14); x.fillRect(-w/2,-h/2,w,h); x.restore(); } }
  x.globalAlpha=1; g=x.createRadialGradient(540,880,560,540,880,1300); g.addColorStop(0,'rgba(0,0,0,0)'); g.addColorStop(1,'rgba(0,0,0,.45)'); x.fillStyle=g; x.fillRect(0,0,RVW,RVH);
  const dust=[...Array(150)].map((_,i)=>({x:rvRnd(i,11)*RVW,y:180+rvRnd(i,12)*(RVH-360),r:.7+rvRnd(i,13)*1.7,a:.18+rvRnd(i,14)*.5,ph:rvRnd(i,15)*6.28,col:rvRnd(i,16)<.35?'#f5dfa6':'#e6ecff'}));
  return RV_ASSETS={desk,dust,sh:{},glow:{}}; }
// 映り込み：カードの下の部分を上下逆さにして、ぼかし（縮めて広げる）、下へ向かって消えるようにした絵
function rvReflection(src,w,h){ const rh=Math.round(h*.42), sm=rvCanvas(w/6,rh/6), o=rvCanvas(w,rh), y=o.getContext('2d'), s2=sm.getContext('2d');
  s2.save(); s2.scale(1,-1); s2.drawImage(src,0,0,src.width,src.height,0,-h/6,w/6,h/6); s2.restore();
  y.imageSmoothingQuality='high'; y.drawImage(sm,0,0,w,rh); y.globalCompositeOperation='destination-in'; const g=y.createLinearGradient(0,0,0,rh); g.addColorStop(0,'rgba(0,0,0,.55)'); g.addColorStop(.35,'rgba(0,0,0,.18)'); g.addColorStop(1,'rgba(0,0,0,0)'); y.fillStyle=g; y.fillRect(0,0,w,rh); return o; }
function rvBlank(w,h){ const o=rvCanvas(w,h), x=o.getContext('2d'), g=x.createLinearGradient(0,0,w,h); g.addColorStop(0,'#16183a'); g.addColorStop(1,'#090b1d'); x.fillStyle=g; x.fillRect(0,0,w,h);
  x.strokeStyle='rgba(233,211,154,.42)'; x.lineWidth=2; rvRR(x,14,14,w-28,h-28,8); x.stroke(); x.strokeStyle='rgba(233,211,154,.16)'; x.lineWidth=1; rvRR(x,26,26,w-52,h-52,5); x.stroke(); return o; }
// 影と光：ぼかしは重いので、1回だけ描いて使い回す（shadowBlur で、図形は枠の外に置いて影だけを写す）
function rvBlurSprite(w,h,blur,col,r){ const pad=blur*2.2, o=rvCanvas(w+pad*2,h+pad*2), x=o.getContext('2d'); x.shadowColor=col; x.shadowBlur=blur; x.shadowOffsetX=o.width; x.fillStyle='#000'; rvRR(x,pad-o.width,pad,w,h,r); x.fill(); return {cv:o,pad}; }
function rvShadowOf(A,w,h){ const k=w+'x'+h; return A.sh[k]||(A.sh[k]={hard:rvBlurSprite(w,h,10,'rgba(0,0,0,.95)',12),soft:rvBlurSprite(w,h,46,'rgba(0,0,0,.9)',12)}); }
function rvGlowOf(A,w,h,rk){ const k=w+'x'+h+(rk.myth?'myth':rk.col); if(A.glow[k]) return A.glow[k];
  if(!rk.myth) return A.glow[k]=rvBlurSprite(w,h,64,rk.col,14);
  const s=rvBlurSprite(w,h,64,RV_RB[0],14), x=s.cv.getContext('2d'); x.globalCompositeOperation='lighter'; // 虹：色違いの光を少しずつずらして重ねる
  RV_RB.slice(1,5).forEach((c,i)=>{ const a=i*Math.PI/2, t=rvBlurSprite(w,h,64,c,14); x.globalAlpha=.75; x.drawImage(t.cv,Math.cos(a)*40,Math.sin(a)*40); }); return A.glow[k]=s; }
function rvSprite(x,sp,w,h,alpha,op){ if(alpha<=0) return; x.save(); if(op) x.globalCompositeOperation=op; x.globalAlpha*=alpha; x.drawImage(sp.cv,-w/2-sp.pad,-h/2-sp.pad); x.restore(); }
/* ---- 段取り：1枚ずつの時刻を決める ---- */
// drop の pre＝カードはまだ画面の外で、影だけが近づいてくる時間
const RV_T={drop:{lead:250,pre:430,preBest:2000,fall:230,read:1050,after:1900},photo:{lead:250,fall:1050,read:780,charge:750,after:1900},foil:{lead:150,read:2150,charge:750,after:2100}};
// テンポ：いちばんのカードの直前の1枚までは、同じ駆け足で → 直前の1枚だけ少し落とす（溜めにつなぐ）。sp＝時間の倍率
function rvTempo(k,m){ if(m<=1) return 1; return k===m-1?.7:.34; }
function rvPlan(items,v,mode){ const T=RV_T[v], n=items.length, A=rvAssets(), ev=[]; let t=T.lead;
  items.forEach((it,k)=>{ const best=k===n-1; it.best=best; it.t0=t; it.dir=rvRnd(k,7)<.5?-1:1;
    if(v==='photo'){ it.W=900; it.H=506; } else { it.W=980; it.H=551; }
    it.img1=rvScaled(it.img,it.W,it.H); if(v!=='foil') it.refl=rvReflection(it.img1,it.W,it.H); if(v==='foil') it.emb=rvEmboss(it.img,it.W,it.H);
    it.rest=best?{x:RV_CX,y:RV_CY,rot:0}:{x:RV_CX+(rvRnd(k,8)-.5)*90,y:RV_CY+(rvRnd(k,9)-.5)*70,rot:(rvRnd(k,10)-.5)*.24};
    if(v==='foil'){ it.off=best?T.charge:0; it.press=t+380+it.off; it.infoIn=it.press+770; it.starAt=it.infoIn+430; it.press2=best?it.infoIn+900:0; it.land=it.press; t+=T.read+it.off; }
    else{ const sp=it.sp=best?1:rvTempo(k,n-1); it.drop=t+(v==='drop'?(best?T.preBest:T.pre*sp):(best?T.charge:0)); it.fall=v==='drop'?(best?T.fall:Math.max(140,T.fall*Math.sqrt(sp))):T.fall*(best?1:Math.max(.6,sp)); it.land=it.drop+it.fall; it.infoIn=it.land+(v==='drop'?220:100)*sp; it.starAt=it.infoIn+260*sp; t=it.land+T.read*sp;
      const w=it.W+(v==='photo'?32:0), h=it.H+(v==='photo'?32:0);
      ev.push({t0:it.land,x:it.rest.x,y:it.rest.y,rot:it.rest.rot,w,h,col:it.rk.myth?'#efe6ff':it.rk.col,str:(v==='photo'?.42:.72)*(best?1.4:1),rings:best?[[0,1],[220,.6]]:[[0,1]]}); } });
  items.forEach((it,k)=>{ it.nx=k<n-1?items[k+1].t0:0; });
  const b=items[n-1], E=v==='foil'?b.infoIn+2200:b.land+T.after; return {v,mode,items,events:ev,A,E,total:E+1500}; }
/* ---- 1コマを描く ---- */
function rvDraw(x,P,t){ const A=P.A; x.setTransform(1,0,0,1,0,0); x.globalCompositeOperation='source-over'; x.globalAlpha=1; x.drawImage(A.desk,0,0);
  // 光の風圧：輪が広がり、机の星屑を押し流す
  const evs=P.events.filter(e=>t>e.t0), RR=(e,dt)=>e.str*430*(1-Math.exp(-dt/380)); // 輪はカードの縁から外へ、机の上に収まる大きさまで
  // 落ちるカード：いちばんのカードを待つあいだ、星屑が落ちる場所へだんだん速く吸い寄せられる（着地の風圧で一気に外へ）
  const bb=P.items[P.items.length-1], suck=P.v==='drop'&&P.items.length>1&&t>=bb.t0?(t<bb.land?Math.pow(rvCl((t-bb.t0)/(bb.drop-bb.t0)),2):Math.exp(-(t-bb.land)/90)):0;
  for(const d of A.dust){ let dx=0,dy=0,b=0; if(suck>0.002){ const vx=bb.rest.x-d.x, vy=bb.rest.y-d.y, dd=Math.hypot(vx,vy)||1, m=Math.min(dd*.55,260)*suck; dx+=vx/dd*m; dy+=vy/dd*m; b+=suck*.7; } for(const e of evs){ const dt=t-e.t0, R=RR(e,dt), vx=d.x-e.x, vy=d.y-e.y, dd=Math.hypot(vx,vy)||1, ex=Math.max(0,dd-Math.max(e.w,e.h)*.42);
      if(R>ex){ const m=e.str*150*Math.exp(-ex/650)*rvCl((R-ex)/240); dx+=vx/dd*m; dy+=vy/dd*m; } b+=Math.exp(-Math.pow((R-ex)/80,2))*e.str*Math.max(0,1-dt/1800); }
    x.globalAlpha=Math.min(1,d.a*(.72+.28*Math.sin(t*.0016+d.ph))+b*.7); x.fillStyle=d.col; x.beginPath(); x.arc(d.x+dx,d.y+dy,d.r*(1+b),0,6.283); x.fill(); }
  x.globalAlpha=1;
  for(const e of evs) for(const [dl,k] of e.rings){ const dt=t-e.t0-dl; if(dt<0||dt>1400) continue; const R=RR(e,dt), al=Math.pow(1-dt/1400,2)*Math.pow(1-R/(e.str*430+1),1.2)*Math.min(1,e.str*1.2)*k; // 広がるほど薄く
    x.save(); x.translate(e.x,e.y); x.rotate(e.rot); x.strokeStyle=e.col; for(const [lw,a] of [[36,.08],[14,.16],[3,.3]]){ x.globalAlpha=al*a; x.lineWidth=lw; rvRR(x,-e.w/2-R,-e.h/2-R,e.w+2*R,e.h+2*R,12+R*.9); x.stroke(); } x.restore(); }
  x.globalAlpha=1;
  if(!P.noCards){ if(P.v==='foil') rvDrawFoil(x,P,t); else rvDrawPile(x,P,t);
    if(P.v==='drop'){ rvDrawSpot(x,P,t); rvDrawSeal(x,P,t); }
  }
  rvDrawInfo(x,P,t); rvDrawFrame(x,P,t); } // noCards：一覧へ広げるとき、カードは上に重ねた一覧に任せて、机と文字だけを描く（机ごとゆっくり消える）
// 落ちるカード：いちばんのカードの溜め。見てほしいのは「これから降りてくる場所」（P.pre：spot＝A／stars＝B／both）
//   A スポットライト：落ちる場所に真上から光の輪が差し、まわりが少し沈む
//   B 天板に灯る星座：落ちる場所に、そのカードの星座（5部位の星。★の数ではない）が、鼓動に合わせて1つずつ灯り、線でつながる。カードの星座とぴたりと重なって着地し、着地で外へはじける
function rvPreQ(P,t){ const b=P.items[P.items.length-1]; if(P.v!=='drop'||t<b.t0) return null; return {b,q:rvCl((t-b.t0)/(b.drop-b.t0)),u:t<b.land?-1:(t-b.land)/550}; }
function rvDrawSpot(x,P,t){ const Q=rvPreQ(P,t); if(!Q||!/spot|both/.test(P.pre)||Q.u>1) return; const {b,q,u}=Q, e=q*q*(3-2*q), f=(u<0?e:1-u)*(P.items.length>1?1:.8), cx=b.rest.x, cy=b.rest.y;
  x.save(); x.translate(cx,cy); x.scale(1.3,1); let g=x.createRadialGradient(0,0,300,0,0,860); g.addColorStop(0,'rgba(2,3,10,0)'); g.addColorStop(1,`rgba(2,3,10,${.72*f})`); x.fillStyle=g; x.fillRect(-RVW,-RVH,RVW*2,RVH*2); // まわりが沈む
  x.globalCompositeOperation='lighter'; g=x.createRadialGradient(0,0,0,0,0,500); g.addColorStop(0,`rgba(255,240,212,${.2*f})`); g.addColorStop(.6,`rgba(255,240,212,${.09*f})`); g.addColorStop(1,'rgba(255,240,212,0)'); x.fillStyle=g; x.fillRect(-500,-500,1000,1000); x.restore(); } // 真上からの光
function rvStarsOf(st){ const cx0=360, cy0=361, R0=58, R=246, BND=[1,7,30,90,365,1095,10950], ANG={flower:-90,plume:-18,sands:54,goblet:126,circlet:198}; // カードの星座と同じ計算（中心・半径・部位の向き・ランクの帯ごとの目盛り）
  const rad=d=>{ if(!(d>1)) return R0; if(d>=10950) return R; let k=0; while(k<5&&d>=BND[k+1]) k++; return R0+(k+(Math.log(d)-Math.log(BND[k]))/(Math.log(BND[k+1])-Math.log(BND[k])))/6*(R-R0); };
  return SLOTS.map(s=>{ const d=st.slots[s].age, r=rad(isFinite(d)?d:1e9), a=ANG[s]*Math.PI/180; return {s,has:d>0,x:cx0+r*Math.cos(a),y:cy0+r*Math.sin(a)}; }); }
function rvDrawSeal(x,P,t){ const Q=rvPreQ(P,t); if(!Q||!/stars|both/.test(P.pre)||Q.u>1) return; const {b,q,u}=Q, S=b.stars||(b.stars=rvStarsOf(b.st)), on=S.filter(p=>p.has), kx=b.W/1200, ky=b.H/675;
  // 星座は、はじめひと回り大きく（1.3倍）灯り、溜めが進むにつれて中心へ集まって、着地の瞬間にカードの星座の大きさにぴたりと収まる
  const C=[b.rest.x+(360-600)*kx,b.rest.y+(361-337.5)*ky], cq=rvCl((q-.05)/.92), sz=u<0?1.3-.3*cq*cq*(3-2*cq):1;
  const X=p=>C[0]+(b.rest.x+(p.x-600)*kx-C[0])*sz, Y=p=>C[1]+(b.rest.y+(p.y-337.5)*ky-C[1])*sz, T=k=>.12+k*.15, fade=u<0?1:1-u, burst=u<0?0:u;
  x.save(); x.globalCompositeOperation='lighter'; x.lineCap='round';
  // 線：5つ灯ったあとに、花→羽→砂→杯→冠→花の順でつながる
  const lp=rvCl((q-.8)/.17); if(lp>0) for(let i=0;i<5;i++){ const p1=S[i], p2=S[(i+1)%5]; if(!p1.has||!p2.has) continue; const f=rvCl(lp*5-i); if(f<=0) continue;
    const x1=X(p1), y1=Y(p1), x2=x1+(X(p2)-x1)*f, y2=y1+(Y(p2)-y1)*f; for(const [lw,a] of [[7,.12],[2,.7]]){ x.globalAlpha=a*fade; x.strokeStyle='#f0d898'; x.lineWidth=lw; x.beginPath(); x.moveTo(x1,y1); x.lineTo(x2,y2); x.stroke(); } }
  // 星：鼓動に合わせて1つずつ。灯るときに小さくふくらむ。着地で外へ広がって消える
  on.forEach((p,k)=>{ const v=(q-T(k))/.08; if(v<=0) return; const sc=(v<1?rvOB(rvCl(v)):1)*(1+burst*1.6), r=9*sc, cx=X(p), cy=Y(p);
    const g=x.createRadialGradient(cx,cy,0,cx,cy,r*5); g.addColorStop(0,`rgba(255,236,190,${.55*fade})`); g.addColorStop(1,'rgba(255,236,190,0)'); x.globalAlpha=1; x.fillStyle=g; x.fillRect(cx-r*5,cy-r*5,r*10,r*10);
    x.globalAlpha=fade; x.fillStyle='#fff6dc'; x.beginPath(); for(let i=0;i<8;i++){ const a=i*Math.PI/4, rr=i%2?r*.28:r*1.6; x.lineTo(cx+Math.cos(a)*rr,cy+Math.sin(a)*rr); } x.closePath(); x.fill(); });
  x.restore(); }
function rvPose(P,it,t){ const r=it.rest, T=RV_T[P.v], fl=t<it.drop?Math.sin((t-it.t0)/280)*5:0;
  // 落ちるカード：はじめはカメラより上にあって画面に映らず、影だけが机に落ちて近づいてくる（h：1.6→0.5）。最後に一気に落ちる（0.5→0）
  if(P.v==='drop'){ const pre=t<it.drop; let h; if(pre){ const q=rvCl((t-it.t0)/(it.drop-it.t0)); h=1.6-1.1*q*q*(3-2*q); } else { const p=rvCl((t-it.drop)/it.fall); h=.5*(1-p*p); }
    let s=1+h*.85; const dl=t-it.land; if(dl>0&&dl<200) s*=1-.012*Math.sin(Math.PI*dl/200);
    return {x:r.x+h*it.dir*70,y:r.y-h*150,rot:r.rot+h*it.dir*.16,s,sy:1-Math.min(h,.6)*.3,h,a:pre?0:1,sa:rvCl((t-it.t0)/300),edge:5+Math.min(h,.6)*30}; }
  // 写真：減速しながら降り、一度だけ大きく揺れて（ヒラっと）置かれる
  const p=t<it.drop?0:rvCl((t-it.drop)/it.fall), h=Math.pow(1-p,1.7), sw=Math.cos(1.25*Math.PI*p)*Math.pow(1-p,.8);
  return {x:r.x+it.dir*150*sw,y:r.y-h*130+fl,rot:r.rot+it.dir*.26*sw,s:1+h*.4,sy:1-.22*Math.abs(Math.sin(1.25*Math.PI*p))*(1-p),h,a:rvCl((t-it.t0)/260),edge:0}; }
function rvCardDraw(x,it,ps,kind,dim,L,lit){ const W=it.W, H=it.H; x.save(); x.globalAlpha*=ps.a; x.translate(ps.x,ps.y); x.rotate(ps.rot); x.scale(ps.s,ps.s*ps.sy);
  if(kind!=='photo'){ const e=ps.edge, g=x.createLinearGradient(0,H/2-6,0,H/2+e); g.addColorStop(0,'#d8bb72'); g.addColorStop(.45,'#8a6c34'); g.addColorStop(1,'#33270f'); x.fillStyle=g; rvRR(x,-W/2+1,-H/2+e,W-2,H,12); x.fill(); } // 厚み：金の小口
  else{ x.fillStyle='#f3efe6'; rvRR(x,-W/2-16,-H/2-16,W+32,H+32,3); x.fill(); x.fillStyle='rgba(0,0,0,.06)'; x.fillRect(-W/2-16,H/2+10,W+32,6); } // 写真の白い縁
  x.save(); rvRR(x,-W/2,-H/2,W,H,kind==='photo'?2:12); x.clip();
  const im=ps.s*ps.sy<=1.05?it.img1:(it.img||it.img1);
  if(L){ x.drawImage(L.blank,-W/2,-H/2,W,H); if(L.emb>0){ x.globalAlpha=ps.a*L.emb; x.drawImage(it.emb,-W/2,-H/2,W,H); } if(L.col>0){ x.globalAlpha=ps.a*L.col; x.drawImage(im,-W/2,-H/2,W,H); } x.globalAlpha=ps.a;
    if(L.plate>0){ const g=x.createLinearGradient(0,-H/2,0,H/2); g.addColorStop(0,`rgba(255,236,190,${.1*L.plate})`); g.addColorStop(1,`rgba(255,236,190,${.02*L.plate})`); x.fillStyle=g; x.fillRect(-W/2,-H/2,W,H); }
    if(L.flash>0){ x.fillStyle=`rgba(255,246,220,${L.flash})`; x.fillRect(-W/2,-H/2,W,H); } }
  else x.drawImage(im,-W/2,-H/2,W,H);
  if(lit!=null&&lit<1){ const W2=W*1.15, D='rgba(6,8,22,.72)'; if(lit<=0) x.fillStyle=D; else { const g=x.createRadialGradient(0,0,lit*W2,0,0,lit*W2+300); g.addColorStop(0,'rgba(6,8,22,0)'); g.addColorStop(1,D); x.fillStyle=g; } x.fillRect(-W/2,-H/2,W,H); } // 落ちてくるあいだは逆光で暗く、着地で中央から灯る
  x.restore(); if(dim>0){ x.fillStyle=`rgba(2,3,10,${dim})`; const b=kind==='photo'?16:0; rvRR(x,-W/2-b,-H/2-b,W+2*b,H+2*b,kind==='photo'?3:12); x.fill(); } // 下になったカードは沈める（写真は白い縁ごと）
  if(lit!=null&&lit<1){ const ra=1-rvCl(lit*1.6); x.save(); x.globalAlpha*=ra; x.strokeStyle='#f3dc9e'; x.shadowColor='#f5dfa6'; x.shadowBlur=18; x.lineWidth=3/ps.s; rvRR(x,-W/2,-H/2,W,H,12); x.stroke(); x.globalAlpha*=.5; x.lineWidth=1.2/ps.s; rvRR(x,-W/2+10,-H/2+10,W-20,H-20,8); x.stroke(); x.restore(); } // 逆光の縁：暗くても「カード」と分かるように
  x.restore(); }
function rvShadowDraw(x,A,it,ps,kind){ const w=it.W+(kind==='photo'?32:0), h=it.H+(kind==='photo'?32:0), S=rvShadowOf(A,w,h), sc=1+ps.h*.22;
  x.save(); x.translate(ps.x+8+ps.h*60,ps.y+14+ps.h*110); x.rotate(ps.rot); x.scale(sc,sc*ps.sy); x.globalAlpha=ps.sa!=null?ps.sa:ps.a;
  rvSprite(x,S.hard,w,h,Math.max(0,1-ps.h)*(kind==='photo'?.45:.5)); rvSprite(x,S.soft,w,h,kind==='drop'?Math.min(.34,.08+(1.6-ps.h)*.24):.25+ps.h*.35); x.restore(); } // 影：遠いほど薄くぼやけ、近づくほど濃くくっきり
function rvGlowDraw(x,A,it,ps,a,kind){ if(a<=0) return; const w=it.W+(kind==='photo'?32:0), h=it.H+(kind==='photo'?32:0), G=rvGlowOf(A,w,h,it.rk);
  x.save(); x.translate(ps.x,ps.y); x.rotate(ps.rot); x.scale(ps.s,ps.s*ps.sy); rvSprite(x,G,w,h,a*(it.rk.myth?.55:1),'lighter'); x.restore(); } // 虹の光は重ねて明るいので弱める
function rvDrawPile(x,P,t){ const kind=P.v, its=P.items, b=its[its.length-1], spot=kind==='drop'&&its.length>1?(.2*rvCl((t-b.t0)/450)+.38*(q=>q*q*(3-2*q))(rvCl((t-b.t0)/(b.drop-b.t0))))*(1-rvCl((t-b.land)/600)):0; // いちばんのカードを待つあいだ、机のカードをだんだん深く沈める（下のカードの星座が、天板に灯る星座と二重に見えないように）
  // いちばんのカードを待つあいだ、落ちる場所の机からランク色の光が漏れてくる（机のカードの下から、縁にだけ見える）
  if(kind==='drop'&&t>=b.t0&&t<b.land){ const q=rvCl((t-b.t0)/(b.drop-b.t0)), hb=q*.5+.38*Math.exp(-Math.pow((q-.4)/.07,2))+.5*Math.exp(-Math.pow((q-.72)/.07,2))+(q>.84?(q-.84)/.16*.45:0); rvGlowDraw(x,P.A,b,{x:b.rest.x,y:b.rest.y,rot:0,s:1.04,sy:1},Math.min(1,hb)*.95,kind); } // 光はドクン、ドクンと2回脈打ってから最大に
  // 映り込み：天板に映ったカード。カードが高いほど縁から離れて薄く、着地で縁にぴたりと合う（上に重なったカードに隠れる分は見えない）
  its.forEach(it=>{ if(t<it.t0||!it.refl) return; const ps=rvPose(P,it,t); if(ps.a<=0) return; const gap=ps.h*240, a=ps.a*(1-Math.min(1,ps.h)*.6)*(kind==='photo'?.7:1);
    x.save(); x.globalAlpha=a; x.translate(ps.x,ps.y); x.rotate(ps.rot); x.scale(ps.s,ps.s*ps.sy); x.drawImage(it.refl,-it.W/2,it.H/2+(kind==='photo'?32:4)+gap/ps.s,it.W,it.refl.height); x.restore(); });
  its.forEach((it,k)=>{ if(t<it.t0) return; const ps=rvPose(P,it,t); let dim=0; for(let j=k+1;j<its.length;j++) if(t>its[j].land) dim+=.34*rvCl((t-its[j].land)/380); dim=Math.min(.6,dim+(it.best?0:spot));
    rvShadowDraw(x,P.A,it,ps,kind);
    // 光：いちばんのカードは溜めのあいだ強まり、着地で強く光って、そのまま残る。ほかのカードは着地で一度だけ
    const dl=t-it.land; let ga=0; if(it.best){ ga=t<it.drop?rvCl((t-it.t0)/(it.drop-it.t0))*.85:dl<0?.85:.45+.55*Math.exp(-dl/500); } else if(dl>0) ga=.42*Math.exp(-dl/420)*(1-dim);
    if(!(kind==='drop'&&it.best&&dl<0)) rvGlowDraw(x,P.A,it,ps,ga*ps.a,kind);
    if(ps.a>0) rvCardDraw(x,it,ps,kind,dim,null,kind==='drop'?(dl<0?0:rvCl(dl/520)):null); }); }
function rvDrawFoil(x,P,t){ for(const it of P.items){ if(t<it.t0) continue; let X=RV_CX+(1-rvOC(rvCl((t-it.t0)/380)))*1150;
    if(it.nx){ const po=rvCl((t-it.nx)/380); if(po>=1) continue; X-=rvIC(po)*1150; }
    const tp=t-it.press, t2=it.press2?t-it.press2:-1; let s=1; if(tp>=0&&tp<170) s=1-.016*Math.sin(Math.PI*tp/170); if(t2>=0&&t2<170) s=1-.016*Math.sin(Math.PI*t2/170);
    const ps={x:X,y:RV_CY,rot:0,s,sy:1,h:0,a:1,edge:6};
    const plate=it.best&&tp<0?rvCl((t-it.t0-380)/it.off):tp<0?rvCl((t-it.t0-220)/160):0;
    const flash=Math.max(tp>=0&&tp<300?Math.pow(1-tp/300,2)*.35:0,t2>=0&&t2<420?Math.pow(1-t2/420,2)*.3:0);
    rvShadowDraw(x,P.A,it,ps,'foil');
    let ga=0; if(it.best) ga=tp<0?plate*.8:.45+.45*Math.exp(-Math.max(0,t2<0?tp:t2)/600); else if(tp>0) ga=.38*Math.exp(-(tp-500)/500)*rvCl((tp-500)/200);
    rvGlowDraw(x,P.A,it,ps,ga,'foil');
    rvCardDraw(x,it,ps,'foil',0,{blank:P.blank||(P.blank=rvBlank(it.W,it.H)),emb:rvCl((tp-120)/380),col:rvCl((tp-520)/360),plate,flash}); } }
/* ---- 名前・★・秘境レベル（カードの下） ---- */
function rvLS(x,v){ if('letterSpacing' in x) x.letterSpacing=v; }
function rvFoilText(x,txt,cx,y,size,dt,long){ // 金の箔：縦の金のグラデーションで塗り、光の帯を横切らせる
  if(dt<0) return; const a=rvCl(dt/150), sc=1+.05*(1-rvOC(rvCl(dt/170))); x.save(); x.globalAlpha*=a; x.translate(cx,y); x.scale(sc,sc); x.textAlign='center';
  let g=x.createLinearGradient(0,-size*.85,0,size*.1); g.addColorStop(0,'#fff4cc'); g.addColorStop(.42,'#e8c56c'); g.addColorStop(.55,'#a67a2e'); g.addColorStop(1,'#f0d48a'); x.fillStyle=g; x.fillText(txt,0,0);
  const sd=long?1300:750, p=(dt-120)/sd; if(p>0&&p<1){ const w=x.measureText(txt).width, sx=-w/2-160+p*(w+320); g=x.createLinearGradient(sx-110,0,sx+110,0); g.addColorStop(0,'rgba(255,255,255,0)'); g.addColorStop(.5,'rgba(255,255,255,.95)'); g.addColorStop(1,'rgba(255,255,255,0)'); x.fillStyle=g; x.fillText(txt,0,0); }
  x.restore(); }
function rvStarPath(x,R){ x.beginPath(); for(let i=0;i<10;i++){ const a=-Math.PI/2+i*Math.PI/5, r=i%2?R*.44:R; x.lineTo(Math.cos(a)*r,Math.sin(a)*r); } x.closePath(); }
function rvDrawStars(x,it,t,cy,stamp){ const rk=it.rk, n=rk.stars, tot=n+(rk.plus?1:0); if(!tot) return; const R=27, gap=70, x0=RV_CX-(tot-1)*gap/2;
  for(let k=0;k<tot;k++){ const sp=it.sp||1, tk=it.starAt+k*(stamp?135:105*sp), p=(t-tk)/(stamp?170:260*Math.sqrt(sp)); if(p<=0) continue; const q=rvCl(p), sc=stamp?1.7-.7*rvOC(q):rvOB(q), col=rk.myth?RV_RB[k%5]:rk.col;
    x.save(); x.globalAlpha*=stamp?q:rvCl(q*2.2); x.translate(x0+k*gap,cy); x.scale(sc,sc); x.fillStyle=col; x.shadowColor=col; x.shadowBlur=it.best?22:14;
    if(k<n){ rvStarPath(x,R); x.fill(); } else { const b=R*.2, l=R*.72; rvRR(x,-l,-b,l*2,b*2,b); x.fill(); rvRR(x,-b,-l,b*2,l*2,b); x.fill(); } // ★5+ の「＋」
    x.restore();
    if(stamp&&p>.9&&p<2.6){ const r=(p-.9)/1.7; x.save(); x.globalAlpha*=(1-r)*.5; x.strokeStyle=col; x.lineWidth=2; x.beginPath(); x.arc(x0+k*gap,cy,R*(1.15+r*.9),0,6.283); x.stroke(); x.restore(); } } } // 印を押した跡の輪
function rvDrawInfo(x,P,t){ for(const it of P.items){ const foil=P.v==='foil', sp=it.sp||1, a=rvCl((t-it.infoIn)/(foil?1:420*sp))*(it.nx?1-rvCl((t-it.nx)/(200*Math.min(1,sp*1.6))):1); if(a<=0) continue;
    const up=foil?0:(1-rvOC(rvCl((t-it.infoIn)/(560*sp))))*16, st=it.st, mm=fmtAge(st.age||0).match(/^([\d.,]+[KMB]?)\s*(.*)$/);
    x.save(); x.globalAlpha=a; x.textAlign='center'; x.textBaseline='alphabetic';
    x.font=`700 68px ${RV_MINCHO}`; rvLS(x,'6px'); const nm=it.c.name||'（名前なし）';
    if(foil) rvFoilText(x,nm,RV_CX,1240,68,t-it.infoIn,it.best); else { x.fillStyle='#f4ecd6'; x.shadowColor='rgba(0,0,0,.6)'; x.shadowBlur=12; x.fillText(nm,RV_CX,1240+up); x.shadowBlur=0; }
    rvDrawStars(x,it,t,1334+up,foil);
    const la=foil?rvCl((t-it.infoIn-80)/300):1; x.globalAlpha=a*la; x.font=`400 22px ${RV_SANS}`; rvLS(x,'8px'); x.fillStyle='#8f8a7c'; x.fillText('秘境レベル',RV_CX,1428+up);
    // 数字は大きく、単位は小さく。2つを並べて中央に
    const num=mm?mm[1]:fmtAge(st.age||0), unit=mm?mm[2]:''; x.font=`400 70px ${RV_SANS}`; rvLS(x,'1px'); const w1=x.measureText(num).width; x.font=`400 28px ${RV_SANS}`; rvLS(x,'5px'); const w2=unit?x.measureText(unit).width+12:0, x1=RV_CX-(w1+w2)/2;
    x.textAlign='left'; x.globalAlpha=a;
    if(foil){ x.font=`400 70px ${RV_SANS}`; rvLS(x,'1px'); rvFoilText(x,num,x1+w1/2,1508,70,t-it.infoIn-60,it.best); x.textAlign='left'; }
    else{ x.font=`400 70px ${RV_SANS}`; rvLS(x,'1px'); x.fillStyle='#f6efdc'; x.fillText(num,x1,1508+up); }
    if(unit){ x.globalAlpha=a*la; x.font=`400 28px ${RV_SANS}`; rvLS(x,'5px'); x.fillStyle='#c9c1ad'; x.fillText(unit,x1+w1+12,1508+up); }
    if(it.rk.myth){ x.textAlign='center'; x.font=`700 22px ${RV_SANS}`; rvLS(x,'7px'); const g=x.createLinearGradient(RV_CX-220,0,RV_CX+220,0); RV_RB.slice(0,5).forEach((c,i)=>g.addColorStop(i/4,c)); x.fillStyle=g; x.globalAlpha=a*la; x.fillText(it.rk.dawn?'SINCE THE DAWN OF TIME':'ONCE IN A CENTURY',RV_CX,1562+up); }
    rvLS(x,'0px'); x.restore(); } }
function rvDrawFrame(x,P,t){ x.save(); x.textAlign='center'; x.globalAlpha=rvCl(t/500)*.85; x.font=`700 30px ${RV_MINCHO}`; rvLS(x,'12px'); x.fillStyle='#e9d39a'; x.fillText('命ノ星座カード',RV_CX,150);
  if(P.mode==='all'&&P.items.length>1){ let k=0; P.items.forEach((it,i)=>{ if(t>=it.t0) k=i; }); x.globalAlpha=rvCl(t/500)*.55; x.font=`400 22px ${RV_SANS}`; rvLS(x,'4px'); x.fillStyle='#b9b2a3'; x.fillText(`${k+1} / ${P.items.length}`,RV_CX,200); }
  // 落ちるカード：いちばんのカードの前に「最後の1枚」と出す（何を待っているのかが分かるように）
  { const b=P.items[P.items.length-1]; if(P.v==='drop'&&P.items.length>1&&t>=b.t0&&t<b.drop){ x.globalAlpha=rvCl((t-b.t0-220)/380)*(1-rvCl((t-b.drop+200)/200))*.9; x.font=`700 40px ${RV_MINCHO}`; rvLS(x,'14px'); x.fillStyle='#e9d39a'; x.fillText('最後の1枚',RV_CX,1240); } }
  const fa=rvCl((t-P.E)/650); if(fa>0){ x.globalAlpha=fa; x.font=`700 30px ${RV_SANS}`; rvLS(x,'4px'); x.fillStyle='#e9d39a'; x.fillText('#命ノ星座カード',RV_CX,1760); x.globalAlpha=fa*.7; x.font=`400 24px ${RV_SANS}`; rvLS(x,'1px'); x.fillStyle='#b9b2a3'; x.fillText(SITE_URL.replace(/^https:\/\//,'').replace(/\/$/,''),RV_CX,1812); }
  rvLS(x,'0px'); x.restore(); }
/* ---- 流す ---- */
function rvClose(){ const R=window.RV; if(!R) return; R.dead=true; clearTimeout(R.lt); R.ov.remove(); document.body.style.overflow=R.ovf; document.removeEventListener('keydown',R.key); window.RV=null; if(R.onClose) R.onClose(); }
async function revealPlay(cs,v,opt){ opt=opt||{}; if(window.RV) rvClose(); if(!cs.length) return; v=REVEAL_VARS[v]?v:'drop'; const mode=opt.mode==='one'?'one':'all';
  const ag=c=>{ const a=charStats(c).age||0; return isFinite(a)?a:1e15; }, ord=cs.slice().sort((a,b)=>ag(a)-ag(b)), list=mode==='one'?[ord[ord.length-1]]:ord;
  const ov=cardEl('div',{class:'rv-ov',role:'dialog','aria-modal':'true','aria-label':'カードの登場'}), cv=cardEl('canvas',{class:'rv-cv',width:RVW,height:RVH}), bar=cardEl('div',{class:'rv-bar'}), skip=cardEl('button',{class:'rv-skip',type:'button'},'スキップ');
  bar.hidden=true; ov.append(skip,cv,bar); document.body.appendChild(ov);
  const R=window.RV={ov,dead:false,ovf:document.body.style.overflow,onClose:opt.onClose}, x=cv.getContext('2d'); document.body.style.overflow='hidden';
  // 操作：画面を押す（Enter・スペース）と次のカードへ。スキップ（Esc）で最後へ。終わったあとに押すと、すぐ一覧へ
  R.key=e=>{ if(R.list) { if(e.key==='Escape'){ e.preventDefault(); rvClose(); } return; }
    if(e.key==='Escape'){ e.preventDefault(); if(R.ended) rvList(R); else R.jump=true; } else if(e.key==='Enter'||e.key===' '){ if(e.target.closest&&e.target.closest('button')) return; e.preventDefault(); if(R.ended) rvList(R); else rvNext(R); } };
  document.addEventListener('keydown',R.key); skip.addEventListener('click',()=>{ R.jump=true; }); skip.focus();
  ov.addEventListener('pointerdown',e=>{ if(R.list||!R.P||(e.target.closest&&e.target.closest('button'))) return; if(R.ended) rvList(R); else rvNext(R); });
  // 準備：机を出して、カードの絵と書体を用意する
  const A=rvAssets(); x.drawImage(A.desk,0,0); x.textAlign='center'; x.font=`400 24px ${RV_SANS}`; x.fillStyle='rgba(185,178,163,.6)'; x.fillText('カードを用意しています…',RV_CX,RV_CY);
  const fonts=Promise.all([document.fonts.load(`700 68px ${RV_MINCHO}`,list.map(c=>c.name||'').join('')+'命ノ星座カード（名前なし）'),document.fonts.load(`400 70px ${RV_SANS}`,'0123456789.,秘境レベルDAYSWEKMONTHYRAX'),document.fonts.load(`700 30px ${RV_SANS}`,'#命ノ星座カード')]).catch(()=>{});
  const items=await Promise.all(list.map(async c=>{ const st=charStats(c); return {c,st,rk:rvRank(st.age||0),img:await rvCardImg(c)}; }));
  await Promise.race([fonts,new Promise(r=>setTimeout(r,2500))]); if(R.dead) return;
  const P=rvPlan(items,v,mode); P.pre=opt.pre||'both'; R.P=P; R.drawAt=t=>{ R.hold=true; rvDraw(x,P,t); }; // drawAt：好きな時刻の1コマを描いて止める（確認・動画の書き出し用）
  R.items=items; R.opt=opt; R.cv=cv; R.bar=bar;
  bar.hidden=false; bar.innerHTML=`<span class="rv-hint">${items.length>1?'画面を押すと次のカードへ':'画面を押すと先へ'}</span>`;
  // 終わり：全員のときは、少し余韻をおいて一覧へ。1枚のときはボタンだけ
  const end=()=>{ if(R.ended) return; R.ended=true; skip.remove();
    if(items.length>1){ bar.innerHTML='<span class="rv-hint">画面を押すと、カードを広げます</span>'; return; }
    bar.innerHTML=(opt.replay?'<button class="btn" type="button" data-rvre>もう一度</button>':'')+`<button class="btn primary" type="button" data-rvok>${esc(opt.okLabel||'カードを見る')}</button>`;
    bar.querySelector('[data-rvok]').addEventListener('click',rvClose); const re=bar.querySelector('[data-rvre]'); if(re) re.addEventListener('click',opt.replay); bar.querySelector('[data-rvok]').focus(); };
  if(rvStill()||R.jump){ R.t=P.total; rvDraw(x,P,P.total); return end(); }
  R.off=0; const t0=performance.now(); const step=now=>{ if(R.dead||R.hold) return; const t=R.jump?P.total:Math.min(P.total,now-t0+R.off); R.t=t; rvDraw(x,P,t); if(t>=P.total) return end(); requestAnimationFrame(step); }; requestAnimationFrame(step); }
// 次へ：いまのカードの続きを飛ばして、次のカードの始まりへ。いちばんのカードの溜め中なら落ちる瞬間へ、着地のあとなら締めへ
function rvNext(R){ const P=R.P, t=R.t||0, its=P.items, b=its[its.length-1], tg=[];
  its.forEach(it=>{ if(!it.best) tg.push(it.t0); }); tg.push(P.v==='drop'&&its.length>1?b.t0-300:b.t0); tg.push(P.v==='foil'?b.press:b.drop); tg.push(P.E,P.total);
  const nx=tg.filter(v=>v>t+40).sort((p,q)=>p-q)[0]; if(nx!=null) R.off+=nx-t; }
/* 演出のあと：取り込んだ全員のカードを一覧で（秘境レベルの高い順。いちばんのカードは金の枠）。押すとそのカードのページへ */
function rvList(R){ if(R.list||R.dead||!R.P) return; R.list=true; clearTimeout(R.lt); const ov=R.ov, opt=R.opt||{}, P=R.P, ag=it=>{ const a=it.st.age||0; return isFinite(a)?a:1e15; };
  const its=R.items.slice().sort((p,q)=>ag(q)-ag(p)), best=its[0], still=rvStill();
  // 机（キャンバス）はいまの場所に留めて、カードだけを消す。その上に一覧を重ねる
  const r=R.cv.getBoundingClientRect(), k=r.width/RVW; Object.assign(R.cv.style,{position:'fixed',left:r.left+'px',top:r.top+'px',width:r.width+'px',height:r.height+'px',margin:'0'});
  R.bar.remove(); P.noCards=true; rvDraw(R.cv.getContext('2d'),P,P.total); ov.classList.add('rv-ovl'); ov.scrollTop=0;
  const box=cardEl('div',{class:'rv-list'+(still?'':' spread')}); box.innerHTML=`<div class="rv-lh"><h2>取り込んだカード<small>${its.length}人</small></h2><button class="rv-x" type="button" aria-label="閉じる">×</button></div>
    <div class="rv-lg">${its.map((it,i)=>`<button class="rv-lc${it===best?' best':''}" type="button" data-i="${i}"><span class="th"></span><span class="m"><b>${esc(it.c.name||'（名前なし）')}</b>${it===best?'<i>いちばん</i>':''}<span class="st${it.rk.myth?' myth':''}" style="color:${it.rk.col}">${'★'.repeat(it.rk.stars)}${it.rk.plus?'+':''}</span><span class="a">${esc(fmtAge(it.st.age||0))}</span></span></button>`).join('')}</div>
    <div class="rv-lf">${opt.replay?'<button class="btn" type="button" data-rvre>もう一度</button>':''}<button class="btn primary" type="button" data-rvok>${opt.replay?'閉じる':'いちばんのカードを見る'}</button>${opt.replay?'':'<button class="rv-off" type="button" data-rvoff>次から演出を出さない</button>'}</div>`;
  ov.appendChild(box);
  its.forEach((it,i)=>{ const th=box.querySelector(`[data-i="${i}"] .th`), c=rvCanvas(490,276); if(it.img1) c.getContext('2d').drawImage(it.img1,0,0,490,276); th.appendChild(c); });
  // 広げる：一覧のカードを、机の上で重なっていた位置・角度・大きさに置いてから、自分の場所へ滑らせる（上に重なっていたカードから順に）
  if(!still){ const n=R.items.length;
    R.items.forEach((it,pi)=>{ const th=box.querySelector(`[data-i="${its.indexOf(it)}"] .th`), ps=rvPose(P,it,P.total), tr=th.getBoundingClientRect();
      const dx=r.left+ps.x*k-(tr.left+tr.width/2), dy=r.top+ps.y*k-(tr.top+tr.height/2), sc=it.W*k*ps.s/tr.width;
      th.style.zIndex=String(pi+1); th.style.transform=`translate(${dx}px,${dy}px) rotate(${ps.rot}rad) scale(${sc})`; th.dataset.d=String((n-1-pi)*55); });
    void box.offsetWidth;
    requestAnimationFrame(()=>{ box.querySelectorAll('.th').forEach(th=>{ th.style.transition=`transform .85s cubic-bezier(.22,.8,.24,1) ${th.dataset.d}ms`; th.style.transform='none'; });
      R.cv.style.transition='opacity 1s ease .1s'; R.cv.style.opacity='0'; R.lt=setTimeout(()=>{ box.classList.remove('spread'); box.querySelectorAll('.th').forEach(th=>{ th.style.zIndex=''; th.style.transition=''; }); },850+(n-1)*55); }); }
  else R.cv.style.opacity='0';
  box.querySelectorAll('[data-i]').forEach(el=>el.addEventListener('click',()=>{ if(box.classList.contains('spread')) return; const it=its[+el.dataset.i]; if(opt.replay||!CHARS.some(c=>c.id===it.c.id)) return; CH_OPEN=it.c.id; renderChars(); cardShowPage('card'); rvClose(); }));
  box.querySelector('.rv-x').addEventListener('click',rvClose); box.querySelector('[data-rvok]').addEventListener('click',rvClose);
  const re=box.querySelector('[data-rvre]'); if(re) re.addEventListener('click',opt.replay);
  const off=box.querySelector('[data-rvoff]'); if(off) off.addEventListener('click',()=>{ store.set('revealOff',1); off.textContent='次から演出を出しません（設定で戻せます）'; off.disabled=true; });
  box.querySelector('[data-rvok]').focus({preventScroll:true}); }
/* ---- 試作の見比べ：#reveal で開くと、見本のキャラで流す操作盤を出す（保存はしない） ---- */
function rvDemoChars(n,top){ const names=['ベネット','行秋','香菱','夜蘭','ナヒーダ','鍾離','雷電将軍','フリーナ','ヌヴィレット','楓原万葉','胡桃'], BANDS=[[1,7],[7,30],[30,90],[90,365],[365,1095],[1095,36500],[36500,Infinity]];
  const P=(main,lines)=>{ const rolls={}, subs=lines.map(([k,t])=>{ rolls[k]=t; const v=t.reduce((a,x)=>a+ROLL[k][x],0); return {s:k,v:FLAT.has(k)?String(Math.round(v+1e-9)):(Math.round((v+1e-9)*10)/10).toFixed(1)}; }); return {main,subs,rolls}; };
  const SUBS={flower:['CR','CD','ATK%','DEF'],plume:['CR','CD','ATK%','HP'],sands:['CR','CD','EM','DEF'],goblet:['CR','CD','ATK%','HP%'],circlet:['CD','ATK%','EM','DEF']}, MAIN={flower:'HP',plume:'ATK',sands:'ATK%',goblet:'DMG_炎',circlet:'CR'};
  let sd=Date.now()%233280; const RN=()=>{ sd=(sd*9301+49297)%233280; return sd/233280; };
  const make=(name,lv)=>{ const pieces={}; for(const s of SLOTS){ const [a,b,c2,x]=SUBS[s], e=Math.max(0,Math.min(5,Math.round(lv+(RN()-.5)*2))), q=lv>3.5?3:lv>2?2:1, t=()=>Math.max(0,Math.min(3,q-(RN()<.35?1:0)+(RN()<.2?1:0)));
      const r={[a]:[t()],[b]:[t()],[c2]:[t()],[x]:[RN()*4|0]}; for(let i=0;i<5;i++){ if(i<e){ const k=[a,b,c2][RN()*(s==='circlet'?2:3)|0]; r[k].push(t()); } else r[x].push(RN()*4|0); }
      pieces[s]=P(MAIN[s],[a,b,c2,x].map(k=>[k,r[k]])); } return {id:'rvdemo-'+name,name,set:'燃え盛る炎の魔女4',eff:['ATK%','CR','CD'],date:'見本',pieces}; };
  const pick=(name,band)=>{ const [lo,hi]=BANDS[band]; let bc=null, bd=1e99; for(let k=0;k<60;k++){ const c=make(name,band*.85+RN()*1.2), a=charStats(c).age||0; if(a>=lo&&a<hi) return c; const dd=Math.abs(Math.log((isFinite(a)?a:1e9)+1)-Math.log(Math.min(lo*2,1e9))); if(dd<bd){ bd=dd; bc=c; } } return bc; };
  const out=[]; for(let i=0;i<n-1;i++) out.push(pick(names[i%names.length],Math.min(top-1,RN()*Math.max(1,top)|0)));
  out.push(pick('スカーク',top)); return out; }
function revealDemoPanel(){ if($('rvDemo')) return; const box=cardEl('div',{class:'rv-demo',id:'rvDemo'});
  const st={v:'drop',m:'all',n:6,top:5,pre:'both'}, tops=[[3,'★4'],[4,'★5'],[5,'★5+'],[6,'百年級（虹）']], B=(k,v,t,on)=>`<button class="btn" style="padding:3px 10px;font-size:12px" data-${k}="${v}" aria-pressed="${on}">${t}</button>`;
  const play=()=>{ const cs=rvDemoChars(st.m==='one'?1:st.n,st.top); const go=()=>revealPlay(cs,st.v,{mode:st.m,pre:st.pre,replay:go,okLabel:'閉じる'}); go(); };
  const draw=()=>{ box.innerHTML=`<div class="row"><b>演出の試作</b><span class="note">見本のキャラで流します（保存はしません）</span><button class="btn" style="margin-left:auto;padding:2px 8px;font-size:11px" data-x>閉じる</button></div>
    <div class="row">案 ${Object.entries(REVEAL_VARS).map(([k,t])=>B('v',k,t,st.v===k)).join('')}</div>
    <div class="row">${B('m','all','全員',st.m==='all')}${B('m','one','1枚',st.m==='one')}　人数 ${[3,6,8,12].map(k=>B('n',k,k+'人',st.n===k)).join('')}</div>
    <div class="row">最後 ${tops.map(([k,t])=>B('t',k,t,st.top===k)).join('')}</div>
    <div class="row">溜め（案2） ${[['spot','A スポットライト'],['stars','B 星座'],['both','A＋B']].map(([k,t])=>B('p',k,t,st.pre===k)).join('')}</div>
    <div class="row"><button class="btn primary" data-go>▶ 流す</button><span class="note">端末で「視差効果を減らす」を選んでいると、最後の絵だけが出ます</span></div>`;
    box.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>{ st.v=b.dataset.v; draw(); }); box.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>{ st.m=b.dataset.m; draw(); });
    box.querySelectorAll('[data-n]').forEach(b=>b.onclick=()=>{ st.n=+b.dataset.n; draw(); }); box.querySelectorAll('[data-t]').forEach(b=>b.onclick=()=>{ st.top=+b.dataset.t; draw(); }); box.querySelectorAll('[data-p]').forEach(b=>b.onclick=()=>{ st.pre=b.dataset.p; draw(); });
    box.querySelector('[data-x]').onclick=()=>box.remove(); box.querySelector('[data-go]').onclick=play; };
  draw(); document.body.appendChild(box); }
/* ---- 共有：スマホは画像ごと共有シートへ。できなければ画像を保存して、X の投稿画面を開くボタン ---- */
async function cardShare(){ const msg=$('cMsg'), c=CHARS.find(x=>x.id===CH_OPEN); if(!c) return; const st=charStats(c), tr=tierOf(st.age||0);
  const text=`${c.name}の聖遺物は「秘境レベル ${fmtAge(st.age)}（${tr[1]}）」でした #命ノ星座カード`;
  const xLink=`<a class="btn" style="padding:3px 10px;font-size:12px" target="_blank" rel="noopener" href="https://x.com/intent/post?text=${encodeURIComponent(text)}&url=${encodeURIComponent(SITE_URL)}">X に投稿する</a>`;
  const r=await cardExport('png',msg,{blobOnly:true}); if(!r||!r.blob){ msg.textContent='画像を作れませんでした'; return; }
  const file=new File([r.blob],r.name,{type:'image/png'}), data={files:[file],text:text+' '+SITE_URL};
  const tryShare=async()=>{ try{ await navigator.share(data); msg.textContent='共有しました'; return true; }catch(e){ if(e&&e.name==='AbortError'){ msg.textContent=''; return true; } return e&&e.name==='NotAllowedError'?'again':false; } };
  if(navigator.canShare&&navigator.canShare({files:[file]})){
    const t=await tryShare(); if(t===true) return;
    if(t==='again'){ msg.innerHTML='画像の準備ができました。<button class="btn primary" style="padding:3px 10px;font-size:12px" id="cShare2">画像を共有する</button>'; $('cShare2').addEventListener('click',async()=>{ const t2=await tryShare(); if(t2!==true) cardShareFallback(r,xLink); }); return; } }
  cardShareFallback(r,xLink); }
async function cardShareFallback(r,xLink){ const msg=$('cMsg'); const res=await saveBlob(r.name,r.blob);
  msg.innerHTML=(res==='saved'?'画像を保存しました。':res==='declined'?'画像の保存をやめました。':'画像を保存できませんでした。')+` ${xLink}（保存した画像を添付してください）`; }
function cardAppBindDel(){ const b=$('cDel'); if(b) b.addEventListener('click',()=>{ const c=CHARS.find(x=>x.id===CH_OPEN); if(!c) return; const box=$('cDelBox'); box.innerHTML=`<span class="note">「${esc(c.name||'（名前なし）')}」を削除しますか？</span> <button class="btn" id="cDelYes">削除する</button> <button class="btn" id="cDelNo">やめる</button>`;
  $('cDelYes').addEventListener('click',()=>{ CHARS=CHARS.filter(x=>x!==c); CH_OPEN=(cardSorted()[0]||{c:{}}).c.id||null; saveChars(); portraitTx('readwrite',st=>st.delete(c.id)); box.innerHTML='<button class="btn" id="cDel">削除</button>'; cardAppBindDel(); renderChars(); });
  $('cDelNo').addEventListener('click',()=>{ box.innerHTML='<button class="btn" id="cDel">削除</button>'; cardAppBindDel(); }); }); }
"""
rep("showTab((CHARS_ONLY||CARD_APP)?'chars'", JS + "\nshowTab((CHARS_ONLY||CARD_APP)?'chars'")
import os, json as _json
_t = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'enka_tables.json'), encoding='utf-8').read(); _json.loads(_t)
assert s.count('__ENKA_TABLES__') == 1
s = s.replace('__ENKA_TABLES__', _t)
_pp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'portraits', 'portraits.json')
_pj = open(_pp, encoding='utf-8').read() if os.path.exists(_pp) else '{}'
_json.loads(_pj)
assert s.count('__PORTRAITS__') == 1
s = s.replace('__PORTRAITS__', _pj)
open(dst, 'w', encoding='utf-8').write(s)
print('wrote', dst, len(s))
