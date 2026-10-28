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
/* ===== ガチャふうの演出（v2.1 試作） ===== */
.rv-ov{position:fixed; inset:0; z-index:9000; background:radial-gradient(ellipse at 50% 45%,#141838 0%,#070816 60%,#020309 100%); display:flex; flex-direction:column; align-items:center; justify-content:center; padding:56px 16px 24px; overflow:auto; color:#e6dfcf; animation:rvIn .35s ease-out}
@keyframes rvIn{from{opacity:0}}
.rv-skip{position:fixed; top:12px; right:12px; z-index:2; background:rgba(255,255,255,.08); color:#e6dfcf; border:1px solid rgba(233,211,154,.35); border-radius:999px; padding:6px 16px; font-size:13px; cursor:pointer}
.rv-skip:hover{background:rgba(255,255,255,.16)}
.rv-flip{position:relative; width:100%; aspect-ratio:16/9; transform-style:preserve-3d; transition:transform .7s cubic-bezier(.3,.1,.2,1)}
.rv-flip.on{transform:rotateY(180deg)}
.rv-face{position:absolute; inset:0; backface-visibility:hidden; -webkit-backface-visibility:hidden; border-radius:6px; overflow:hidden; box-shadow:0 14px 40px rgba(0,0,0,.6), 0 0 0 1px rgba(233,211,154,.2)}
.rv-face svg{display:block; width:100%; height:100%}
.rv-front{transform:rotateY(180deg)}
/* ランク色の光（--rv に色、虹のときは .myth）。カードの後ろでぼかして光らせる */
.rv-aura{position:relative}
.rv-aura::before{content:''; position:absolute; inset:-6%; border-radius:30px; background:var(--rv,#fff); filter:blur(26px); opacity:0; transition:opacity .5s; pointer-events:none}
.rv-aura.myth::before{background:conic-gradient(from 0deg,#ff8fb1,#ffd27a,#8ff0c4,#8fbaff,#d59bff,#ff8fb1); animation:rvSpin 3s linear infinite}
.rv-aura.lit::before{opacity:.55} .rv-aura.hint::before{animation:rvPulse 1.1s ease-in-out infinite} .rv-aura.myth.hint::before{animation:rvSpin 3s linear infinite, rvPulse 1.1s ease-in-out infinite}
@keyframes rvPulse{0%,100%{opacity:.25; transform:scale(.97)} 50%{opacity:.9; transform:scale(1.03)}}
@keyframes rvSpin{to{filter:blur(26px) hue-rotate(360deg)}}
.rv-stage{width:min(100%,980px,calc((100dvh - 190px)*16/9)); min-width:min(100%,280px)}
.rv-cap{text-align:center; margin-top:18px; min-height:74px}
.rv-cap .n{font-size:clamp(18px,3vw,26px); letter-spacing:.06em} .rv-cap .a{font-size:14px; color:#b9b2a3; margin-top:2px}
.rv-cap .btns{justify-content:center; margin-top:12px}
.rv-cap > *{animation:rvUp .5s ease-out both}
@keyframes rvUp{from{opacity:0; transform:translateY(8px)}}
.rv-grid{display:grid; grid-template-columns:repeat(var(--cols,3),minmax(0,1fr)); gap:14px; width:min(100%,960px)}
.rv-cell{display:grid; gap:6px} .rv-cell .rv-face{border-radius:4px}
.rv-cell .c{font-size:12px; text-align:center; min-height:1.4em; opacity:0; transition:opacity .3s} .rv-cell.open .c{opacity:1}
.rv-cell .c b{font-weight:700}
.rv-sky circle,.rv-sky line{transition:opacity .35s}
.rv-demo{position:fixed; left:50%; bottom:12px; transform:translateX(-50%); z-index:8000; background:rgba(10,12,28,.94); border:1px solid rgba(233,211,154,.4); border-radius:10px; padding:10px 12px; display:grid; gap:6px; font-size:12px; width:min(calc(100% - 24px),560px); box-shadow:0 10px 30px rgba(0,0,0,.5)}
.rv-demo .row{gap:6px; flex-wrap:wrap; align-items:center}
.rv-demo button[aria-pressed="true"]{border-color:var(--gold); color:var(--gold-hi)}
@media (prefers-reduced-motion: reduce){ .rv-ov,.rv-cap > *{animation:none} .rv-flip{transition:none} .rv-aura.hint::before,.rv-aura.myth::before{animation:none} }
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
async function cardRenderSettings(){ const box=$('cPortraits'); if(!box) return; const all=(await portraitTx('readonly',st=>st.getAll()))||[];
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
    <div class="panel" style="margin-top:14px" id="cMoveHost"><h2>データの引っ越し</h2></div>
    <div class="panel" style="margin-top:14px"><h2>このアプリについて</h2><p class="note">命ノ星座カード v2.0。計算は聖遺物厳選ラボと共通です。原神のキャラクター名・画像などの権利は HoYoverse に帰属します。UIDからの取り込みには Enka.Network のデータを、動画からの取り込みには聖遺物ビデオスキャナー（読み取りエンジン：Tesseract.js）を使っています。キャラのデータはこの端末（このブラウザ）に保存され、ラボ本体や別の端末とのやりとりは「データの引っ越し」のJSONで行います（ラボ本体で書き出したものもそのまま読めます）。HoYoverseとは関係のない非公式のファンツールです。</p></div>`;
  const mh=$('cMoveHost'); [...(det||mv).childNodes].forEach(n=>mh.appendChild(n)); mv.remove();
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
  revealPlay(cs,revealVar()); }
/* ================= ガチャふうの演出（v2.1 試作。案を見比べてから1つに絞る） =================
   A 星座：いちばんのキャラだけ。裏面に部位の星が低い順に灯り、線でつながり、ランク色に光ってから表に返る
   B 10連めくり：取り込んだ全員の裏面を並べ、秘境レベルの低い順にめくる。最後の1枚はランク色で匂わせてからめくる
   C 10連＋星座：Bの順にめくり、最後の1枚だけAの星座で返す
   どれもスキップできる。端末で「視差効果を減らす」を選んでいる人には、演出なしで最後のカードだけを出す。
   試作の見比べ：URLの末尾に #reveal を付けて開くと、見本のキャラで流せる操作盤が出る。?reveal=a|b|c で本番の流れの案を切り替え */
const REVEAL_VARS={a:'A 星座',b:'B 10連めくり',c:'C 10連＋星座'};
function revealVar(){ const q=(new URLSearchParams(location.search).get('reveal')||'').toLowerCase(); return REVEAL_VARS[q]?q:'c'; }
function rvStill(){ try{ return matchMedia('(prefers-reduced-motion: reduce)').matches; }catch(e){ return false; } }
function rvRank(a){ const t=a>0?tierOf(a):TIERS[0]; return {t,col:t[2],myth:!isFinite(a)||a>=36500}; } // 100年以上（上限も）は虹
function rvAuraAttr(a){ const r=rvRank(a); return `class="rv-aura${r.myth?' myth':''}" style="--rv:${r.col}"`; }
// 1つのページにカードを何枚も並べるので、SVGの中のidを1枚ずつ付け替える（同じidが並ぶと、隠れた側の模様を拾ってしまう）
var RV_UID=0;
function rvUniq(svg){ const k='_rv'+(++RV_UID); return svg.replace(/\bid="([^"]+)"/g,`id="$1${k}"`).replace(/url\(#([^)]+)\)/g,`url(#$1${k})`).replace(/href="#([^"]+)"/g,`href="#$1${k}"`); }
function rvFront(c){ return rvUniq(cardSVG(c,charStats(c),'SK')); }
// 裏面：カードと同じ夜空に金の枠、真ん中に五つ星の紋（部位の数）
function rvBack(){ const k=++RV_UID; let sd=11; const RN=()=>{ sd=(sd*9301+49297)%233280; return sd/233280; }; let dots='';
  for(let i=0;i<70;i++) dots+=`<circle cx="${(RN()*1200).toFixed(0)}" cy="${(RN()*675).toFixed(0)}" r="${(RN()*1.4+.3).toFixed(1)}" fill="#fff" opacity="${(RN()*.5+.15).toFixed(2)}"/>`;
  const P=[...Array(5)].map((_,i)=>{ const a=(-90+i*72)*Math.PI/180; return [600+70*Math.cos(a),330+70*Math.sin(a)]; }), star=[0,2,4,1,3].map(i=>P[i].map(v=>v.toFixed(1)).join(',')).join(' ');
  return `<svg viewBox="0 0 1200 675" xmlns="http://www.w3.org/2000/svg"><defs><radialGradient id="rvB${k}" cx=".5" cy=".48" r=".8"><stop offset="0" stop-color="#1b1d48"/><stop offset=".55" stop-color="#0b0e22"/><stop offset="1" stop-color="#04050b"/></radialGradient></defs>
    <rect width="1200" height="675" fill="url(#rvB${k})"/>${dots}
    <rect x="16" y="16" width="1168" height="643" rx="10" fill="none" stroke="#e9d39a" stroke-opacity=".6" stroke-width="2.5"/><rect x="30" y="30" width="1140" height="615" rx="6" fill="none" stroke="#e9d39a" stroke-opacity=".22"/>
    <circle cx="600" cy="330" r="112" fill="none" stroke="#e9d39a" stroke-opacity=".45" stroke-width="1.5"/><circle cx="600" cy="330" r="124" fill="none" stroke="#e9d39a" stroke-opacity=".2" stroke-dasharray="2 6"/>
    <polygon points="${star}" fill="none" stroke="#e9d39a" stroke-opacity=".5" stroke-width="1.2"/>${P.map(([x,y])=>`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4" fill="#f5e6bd"/>`).join('')}
    <text x="600" y="510" text-anchor="middle" font-family='"Murecho","M PLUS 1p",sans-serif' font-size="22" font-weight="700" letter-spacing=".5em" fill="#e9d39a" fill-opacity=".7">命ノ星座</text></svg>`; }
// 星の位置：カードの星座（中心・半径・部位の向き・ランクの帯ごとの目盛り）と同じ計算
function rvStars(st){ const cx0=360, cy0=361, R0=58, R=246, BND=[1,7,30,90,365,1095,10950], ANG={flower:-90,plume:-18,sands:54,goblet:126,circlet:198};
  const rad=d=>{ if(!(d>1)) return R0; if(d>=10950) return R; let k=0; while(k<5&&d>=BND[k+1]) k++; return R0+(k+(Math.log(d)-Math.log(BND[k]))/(Math.log(BND[k+1])-Math.log(BND[k])))/6*(R-R0); };
  return SLOTS.map(s=>{ const d=st.slots[s].age, r=rad(isFinite(d)?d:1e9), a=ANG[s]*Math.PI/180; return {s,d,has:d>0,x:cx0+r*Math.cos(a),y:cy0+r*Math.sin(a)}; }); }
const rvWait=(R,ms)=>new Promise(res=>{ if(R.dead) return res(); const t=setTimeout(res,ms); R.timers.push(t); });
function rvClose(){ const R=window.RV; if(!R) return; R.dead=true; R.timers.forEach(clearTimeout); R.ov.remove(); document.body.style.overflow=R.ovf; document.removeEventListener('keydown',R.key); window.RV=null; if(R.onClose) R.onClose(); }
async function revealPlay(cs,v,opt){ opt=opt||{}; if(window.RV) rvClose(); if(!cs.length) return;
  const v2=c=>{ const a=charStats(c).age||0; return isFinite(a)?a:1e15; }, ord=cs.slice().sort((x,y)=>v2(x)-v2(y)), best=ord[ord.length-1];
  const ov=cardEl('div',{class:'rv-ov',role:'dialog','aria-modal':'true','aria-label':'カードの発表'});
  const R=window.RV={ov,dead:false,timers:[],ovf:document.body.style.overflow,onClose:opt.onClose}; document.body.style.overflow='hidden';
  const skip=cardEl('button',{class:'rv-skip',type:'button'},'スキップ'); ov.appendChild(skip); const body=cardEl('div',{style:'width:100%;display:grid;justify-items:center'}); ov.appendChild(body); document.body.appendChild(ov);
  const finish=()=>{ if(R.done) return; R.done=true; R.dead=true; R.timers.forEach(clearTimeout); skip.remove(); rvFinal(R,body,best,ord.length); };
  skip.addEventListener('click',finish); R.key=e=>{ if(e.key==='Escape'){ e.preventDefault(); R.done?rvClose():finish(); } }; document.addEventListener('keydown',R.key); skip.focus();
  // 立ち絵（同梱・自分で選んだもの）の切り出しを先に済ませる。待つのは長くても2.5秒
  await Promise.race([Promise.all(ord.map(c=>{ applyBundled(c); if(!CARD_IMG[c.id]||(c.id in CARD_FIT)) return null; return fitCardArt(CARD_IMG[c.id],CARD_ZOOM[c.id]).then(u=>{ CARD_FIT[c.id]=u||''; }); })),new Promise(r=>setTimeout(r,2500))]);
  if(R.dead) return; if(rvStill()) return finish();
  if(v!=='a'&&ord.length>1) await rvGrid(R,body,ord,{holdLast:v==='c'});
  if(R.dead) return;
  if(v==='b'&&ord.length>1){ await rvWait(R,700); return finish(); }
  await rvConstellation(R,body,best); if(R.dead) return; await rvWait(R,900); finish(); }
/* 10連：裏面を並べて低い順にめくる。最後の1枚は光で匂わせる（holdLast＝めくらずに残して、星座の演出へ渡す） */
async function rvGrid(R,body,ord,o){ const n=ord.length, cols=n<=2?n:n<=4?2:n<=9?3:4;
  body.innerHTML=`<div class="rv-grid" style="--cols:${cols}">${ord.map((c,i)=>`<div class="rv-cell"><div ${rvAuraAttr(charStats(c).age||0)}><div class="rv-flip"><div class="rv-face rv-back">${rvBack()}</div><div class="rv-face rv-front"></div></div></div><div class="c"></div></div>`).join('')}</div>`;
  const cells=[...body.querySelectorAll('.rv-cell')]; await rvWait(R,500);
  for(let i=0;i<n;i++){ if(R.dead) return; const c=ord[i], el=cells[i], st=charStats(c), last=i===n-1, rk=rvRank(st.age||0);
    if(last){ el.querySelector('.rv-aura').classList.add('lit','hint'); await rvWait(R,o.holdLast?1100:1600); if(o.holdLast||R.dead) return; }
    el.querySelector('.rv-front').innerHTML=rvFront(c); el.querySelector('.rv-flip').classList.add('on'); el.classList.add('open');
    el.querySelector('.c').innerHTML=`${esc(c.name||'')}　<b style="color:${rk.col}">${esc(st.age>0?rk.t[1]:'—')}</b>`;
    if(last){ const a=el.querySelector('.rv-aura'); a.classList.remove('hint'); }
    await rvWait(R,last?900:Math.max(220,900/n)+(rk.t[0]>=365?250:0)); } }
/* 星座：裏面に部位の星が低い順に灯り、線でつながり、真ん中がランク色に光ってから表に返る */
async function rvConstellation(R,body,c){ const st=charStats(c), rk=rvRank(st.age||0), S=rvStars(st), on=S.filter(p=>p.has).sort((x,y)=>(isFinite(x.d)?x.d:1e15)-(isFinite(y.d)?y.d:1e15));
  const sky=`<svg class="rv-sky" viewBox="0 0 1200 675" style="position:absolute;inset:0;width:100%;height:100%"><defs><filter id="rvGl" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter><radialGradient id="rvCore"><stop offset="0" stop-color="${rk.myth?'#fff':rk.col}" stop-opacity=".9"/><stop offset="1" stop-color="${rk.myth?'#cbb8ff':rk.col}" stop-opacity="0"/></radialGradient></defs>
    <rect width="1200" height="675" fill="#05060f" opacity=".55"/>
    ${S.map((p,i)=>{ const q=S[(i+1)%5]; return p.has&&q.has?`<line data-ln="${i}" x1="${p.x.toFixed(1)}" y1="${p.y.toFixed(1)}" x2="${q.x.toFixed(1)}" y2="${q.y.toFixed(1)}" stroke="#c4d8ff" stroke-width="2" stroke-opacity=".75" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`:''; }).join('')}
    <circle data-core cx="360" cy="361" r="150" fill="url(#rvCore)" opacity="0"/>
    ${S.filter(p=>p.has).map(p=>`<g data-st="${p.s}" opacity="0"><circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="16" fill="${rvRank(p.d).myth?'#fff':rvRank(p.d).col}" opacity=".35" filter="url(#rvGl)"/><circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="7" fill="${rvRank(p.d).myth?'#fff':rvRank(p.d).col}" filter="url(#rvGl)"/></g>`).join('')}</svg>`;
  body.innerHTML=`<div class="rv-stage"><div ${rvAuraAttr(st.age||0)}><div class="rv-flip"><div class="rv-face rv-back">${rvBack()}${sky}</div><div class="rv-face rv-front">${rvFront(c)}</div></div></div><div class="rv-cap"></div></div>`;
  const svg=body.querySelector('.rv-sky'), A=(el,k,o)=>el&&el.animate?el.animate(k,Object.assign({fill:'forwards'},o)):null;
  A(svg.querySelector('rect'),[{opacity:0},{opacity:.55}],{duration:500}); await rvWait(R,600);
  for(const p of on){ if(R.dead) return; const g=svg.querySelector(`[data-st="${p.s}"]`); A(g,[{opacity:0,transform:'scale(.2)'},{opacity:1,transform:'scale(1.25)',offset:.6},{opacity:1,transform:'scale(1)'}],{duration:480,easing:'ease-out'}); g.style.transformOrigin=`${p.x}px ${p.y}px`; g.style.transformBox='view-box'; await rvWait(R,rvRank(p.d).t[0]>=365?520:380); }
  for(const ln of svg.querySelectorAll('[data-ln]')){ if(R.dead) return; A(ln,[{strokeDashoffset:1},{strokeDashoffset:0}],{duration:220,easing:'ease-in-out'}); await rvWait(R,170); }
  await rvWait(R,250); if(R.dead) return;
  const au=body.querySelector('.rv-aura'); au.classList.add('lit','hint'); A(svg.querySelector('[data-core]'),[{opacity:0,transform:'scale(.4)'},{opacity:1,transform:'scale(1)'}],{duration:900,easing:'ease-out'}); svg.querySelector('[data-core]').style.cssText='transform-origin:360px 361px;transform-box:view-box';
  await rvWait(R,rk.t[0]>=1095?1700:1200); if(R.dead) return;
  au.classList.remove('hint'); body.querySelector('.rv-flip').classList.add('on'); }
/* 最後の画面：いちばんのカードを表で大きく。スキップしたときもここ */
function rvFinal(R,body,c,n){ const st=charStats(c), rk=rvRank(st.age||0);
  if(!body.querySelector('.rv-stage')||!body.querySelector('.rv-flip.on')){ body.innerHTML=`<div class="rv-stage"><div ${rvAuraAttr(st.age||0)}><div class="rv-flip on" style="transition:none"><div class="rv-face rv-back">${rvBack()}</div><div class="rv-face rv-front">${rvFront(c)}</div></div></div><div class="rv-cap"></div></div>`;
    const f=body.querySelector('.rv-stage'); if(f.animate&&!rvStill()) f.animate([{opacity:0,transform:'scale(.92)'},{opacity:1,transform:'scale(1)'}],{duration:450,easing:'ease-out'}); }
  body.querySelector('.rv-aura').classList.add('lit'); body.querySelector('.rv-aura').classList.remove('hint');
  body.querySelector('.rv-cap').innerHTML=`<div class="n">${n>1?`${n}人の中で、いちばんは `:''}<b class="gold">${esc(c.name||'（名前なし）')}</b></div><div class="a">秘境レベル <b style="color:${rk.col}">${esc(fmtAge(st.age))}</b>（${esc(rk.t[1])}）</div><div class="btns"><button class="btn primary" type="button" data-rvok>カードを見る</button></div>`;
  const ok=body.querySelector('[data-rvok]'); ok.addEventListener('click',rvClose); ok.focus(); }
/* ---- 試作の見比べ：#reveal で開くと、見本のキャラで演出を流す操作盤を出す（保存はしない） ---- */
function rvDemoChars(n,top){ const names=['ベネット','行秋','香菱','夜蘭','ナヒーダ','鍾離','雷電将軍','フリーナ','ヌヴィレット','楓原万葉','胡桃'], BANDS=[[1,7],[7,30],[30,90],[90,365],[365,1095],[1095,36500],[36500,Infinity]];
  const P=(main,lines)=>{ const rolls={}, subs=lines.map(([k,t])=>{ rolls[k]=t; const v=t.reduce((a,x)=>a+ROLL[k][x],0); return {s:k,v:FLAT.has(k)?String(Math.round(v+1e-9)):(Math.round((v+1e-9)*10)/10).toFixed(1)}; }); return {main,subs,rolls}; };
  const SUBS={flower:['CR','CD','ATK%','DEF'],plume:['CR','CD','ATK%','HP'],sands:['CR','CD','EM','DEF'],goblet:['CR','CD','ATK%','HP%'],circlet:['CD','ATK%','EM','DEF']}, MAIN={flower:'HP',plume:'ATK',sands:'ATK%',goblet:'DMG_炎',circlet:'CR'};
  let sd=Date.now()%233280; const RN=()=>{ sd=(sd*9301+49297)%233280; return sd/233280; };
  const make=(name,lv)=>{ const pieces={}; for(const s of SLOTS){ const [a,b,c2,x]=SUBS[s], e=Math.max(0,Math.min(5,Math.round(lv+(RN()-.5)*2))), q=lv>3.5?3:lv>2?2:1, t=()=>Math.max(0,Math.min(3,q-(RN()<.35?1:0)+(RN()<.2?1:0)));
      const r={[a]:[t()],[b]:[t()],[c2]:[t()],[x]:[RN()*4|0]}; for(let i=0;i<5;i++){ if(i<e){ const k=[a,b,c2][RN()*(s==='circlet'?2:3)|0]; r[k].push(t()); } else r[x].push(RN()*4|0); }
      pieces[s]=P(MAIN[s],[a,b,c2,x].map(k=>[k,r[k]])); } return {id:'rvdemo-'+name,name,set:'燃え盛る炎の魔女4',eff:['ATK%','CR','CD'],date:'見本',pieces}; };
  const pick=(name,band)=>{ const [lo,hi]=BANDS[band]; let bestc=null, bd=1e99; for(let k=0;k<60;k++){ const c=make(name,band*.85+RN()*1.2); const a=charStats(c).age||0; if(a>=lo&&a<hi) return c; const dd=Math.abs(Math.log((isFinite(a)?a:1e9)+1)-Math.log(Math.min(lo*2,1e9))); if(dd<bd){ bd=dd; bestc=c; } } return bestc; };
  const out=[]; for(let i=0;i<n-1;i++) out.push(pick(names[i%names.length],Math.min(top-1,RN()*Math.max(1,top)|0)));
  out.push(pick('スカーク',top)); return out; }
function revealDemoPanel(){ if($('rvDemo')) return; const box=cardEl('div',{class:'rv-demo',id:'rvDemo'});
  const st={v:'c',n:6,top:5}, tops=[[3,'★4'],[4,'★5'],[5,'★5+'],[6,'百年級（虹）']];
  const draw=()=>{ box.innerHTML=`<div class="row"><b>演出の試作</b><span class="note">見本のキャラで流します（保存はしません）</span><button class="btn" style="margin-left:auto;padding:2px 8px;font-size:11px" data-x>閉じる</button></div>
    <div class="row">案 ${Object.entries(REVEAL_VARS).map(([k,t])=>`<button class="btn" style="padding:3px 10px;font-size:12px" data-v="${k}" aria-pressed="${st.v===k}">${t}</button>`).join('')}</div>
    <div class="row">人数 ${[1,3,6,10].map(k=>`<button class="btn" style="padding:3px 10px;font-size:12px" data-n="${k}" aria-pressed="${st.n===k}">${k}人</button>`).join('')}　最後 ${tops.map(([k,t])=>`<button class="btn" style="padding:3px 10px;font-size:12px" data-t="${k}" aria-pressed="${st.top===k}">${t}</button>`).join('')}</div>
    <div class="row"><button class="btn primary" data-go>▶ 流す</button><span class="note">端末で「視差効果を減らす」を選んでいると、最後のカードだけが出ます</span></div>`;
    box.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>{ st.v=b.dataset.v; draw(); }); box.querySelectorAll('[data-n]').forEach(b=>b.onclick=()=>{ st.n=+b.dataset.n; draw(); }); box.querySelectorAll('[data-t]').forEach(b=>b.onclick=()=>{ st.top=+b.dataset.t; draw(); });
    box.querySelector('[data-x]').onclick=()=>box.remove(); box.querySelector('[data-go]').onclick=()=>revealPlay(rvDemoChars(st.n,st.top),st.v); };
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
