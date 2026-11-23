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
    "const $=id=>document.getElementById(id);\nconst CARD_APP=window.LAB_MODE==='card'; // 単品のカードアプリとして動かす\n/* 物差しの名前（v2.10）：「秘境レベル」から改めた。名前を変えるときはここだけ直す（カード・ホーム・設定・キャラ一覧・聖遺物のページが同じ名前を使う） */\nconst RANK_NAME='希少ランク';")

# --- 単位：カードアプリでは英語（DAYS／MONTHS／YEARS）だけ ---
rep("function fmtWait(d,L){ L=WAIT_UNITS[L]?L:'jp';",
    "function fmtWait(d,L){ if(CARD_APP) return fmtMonths(d); L=WAIT_UNITS[L]?L:(CARD_APP?'en3c':'jp');")
# --- 単位：カードアプリでは、日数はすべて MONTHS（小数第1位）で出す（v2.3）。目盛り・ランクの境目の表記も同じ ---
rep("en3c:{7:'1 WEEK',30:'1 MONTH',90:'3 MONTHS',365:'1 YEAR',1095:'3 YEARS',3650:'10 YEARS'}})[UL]||TIER_DAY_JP_G,",
    "en3c:{7:'1 WEEK',30:'1 MONTH',90:'3 MONTHS',365:'1 YEAR',1095:'3 YEARS',3650:'10 YEARS'}})[CARD_APP?'mo':UL]||(CARD_APP?moLabels():TIER_DAY_JP_G),")
rep("const TIER_DAY_JP_G={7:'1週',30:'1か月',90:'3か月',365:'1年',1095:'3年',3650:'10年'};",
    "const TIER_DAY_JP_G=CARD_APP?moLabels():{7:'1週',30:'1か月',90:'3か月',365:'1年',1095:'3年',3650:'10年'};")
_tk = "[[1,'1日'],[7,'1週'],[30,'1か月'],[90,'3か月'],[365,'1年'],[1095,'3年'],[3650,'10年'],[36500,'100年'],[365000,'1000年'],[3650000,'1万年']]"
assert s.count(_tk) == 3
s = s.replace(_tk, "(CARD_APP?moTicks(" + _tk + "):" + _tk + ")")

# --- 一覧の行を押したら、カードのページへ ---
rep("if(CH_OPEN) $('chList').scrollIntoView({behavior:'smooth',block:'nearest'}); };",
    "if(CH_OPEN){ if(CARD_APP){ store.set('cardLast',CH_OPEN); cardShowPage('card'); } else $('chList').scrollIntoView({behavior:'smooth',block:'nearest'}); } };")
# --- キャラ一覧の行に「カードを作成」の札（行のどこを押しても同じ。v2.2） ---
rep("stroke=\"${neon?col:'#e9d39a'}\" stroke-opacity=\"${neon?.6:.16}\" ${neon?'filter=\"url(#tlGlow)\"':''}/>`;",
    "stroke=\"${neon?col:'#e9d39a'}\" stroke-opacity=\"${neon?.6:.16}\" ${neon?'filter=\"url(#tlGlow)\"':''}/>`+(CARD_APP?`<g class=\"tl-mk\"><rect x=\"${LN-24+pw+28+MW+CW2-96}\" y=\"${y-laneH/2-8}\" width=\"88\" height=\"16\" rx=\"8\" fill=\"#1c1810\" stroke=\"#e9d39a\" stroke-opacity=\".75\"/><text x=\"${LN-24+pw+28+MW+CW2-52}\" y=\"${y-laneH/2+3.5}\" text-anchor=\"middle\" font-size=\"10\" font-weight=\"700\" fill=\"#f3e3b4\">カードを作成 ›</text></g>`:'');")
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

# --- セット欄を選ぶ形に（v2.2）：4セットはセット名、2セット＋2セットは2セット効果。値は UID と同じ形（「〇〇4」）か、効果（「攻撃力+18%＋攻撃力+18%」） ---
rep('<label class="f" for="ceSet">狙いのセット（秘境）<input type="text" id="ceSet" value="${esc(c.set)}" placeholder="任意"></label>',
    '${CARD_APP?`<label class="f">セット${setPickHTML(c.set,\'id="ceSet"\')}</label>`:`<label class="f" for="ceSet">狙いのセット（秘境）<input type="text" id="ceSet" value="${esc(c.set)}" placeholder="任意"></label>`}')
rep("  $('chEditor').innerHTML=h; editorRead(); editorPreview();", "  $('chEditor').innerHTML=h; if(CARD_APP) setPickBind($('chEditor')); editorRead(); editorPreview();")
rep('      <label class="f" style="max-width:520px">スコアの型<select data-istype>', '      ${CARD_APP?`<label class="f" style="max-width:520px">セット${setPickHTML(g.set||\'\',\'data-iset\')}</label>`:\'\'}<label class="f" style="max-width:520px">スコアの型<select data-istype>')
rep("  box.innerHTML=h;\n  box.querySelectorAll('[data-islot]')", "  box.innerHTML=h; if(CARD_APP) setPickBind(box);\n  box.querySelectorAll('[data-islot]')")
rep("g.name=ge.querySelector('[data-iname]').value.trim(); g.stype=ge.querySelector('[data-istype]').value;", "g.name=ge.querySelector('[data-iname]').value.trim(); g.stype=ge.querySelector('[data-istype]').value; { const st=ge.querySelector('[data-iset]'); if(st) g.set=st.value; }")
rep("if(g.name) c.name=g.name; if(!c.sig){ c.sig=g.owner; c.face=g.face; } }", "if(g.name) c.name=g.name; if(g.set) c.set=g.set; if(!c.sig){ c.sig=g.owner; c.face=g.face; } }")
rep("else { c=Object.assign(blankChar(),{name:g.name,eff:g.eff.slice(),pieces,", "else { c=Object.assign(blankChar(),{name:g.name,set:g.set||'',eff:g.eff.slice(),pieces,")

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

# カードの下の一文の名前も、物差しの名前（RANK_NAME）から
rep('font-weight="700">秘境レベル</tspan>${CARD_APP?`＝この有効RV', 'font-weight="700">${CARD_APP?RANK_NAME:\'秘境レベル\'}</tspan>${CARD_APP?`＝この有効RV')
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
.rv-ov{transition:background-color .9s ease}
.rv-ov.rv-fade{background-color:transparent}
.rv-fly canvas{position:fixed; border-radius:6px; transform-origin:50% 50%; box-shadow:0 8px 24px rgba(0,0,0,.5)}
/* UIDのショーケース（v2.2） */
.ushow{margin-top:14px}
.ushow-h{display:flex; flex-wrap:wrap; gap:8px 16px; align-items:flex-end; justify-content:space-between; margin-bottom:12px}
.ushow-h h2{font-family:"Shippori Mincho B1","Hiragino Mincho ProN",serif; font-size:clamp(20px,3.2vw,26px); letter-spacing:.12em; color:#e9d39a; margin:0 0 4px}
.ushow-h h2::before{display:none}
.ushow .th{display:block; aspect-ratio:16/9; border-radius:6px; background:#0b0e22}
.ushow .rv-lg{grid-template-columns:repeat(auto-fill,minmax(300px,1fr))} .ushow .rv-lc{min-width:0} .ushow .rv-lc .m .a{white-space:nowrap}
.ushow .th canvas{display:block; width:100%; height:auto}
.ushow .m{transition:opacity .5s ease}
.ushow.landing .th canvas{visibility:hidden} .ushow.landing .m{opacity:0}
.uv-ov{position:fixed; inset:0; z-index:8500; background:rgba(2,3,9,.86); overflow:auto; padding:16px; animation:rvIn .25s ease-out}
.uv-box{width:min(100%,980px); margin:0 auto; background:var(--panel,#0c0f22); border:1px solid rgba(233,211,154,.25); border-radius:12px; padding:14px 16px 18px; display:grid; gap:12px}
.uv-h{display:flex; justify-content:space-between; align-items:center; gap:12px}
.uv-h b{font-family:"Shippori Mincho B1","Hiragino Mincho ProN",serif; font-size:20px; letter-spacing:.1em; margin-right:10px}
.uv-card svg{display:block; width:100%; height:auto; border-radius:6px; box-shadow:0 12px 36px rgba(0,0,0,.55)}
.uv-sec{border-top:1px solid var(--line); padding-top:10px} .uv-sec h3{margin:0 0 4px; font-size:14px}
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
  if(p==='set') cardRenderSettings(); if(p==='card') cardAfterRender(); if(p==='inv') invRender(); window.scrollTo({top:0}); }
const LIST_SORTS={desc:'高い順',asc:'低い順',added:'追加した順'};
function listSortMode(){ const m=store.get('listSort','desc'); return LIST_SORTS[m]?m:'desc'; }
function cardListSort(rows){ const m=listSortMode(), r=rows.slice(); // 秘境レベルの高い順・低い順（「上限」は最後尾の扱い）、追加した順（新しく入ったキャラが上）
  if(m==='added'){ const ix=new Map(CHARS.map((c,i)=>[c.id,i])); return r.sort((a,b)=>ix.get(b.c.id)-ix.get(a.c.id)); }
  const v=x=>{ const a=x.st.age||0; return isFinite(a)?a:1e15; }; return r.sort((a,b)=>m==='asc'?v(a)-v(b):v(b)-v(a)); }
function cardSorted(){ return cardListSort(CHARS.map(c=>({c,st:charStats(c)}))); }
function cardAfterRender(){ document.querySelectorAll('[data-lsort]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lsort===listSortMode()))); const host=$('cardHost'); if(!host) return;
  const det=$('cardBox')&&$('cardBox').closest('.chdetail');
  host.innerHTML=''; if(det) host.appendChild(det);
  if(!CH_OPEN||!det) host.innerHTML=`<div class="empty">${CHARS.length?'キャラ一覧で「カードを作成」を押すと、ここにそのキャラのカードが出ます。':'まだキャラがいません。UIDで取り込んだカードはホームに並びます。ここには、動画・スクショ・手入力で取り込んだキャラ（キャラ一覧）のカードが出ます。'}</div>`;
  const sel=$('cSel'); if(sel){ const rows=cardSorted(); sel.innerHTML=rows.map(({c})=>`<option value="${c.id}"${c.id===CH_OPEN?' selected':''}>${esc(c.name||'（名前なし）')}</option>`).join('')||'<option value="">—</option>'; }
  const z=$('cZoom'); if(z) z.value=String(CARD_ZOOM[CH_OPEN]||100);
  const has=!!(CH_OPEN&&CARD_IMG[CH_OPEN]), own=has&&!/^portraits\//.test(CARD_IMG[CH_OPEN]); if($('cZoomWrap')) $('cZoomWrap').hidden=!has; if($('cArtDel')) $('cArtDel').hidden=!own;
  // 保存してある立ち絵（なければ同梱の立ち絵）は、開いたときに切り出し直す。切り出せない画像（背景つき）は、そのまま貼る
  const id=CH_OPEN; applyBundled(CHARS.find(x=>x.id===id)); if(id&&CARD_IMG[id]&&!(id in CARD_FIT)&&!CARD_FITTING[id]){ CARD_FITTING[id]=1; fitCardArt(CARD_IMG[id],CARD_ZOOM[id]).then(u=>{ delete CARD_FITTING[id]; CARD_FIT[id]=u||''; renderChars(); }); }
}
/* ---- 立ち絵の保存（この端末のIndexedDB。ほかの人には見えない） ---- */
function cardDB(){ if(CARD_DB) return CARD_DB; CARD_DB=new Promise((res)=>{ try{ const r=indexedDB.open('meinoseiza-card',1); r.onupgradeneeded=()=>{ r.result.createObjectStore('portraits',{keyPath:'id'}); }; r.onsuccess=()=>res(r.result); r.onerror=()=>res(null); }catch(e){ res(null); } }); return CARD_DB; }
async function portraitTx(mode,fn){ const db=await cardDB(); if(!db) return null; return new Promise(res=>{ try{ const tx=db.transaction('portraits',mode), st=tx.objectStore('portraits'); const r=fn(st); tx.oncomplete=()=>res(r&&r.result); tx.onerror=()=>res(null); }catch(e){ res(null); } }); }
function portraitSave(id){ if(!CARD_APP||!id||!CARD_IMG[id]) return; const c=CHARS.find(x=>x.id===id)||uidFind(id);
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
  box.innerHTML=all.length?`<div class="cthumbs">${all.map(p=>{ const c=CHARS.find(x=>x.id===p.id)||uidFind(p.id); return `<div class="cthumb"><img src="${p.src}" alt=""><b>${esc((c&&c.name)||p.name||'（削除したキャラ）')}</b><button class="btn" style="padding:3px 10px;font-size:12px" data-pdel="${p.id}">削除</button></div>`; }).join('')}</div>`:'<div class="empty">まだ保存した立ち絵はありません。カードのページの「立ち絵を選ぶ」で選ぶと、ここに並びます。</div>';
  box.querySelectorAll('[data-pdel]').forEach(b=>b.addEventListener('click',()=>portraitDelete(b.dataset.pdel))); }
/* ---- 組み立て ---- */
function cardAppInit(){
  document.body.classList.add('mode-card'); buildsApply(); // 有効OPが推定のキャラに、初期値の表（src/builds.csv）を当てる
  // 見た目は決定済みの値に固定（試作用の切り替えは出さない）
  CC_LABEL='glass'; CC_FONT='murecho'; CC_FRAME='gold'; CC_LINE='star'; CC_MYTH='m1'; CC_MYTHLANG='en'; CC_UNITS='en3c'; CC_SLOTID='badge';
  const head=document.querySelector('header.top'); head.querySelector('h1').innerHTML='<small>秘境で何日回ると、どこまで行く？</small>命ノ星座カード';
  const nav=cardEl('div',{class:'tabs cnav',role:'tablist','aria-label':'ページ'},
    '<button role="tab" data-page="home">ホーム</button><button role="tab" data-page="list">キャラ一覧</button><button role="tab" data-page="card">カード</button><button role="tab" data-page="inv">聖遺物</button><button role="tab" data-page="scan">取り込む</button><button role="tab" data-page="set">設定</button>');
  head.appendChild(nav); nav.querySelectorAll('[data-page]').forEach(b=>b.addEventListener('click',()=>cardShowPage(b.dataset.page)));
  { const h1=head.querySelector('h1'); h1.style.cursor='pointer'; h1.addEventListener('click',()=>cardShowPage('home')); }
  const wrap=document.querySelector('.wrap'), view=$('view-chars');
  const pHome=cardEl('section',{id:'pg-home',class:'cpage'}), pList=cardEl('section',{id:'pg-list',class:'cpage',hidden:''}), pCard=cardEl('section',{id:'pg-card',class:'cpage',hidden:''}), pSet=cardEl('section',{id:'pg-set',class:'cpage',hidden:''}), pScan=cardEl('section',{id:'pg-scan',class:'cpage',hidden:''}), pInv=cardEl('section',{id:'pg-inv',class:'cpage',hidden:''});
  view.parentNode.insertBefore(pHome,view); view.parentNode.insertBefore(pList,view); view.parentNode.insertBefore(pCard,view); view.parentNode.insertBefore(pInv,view); view.parentNode.insertBefore(pScan,view); view.parentNode.insertBefore(pSet,view);
  // キャラ一覧：横棒の一覧＋取り込みの入口（取り込みの確認と手入力は、この上に出る）
  const tl=$('chTimeline').closest('.panel');
  pList.appendChild($('chEditor')); pList.appendChild($('chImport')); pList.appendChild(tl);
  tl.style.marginTop='14px';
  const h=tl.querySelector('.row'); h.querySelector('h2').textContent='手持ちのキャラ';
  const ctrl=h.querySelector('.row'); ctrl.innerHTML=''; const shots=$('chShots').closest('label'); const so=cardEl('div',{class:'seg',role:'group','aria-label':'並び順'},Object.entries(LIST_SORTS).map(([k,v])=>`<button data-lsort="${k}">${v}</button>`).join('')); ctrl.appendChild(so); ctrl.appendChild(shots); ctrl.appendChild($('chAdd'));
  so.querySelectorAll('[data-lsort]').forEach(b=>b.addEventListener('click',()=>{ store.set('listSort',b.dataset.lsort); renderChars(); }));
  const tln=tl.querySelector('p.note'); if(tln) tln.innerHTML='行を押すと、そのキャラの<b>育成候補</b>（手持ちの聖遺物のうち、いまの部位を超えうるもの）が開きます。押した棒の部位が先に出ます。カードは行の右上の「カードを作成 ›」から。並び順は右上で切り替えられます（カードのページの ◀ ▶ も同じ順）。スクショは端末の中で読み取り、どこにも送りません（このページへのドラッグや貼り付けでも取り込めます）。棒の長さ＝部位ごとの'+RANK_NAME+'、右の数字＝5部位の合計の'+RANK_NAME+'。色はランク（<span id="tierLegend"></span>）。';
  // カード
  pCard.innerHTML=`<div class="panel" style="margin-top:14px"><div class="ctool"><div class="grp2"><button class="btn" id="cEdit">編集</button><span id="cDelBox"><button class="btn" id="cDel">削除</button></span></div>
    <div class="grp2"><label class="btn" style="cursor:pointer">立ち絵を選ぶ<input type="file" id="cArt" accept="image/*" hidden></label><label id="cZoomWrap" class="row" style="gap:6px;font-size:12px;color:var(--muted)" hidden>大きさ<input type="range" id="cZoom" min="60" max="170" step="5" value="100" style="width:110px"></label><button class="btn" id="cArtDel" hidden>立ち絵を外す</button><button class="btn primary" id="cShare">共有</button><button class="btn" id="cPng">PNGで保存</button><button class="btn" id="cWebp">WebP</button></div></div>
    <p class="note" id="cMsg" aria-live="polite" style="margin-top:6px"></p><div id="cardHost" style="margin-top:6px"></div>
    <p class="note" style="margin-top:8px">立ち絵はこの端末（このブラウザ）に保存され、ほかの人には見えません。絵はドラッグで位置を動かせます（ダブルクリックで元の位置）。保存した画像は2400×1350です。PNGはどこに上げても確実、WebPは軽いかわりに受け付けないサービスもあります。</p></div>`;
  $('cEdit').addEventListener('click',()=>{ if(!CH_OPEN) return; cardShowPage('list'); openEditor(CH_OPEN); $('chEditor').scrollIntoView({behavior:'smooth',block:'start'}); });
  cardAppBindDel();
  $('cArt').addEventListener('change',e=>{ const f=e.target.files[0]; e.target.value=''; if(!f||!CH_OPEN) return; const rd=new FileReader(); rd.onload=async()=>{ const id=CH_OPEN; CARD_IMG[id]=await portraitShrink(rd.result); delete CARD_FIT[id]; delete CARD_POS[id]; portraitSave(id); renderChars(); }; rd.readAsDataURL(f); });
  $('cZoom').addEventListener('change',e=>{ const id=CH_OPEN, src=CARD_IMG[id]; if(!src) return; CARD_ZOOM[id]=+e.target.value; portraitSave(id); fitCardArt(src,CARD_ZOOM[id]).then(u=>{ if(u&&CARD_IMG[id]===src){ CARD_FIT[id]=u; renderChars(); } }); });
  $('cArtDel').addEventListener('click',()=>{ if(CH_OPEN) portraitDelete(CH_OPEN); });
  $('cShare').addEventListener('click',cardShare); $('cPng').addEventListener('click',()=>cardExport('png',$('cMsg'))); $('cWebp').addEventListener('click',()=>cardExport('webp',$('cMsg')));
  // 取り込む：UID（Enka.Network のJSONを受け渡し）と、動画（聖遺物ビデオスキャナーを scan/ に置き、枠の中で動かす）。UIDはホームのショーケースへ（v2.2）、動画はキャラ一覧へ
  pScan.innerHTML=`<div class="panel" style="margin-top:14px"><h2>UIDから取り込む</h2>
    <p class="note">ゲームのショーケースに並べたキャラの聖遺物を、Enka.Network から取り込みます（ゲームのプロフィールで、キャラの詳細を見られるようにしておいてください）。UIDを入れて「UIDで取得」を押します。取り込んだキャラは、キャラ一覧ではなくホームにカードで並びます（取り直すと入れ替わります）。</p>
    <div class="row" style="margin-top:10px"><label class="f" for="enkaUid">UID<input type="text" id="enkaUid" inputmode="numeric" autocomplete="off" maxlength="10" placeholder="例：800123456" style="width:9em"></label><button class="btn primary" id="enkaGet">UIDで取得</button></div>
    <div class="note" id="enkaMsg" aria-live="polite" style="margin-top:8px"></div>
    <details class="more" id="enkaManual" style="margin-top:10px"><summary>「UIDで取得」がうまくいかないとき（手で受け渡す）</summary>
    <ol class="note csteps"><li>UIDを入れて「Enkaで開く」を押す（別のタブで文字だらけのページが開きます）</li><li>開いたページの文字を全部選んでコピーする（Firefoxは「生データ」のタブで）。または、そのページを保存する</li><li>下の欄に貼り付けて「読み込む」を押す（保存したときは「ファイルから読み込む」）</li></ol>
    <div class="btns"><a class="btn" id="enkaOpen" target="_blank" rel="noopener" aria-disabled="true">Enkaで開く</a></div>
    <textarea id="enkaText" rows="3" aria-label="Enka のページの文字" placeholder="Enka のページの文字を、ここに貼り付けます" style="width:100%;margin-top:10px;font:12px/1.4 ui-monospace,monospace;color:var(--ink);background:var(--inset);border:1px solid var(--line);border-radius:8px;padding:8px"></textarea>
    <div class="btns"><button class="btn primary" id="enkaIn">読み込む</button><label class="btn" style="cursor:pointer">ファイルから読み込む<input type="file" id="enkaFile" accept=".json,.txt,application/json,text/plain" hidden></label></div></details>
    <p class="note" style="margin-top:8px">★5の聖遺物だけを取り込みます。Enka のデータにはサブOPが伸びた1回ごとの幅が入っているので、有効RVは推定ではなく実際の値で計算します。同じUIDをすぐ開き直しても、しばらくは同じ内容が返ります。データ：Enka.Network</p></div>
    <div class="panel" style="margin-top:14px"><h2>動画から取り込む</h2><p class="note">ゲームの所持品画面（聖遺物）を録画した動画から、聖遺物を読み取ります。読み終わったら「キャラ一覧に入れる」で、装備中のキャラがキャラ一覧に、すべての★5の聖遺物が「手持ち」（聖遺物のページと育成候補）に入ります。+20になっていない聖遺物はいまの値で評価し、カードに「+8」などの印が付きます。★4の聖遺物は外します。動画はこの端末の中だけで処理し、どこにも送りません。</p>
    <div class="btns" id="scanStartBox"><button class="btn primary" id="scanStart">動画の読み取りを始める</button><span class="note" style="align-self:center">読み取りの道具（約15MB）を読み込みます</span></div>
    <div class="note" id="scanMsg" aria-live="polite" style="margin-top:6px"></div></div>
    <div class="panel" style="margin-top:14px"><h2>GOOD形式のファイルから取り込む</h2><p class="note">聖遺物ビデオスキャナーなどが書き出す「GOOD形式」のファイル（artifacts_GOOD.json など）を読み込みます。装備中のキャラはキャラ一覧へ、すべての★5の聖遺物は「手持ち」として保存し、聖遺物のページと育成候補に使います（読み込むたびに、手持ちはまるごと入れ替わります）。ファイルはこの端末の中だけで読み、どこにも送りません。</p>
    <div class="btns"><label class="btn primary" style="cursor:pointer">ファイルを選ぶ<input type="file" id="goodFile" accept=".json,application/json" hidden></label></div>
    <div class="note" id="goodMsg" aria-live="polite" style="margin-top:6px"></div></div>
    <iframe id="scanFrame" title="聖遺物ビデオスキャナー" hidden style="display:block;width:100%;height:900px;border:0;margin-top:14px;background:transparent;color-scheme:dark"></iframe>`;
  $('scanStart').addEventListener('click',scanOpen);
  $('goodFile').addEventListener('change',async e=>{ const f=e.target.files[0]; e.target.value=''; if(f) goodImportFile(await f.text(),$('goodMsg')); });
  invInit(pInv);
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
    <dt>${RANK_NAME}</dt><dd>そのキャラ（メインOP・有効OP）の条件で、いまの有効RVを秘境だけで揃えるのにかかる、平均的な人の日数</dd><dt>ランクの境目</dt><dd>★1 〜0.2 MONTHS／★2 〜1.0 MONTHS／★3 〜3.0 MONTHS／★4 〜12.0 MONTHS／★5 〜36.0 MONTHS／★5+ 36.0 MONTHS〜（1,200 MONTHS 以上は ONCE IN A CENTURY、60,000 MONTHS 以上は SINCE THE DAWN OF TIME）。期間はすべて MONTHS（30.4日＝1か月）で表します</dd>
    <dt>確率の出典</dt><dd>KQM「Genshin Impact Artifacts Guide」、Genshin Impact Wiki（Fandom）「Artifact/Distribution」（草元素追加後の値）</dd></dl></div>
    <div class="panel" style="margin-top:14px"><h2>保存した立ち絵</h2><p class="note" style="margin-bottom:8px">この端末（このブラウザ）にだけ保存されています。ほかの人には見えません。大きい画像は、長い辺1600pxに縮めて保存します（カードの見た目は変わりません）。</p><div id="cPortraits"></div></div>
    <div class="panel" style="margin-top:14px"><h2>カードの登場の演出</h2><label class="row" style="gap:8px;align-items:center"><input type="checkbox" id="cRevealOn">UIDで取り込んだあと、カードが机に落ちてくる演出を出す</label><p class="note" style="margin-top:6px">演出の途中で画面を押す（Enter・スペースでも）と次のカードへ進み、右上の「スキップ」で最後まで飛べます。</p></div>
    <div class="panel" style="margin-top:14px" id="cMoveHost"><h2>データの引っ越し</h2></div>
    <div class="panel" style="margin-top:14px"><h2>このアプリについて</h2><p class="note">命ノ星座カード v2.9。計算は聖遺物厳選ラボと共通です。原神のキャラクター名・画像などの権利は HoYoverse に帰属します。UIDからの取り込みには Enka.Network のデータを、動画からの取り込みには聖遺物ビデオスキャナー（読み取りエンジン：Tesseract.js）を使っています。キャラのデータはこの端末（このブラウザ）に保存され、ラボ本体や別の端末とのやりとりは「データの引っ越し」のJSONで行います（ラボ本体で書き出したものもそのまま読めます）。HoYoverseとは関係のない非公式のファンツールです。</p></div>`;
  const mh=$('cMoveHost'); [...(det||mv).childNodes].forEach(n=>mh.appendChild(n)); mv.remove();
  { const cb=$('cRevealOn'); cb.checked=!store.get('revealOff',0); cb.addEventListener('change',()=>store.set('revealOff',cb.checked?0:1)); }
  // ドラッグで取り込み（どのページでも）
  document.addEventListener('dragover',e=>{ if(e.dataTransfer&&[...e.dataTransfer.types].includes('Files')) e.preventDefault(); });
  document.addEventListener('drop',e=>{ if(e.target.closest&&e.target.closest('#cardHost')) return; const fs=e.dataTransfer?[...e.dataTransfer.files]:[]; if(fs.length){ e.preventDefault(); if(CARD_PAGE==='scan'||fs.every(f=>/^video\//.test(f.type))){ cardShowPage('scan'); scanOpen(); $('scanMsg').textContent='動画は、下の枠（録画ファイルをここにドロップ）に落としてください。'; return; } cardShowPage('list'); importShots(fs); } });
  // 取り込み・手入力を始めたら一覧のページへ
  $('chAdd').addEventListener('click',()=>cardShowPage('list'));
  { const l=store.get('cardLast',null); if(l&&CHARS.some(c=>c.id===l)) CH_OPEN=l; } // カードのページは、最後に「カードを作成」したキャラ
  portraitLoadAll().then(()=>{ renderChars(); });
  uidLoad(); homeInit(pHome); cardShowPage('home');
  renderChars();
  if(h0==='reveal'||window.REVEAL_DEMO) revealDemoPanel(); // showTab が先に # を書き換えるので、開いたときの値（h0）で見る
  if(h0==='card2') cc2Proto(); // カードのデザインの見直し（試作・ROADMAP 2.9。作り手の確認用）
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
      if(d.good){ const iv=invFromGood(d.good); if(iv) r+=iv; }
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
/* キャラ全体の値（2.10）：Enka の fightPropMap＝ゲームのキャラ画面と同じ最終値（突破・武器・聖遺物・セットの常時効果込み）。％は小数第1位の％に、攻撃・HP・防御は合計の実数。
   あわせて武器（id・Lv・精錬・★）・凸数・キャラのLvを残す（ダメージの式で、実際の武器・凸を使えるようにするため）。右下の段の「パラメータの実際の値」に使う */
const ENKA_FP={2000:'HP',2001:'ATK',2002:'DEF',20:'CR',22:'CD',23:'ER',26:'HEAL',28:'EM',30:'PHYS',40:'DMG_炎',41:'DMG_雷',42:'DMG_水',43:'DMG_草',44:'DMG_風',45:'DMG_岩',46:'DMG_氷'};
function enkaStat(av){ const m=av&&av.fightPropMap; if(!m) return {}; const fp={};
  for(const [k,n] of Object.entries(ENKA_FP)){ const v=+m[k]; if(!isFinite(v)||(!v&&!['CR','CD','ER','EM'].includes(n))) continue; /* 0 の治療・物理・元素ダメは残さない */ fp[n]=['HP','ATK','DEF','EM'].includes(n)?Math.round(v):Math.round(v*1000)/10; }
  const wq=(av.equipList||[]).find(e=>e&&e.flat&&e.flat.itemType==='ITEM_WEAPON'), w=wq?{id:wq.itemId,lv:+((wq.weapon||{}).level)||0,r:1+(+Object.values((wq.weapon||{}).affixMap||{})[0]||0),star:+wq.flat.rankLevel||0}:null;
  const lv=+(((av.propMap||{})['4001']||{}).val)||0, base={}; /* 基礎の値（キャラ＋武器の基礎。1＝HP・4＝攻撃・7＝防御）：HP・攻撃・防御の伸びを「基礎の何%」にするため */
  [[1,'HP'],[4,'ATK'],[7,'DEF']].forEach(([k,n])=>{ const v=+m[k]; if(isFinite(v)&&v>0) base[n]=Math.round(v); });
  return {uidStat:Object.assign({fp,cons:(av.talentIdList||[]).length},Object.keys(base).length?{base}:{},lv?{lv}:{},w?{w}:{})}; }
function enkaToLab(d){ const out=[], notes={low:0,partial:0,unknown:0,odd:0};
  for(const av of (d&&d.avatarInfoList)||[]){ const pieces={}, cnt={}, low={};
    for(const e of av.equipList||[]){ const f=e.flat||{}, r=e.reliquary; if(f.itemType!=='ITEM_RELIQUARY'||!r) continue;
      const slot=ENKA_SLOT[f.equipType], main=ENKA_PROP[(f.reliquaryMainstat||{}).mainPropId]; if(f.rankLevel!==5){ notes.low++; if(f.rankLevel===4&&slot&&main){ low[slot]={main,r:4,lv:Math.max(0,(+r.level||1)-1)}; if(f.setId) low[slot].setId=String(f.setId); } continue; } if(!slot||!main){ notes.odd++; continue; }
      const lv=Math.max(0,Math.min(20,(+r.level||1)-1)), rolls={}; let bad=false;
      for(const id of r.appendPropIdList||[]){ const x=ENKA.affix[String(id)]; if(!x){ bad=true; continue; } (rolls[x[0]]=rolls[x[0]]||[]).push(x[1]); }
      const subs=(f.reliquarySubstats||[]).map(q=>{ const s=ENKA_PROP[q.appendPropId], v=+q.statValue; return {s,v:FLAT.has(s)?String(Math.round(v)):v.toFixed(1)}; }).filter(q=>q.s);
      if(subs.length<3||subs.length>4){ notes.odd++; continue; }
      if(subs.length===3) subs.push({s:'',v:'',off:true}); // +0の3OP：4つ目は Enka には出てこない（種類も分からない）
      const p={main,subs}; if(f.setId) p.setId=String(f.setId); if(lv<20){ p.lv=lv; notes.partial++; } if(!bad) p.rolls=rolls; pieces[slot]=p;
      if(f.setId) cnt[f.setId]=(cnt[f.setId]||0)+1; }
    if(!Object.keys(pieces).length) continue;
    const nm=ENKA.avatar[String(av.avatarId)]; if(!nm) notes.unknown++;
    const set=Object.entries(cnt).sort((a,b)=>b[1]-a[1]).filter(x=>x[1]>=2).map(([k,n])=>(ENKA.set[k]||'セット'+k)+(n>=4?'4':'2')).join('＋');
    out.push(Object.assign({id:'uid-'+av.avatarId,name:nm||`不明なキャラ（${av.avatarId}）`,set,pieces,date:today()},Object.keys(low).length?{low}:{},enkaStat(av))); } // low：★4の聖遺物（計算に入れず、カードで「★4」と表示するだけ）
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
  const uid=d.uid&&/^\d{9,10}$/.test(String(d.uid))?String(d.uid):(store.get('enkaUid','')||''); uidSave(uid,chars); const ex=[]; let r=`${chars.length}人のカードを、ホームに並べました`;
  if(notes.partial) ex.push(`+20になっていない聖遺物 ${notes.partial}個は、いまの値で評価しています`); if(notes.low) ex.push(`★4以下の聖遺物 ${notes.low}個は外しました`);
  if(notes.unknown) ex.push(`名前の分からないキャラが ${notes.unknown}人います（アプリの更新待ち）`); if(notes.odd) ex.push(`読めなかった聖遺物が ${notes.odd}個ありました`);
  if(ex.length) r+='。'+ex.join('。')+'。'; if(uid){ $('enkaUid').value=uid; try{ store.set('enkaUid',uid); }catch(e){} }
  $('enkaText').value=''; box.innerHTML=`<p>${esc(r)}</p>`; HOME_NOTE=r; uidReveal(); return chars.map(c=>c.name); }
/* ================= ホーム（v2.0）：見本のカード → UID → いちばんすごいカード ================= */
const SITE_URL='https://wayfaringgene-code.github.io/genshin-lab/';
const ON_SITE=/(^|\.)github\.io$/.test(location.hostname)||location.hostname==='localhost'; // GitHub Pages（と手元の確認）で開いているか
const LAB_URL=ON_SITE?'lab/':'https://claude.ai/artifact/CyumpKAACPGCbSeY8sFpFA';
/* ---- 同梱の立ち絵：portraits/{avatarId}.webp（tools/build_portraits.py で作る）。自分で選んだ立ち絵があれば、そちらが優先 ---- */
const PORTRAITS=__PORTRAITS__; // {avatarId:{file, name, zoom?, pos?}}
let _N2A=null; function name2aid(n){ if(!_N2A){ _N2A={}; for(const [k,v] of Object.entries(ENKA.avatar)) if(!(v in _N2A)) _N2A[v]=k; } return _N2A[n]; }
function bundledPortrait(c){ if(!ON_SITE||!c) return null; const a=((/^(?:uid|enka|sample)-(\d+)$/.exec(c.id||''))||[])[1]||name2aid(c.name); const q=(a&&PORTRAITS[a])||Object.values(PORTRAITS).find(x=>x&&x.name===c.name); return q?{src:'portraits/'+q.file,zoom:q.zoom||0,pos:q.pos||null}:null; }
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
  box.innerHTML=`<div id="homeShow"></div><section class="chero">
    <div class="chero-copy"><p class="ceyebrow">原神・聖遺物の「珍しさ」を測る</p>
      <h2 class="chero-q"><span class="nw">あなたの聖遺物は、</span><span class="nw">秘境を何日回った</span><span class="nw">人のレベル？</span></h2>
      <p class="chero-lead">UIDを入れるだけで、ショーケースに並べたキャラの聖遺物を「${RANK_NAME}」で測って、カードにします。</p>
      <form id="homeForm" class="chero-form" novalidate><label class="sr" for="homeUid">UID</label><input type="text" id="homeUid" inputmode="numeric" autocomplete="off" maxlength="10" placeholder="UID（9〜10けた）"><button class="btn primary big" id="homeGo" type="submit">カードを作る</button></form>
      <div class="note" id="homeMsg" aria-live="polite"></div>
      <p class="ctrust">ログイン不要・入れるのはUIDだけ・データはこの端末の中だけに保存</p></div>
    <figure class="chero-card"><div id="homeSample" aria-label="カードの見本"></div><figcaption>見本：こんなカードができます</figcaption></figure></section>
    <div id="homeBack"></div>
    <div class="panel" style="margin-top:14px"><details class="more"><summary>「${RANK_NAME}」って？</summary><dl class="ckv" style="margin-top:6px">
      <dt>${RANK_NAME}</dt><dd>そのキャラ（メインOP・有効OP）の条件で、いまの聖遺物と同じだけの有効RVを、秘境だけで揃えるのにかかる平均の日数です（1日9周＝樹脂180）。強さではなく「どれだけ珍しいか」の物差しです。</dd>
      <dt>ランク</dt><dd>★1 〜0.2 MONTHS／★2 〜1.0 MONTHS／★3 〜3.0 MONTHS／★4 〜12.0 MONTHS／★5 〜36.0 MONTHS／★5+ 36.0 MONTHS〜。1,200 MONTHS 以上は ONCE IN A CENTURY、60,000 MONTHS 以上は SINCE THE DAWN OF TIME。</dd>
      <dt>有効RV</dt><dd>有効なサブOP（そのキャラに役立つもの）が伸びた量の合計です。1回でいちばん大きく伸びたときを100%として数えます。</dd>
      <dt>使い方のヒント</dt><dd>部位ごとの${RANK_NAME}が、これから秘境を回るつもりの日数より長ければ、その期間にその部位を更新できる見込みは五分以下です。</dd></dl></details></div>
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
  // UIDのショーケース（ホームのいちばん上）と、キャラ一覧への案内
  uidRender(); const back=$('homeBack'); if(!CHARS.length){ back.innerHTML=''; return; }
  back.innerHTML=`<div class="panel chome-back" style="margin-top:14px"><h2>キャラ一覧</h2><p class="note">動画・スクショ・手入力で取り込んだキャラが ${CHARS.length}人います。キャラ一覧の「カードを作成」から、1人ずつカードにできます。</p>
    <div class="btns"><button class="btn" data-hb="list">キャラ一覧へ</button></div></div>`;
  back.querySelector('[data-hb="list"]').addEventListener('click',()=>cardShowPage('list')); }
async function homeGo(e){ if(e) e.preventDefault(); const msg=$('homeMsg'), btn=$('homeGo'), uid=$('homeUid').value.replace(/\D/g,'');
  if(!/^\d{9,10}$/.test(uid)){ msg.textContent='UIDは9けたか10けたの数字です（ゲームのメニュー画面の右下などに出ています）。'; return; }
  $('enkaUid').value=uid; try{ store.set('enkaUid',uid); }catch(err){}
  btn.disabled=true; msg.textContent='Enka に問い合わせています…'; let names=null;
  try{ names=await enkaFetch(); }catch(err){} finally{ btn.disabled=false; }
  if(names&&names.length) return; // 取り込みが済むと、enkaImport がホームに並べて演出を流す
  const why=($('enkaMsg').querySelector('p')||$('enkaMsg')).innerText.trim();
  msg.innerHTML=`<p class="err">${esc(why||'取得できませんでした。')}</p><p style="margin-top:4px"><a href="#" id="homeAlt">ほかの方法で取り込む（動画・スクショ・手で受け渡す）</a></p>`;
  $('homeAlt').addEventListener('click',ev=>{ ev.preventDefault(); cardShowPage('scan'); }); }
/* ---- セットを選ぶ（v2.2）：種類（なし／4セット／2セット＋2セット／2セット）→ セット名か2セット効果。選んだ結果を隠し欄に入れる ---- */
function setPickLists(){ const names=[...new Set(Object.values(ENKA.set))].reverse(), ord=['攻撃力+18%','元素熟知+80','元素チャージ効率+20%','HP+20%','防御力+30%','会心率+12%'];
  const labs=[...new Set(Object.values(SET_BONUS2))].sort((a,b)=>{ const i=ord.indexOf(a), j=ord.indexOf(b); return (i<0?99:i)-(j<0?99:j)||a.localeCompare(b,'ja'); }); return {names,labs}; }
function setPickParse(v){ const parts=String(v||'').split('＋').map(x=>x.trim()).filter(Boolean), {names,labs}=setPickLists(); if(!parts.length) return {t:'',a:'',b:''};
  const f=parts.map(x=>/^(.+?)4$/.exec(x)).find(Boolean); if(f&&names.includes(f[1])) return {t:'4',a:f[1],b:''};
  const L=parts.map(x=>{ const m=/^(.+?)2$/.exec(x); return m?(SET_BONUS2[m[1]]||null):(labs.includes(x)?x:null); });
  if(L.every(Boolean)&&L.length<=2) return L.length===2?{t:'22',a:L[0],b:L[1]}:{t:'2',a:L[0],b:''};
  if(parts.length===1&&names.includes(parts[0])) return {t:'4',a:parts[0],b:''};
  return {t:'raw',a:String(v),b:''}; }
function setPickHTML(v,attr){ const {names,labs}=setPickLists(), p=setPickParse(v), O=(arr,cur)=>arr.map(x=>`<option${x===cur?' selected':''}>${esc(x)}</option>`).join('');
  return `<span class="setpick"><input type="hidden" ${attr} value="${esc(v||'')}"><select data-sp="t" aria-label="セットの種類"><option value=""${p.t===''?' selected':''}>なし（分からない）</option><option value="4"${p.t==='4'?' selected':''}>4セット</option><option value="22"${p.t==='22'?' selected':''}>2セット＋2セット</option><option value="2"${p.t==='2'?' selected':''}>2セットだけ</option>${p.t==='raw'?`<option value="raw" selected>いまの書き方のまま</option>`:''}</select>`
    +`<select data-sp="n" aria-label="セット"${p.t==='4'?'':' hidden'}><option value="">セットを選ぶ</option>${O(names,p.t==='4'?p.a:'')}</select>`
    +`<select data-sp="a" aria-label="2セット効果（1つ目）"${/^2/.test(p.t)?'':' hidden'}><option value="">2セット効果を選ぶ</option>${O(labs,/^2/.test(p.t)?p.a:'')}</select>`
    +`<select data-sp="b" aria-label="2セット効果（2つ目）"${p.t==='22'?'':' hidden'}><option value="">2セット効果を選ぶ</option>${O(labs,p.t==='22'?p.b:'')}</select>${p.t==='raw'?`<span class="note">${esc(v)}</span>`:''}</span>`; }
function setPickBind(root){ root.querySelectorAll('.setpick').forEach(sp=>{ const q=k=>sp.querySelector(`[data-sp="${k}"]`), hid=sp.querySelector('input[type=hidden]'), raw=hid.value;
  const upd=()=>{ const t=q('t').value; q('n').hidden=t!=='4'; q('a').hidden=!/^2/.test(t); q('b').hidden=t!=='22';
    hid.value=t==='4'?(q('n').value?q('n').value+'4':''):t==='22'?[q('a').value,q('b').value].filter(Boolean).join('＋'):t==='2'?q('a').value:t==='raw'?raw:''; };
  sp.querySelectorAll('select').forEach(el=>el.addEventListener('input',upd)); }); }
/* ================= UIDのショーケース（v2.2）：UIDで取り込んだキャラは、キャラ一覧とは別のラインでホームに並べる =================
   いつも最後にUIDで取り込んだキャラだけ（取り直すと、まるごと入れ替わる）。履歴なし・引っ越しなし・ラボからは見えない（保存名 uidShow）。
   立ち絵はUIDのカードだけのもの（id は uid-{avatarId}。キャラ一覧の立ち絵とは別に保存）。有効OPは「名前＋セット」ごとに1つ（effPut） */
let UID_SHOW=null, UID_THUMB={}, UID_THUMB_BUSY=false, HOME_NOTE='', UV=null;
// 1つのページにカードのSVGが2枚以上並ぶ（ホームの見本と、大きく開いたカード）ので、SVGの中のidを付け替える（同じidが並ぶと、隠れた側の模様を拾ってしまう）
var RV_UID=0;
function rvUniq(svg){ const k='_u'+(++RV_UID); return svg.replace(/\bid="([^"]+)"/g,`id="$1${k}"`).replace(/url\(#([^)]+)\)/g,`url(#$1${k})`).replace(/href="#([^"]+)"/g,`href="#$1${k}"`); }
function uidEff(c){ const e=effOf(c); if(e){ c.eff=e; delete c.effGuess; } else if(!Array.isArray(c.eff)||!c.eff.length||(c.effGuess&&buildEff(c))){ const g=guessEffFor(c); c.eff=g||S.eff.slice(); c.effGuess=true; } }
function uidLoad(){ const v=store.get('uidShow',null); UID_SHOW=v&&Array.isArray(v.chars)&&v.chars.length?v:null; if(UID_SHOW) UID_SHOW.chars.forEach(uidEff); }
function uidSave(uid,chars){ chars.forEach(uidEff); UID_SHOW={uid,date:today(),chars}; UID_THUMB={}; store.set('uidShow',UID_SHOW); }
function uidFind(id){ return UID_SHOW&&UID_SHOW.chars.find(c=>c.id===id)||null; }
function uidSorted(){ const v=c=>{ const a=charStats(c).age||0; return isFinite(a)?a:1e15; }; return (UID_SHOW?UID_SHOW.chars:[]).slice().sort((a,b)=>v(b)-v(a)); }
// 有効OPがどこかで直されたら（effPut から呼ばれる）、同じ「名前＋セット」のUIDのカードにも効かせる
function effPutMore(k,eff){ if(!UID_SHOW) return; let ch=false; for(const c of UID_SHOW.chars) if(effKeyOf(c)===k){ c.eff=eff.slice(); delete c.effGuess; delete UID_THUMB[c.id]; ch=true; } if(ch){ store.set('uidShow',UID_SHOW); if(CARD_PAGE==='home') uidRender(); } }
/* ---- ホームの並び ---- */
function uidRender(){ const box=$('homeShow'); if(!box) return; const cs=uidSorted(); if(!cs.length){ box.innerHTML=''; return; } const best=cs[0];
  box.innerHTML=`<section class="ushow"><div class="ushow-h"><div><h2>あなたのショーケース</h2><p class="note">UID ${esc(UID_SHOW.uid||'—')}・${esc(UID_SHOW.date||'')} に取り込み・${cs.length}人。カードを押すと、保存・共有・有効OP・立ち絵の調整ができます</p></div>
    <div class="btns"><button class="btn" type="button" data-ure>演出をもう一度</button><button class="btn" type="button" data-uzip>全員をまとめて保存</button></div></div><p class="note" data-umsg aria-live="polite"></p>
    <div class="rv-lg">${cs.map(c=>{ const st=charStats(c), rk=rvRank(st.age||0); return `<button class="rv-lc${c===best?' best':''}" type="button" data-uid="${esc(c.id)}"><span class="th"></span><span class="m"><b>${esc(c.name||'')}</b>${c===best?'<i>いちばん</i>':''}<span class="st${rk.myth?' myth':''}" style="color:${rk.col}">${'★'.repeat(rk.stars)}${rk.plus?'+':''}</span><span class="a">${esc(fmtAge(st.age||0))}</span></span></button>`; }).join('')}</div></section>`;
  box.querySelectorAll('[data-uid]').forEach(el=>el.addEventListener('click',()=>uidOpen(el.dataset.uid)));
  box.querySelector('[data-ure]').addEventListener('click',()=>uidReveal(true));
  box.querySelector('[data-uzip]').addEventListener('click',e=>uidZip(e.currentTarget,box.querySelector('[data-umsg]')));
  uidThumbs(); }
// 小さなカードの絵：作ったものは覚えておき、まだのものを1枚ずつ作って並びに差し込む
function uidFill(){ const box=$('homeShow'); if(!box) return; box.querySelectorAll('[data-uid]').forEach(el=>{ const th=el.querySelector('.th'), t=UID_THUMB[el.dataset.uid]; if(th&&t&&!th.firstChild){ const c=rvCanvas(490,276); c.getContext('2d').drawImage(t,0,0,490,276); th.appendChild(c); } }); }
async function uidThumbs(){ uidFill(); if(UID_THUMB_BUSY) return; UID_THUMB_BUSY=true;
  try{ for(;;){ const c=uidSorted().find(x=>!UID_THUMB[x.id]); if(!c) break; UID_THUMB[c.id]=rvScaled(await rvCardImg(c),980,551); uidFill(); } } finally{ UID_THUMB_BUSY=false; } }
// 取り込んだあと（again＝ホームの「演出をもう一度」）：ホームに並べて、演出を重ねる。演出のあと、広がったカードがホームの並びに着地する
function uidReveal(again){ if(!UID_SHOW) return; cardShowPage('home'); const m=$('homeMsg'); if(m&&!again) m.textContent=HOME_NOTE||'';
  if(!again&&store.get('revealOff',0)){ const s=$('homeShow'); if(s) s.scrollIntoView({block:'start'}); return; }
  revealPlay(UID_SHOW.chars,{toHome:true}); }
/* ---- カード1枚を大きく開く：保存・共有・有効OP・立ち絵（選ぶ・大きさ・ドラッグで位置） ---- */
function uidOpen(id){ if(!uidFind(id)) return; uidClose(true); const ov=cardEl('div',{class:'uv-ov',role:'dialog','aria-modal':'true'});
  document.body.appendChild(ov); UV={ov,id,ovf:document.body.style.overflow}; document.body.style.overflow='hidden';
  UV.key=e=>{ if(e.key==='Escape') uidClose(); }; document.addEventListener('keydown',UV.key); ov.addEventListener('click',e=>{ if(e.target===ov) uidClose(); }); uidDraw(); }
function uidClose(quiet){ if(!UV) return; UV.ov.remove(); document.body.style.overflow=UV.ovf; document.removeEventListener('keydown',UV.key); UV=null; if(!quiet) uidRender(); }
function uidDraw(){ if(!UV) return; const c=uidFind(UV.id); if(!c) return uidClose(); const id=c.id; applyBundled(c);
  if(CARD_IMG[id]&&!(id in CARD_FIT)){ if(!CARD_FITTING[id]){ CARD_FITTING[id]=1; fitCardArt(CARD_IMG[id],CARD_ZOOM[id]).then(u=>{ delete CARD_FITTING[id]; CARD_FIT[id]=u||''; uidDraw(); }); } }
  const st=charStats(c), own=CARD_IMG[id]&&!/^portraits\//.test(CARD_IMG[id]), sk=setKeyOf(c.set), keep=UV.ov.querySelector('[data-umsg2]'), msgText=keep?keep.innerHTML:'';
  UV.ov.innerHTML=`<div class="uv-box"><div class="uv-h"><div><b>${esc(c.name||'')}</b>${sk?`<span class="note">${esc(sk)}</span>`:''}</div><button class="rv-x" type="button" data-ux aria-label="閉じる">×</button></div>
    <div class="uv-card">${rvUniq(cardSVG(c,st,'SK'))}</div>
    <div class="btns"><button class="btn primary" type="button" data-ush>共有</button><button class="btn" type="button" data-upng>PNGで保存</button><button class="btn" type="button" data-uwebp>WebP</button></div><p class="note" data-umsg2 aria-live="polite">${msgText}</p>
    <div class="uv-sec"><h3>有効OP</h3><p class="note">${c.effGuess?'<b class="err">推定</b>：装備から見立てたものです。':''}同じ名前・同じセットのキャラ（キャラ一覧・ラボも）に、まとめて効きます。</p>
      <div class="checks">${effOptsFor(c).map(s2=>`<label class="chk"><input type="checkbox" data-ue="${s2}" ${c.eff.includes(s2)?'checked':''}><span>${effChip(s2)}</span></label>`).join('')}</div>${c.effGuess?'<button class="btn" type="button" data-ueok style="margin-top:6px">これでよい</button>':''}</div>
    <div class="uv-sec"><h3>立ち絵</h3><div class="btns"><label class="btn" style="cursor:pointer">立ち絵を選ぶ<input type="file" accept="image/*" hidden data-uart></label>${CARD_IMG[id]?`<label class="row" style="gap:6px;font-size:12px;color:var(--muted)">大きさ<input type="range" min="60" max="170" step="5" value="${CARD_ZOOM[id]||100}" data-uzoom style="width:120px"></label>`:''}${own?'<button class="btn" type="button" data-uartdel>立ち絵を外す</button>':''}</div>
      <p class="note">${CARD_IMG[id]?'絵はドラッグで動かせます（ダブルクリックで元の位置）。':''}UIDのカードの立ち絵は、キャラ一覧のカードとは別に保存されます。</p></div></div>`;
  const q=k=>UV.ov.querySelector(k), msg=q('[data-umsg2]'), changed=()=>{ delete UID_THUMB[id]; };
  q('[data-ux]').addEventListener('click',()=>uidClose());
  q('[data-ush]').addEventListener('click',()=>cardShareWith(c,()=>uidBlob(c,'png'),msg));
  q('[data-upng]').addEventListener('click',()=>uidSaveOne(c,'png',msg)); q('[data-uwebp]').addEventListener('click',()=>uidSaveOne(c,'webp',msg));
  UV.ov.querySelectorAll('[data-ue]').forEach(el=>el.addEventListener('change',()=>{ const s2=el.dataset.ue; c.eff=el.checked?SUBS.filter(x=>x===s2||c.eff.includes(x)):c.eff.filter(x=>x!==s2); delete c.effGuess; effPut(c); saveChars(); changed(); store.set('uidShow',UID_SHOW); uidDraw(); }));
  { const ok=q('[data-ueok]'); if(ok) ok.addEventListener('click',()=>{ delete c.effGuess; effPut(c); store.set('uidShow',UID_SHOW); uidDraw(); }); }
  q('[data-uart]').addEventListener('change',e=>{ const f=e.target.files[0]; e.target.value=''; if(!f) return; const rd=new FileReader(); rd.onload=async()=>{ const src=await portraitShrink(rd.result); CARD_IMG[id]=src; delete CARD_FIT[id]; delete CARD_POS[id]; delete CARD_ZOOM[id]; portraitSave(id); changed(); uidDraw(); }; rd.readAsDataURL(f); });
  { const z=q('[data-uzoom]'); if(z) z.addEventListener('change',()=>{ const src=CARD_IMG[id]; if(!src) return; CARD_ZOOM[id]=+z.value; portraitSave(id); fitCardArt(src,CARD_ZOOM[id]).then(u=>{ if(CARD_IMG[id]===src){ CARD_FIT[id]=u||''; changed(); uidDraw(); } }); }); }
  { const d=q('[data-uartdel]'); if(d) d.addEventListener('click',async()=>{ await portraitDelete(id); changed(); uidDraw(); }); }
  // ドラッグで立ち絵の位置を動かす（カードの座標で dx・dy を覚える）
  const svg=q('.uv-card svg'), img=svg&&svg.querySelector('image[data-bx]');
  if(img){ const bx=+img.dataset.bx, by=+img.dataset.by; let drag=null; svg.style.cursor='grab'; svg.style.touchAction='none';
    svg.addEventListener('pointerdown',e=>{ const p=CARD_POS[id]||{dx:0,dy:0}; drag={x:e.clientX,y:e.clientY,dx:p.dx,dy:p.dy,k:1200/svg.getBoundingClientRect().width}; svg.setPointerCapture(e.pointerId); svg.style.cursor='grabbing'; });
    svg.addEventListener('pointermove',e=>{ if(!drag) return; const dx=drag.dx+(e.clientX-drag.x)*drag.k, dy=drag.dy+(e.clientY-drag.y)*drag.k; img.setAttribute('x',bx+dx); img.setAttribute('y',by+dy); drag.nx=dx; drag.ny=dy; });
    const end=()=>{ if(drag&&drag.nx!=null){ CARD_POS[id]={dx:drag.nx,dy:drag.ny}; portraitSave(id); changed(); } drag=null; svg.style.cursor='grab'; };
    svg.addEventListener('pointerup',end); svg.addEventListener('pointercancel',end);
    svg.addEventListener('dblclick',()=>{ CARD_POS[id]={dx:0,dy:0}; portraitSave(id); changed(); uidDraw(); }); } }
/* ---- 保存：1枚（PNG・WebP、2400×1350）と、全員をZIPで ---- */
async function uidBlob(c,fmt){ const cv=await rvCardImg(c,2400,1350); if(!cv) return null; const type=fmt==='webp'?'image/webp':'image/png';
  let blob=await new Promise(r=>cv.toBlob(r,type,.95)), ext=fmt; if(!blob||blob.type!==type){ blob=await new Promise(r=>cv.toBlob(r,'image/png')); ext='png'; }
  const d=new Date(), ds=`${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}`;
  return {blob,ext,name:`命ノ星座_${(c.name||'card').replace(/[\\/:*?"<>|]/g,'')}_${ds}.${ext}`}; }
async function uidSaveOne(c,fmt,msg){ msg.textContent='画像を作っています…'; const r=await uidBlob(c,fmt); if(!r){ msg.textContent='画像を作れませんでした'; return; }
  const res=await saveBlob(r.name,r.blob); msg.textContent=res==='saved'?`${r.ext.toUpperCase()}で保存しました（2400×1350）${r.ext!==fmt?'。このブラウザはWebPを書き出せないのでPNGにしました':''}`:res==='declined'?'保存を取りやめました':'保存できませんでした'; }
async function uidZip(btn,msg){ const cs=uidSorted(); if(!cs.length) return; const say=t=>{ if(msg) msg.textContent=t; }; btn.disabled=true; const files=[];
  try{ for(let i=0;i<cs.length;i++){ say(`${i+1}/${cs.length}人目（${cs[i].name||''}）を描いています…`); const r=await uidBlob(cs[i],'png'); if(!r) throw new Error('image'); files.push({name:`${String(i+1).padStart(2,'0')}_${r.name}`,data:new Uint8Array(await r.blob.arrayBuffer())}); }
    const d=new Date(), ds=`${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}`; say('ZIPにまとめています…');
    const res=await saveBlob(`命ノ星座_UID_${cs.length}人_${ds}.zip`,zipStore(files)); say(res==='saved'?`${cs.length}人ぶんのカード（PNG・2400×1350）をZIPで保存しました`:res==='declined'?'保存を取りやめました':'この画面ではZIPを保存できません。カードを押して1枚ずつ保存してください'); }
  catch(e){ say('画像を作れませんでした。カードを押して1枚ずつ保存してください'); } finally{ btn.disabled=false; } }
/* ================= カードの登場の演出（v2.1）：落ちるカード =================
   思想：お気に入りのキャラのカードが、自分のものとして形になる瞬間を祝う。全員を同じ儀式で迎え、ランクの差は色と★の数で静かに見せる。
         いちばんのカードだけ、溜めを少し長く、光を少し強く。見せ場は縦動画（SNS）。アプリの中ではスキップされる前提
   流れ：夜空を映した漆の机に、厚みのあるカードが1枚ずつ落ちてくる（影が先に近づき、着地で光の風圧が星屑を押し流し、表が灯る）。
         最後の1枚の前は「最後の1枚」・星屑の吸い込み・光の鼓動・スポットライト・天板に灯る星座で溜める。押すと、重なったカードが一覧へ広がる
   描き方：1080×1920 のキャンバスに、時刻 t（ミリ秒）だけから1コマを描く（rvDraw）。スキップは最後の時刻に飛ぶだけ。縦動画の書き出しも同じ関数でコマを作る
   見本で流す：URLの末尾に #reveal を付けて開くと、見本のキャラで流す操作盤が出る（作り手の確認用。保存はしない） */
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
async function rvCardImg(c,W,H){ W=W||1960; H=H||1102; applyBundled(c); if(CARD_IMG[c.id]&&!(c.id in CARD_FIT)){ const u=await fitCardArt(CARD_IMG[c.id],CARD_ZOOM[c.id]); CARD_FIT[c.id]=u||''; }
  const NS='http://www.w3.org/2000/svg', box=document.createElement('div'); box.innerHTML=cardSVG(c,charStats(c),'SK'); const el=box.querySelector('svg'); if(!el) return null;
  el.setAttribute('xmlns',NS); el.setAttribute('xmlns:xlink','http://www.w3.org/1999/xlink'); el.setAttribute('width',W); el.setAttribute('height',H); el.removeAttribute('style'); await svgInlineImages(el);
  try{ const css=await cardFontCSS([...new Set([...el.textContent].map(ch=>ch.codePointAt(0)))]); const st=document.createElementNS(NS,'style'); st.textContent=css; el.insertBefore(st,el.firstChild); }catch(e){}
  const url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(el)],{type:'image/svg+xml'}));
  try{ const im=new Image(); await new Promise((res,rej)=>{ im.onload=res; im.onerror=rej; im.src=url; }); try{ await im.decode(); }catch(e){} await new Promise(r=>setTimeout(r,200));
    const cv=rvCanvas(W,H); cv.getContext('2d').drawImage(im,0,0,W,H); return cv; }catch(e){ return null; } finally{ URL.revokeObjectURL(url); } }
function rvScaled(src,w,h){ const o=rvCanvas(w,h); if(src) o.getContext('2d').drawImage(src,0,0,w,h); return o; }
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
const RV_T={lead:250,pre:430,preBest:2000,fall:230,read:1050,after:1900};
// テンポ：いちばんのカードの直前の1枚までは、同じ駆け足で → 直前の1枚だけ少し落とす（溜めにつなぐ）。sp＝時間の倍率
function rvTempo(k,m){ if(m<=1) return 1; return k===m-1?.7:.34; }
// カードの絵から、描くのに使う絵（縮小・映り込み）を作る。絵ができたカードから順に ready になる
function rvPrep(it){ it.img1=rvScaled(it.img,it.W,it.H); it.refl=rvReflection(it.img1,it.W,it.H); it.ready=true; }
function rvPlan(items,mode){ const T=RV_T, n=items.length, A=rvAssets(), ev=[]; let t=T.lead;
  items.forEach((it,k)=>{ const best=k===n-1; it.best=best; it.t0=t; it.dir=rvRnd(k,7)<.5?-1:1; it.W=980; it.H=551;
    it.rest=best?{x:RV_CX,y:RV_CY,rot:0}:{x:RV_CX+(rvRnd(k,8)-.5)*90,y:RV_CY+(rvRnd(k,9)-.5)*70,rot:(rvRnd(k,10)-.5)*.24};
    const sp=it.sp=best?1:rvTempo(k,n-1); it.drop=t+(best?T.preBest:T.pre*sp); it.fall=best?T.fall:Math.max(140,T.fall*Math.sqrt(sp)); it.land=it.drop+it.fall; it.infoIn=it.land+220*sp; it.starAt=it.infoIn+260*sp; t=it.land+T.read*sp;
    ev.push({t0:it.land,x:it.rest.x,y:it.rest.y,rot:it.rest.rot,w:it.W,h:it.H,col:it.rk.myth?'#efe6ff':it.rk.col,str:.72*(best?1.4:1),rings:best?[[0,1],[220,.6]]:[[0,1]]}); });
  items.forEach((it,k)=>{ it.nx=k<n-1?items[k+1].t0:0; });
  const b=items[n-1], E=b.land+T.after; return {mode,items,events:ev,A,E,total:E+1500}; }
/* ---- 1コマを描く ---- */
function rvDraw(x,P,t){ const A=P.A; x.setTransform(1,0,0,1,0,0); x.globalCompositeOperation='source-over'; x.globalAlpha=1; x.drawImage(A.desk,0,0);
  // 光の風圧：輪が広がり、机の星屑を押し流す
  const evs=P.events.filter(e=>t>e.t0), RR=(e,dt)=>e.str*430*(1-Math.exp(-dt/380)); // 輪はカードの縁から外へ、机の上に収まる大きさまで
  // 落ちるカード：いちばんのカードを待つあいだ、星屑が落ちる場所へだんだん速く吸い寄せられる（着地の風圧で一気に外へ）
  const bb=P.items[P.items.length-1], suck=P.items.length>1&&t>=bb.t0?(t<bb.land?Math.pow(rvCl((t-bb.t0)/(bb.drop-bb.t0)),2):Math.exp(-(t-bb.land)/90)):0;
  for(const d of A.dust){ let dx=0,dy=0,b=0; if(suck>0.002){ const vx=bb.rest.x-d.x, vy=bb.rest.y-d.y, dd=Math.hypot(vx,vy)||1, m=Math.min(dd*.55,260)*suck; dx+=vx/dd*m; dy+=vy/dd*m; b+=suck*.7; } for(const e of evs){ const dt=t-e.t0, R=RR(e,dt), vx=d.x-e.x, vy=d.y-e.y, dd=Math.hypot(vx,vy)||1, ex=Math.max(0,dd-Math.max(e.w,e.h)*.42);
      if(R>ex){ const m=e.str*150*Math.exp(-ex/650)*rvCl((R-ex)/240); dx+=vx/dd*m; dy+=vy/dd*m; } b+=Math.exp(-Math.pow((R-ex)/80,2))*e.str*Math.max(0,1-dt/1800); }
    x.globalAlpha=Math.min(1,d.a*(.72+.28*Math.sin(t*.0016+d.ph))+b*.7); x.fillStyle=d.col; x.beginPath(); x.arc(d.x+dx,d.y+dy,d.r*(1+b),0,6.283); x.fill(); }
  x.globalAlpha=1;
  for(const e of evs) for(const [dl,k] of e.rings){ const dt=t-e.t0-dl; if(dt<0||dt>1400) continue; const R=RR(e,dt), al=Math.pow(1-dt/1400,2)*Math.pow(1-R/(e.str*430+1),1.2)*Math.min(1,e.str*1.2)*k; // 広がるほど薄く
    x.save(); x.translate(e.x,e.y); x.rotate(e.rot); x.strokeStyle=e.col; for(const [lw,a] of [[36,.08],[14,.16],[3,.3]]){ x.globalAlpha=al*a; x.lineWidth=lw; rvRR(x,-e.w/2-R,-e.h/2-R,e.w+2*R,e.h+2*R,12+R*.9); x.stroke(); } x.restore(); }
  x.globalAlpha=1;
  if(!P.noCards){ rvDrawPile(x,P,t); rvDrawSpot(x,P,t); rvDrawSeal(x,P,t); }
  rvDrawInfo(x,P,t); rvDrawFrame(x,P,t); } // noCards：一覧へ広げるとき、カードは上に重ねた一覧に任せて、机と文字だけを描く（机ごとゆっくり消える）
// いちばんのカードの溜め。見てほしいのは「これから降りてくる場所」
//   A スポットライト：落ちる場所に真上から光の輪が差し、まわりが少し沈む
//   B 天板に灯る星座：落ちる場所に、そのカードの星座（5部位の星。★の数ではない）が、鼓動に合わせて1つずつ灯り、線でつながる。カードの星座とぴたりと重なって着地し、着地で外へはじける
function rvPreQ(P,t){ const b=P.items[P.items.length-1]; if(t<b.t0) return null; return {b,q:rvCl((t-b.t0)/(b.drop-b.t0)),u:t<b.land?-1:(t-b.land)/550}; }
function rvDrawSpot(x,P,t){ const Q=rvPreQ(P,t); if(!Q||Q.u>1) return; const {b,q,u}=Q, e=q*q*(3-2*q), f=(u<0?e:1-u)*(P.items.length>1?1:.8), cx=b.rest.x, cy=b.rest.y;
  x.save(); x.translate(cx,cy); x.scale(1.3,1); let g=x.createRadialGradient(0,0,300,0,0,860); g.addColorStop(0,'rgba(2,3,10,0)'); g.addColorStop(1,`rgba(2,3,10,${.72*f})`); x.fillStyle=g; x.fillRect(-RVW,-RVH,RVW*2,RVH*2); // まわりが沈む
  x.globalCompositeOperation='lighter'; g=x.createRadialGradient(0,0,0,0,0,500); g.addColorStop(0,`rgba(255,240,212,${.2*f})`); g.addColorStop(.6,`rgba(255,240,212,${.09*f})`); g.addColorStop(1,'rgba(255,240,212,0)'); x.fillStyle=g; x.fillRect(-500,-500,1000,1000); x.restore(); } // 真上からの光
function rvStarsOf(st){ const cx0=360, cy0=361, R0=58, R=246, BND=[1,7,30,90,365,1095,10950], ANG={flower:-90,plume:-18,sands:54,goblet:126,circlet:198}; // カードの星座と同じ計算（中心・半径・部位の向き・ランクの帯ごとの目盛り）
  const rad=d=>{ if(!(d>1)) return R0; if(d>=10950) return R; let k=0; while(k<5&&d>=BND[k+1]) k++; return R0+(k+(Math.log(d)-Math.log(BND[k]))/(Math.log(BND[k+1])-Math.log(BND[k])))/6*(R-R0); };
  return SLOTS.map(s=>{ const d=st.slots[s].age, r=rad(isFinite(d)?d:1e9), a=ANG[s]*Math.PI/180; return {s,has:d>0,x:cx0+r*Math.cos(a),y:cy0+r*Math.sin(a)}; }); }
function rvDrawSeal(x,P,t){ const Q=rvPreQ(P,t); if(!Q||Q.u>1) return; const {b,q,u}=Q, S=b.stars||(b.stars=rvStarsOf(b.st)), on=S.filter(p=>p.has), kx=b.W/1200, ky=b.H/675;
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
function rvPose(P,it,t){ const r=it.rest;
  // 落ちるカード：はじめはカメラより上にあって画面に映らず、影だけが机に落ちて近づいてくる（h：1.6→0.5）。最後に一気に落ちる（0.5→0）
  const pre=t<it.drop; let h; if(pre){ const q=rvCl((t-it.t0)/(it.drop-it.t0)); h=1.6-1.1*q*q*(3-2*q); } else { const p=rvCl((t-it.drop)/it.fall); h=.5*(1-p*p); }
    let s=1+h*.85; const dl=t-it.land; if(dl>0&&dl<200) s*=1-.012*Math.sin(Math.PI*dl/200);
  return {x:r.x+h*it.dir*70,y:r.y-h*150,rot:r.rot+h*it.dir*.16,s,sy:1-Math.min(h,.6)*.3,h,a:pre?0:1,sa:rvCl((t-it.t0)/300),edge:5+Math.min(h,.6)*30}; }
function rvCardDraw(x,it,ps,dim,lit){ const W=it.W, H=it.H; x.save(); x.globalAlpha*=ps.a; x.translate(ps.x,ps.y); x.rotate(ps.rot); x.scale(ps.s,ps.s*ps.sy);
  { const e=ps.edge, g=x.createLinearGradient(0,H/2-6,0,H/2+e); g.addColorStop(0,'#d8bb72'); g.addColorStop(.45,'#8a6c34'); g.addColorStop(1,'#33270f'); x.fillStyle=g; rvRR(x,-W/2+1,-H/2+e,W-2,H,12); x.fill(); } // 厚み：金の小口
  x.save(); rvRR(x,-W/2,-H/2,W,H,12); x.clip();
  const im=ps.s*ps.sy<=1.05?it.img1:(it.img||it.img1);
  if(im) x.drawImage(im,-W/2,-H/2,W,H); else { x.fillStyle='#0b0e22'; x.fillRect(-W/2,-H/2,W,H); } // 絵がまだできていないカード（確認用に先の時刻を描いたときだけ）
  if(lit!=null&&lit<1){ const W2=W*1.15, D='rgba(6,8,22,.72)'; if(lit<=0) x.fillStyle=D; else { const g=x.createRadialGradient(0,0,lit*W2,0,0,lit*W2+300); g.addColorStop(0,'rgba(6,8,22,0)'); g.addColorStop(1,D); x.fillStyle=g; } x.fillRect(-W/2,-H/2,W,H); } // 落ちてくるあいだは逆光で暗く、着地で中央から灯る
  x.restore(); if(dim>0){ x.fillStyle=`rgba(2,3,10,${dim})`; rvRR(x,-W/2,-H/2,W,H,12); x.fill(); } // 下になったカードは沈める
  if(lit!=null&&lit<1){ const ra=1-rvCl(lit*1.6); x.save(); x.globalAlpha*=ra; x.strokeStyle='#f3dc9e'; x.shadowColor='#f5dfa6'; x.shadowBlur=18; x.lineWidth=3/ps.s; rvRR(x,-W/2,-H/2,W,H,12); x.stroke(); x.globalAlpha*=.5; x.lineWidth=1.2/ps.s; rvRR(x,-W/2+10,-H/2+10,W-20,H-20,8); x.stroke(); x.restore(); } // 逆光の縁：暗くても「カード」と分かるように
  x.restore(); }
function rvShadowDraw(x,A,it,ps){ const w=it.W, h=it.H, S=rvShadowOf(A,w,h), sc=1+ps.h*.22;
  x.save(); x.translate(ps.x+8+ps.h*60,ps.y+14+ps.h*110); x.rotate(ps.rot); x.scale(sc,sc*ps.sy); x.globalAlpha=ps.sa!=null?ps.sa:ps.a;
  rvSprite(x,S.hard,w,h,Math.max(0,1-ps.h)*.5); rvSprite(x,S.soft,w,h,Math.min(.34,.08+(1.6-ps.h)*.24)); x.restore(); } // 影：遠いほど薄くぼやけ、近づくほど濃くくっきり
function rvGlowDraw(x,A,it,ps,a){ if(a<=0) return; const w=it.W, h=it.H, G=rvGlowOf(A,w,h,it.rk);
  x.save(); x.translate(ps.x,ps.y); x.rotate(ps.rot); x.scale(ps.s,ps.s*ps.sy); rvSprite(x,G,w,h,a*(it.rk.myth?.55:1),'lighter'); x.restore(); } // 虹の光は重ねて明るいので弱める
function rvDrawPile(x,P,t){ const its=P.items, b=its[its.length-1], spot=its.length>1?(.2*rvCl((t-b.t0)/450)+.38*(q=>q*q*(3-2*q))(rvCl((t-b.t0)/(b.drop-b.t0))))*(1-rvCl((t-b.land)/600)):0; // いちばんのカードを待つあいだ、机のカードをだんだん深く沈める（下のカードの星座が、天板に灯る星座と二重に見えないように）
  // いちばんのカードを待つあいだ、落ちる場所の机からランク色の光が漏れてくる（机のカードの下から、縁にだけ見える）
  if(t>=b.t0&&t<b.land){ const q=rvCl((t-b.t0)/(b.drop-b.t0)), hb=q*.5+.38*Math.exp(-Math.pow((q-.4)/.07,2))+.5*Math.exp(-Math.pow((q-.72)/.07,2))+(q>.84?(q-.84)/.16*.45:0); rvGlowDraw(x,P.A,b,{x:b.rest.x,y:b.rest.y,rot:0,s:1.04,sy:1},Math.min(1,hb)*.95); } // 光はドクン、ドクンと2回脈打ってから最大に
  // 映り込み：天板に映ったカード。カードが高いほど縁から離れて薄く、着地で縁にぴたりと合う（上に重なったカードに隠れる分は見えない）
  its.forEach(it=>{ if(t<it.t0||!it.refl) return; const ps=rvPose(P,it,t); if(ps.a<=0) return; const gap=ps.h*240, a=ps.a*(1-Math.min(1,ps.h)*.6);
    x.save(); x.globalAlpha=a; x.translate(ps.x,ps.y); x.rotate(ps.rot); x.scale(ps.s,ps.s*ps.sy); x.drawImage(it.refl,-it.W/2,it.H/2+4+gap/ps.s,it.W,it.refl.height); x.restore(); });
  its.forEach((it,k)=>{ if(t<it.t0) return; const ps=rvPose(P,it,t); let dim=0; for(let j=k+1;j<its.length;j++) if(t>its[j].land) dim+=.34*rvCl((t-its[j].land)/380); dim=Math.min(.6,dim+(it.best?0:spot));
    rvShadowDraw(x,P.A,it,ps);
    // 光：いちばんのカードは溜めのあいだ強まり、着地で強く光って、そのまま残る。ほかのカードは着地で一度だけ
    const dl=t-it.land; let ga=0; if(it.best){ ga=t<it.drop?rvCl((t-it.t0)/(it.drop-it.t0))*.85:dl<0?.85:.45+.55*Math.exp(-dl/500); } else if(dl>0) ga=.42*Math.exp(-dl/420)*(1-dim);
    if(!(it.best&&dl<0)) rvGlowDraw(x,P.A,it,ps,ga*ps.a);
    if(ps.a>0) rvCardDraw(x,it,ps,dim,dl<0?0:rvCl(dl/520)); }); }
/* ---- 名前・★・秘境レベル（カードの下） ---- */
function rvLS(x,v){ if('letterSpacing' in x) x.letterSpacing=v; }
function rvStarPath(x,R){ x.beginPath(); for(let i=0;i<10;i++){ const a=-Math.PI/2+i*Math.PI/5, r=i%2?R*.44:R; x.lineTo(Math.cos(a)*r,Math.sin(a)*r); } x.closePath(); }
function rvDrawStars(x,it,t,cy){ const rk=it.rk, n=rk.stars, tot=n+(rk.plus?1:0); if(!tot) return; const R=27, gap=70, x0=RV_CX-(tot-1)*gap/2;
  for(let k=0;k<tot;k++){ const sp=it.sp||1, tk=it.starAt+k*105*sp, p=(t-tk)/(260*Math.sqrt(sp)); if(p<=0) continue; const q=rvCl(p), sc=rvOB(q), col=rk.myth?RV_RB[k%5]:rk.col;
    x.save(); x.globalAlpha*=rvCl(q*2.2); x.translate(x0+k*gap,cy); x.scale(sc,sc); x.fillStyle=col; x.shadowColor=col; x.shadowBlur=it.best?22:14;
    if(k<n){ rvStarPath(x,R); x.fill(); } else { const b=R*.2, l=R*.72; rvRR(x,-l,-b,l*2,b*2,b); x.fill(); rvRR(x,-b,-l,b*2,l*2,b); x.fill(); } // ★5+ の「＋」
    x.restore(); } }
function rvDrawInfo(x,P,t){ for(const it of P.items){ const sp=it.sp||1, a=rvCl((t-it.infoIn)/(420*sp))*(it.nx?1-rvCl((t-it.nx)/(200*Math.min(1,sp*1.6))):1); if(a<=0) continue;
    const up=(1-rvOC(rvCl((t-it.infoIn)/(560*sp))))*16, st=it.st, mm=fmtAge(st.age||0).match(/^([\d.,]+[KMB]?)\s*(.*)$/);
    x.save(); x.globalAlpha=a; x.textAlign='center'; x.textBaseline='alphabetic';
    x.font=`700 68px ${RV_MINCHO}`; rvLS(x,'6px'); const nm=it.c.name||'（名前なし）';
    x.fillStyle='#f4ecd6'; x.shadowColor='rgba(0,0,0,.6)'; x.shadowBlur=12; x.fillText(nm,RV_CX,1240+up); x.shadowBlur=0;
    rvDrawStars(x,it,t,1334+up);
    const la=1; x.globalAlpha=a*la; x.font=`400 22px ${RV_SANS}`; rvLS(x,'8px'); x.fillStyle='#8f8a7c'; x.fillText('秘境レベル',RV_CX,1428+up);
    // 数字は大きく、単位は小さく。2つを並べて中央に
    const num=mm?mm[1]:fmtAge(st.age||0), unit=mm?mm[2]:''; x.font=`400 70px ${RV_SANS}`; rvLS(x,'1px'); const w1=x.measureText(num).width; x.font=`400 28px ${RV_SANS}`; rvLS(x,'5px'); const w2=unit?x.measureText(unit).width+12:0, x1=RV_CX-(w1+w2)/2;
    x.textAlign='left'; x.globalAlpha=a;
    x.font=`400 70px ${RV_SANS}`; rvLS(x,'1px'); x.fillStyle='#f6efdc'; x.fillText(num,x1,1508+up);
    if(unit){ x.globalAlpha=a*la; x.font=`400 28px ${RV_SANS}`; rvLS(x,'5px'); x.fillStyle='#c9c1ad'; x.fillText(unit,x1+w1+12,1508+up); }
    if(it.rk.myth){ x.textAlign='center'; x.font=`700 22px ${RV_SANS}`; rvLS(x,'7px'); const g=x.createLinearGradient(RV_CX-220,0,RV_CX+220,0); RV_RB.slice(0,5).forEach((c,i)=>g.addColorStop(i/4,c)); x.fillStyle=g; x.globalAlpha=a*la; x.fillText(it.rk.dawn?'SINCE THE DAWN OF TIME':'ONCE IN A CENTURY',RV_CX,1562+up); }
    rvLS(x,'0px'); x.restore(); } }
function rvDrawFrame(x,P,t){ x.save(); x.textAlign='center'; x.globalAlpha=rvCl(t/500)*.85; x.font=`700 30px ${RV_MINCHO}`; rvLS(x,'12px'); x.fillStyle='#e9d39a'; x.fillText('命ノ星座カード',RV_CX,150);
  if(P.mode==='all'&&P.items.length>1){ let k=0; P.items.forEach((it,i)=>{ if(t>=it.t0) k=i; }); x.globalAlpha=rvCl(t/500)*.55; x.font=`400 22px ${RV_SANS}`; rvLS(x,'4px'); x.fillStyle='#b9b2a3'; x.fillText(`${k+1} / ${P.items.length}`,RV_CX,200); }
  // いちばんのカードの前に「最後の1枚」と出す（何を待っているのかが分かるように）
  { const b=P.items[P.items.length-1]; if(P.items.length>1&&t>=b.t0&&t<b.drop){ x.globalAlpha=rvCl((t-b.t0-220)/380)*(1-rvCl((t-b.drop+200)/200))*.9; x.font=`700 40px ${RV_MINCHO}`; rvLS(x,'14px'); x.fillStyle='#e9d39a'; x.fillText('最後の1枚',RV_CX,1240); } }
  const fa=rvCl((t-P.E)/650); if(fa>0){ x.globalAlpha=fa; x.font=`700 30px ${RV_SANS}`; rvLS(x,'4px'); x.fillStyle='#e9d39a'; x.fillText('#命ノ星座カード',RV_CX,1760); x.globalAlpha=fa*.7; x.font=`400 24px ${RV_SANS}`; rvLS(x,'1px'); x.fillStyle='#b9b2a3'; x.fillText(SITE_URL.replace(/^https:\/\//,'').replace(/\/$/,''),RV_CX,1812); }
  rvLS(x,'0px'); x.restore(); }
/* ---- 流す ---- */
function rvClose(){ const R=window.RV; if(!R) return; R.dead=true; clearTimeout(R.lt); R.ov.remove(); document.body.style.overflow=R.ovf; document.removeEventListener('keydown',R.key); window.RV=null; if(R.onClose) R.onClose(); }
async function revealPlay(cs,opt){ opt=opt||{}; if(window.RV) rvClose(); if(!cs.length) return; const mode=opt.mode==='one'?'one':'all';
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
  const fonts=Promise.all([document.fonts.load(`700 68px ${RV_MINCHO}`,list.map(c=>c.name||'').join('')+'命ノ星座カード（名前なし）'),document.fonts.load(`400 70px ${RV_SANS}`,'0123456789.,秘境レベルDAYSWEKMONTHYRAX'+RANK_NAME),document.fonts.load(`700 30px ${RV_SANS}`,'#命ノ星座カード')]).catch(()=>{});
  // カードの絵は、出てくる順に用意する（2枚ずつ並行）。最初の1枚ができたら流し始め、残りは流しながら用意する（間に合わないカードがあれば、そのカードの手前で時計を止めて待つ）
  const items=list.map(c=>{ const st=charStats(c); return {c,st,rk:rvRank(st.age||0),img:null,ready:false}; });
  const P=rvPlan(items,mode); R.P=P;
  let qi=0; const work=async()=>{ while(qi<items.length&&!R.dead){ const it=items[qi++]; it.img=await rvCardImg(it.c); rvPrep(it); } }, all=Promise.all([work(),work()]); R.ready=all; // 全員の絵ができたら解決（動画の書き出しは、これを待ってから）
  await Promise.race([Promise.all([fonts,new Promise(r=>{ const w=()=>items[0].ready||R.dead?r():setTimeout(w,30); w(); })]),new Promise(r=>setTimeout(r,4000))]); if(R.dead) return; R.drawAt=t=>{ R.hold=true; rvDraw(x,P,t); }; // drawAt：好きな時刻の1コマを描いて止める（確認・動画の書き出し用）
  R.items=items; R.opt=opt; R.cv=cv; R.bar=bar;
  bar.hidden=false; bar.innerHTML=`<span class="rv-hint">${items.length>1?'画面を押すと次のカードへ':'画面を押すと先へ'}</span>`;
  // 終わり：全員のときは、少し余韻をおいて一覧へ。1枚のときはボタンだけ
  const end=()=>{ if(R.ended) return; R.ended=true; skip.remove();
    if(items.length>1||opt.toHome){ bar.innerHTML=`<span class="rv-hint">${items.length>1?'画面を押すと、カードを広げます':'画面を押すと、ホームへ'}</span>`; return; }
    bar.innerHTML=(opt.replay?'<button class="btn" type="button" data-rvre>もう一度</button>':'')+`<button class="btn primary" type="button" data-rvok>${esc(opt.okLabel||'カードを見る')}</button>`;
    bar.querySelector('[data-rvok]').addEventListener('click',rvClose); const re=bar.querySelector('[data-rvre]'); if(re) re.addEventListener('click',opt.replay); bar.querySelector('[data-rvok]').focus(); };
  if(rvStill()||R.jump){ await all; if(R.dead) return; R.t=P.total; rvDraw(x,P,P.total); return end(); }
  const due=it=>it.drop-60; // そのカードの絵が要る時刻（表が見える少し前）
  R.off=0; R.paused=0; const t0=performance.now(); const step=now=>{ if(R.dead||R.hold) return; let t=Math.min(P.total,now-t0+R.off-R.paused);
    const need=P.items.find(it=>!it.ready&&t>=due(it)); if(need){ R.paused+=t-due(need); t=due(need); } // 絵が間に合っていなければ、ここで待つ
    if(R.jump&&P.items.every(it=>it.ready)) t=P.total; R.t=t; rvDraw(x,P,t); if(t>=P.total) return end(); requestAnimationFrame(step); }; requestAnimationFrame(step); }
// 次へ：いまのカードの続きを飛ばして、次のカードの始まりへ。いちばんのカードの溜め中なら落ちる瞬間へ、着地のあとなら締めへ
function rvNext(R){ const P=R.P, t=R.t||0, its=P.items, b=its[its.length-1], tg=[];
  its.forEach(it=>{ if(!it.best) tg.push(it.t0); }); tg.push(its.length>1?b.t0-300:b.t0); tg.push(b.drop); tg.push(P.E,P.total);
  const nx=tg.filter(v=>v>t+40).sort((p,q)=>p-q)[0]; if(nx!=null) R.off+=nx-t; }
/* 演出のあと：取り込んだ全員のカードを一覧で（秘境レベルの高い順。いちばんのカードは金の枠）。押すとそのカードのページへ */
function rvList(R){ if(R.opt&&R.opt.toHome) return rvToHome(R); if(R.list||R.dead||!R.P) return; R.list=true; clearTimeout(R.lt); const ov=R.ov, opt=R.opt||{}, P=R.P, ag=it=>{ const a=it.st.age||0; return isFinite(a)?a:1e15; };
  const its=R.items.slice().sort((p,q)=>ag(q)-ag(p)), best=its[0], still=rvStill();
  // 机（キャンバス）はいまの場所に留めて、カードだけを消す。その上に一覧を重ねる
  const r=R.cv.getBoundingClientRect(), k=r.width/RVW; Object.assign(R.cv.style,{position:'fixed',left:r.left+'px',top:r.top+'px',width:r.width+'px',height:r.height+'px',margin:'0'});
  R.bar.remove(); P.noCards=true; rvDraw(R.cv.getContext('2d'),P,P.total); ov.classList.add('rv-ovl'); ov.scrollTop=0;
  const box=cardEl('div',{class:'rv-list'+(still?'':' spread')}); box.innerHTML=`<div class="rv-lh"><h2>取り込んだカード<small>${its.length}人</small></h2><button class="rv-x" type="button" aria-label="閉じる">×</button></div>
    <div class="rv-lg">${its.map((it,i)=>`<button class="rv-lc${it===best?' best':''}" type="button" data-i="${i}"><span class="th"></span><span class="m"><b>${esc(it.c.name||'（名前なし）')}</b>${it===best?'<i>いちばん</i>':''}<span class="st${it.rk.myth?' myth':''}" style="color:${it.rk.col}">${'★'.repeat(it.rk.stars)}${it.rk.plus?'+':''}</span><span class="a">${esc(fmtAge(it.st.age||0))}</span></span></button>`).join('')}</div>
    <div class="rv-lf">${opt.replay?'<button class="btn" type="button" data-rvre>もう一度</button>':''}<button class="btn primary" type="button" data-rvok>${opt.replay?'閉じる':'カードのページへ'}</button>${opt.replay?'':'<button class="rv-off" type="button" data-rvoff>次から演出を出さない</button>'}</div>`;
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
// ホームへ：机のカードを、ホームの並びの自分の場所へ滑らせる。そのあいだに演出の画面（背景と机）は透けて消え、本物の並びに入れ替わる
function rvToHome(R){ if(R.list||R.dead||!R.P) return; R.list=true; const P=R.P, ov=R.ov, n=R.items.length, still=rvStill();
  R.items.forEach(it=>{ if(it.img1) UID_THUMB[it.c.id]=it.img1; });
  const r=R.cv.getBoundingClientRect(), k=r.width/RVW; Object.assign(R.cv.style,{position:'fixed',left:r.left+'px',top:r.top+'px',width:r.width+'px',height:r.height+'px',margin:'0'});
  R.bar.remove(); P.noCards=true; rvDraw(R.cv.getContext('2d'),P,P.total);
  cardShowPage('home'); const show=$('homeShow'), sec=show&&show.querySelector('.ushow'); if(!sec){ rvClose(); return; }
  window.scrollTo(0,Math.max(0,show.getBoundingClientRect().top+window.scrollY-12)); sec.classList.add('landing');
  const layer=cardEl('div',{class:'rv-fly'}); ov.appendChild(layer);
  R.items.forEach((it,pi)=>{ const th=show.querySelector(`[data-uid="${CSS.escape(it.c.id)}"] .th`); if(!th) return; const tr=th.getBoundingClientRect(), ps=rvPose(P,it,P.total), c=rvCanvas(490,276);
    if(it.img1) c.getContext('2d').drawImage(it.img1,0,0,490,276);
    const dx=r.left+ps.x*k-(tr.left+tr.width/2), dy=r.top+ps.y*k-(tr.top+tr.height/2), sc=it.W*k*ps.s/tr.width;
    Object.assign(c.style,{left:tr.left+'px',top:tr.top+'px',width:tr.width+'px',height:tr.height+'px',zIndex:String(pi+1),transform:`translate(${dx}px,${dy}px) rotate(${ps.rot}rad) scale(${sc})`});
    c.dataset.d=String((n-1-pi)*55); layer.appendChild(c); });
  void layer.offsetWidth;
  requestAnimationFrame(()=>{ layer.querySelectorAll('canvas').forEach(c=>{ c.style.transition=still?'none':`transform .85s cubic-bezier(.22,.8,.24,1) ${c.dataset.d}ms`; c.style.transform='none'; });
    ov.classList.add('rv-fade'); R.cv.style.transition='opacity 1s ease .1s'; R.cv.style.opacity='0';
    R.lt=setTimeout(()=>{ uidFill(); sec.classList.remove('landing'); rvClose(); },still?60:950+(n-1)*55); }); }
/* ---- 見本で流す：#reveal で開くと、見本のキャラで流す操作盤を出す（作り手の確認用。保存はしない） ---- */
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
  const st={m:'all',n:6,top:5}, tops=[[3,'★4'],[4,'★5'],[5,'★5+'],[6,'百年級（虹）']], B=(k,v,t,on)=>`<button class="btn" style="padding:3px 10px;font-size:12px" data-${k}="${v}" aria-pressed="${on}">${t}</button>`;
  const play=()=>{ const cs=rvDemoChars(st.m==='one'?1:st.n,st.top); const go=()=>revealPlay(cs,{mode:st.m,replay:go,okLabel:'閉じる'}); go(); };
  const draw=()=>{ box.innerHTML=`<div class="row"><b>演出を見本で流す</b><span class="note">見本のキャラで流します（保存はしません）</span><button class="btn" style="margin-left:auto;padding:2px 8px;font-size:11px" data-x>閉じる</button></div>
    <div class="row">${B('m','all','全員',st.m==='all')}${B('m','one','1枚',st.m==='one')}　人数 ${[3,6,8,12].map(k=>B('n',k,k+'人',st.n===k)).join('')}</div>
    <div class="row">最後 ${tops.map(([k,t])=>B('t',k,t,st.top===k)).join('')}</div>
    <div class="row"><button class="btn primary" data-go>▶ 流す</button><span class="note">端末で「視差効果を減らす」を選んでいると、最後の絵だけが出ます</span></div>`;
    box.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>{ st.m=b.dataset.m; draw(); });
    box.querySelectorAll('[data-n]').forEach(b=>b.onclick=()=>{ st.n=+b.dataset.n; draw(); }); box.querySelectorAll('[data-t]').forEach(b=>b.onclick=()=>{ st.top=+b.dataset.t; draw(); });
    box.querySelector('[data-x]').onclick=()=>box.remove(); box.querySelector('[data-go]').onclick=play; };
  draw(); document.body.appendChild(box); }
/* ---- カードのデザインの見直し（試作・ROADMAP 2.9）：#card2 で開くと、決まった見本で左の物差しの案を見比べる（作り手の確認用。保存はしない）
   右＝部位の★の札が主役の5行（値は白系で裏付け、棒は5行で縮尺をそろえる、サブOPは枠なしの小さな文字）
   左＝全体の★が物差しのどこにいるか（百年級・有史以来の上限と、原神のリリースの日からの線つき）
   A 左端に縦の物差し／B 立ち絵の下に横の物差し。全体の★と値は物差しの印の横（2回目。C 外周の弧・D 縦の棒は1回目でやめた） ---- */
window.CC2_ELEM=/*__ELEM_ICONS__*/{};
const CC2={v:'G',ci:0,b:'card',tight:0,ov:'pt',xs:'log',pz:'none',fl:2,up:'br',gs:'mid',fw:'365',mv:'type',un:'ym3',yk:'R4',pb:'PX',ib:'tick',ie:'s',adjOn:0,adj:(()=>{ try{ return JSON.parse(localStorage.getItem('lab:cc2Adj')||'{}')||{}; }catch(e){ return {}; } })(),list:[]}, CARD_FIT2={}, CC2_VS=[['G','G 立ち絵＋分析＋グラフ'],['E','E グラフ（5部位を積み上げ）'],['F','F グラフ（全体だけ）'],['A','A 縦の物差し'],['B','B 横の物差し']], CC2_BS=[['card','カード'],['p','平行四辺形'],['g','金の文字'],['e','星の紋章'],['f','箔押し'],['medal','メダル'],['hex','六角形'],['pill','小さな札'],['split','二分割'],['under','下線'],['glass','すりガラス'],['shield','盾'],['diamond','ひし形']];
function cc2Samples(){ // 見本（実在のプレイヤーのデータではなく、伸び方を決めて作った例）。フリーナはホームの見本と同じ
  const P=(main,lines)=>{ const rolls={}, subs=lines.map(([k,t])=>{ rolls[k]=t; const v=t.reduce((a,x)=>a+ROLL[k][x],0); return {s:k,v:FLAT.has(k)?String(Math.round(v+1e-9)):(Math.round((v+1e-9)*10)/10).toFixed(1)}; }); return {main,subs,rolls}; };
  const sm=HOME_SAMPLE||(HOME_SAMPLE=homeSampleChar()), PS2=(c,set,off,offSet)=>{ for(const k of SLOTS) if(c.pieces[k]) c.pieces[k].set=k===off?offSet:set; return c; }; PS2(sm,'黄金の劇団','goblet','千岩牢固');
  const s2={id:'cc2-low',name:'行秋',set:'絶縁の旗印4',eff:['ATK%','CR','CD','ER'],date:'見本',pieces:{
    flower:P('HP',[['CR',[1,2,1]],['CD',[0,1]],['DEF',[2]],['EM',[1]]]),
    plume:P('ATK',[['ATK%',[0,1]],['CR',[2,1]],['DEF%',[1]],['EM',[3]]]),
    sands:P('ATK%',[['CD',[1,3]],['CR',[0,2]],['DEF',[3]],['EM',[2]]]),
    goblet:P('DMG_水',[['CR',[0,1]],['ER',[1,2]],['DEF%',[2]],['EM',[1]]]),
    circlet:P('CR',[['CD',[1,2,0]],['ATK',[0]],['HP%',[3]],['DEF',[1]]])}};
  const s100={id:'cc2-myth',name:'雷電将軍',set:'絶縁の旗印4',eff:['ATK%','CR','CD','ER'],date:'見本',pieces:{
    flower:P('HP',[['CR',[3,3,3]],['CD',[3,3,3]],['ATK%',[3]],['ER',[2]]]),
    plume:P('ATK',[['CR',[3,3,3]],['CD',[3,3,3,2]],['ATK%',[2]],['DEF',[1]]]),
    sands:P('ER',[['CR',[3,3,2]],['CD',[3,3,3]],['ATK%',[2,3]],['DEF',[0]]]),
    goblet:P('DMG_雷',[['CR',[3,3,3]],['CD',[3,3,3,3]],['ATK%',[2]],['HP',[3]]]),
    circlet:P('CR',[['CD',[3,3,2,2,2]],['ATK%',[3]],['ER',[2,3]],['DEF',[0]]])}};
  PS2(s2,'絶縁の旗印','circlet','剣闘士のフィナーレ'); delete s2.pieces.circlet; s2.low={circlet:{main:'CR',r:4,lv:16,set:'教官'}}; PS2(s100,'絶縁の旗印','circlet','剣闘士のフィナーレ');
  const smP=JSON.parse(JSON.stringify(sm)); smP.id='cc2-partial'; smP.pieces.sands.lv=12; smP.pieces.goblet.lv=12;
  /* UID で取り込んだ形の見本（キャラ全体の値 uidStat。実在のプレイヤーではなく、作った値） */
  const smU=JSON.parse(JSON.stringify(sm)); smU.id='cc2-uid'; smU.idealRoll={HP:9,CR:10.5,CD:10,'DMG_水':8}; /* 理想は仮の値（聖遺物の分・サブOP何回分。割合にして使うので比だけが効く）。式のスレッドの結果か、ユーザーの登録で差し替え */ smU.uidStat={fp:{HP:38123,ATK:1021,DEF:802,CR:65.4,CD:211.2,ER:165.6,EM:40,'DMG_水':46.6},base:{HP:15307,ATK:786,DEF:696},cons:2,lv:90,w:{id:11426,lv:90,r:2,star:5}};
  const s100U=JSON.parse(JSON.stringify(s100)); s100U.id='cc2-uid2'; s100U.idealRoll={ATK:7,CR:17,CD:19,'DMG_雷':8}; s100U.uidStat={fp:{HP:21530,ATK:2104,DEF:1012,CR:78.6,CD:224.3,ER:271.4,EM:0,'DMG_雷':73.2},base:{HP:12907,ATK:945,DEF:789},cons:0,lv:90,w:{id:13509,lv:90,r:1,star:5}};
  const smN=JSON.parse(JSON.stringify(smU)); smN.id='cc2-uid3'; delete smN.idealRoll;
  return [{c:sm,l:'見本：フリーナ（★5）'},{c:smP,l:'見本：フリーナ（砂・杯が+12）'},{c:s2,l:'見本：行秋（★2）'},{c:s100,l:'見本：雷電将軍（百年級）'},{c:smU,l:'見本：フリーナ（UID）'},{c:s100U,l:'見本：雷電将軍（UID）'},{c:smN,l:'見本：フリーナ（UID・式なし）'}]; }
// 新しいカード用の立ち絵の切り出し：fitCardArt と同じ切り出しで、減光（下へ薄く・外周を丸く薄く）を焼き込まない。端はカードの側で溶かす
function fitCardArt2(src){ return new Promise(res=>{ const im=new Image(); im.onload=()=>{ try{
  const k=Math.min(1,1600/Math.max(im.width,im.height)), w=Math.round(im.width*k), h=Math.round(im.height*k), cv=document.createElement('canvas'); cv.width=w; cv.height=h; const cx=cv.getContext('2d'); cx.drawImage(im,0,0,w,h);
  const a=cx.getImageData(0,0,w,h).data, ys=[], xs=new Float64Array(h), xn=new Float64Array(h); let tr=0;
  for(let y=0;y<h;y+=2) for(let x=0;x<w;x+=2){ const v=a[(y*w+x)*4+3]; if(v<40){ tr++; continue; } ys.push(y); xs[y]+=x; xn[y]++; }
  if(tr<(w*h/4)*0.08||ys.length<50) return res(null);
  const q=f=>ys[Math.min(ys.length-1,Math.floor(ys.length*f))], y0=q(.02), y1=q(.985), ch=y1-y0, AR=600/560, cw=ch*AR;
  let sx=0,sn=0; for(let y=y0;y<y0+ch&&y<h;y++){ sx+=xs[y]; sn+=xn[y]; } const mx=sn?sx/sn:w/2;
  const OW=900, OH=Math.round(OW/AR), o=document.createElement('canvas'); o.width=OW; o.height=OH; o.getContext('2d').drawImage(cv, mx-cw/2, y0-ch*0.1, cw, ch, 0, 0, OW, OH);
  res(o.toDataURL('image/png')); }catch(e){ res(null); } }; im.onerror=()=>res(null); im.src=src; }); }
function cc2BBox(src){ return new Promise(res=>{ const im=new Image(); im.onload=()=>{ try{ const k=Math.min(1,400/Math.max(im.width,im.height)), w=Math.round(im.width*k), h=Math.round(im.height*k), cv=document.createElement('canvas'); cv.width=w; cv.height=h; const cx=cv.getContext('2d'); cx.drawImage(im,0,0,w,h); const a=cx.getImageData(0,0,w,h).data, xs=[], ys=[];
  for(let y=0;y<h;y++) for(let x=0;x<w;x++) if(a[(y*w+x)*4+3]>=60){ xs.push(x); ys.push(y); }
  if(xs.length<50) return res(null); xs.sort((p,q)=>p-q); ys.sort((p,q)=>p-q); const q=(v,f)=>v[Math.min(v.length-1,Math.floor(v.length*f))];
  res({x0:q(xs,.005)/w,x1:(q(xs,.995)+1)/w,y0:q(ys,.005)/h,y1:(q(ys,.995)+1)/h,ar:im.width/im.height}); }catch(e){ res(null); } }; im.onerror=()=>res(null); im.src=src; }); }
const CC2_BB={};
/* ---- 本番のカード（v2.9）：カードのデザインの見直し（ROADMAP 2.9）で選んだ組み合わせ ----
   立ち絵＋分析＋グラフ（G）・立ち絵は丸ごと（横長）・分析の表は右下へ全部・バッジはカード（金属）・グラフ本体は中間・これからの帯は1年・部位の MONTHS は見出しと同じ字面・横軸は対数
   立ち絵の描かれている範囲（bb）は、同梱の立ち絵は組み立てのときに測っておいたもの（PORTRAITS[id].bb）、選んだ立ち絵はここで測る（測り終えたら描き直す）。
   立ち絵の位置合わせ：同梱の立ち絵ごとの c2（portraits.json）に、カードのページで動かした位置（CARD_POS）と大きさ（CARD_ZOOM）を重ねる */
const CARD_V2_OPT={ov:'pt',xs:'log',pz:'none',fl:2,up:'br',gs:'mid',fw:'365',mv:'type'};
function cardV2(c,st){ const src=CARD_IMG[c.id]||'', aid=cc2Aid(c), pj=(aid&&PORTRAITS[aid])||{}, base=pj.c2||{x:0,y:0,s:1}, z=(CARD_ZOOM[c.id]||100)/100, pos=CARD_POS[c.id]||{dx:0,dy:0};
  let bb=null; if(src){ const own=pj.file&&src==='portraits/'+pj.file&&Array.isArray(pj.bb); if(own){ const b=pj.bb; bb={x0:b[0],y0:b[1],x1:b[2],y1:b[3],ar:b[4]}; } else if(src in CC2_BB) bb=CC2_BB[src]; else { CC2_BB[src]=null; cc2BBox(src).then(b=>{ CC2_BB[src]=b; if(b) cardV2Redraw(); }); } }
  window.CC2_LEFT='G'; window.CC2_BADGE='card'; window.CC2_TIGHT=0; window.CC2_OPT=CARD_V2_OPT; window.CC2_ADJ={x:base.x||0,y:base.y||0,s:(base.s||1)*z}; window.CC2_POS=pos; window.CC2_FIT2=''; window.CC2_WHOLE=src; window.CC2_BB=bb;
  return constellationCardSVG(c,st,'v2'); }
function cardV2Redraw(){ try{ if(CARD_PAGE==='home'&&typeof homeRender==='function') homeRender(); else renderChars(); }catch(e){} }
// 保存する画像・演出の絵：外の画像（立ち絵 portraits/…、聖遺物のアイコン icons/…）を data URL にして埋め込む（SVG を画像として描くと、外の画像は読まれない）
async function svgInlineImages(el){ const memo={}, ims=[...el.querySelectorAll('image')].filter(im=>{ const h=im.getAttribute('href')||''; return h&&!h.startsWith('data:'); });
  await Promise.all(ims.map(async im=>{ const h=im.getAttribute('href'); try{ if(!memo[h]) memo[h]=fetch(h).then(r=>r.ok?r.blob():null).then(b=>b?new Promise(res=>{ const fr=new FileReader(); fr.onload=()=>res(fr.result); fr.onerror=()=>res(null); fr.readAsDataURL(b); }):null); const d=await memo[h]; if(d) im.setAttribute('href',d); }catch(e){} })); }
const cc2Aid=c=>((/^(?:uid|enka|sample)-(\d+)$/.exec(c.id||''))||[])[1]||name2aid(c.name)||'';
const cc2AdjOf=c=>{ const a=cc2Aid(c); return CC2.adj[a]||(PORTRAITS[a]&&PORTRAITS[a].c2)||{x:0,y:0,s:1}; };
function cc2Proto(){ if($('cc2Proto')) return;
  if(!$('cc2Css')) document.head.appendChild(cardEl('style',{id:'cc2Css'},`.cc2-proto{position:fixed;inset:0;z-index:9000;overflow:auto;background:#05060d;padding:0 12px 40px}
    .cc2-bar{position:sticky;top:0;z-index:1;background:rgba(5,6,13,.96);padding:10px 0 8px;display:grid;gap:6px;font-size:12px;max-width:1200px;margin:0 auto}
    .cc2-bar .row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}.cc2-bar .btn{padding:3px 9px;font-size:12px}.cc2-bar select{font-size:12px;padding:3px 6px;max-width:100%}
    .cc2-bar button[aria-pressed="true"]{border-color:var(--gold);color:var(--gold-hi)}
    .cc2-cards{max-width:1200px;margin:8px auto 0;display:grid;gap:16px}.cc2-cards figure{margin:0}.cc2-cards figcaption{font-size:12px;color:#9aa6bb;margin-bottom:4px}`));
  const smp=HOME_SAMPLE||(HOME_SAMPLE=homeSampleChar()), por=Object.entries(PORTRAITS).filter(([a,v])=>v&&v.name).sort((p1,p2)=>p1[1].name.localeCompare(p2[1].name,'ja')).map(([a,v])=>({c:Object.assign({},smp,{id:'sample-'+a,name:v.name}),l:`立ち絵：${v.name}`}));
  CC2.list=[...cc2Samples(),...((UID_SHOW&&UID_SHOW.chars)||[]).map(c=>({c,l:`UID：${c.name||'（名前なし）'}`})),...CHARS.map(c=>({c,l:`一覧：${c.name||'（名前なし）'}`})),...por];
  const box=cardEl('div',{class:'cc2-proto',id:'cc2Proto'}), B=(k,v,t,on)=>`<button class="btn" type="button" data-${k}="${v}" aria-pressed="${on}">${t}</button>`;
  const draw=()=>{ const it=CC2.list[CC2.ci]||CC2.list[0], cc=it.c, st=charStats(cc), vs=CC2.v==='all'?CC2_VS.map(x=>x[0]):[CC2.v];
    applyBundled(cc); if(CARD_IMG[cc.id]&&!(cc.id in CARD_FIT)&&!CARD_FITTING[cc.id]){ CARD_FITTING[cc.id]=1; fitCardArt(CARD_IMG[cc.id],CARD_ZOOM[cc.id]).then(u=>{ delete CARD_FITTING[cc.id]; CARD_FIT[cc.id]=u||''; if($('cc2Proto')) draw(); }); }
    if(CARD_IMG[cc.id]&&!(cc.id in CARD_FIT2)&&!CARD_FITTING['2'+cc.id]){ CARD_FITTING['2'+cc.id]=1; fitCardArt2(CARD_IMG[cc.id]).then(u=>{ delete CARD_FITTING['2'+cc.id]; CARD_FIT2[cc.id]=u||''; if($('cc2Proto')) draw(); }); }
    if(CARD_IMG[cc.id]&&!(CARD_IMG[cc.id] in CC2_BB)){ CC2_BB[CARD_IMG[cc.id]]=null; cc2BBox(CARD_IMG[cc.id]).then(b=>{ CC2_BB[CARD_IMG[cc.id]]=b; if($('cc2Proto')) draw(); }); }
    const aid=cc2Aid(cc), adj=cc2AdjOf(cc);
    const svg=v=>{ if(v==='NOW') return cardSVG(cc,st,'SK'); window.CC2_LEFT=v; window.CC2_BADGE=CC2.b; window.CC2_TIGHT=CC2.tight; window.CC2_OPT={ov:CC2.ov,xs:CC2.xs,pz:CC2.pz,fl:CC2.fl,up:CC2.up,gs:CC2.gs,fw:CC2.fw,mv:CC2.mv,un:CC2.un,yk:CC2.yk,pb:CC2.pb,ib:CC2.ib,ie:CC2.ie}; window.CC2_ADJ=adj; window.CC2_FIT2=CARD_FIT2[cc.id]||''; window.CC2_WHOLE=CARD_IMG[cc.id]||''; window.CC2_BB=CC2_BB[CARD_IMG[cc.id]]||null; return constellationCardSVG(cc,st,'v2'); };
    box.innerHTML=`<div class="cc2-bar"><div class="row"><b>カードのデザインの見直し（試作）</b><span class="note">保存はしません</span><button class="btn" type="button" data-x style="margin-left:auto">閉じる</button></div>
      <div class="row">${[...CC2_VS,['NOW','今のカード'],['all','4案を並べる'],['SHEET','バッジ一覧']].map(([k,t])=>B('v',k,t,CC2.v===k)).join('')}</div>
      <div class="row">バッジ ${CC2_BS.map(([k,t])=>B('b',k,t,CC2.b===k)).join('')}　余白 ${B('tg',0,'標準',!CC2.tight)}${B('tg',1,'詰める',!!CC2.tight)}</div>
      <div class="row">G の立ち絵 ${B('fl',0,'枠',CC2.fl===0)}${B('fl',1,'枠なし',CC2.fl===1)}${B('fl',2,'丸ごと（横長）',CC2.fl===2)}　分析の表 ${[['br','右下へ全部（新）'],['left','左（今のまま）']].map(([k,t])=>B('up',k,t,CC2.up===k)).join('')}　${B('adjOn',CC2.adjOn?0:1,'立ち絵の位置合わせ',!!CC2.adjOn)}</div>
      ${CC2.adjOn?`<div class="row" style="border:1px solid var(--line);border-radius:8px;padding:6px 8px"><span>${esc(cc.name||'')}（${aid||'—'}）：カードの立ち絵を指でドラッグして位置、スライダーで大きさ</span><label class="row" style="gap:6px">大きさ<input type="range" data-adjs min="60" max="250" step="1" value="${Math.round(adj.s*100)}" style="width:160px"><span data-adjv>${Math.round(adj.s*100)}%</span></label><button class="btn" type="button" data-adjreset>この人を戻す</button><button class="btn" type="button" data-adjcopy>値をまとめてコピー（${Object.keys(CC2.adj).length}人）</button><span class="note" data-adjmsg></span></div>`:''}
      <div class="row">グラフ（E・F）：全体の★と値 ${[['pt','点のそば'],['hdr','右上'],['ttl','グラフの見出し'],['axis','横軸の読み']].map(([k,t])=>B('ov',k,t,CC2.ov===k)).join('')}</div>
      <div class="row">年月の表記（試作） ${[['mo','MONTHS（本番）'],['ym1','7年 + 4.0か月'],['ym2','7年4か月／12日'],['ym3','1年9か月／2か月／0.8か月'],['ym4','1年3か月／11か月／29日']].map(([k,t])=>B('un',k,t,CC2.un===k)).join('')}　ym3 の詰め ${[['now','前の形'],['R0','右寄せ'],['R1','詰め1 欄を11か月の幅に'],['R2','詰め2 ＋すき間ほぼ0'],['R3','詰め3 ＋2桁の月の字間'],['R4','詰め4 いちばん詰める']].map(([k,t])=>B('yk',k,t,CC2.yk===k)).join('')}</div>
      <div class="row">右下の段（試作） ${[['now','1か月で更新（本番）'],['U','パラメータの実際の値（UID）'],['B2','横棒・2色（聖遺物／それ以外）'],['B3','横棒・3色（サブを分ける）'],['P2','円：二重の輪（外＝今・内＝理想）'],['P1','円：今の輪＋理想の境目'],['PX','円（仕上げ）'],['BX','100%の帯（仕上げ）']].map(([k,t])=>B('pb',k,t,CC2.pb===k)).join('')}</div>
      <div class="row">理想の目立たせ方（仕上げ） ${[['n','控えめ'],['s','星を大きく光らせる'],['r','＋理想の細い輪・帯']].map(([k,t])=>B('ie',k,t,CC2.ie===k)).join('')}</div>
      <div class="row">理想の描き方 ${[['tick','縦の目印'],['ghost','理想の長さの枠']].map(([k,t])=>B('ib',k,t,CC2.ib===k)).join('')}</div>
      <div class="row">部位の MONTHS ${[['plain','そのまま'],['type','A 見出しと同じ字面'],['next','B 次の狙い'],['both','A＋B']].map(([k,t])=>B('mv',k,t,CC2.mv===k)).join('')}</div>
      <div class="row">グラフ本体 ${[['bold','華やか'],['mid','中間'],['calm','控えめ（前の形）']].map(([k,t])=>B('gs',k,t,CC2.gs===k)).join('')}　これからの帯 ${[['0','なし'],['91','3か月'],['182','半年'],['365','1年']].map(([k,t])=>B('fw',k,t,CC2.fw===k)).join('')}</div>
      <div class="row">横軸 ${[['band','段ごとに等幅'],['log','対数'],['lin','線形']].map(([k,t])=>B('xs',k,t,CC2.xs===k)).join('')}　立ち絵 ${[['none','そのまま'],['fade','溶かす'],['glass','すりガラス'],['side','右へずらす']].map(([k,t])=>B('pz',k,t,CC2.pz===k)).join('')}</div>
      <div class="row"><select data-ci aria-label="キャラ">${CC2.list.map((x,i)=>`<option value="${i}"${i===CC2.ci?' selected':''}>${esc(x.l)}</option>`).join('')}</select></div></div>
      <div class="cc2-cards">${vs.map(v=>`<figure>${CC2.v==='all'?`<figcaption>${(CC2_VS.find(x=>x[0]===v)||[])[1]||v}</figcaption>`:''}${svg(v)}</figure>`).join('')}</div>`;
    box.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>{ CC2.v=b.dataset.v; draw(); });
    box.querySelectorAll('[data-b]').forEach(b=>b.onclick=()=>{ CC2.b=b.dataset.b; draw(); });
    box.querySelectorAll('[data-tg]').forEach(b=>b.onclick=()=>{ CC2.tight=+b.dataset.tg; draw(); });
    box.querySelectorAll('[data-fl]').forEach(b=>b.onclick=()=>{ CC2.fl=+b.dataset.fl; draw(); });
    box.querySelectorAll('[data-adjOn],[data-adjon]').forEach(b=>b.onclick=()=>{ CC2.adjOn=+(b.dataset.adjon); if(CC2.adjOn&&CC2.v!=='G') CC2.v='G'; draw(); });
    if(CC2.adjOn&&aid){ const save=()=>{ CC2.adj[aid]={x:+adj.x.toFixed(3),y:+adj.y.toFixed(3),s:+adj.s.toFixed(2)}; try{ localStorage.setItem('lab:cc2Adj',JSON.stringify(CC2.adj)); }catch(e){} };
      const svgEl=box.querySelector('.cc2-cards svg'), im=svgEl&&svgEl.querySelector('#ccArtImg'), BW=CC2.fl===2?622:CC2.fl?407:306, BH=CC2.fl===2?370:CC2.fl?380:286, BX0=CC2.fl===2?24:CC2.fl?24:30, BY0=CC2.fl===2?96:CC2.fl?100:116;
      const place=()=>{ if(!im) return; let pw=BW*adj.s, ph=BH*adj.s, px=BX0+BW/2-pw/2+adj.x*BW, py=BY0+BH/2-ph/2+adj.y*BH;
        if(CC2.fl===2){ const bb=window.CC2_BB||{x0:0,y0:0,x1:1,y1:1,ar:2}, IA=bb.ar||2, k0=Math.min(BH/(bb.y1-bb.y0),1.3*BW/((bb.x1-bb.x0)*IA)); ph=k0*adj.s; pw=ph*IA; px=BX0+BW/2-((bb.x0+bb.x1)/2)*pw+adj.x*BW; py=BY0+BH/2-((bb.y0+bb.y1)/2)*ph+adj.y*BH; im.removeAttribute('mask'); } // 丸ごと：描かれている範囲に合わせた大きさ（カードと同じ式）。動かしている間は端の溶かしを外す
        im.setAttribute('x',px.toFixed(1)); im.setAttribute('y',py.toFixed(1)); im.setAttribute('width',pw.toFixed(1)); im.setAttribute('height',ph.toFixed(1)); };
      if(svgEl){ svgEl.style.touchAction='none'; svgEl.style.cursor='grab'; let st0=null;
        svgEl.addEventListener('pointerdown',e=>{ st0={px:e.clientX,py:e.clientY,x:adj.x,y:adj.y,k:1200/svgEl.getBoundingClientRect().width}; svgEl.setPointerCapture(e.pointerId); });
        svgEl.addEventListener('pointermove',e=>{ if(!st0) return; adj.x=st0.x+(e.clientX-st0.px)*st0.k/BW; adj.y=st0.y+(e.clientY-st0.py)*st0.k/BH; place(); });
        const end=()=>{ if(!st0) return; st0=null; save(); draw(); }; svgEl.addEventListener('pointerup',end); svgEl.addEventListener('pointercancel',end);
        svgEl.addEventListener('wheel',e=>{ e.preventDefault(); adj.s=Math.max(.6,Math.min(2.5,adj.s*(e.deltaY<0?1.04:1/1.04))); place(); clearTimeout(svgEl._wt); svgEl._wt=setTimeout(()=>{ save(); draw(); },300); },{passive:false}); }
      const rs=box.querySelector('[data-adjs]'); if(rs){ rs.oninput=()=>{ adj.s=+rs.value/100; box.querySelector('[data-adjv]').textContent=rs.value+'%'; place(); }; rs.onchange=()=>{ save(); draw(); }; }
      const rb=box.querySelector('[data-adjreset]'); if(rb) rb.onclick=()=>{ delete CC2.adj[aid]; try{ localStorage.setItem('lab:cc2Adj',JSON.stringify(CC2.adj)); }catch(e){} draw(); };
      const cb=box.querySelector('[data-adjcopy]'); if(cb) cb.onclick=async()=>{ const out={}; for(const [a,v] of Object.entries(CC2.adj)) out[a]=Object.assign({name:(PORTRAITS[a]||{}).name||''},v); const t=JSON.stringify(out); let ok=false; try{ await navigator.clipboard.writeText(t); ok=true; }catch(e){} box.querySelector('[data-adjmsg]').textContent=ok?'コピーしました。Claude に貼って渡してください':'コピーできませんでした：'+t; }; }
    ['ov','xs','pz','up','gs','fw','mv','un','yk','pb','ib','ie'].forEach(k=>box.querySelectorAll(`[data-${k}]`).forEach(b=>b.onclick=()=>{ CC2[k]=b.dataset[k]; draw(); }));
    box.querySelector('[data-ci]').onchange=e=>{ CC2.ci=+e.target.value; draw(); };
    box.querySelector('[data-x]').onclick=()=>box.remove(); };
  window.cc2Debug=()=>CC2.list.map(({c,l})=>{ const st=charStats(c); return l+'  全体 '+fmtAge(st.age)+' '+tierOf(st.age)[1]+' ｜ '+SLOTS.map(s=>fmtAge(st.slots[s].age)+' '+tierOf(st.slots[s].age)[1]).join(' ／ '); }); // 確認用
  draw(); document.body.appendChild(box); }
/* ---- 共有：スマホは画像ごと共有シートへ。できなければ画像を保存して、X の投稿画面を開くボタン ---- */
async function cardShare(){ const c=CHARS.find(x=>x.id===CH_OPEN); if(!c) return; return cardShareWith(c,()=>cardExport('png',$('cMsg'),{blobOnly:true}),$('cMsg')); }
async function cardShareWith(c,getBlob,msg){ const st=charStats(c), tr=tierOf(st.age||0);
  const text=`${c.name}の聖遺物は「秘境レベル ${fmtAge(st.age)}（${tr[1]}）」でした #命ノ星座カード`;
  const xLink=`<a class="btn" style="padding:3px 10px;font-size:12px" target="_blank" rel="noopener" href="https://x.com/intent/post?text=${encodeURIComponent(text)}&url=${encodeURIComponent(SITE_URL)}">X に投稿する</a>`;
  msg.textContent='画像を作っています…'; const r=await getBlob(); if(!r||!r.blob){ msg.textContent='画像を作れませんでした'; return; }
  const file=new File([r.blob],r.name,{type:'image/png'}), data={files:[file],text:text+' '+SITE_URL};
  const tryShare=async()=>{ try{ await navigator.share(data); msg.textContent='共有しました'; return true; }catch(e){ if(e&&e.name==='AbortError'){ msg.textContent=''; return true; } return e&&e.name==='NotAllowedError'?'again':false; } };
  if(navigator.canShare&&navigator.canShare({files:[file]})){
    const t=await tryShare(); if(t===true) return;
    if(t==='again'){ msg.innerHTML='画像の準備ができました。<button class="btn primary" style="padding:3px 10px;font-size:12px" id="cShare2">画像を共有する</button>'; msg.querySelector('#cShare2').addEventListener('click',async()=>{ const t2=await tryShare(); if(t2!==true) cardShareFallback(r,xLink,msg); }); return; } }
  cardShareFallback(r,xLink,msg); }
async function cardShareFallback(r,xLink,msg){ const res=await saveBlob(r.name,r.blob);
  msg.innerHTML=(res==='saved'?'画像を保存しました。':res==='declined'?'画像の保存をやめました。':'画像を保存できませんでした。')+` ${xLink}（保存した画像を添付してください）`; }
function cardAppBindDel(){ const b=$('cDel'); if(b) b.addEventListener('click',()=>{ const c=CHARS.find(x=>x.id===CH_OPEN); if(!c) return; const box=$('cDelBox'); box.innerHTML=`<span class="note">「${esc(c.name||'（名前なし）')}」を削除しますか？</span> <button class="btn" id="cDelYes">削除する</button> <button class="btn" id="cDelNo">やめる</button>`;
  $('cDelYes').addEventListener('click',()=>{ CHARS=CHARS.filter(x=>x!==c); CH_OPEN=(cardSorted()[0]||{c:{}}).c.id||null; saveChars(); portraitTx('readwrite',st=>st.delete(c.id)); box.innerHTML='<button class="btn" id="cDel">削除</button>'; cardAppBindDel(); renderChars(); });
  $('cDelNo').addEventListener('click',()=>{ box.innerHTML='<button class="btn" id="cDel">削除</button>'; cardAppBindDel(); }); }); }
"""
# --- 手持ちの聖遺物・聖遺物のページ・育成候補（v2.3 試作。docs/ROADMAP.md の 2.7） ---
#     手持ち：GOOD 形式（動画の読み取り結果・GOODファイル）の★5を、そのまま「lab:inv」にまるごと保存（1個ごとのIDがないので、読み込むたびに入れ替え）
#     育成候補：キャラの部位ごとに、手持ちの1個を+20まで上げたときの見込み（「1個を評価」と同じ数え方）と、いまの部位を超える確率・平均の伸び
#     キャラの方針：有効OPは「遊ぶ人が決めたもの（effMap）→ 初期値の表（src/builds.csv）→ 装備からの推測」。使えるセット・メインOPは「表 → いまの装備」
rep("if(c.effGuess){ const w=tw('推定')+14", "if(c.effGuess){ const EG=c.effDef?'初期値':'推定', w=tw(EG)+14")
rep('fill="#ffb4a6">推定</text>`;', 'fill="#ffb4a6">${EG}</text>`;')
rep("if(c.effGuess) labs.unshift({t:'推定',guess:true});", "if(c.effGuess) labs.unshift({t:c.effDef?'初期値':'推定',guess:true});")
rep("const hadEff=Array.isArray(c.eff); if(!hadEff){ const g=guessEff(c.pieces);", "const hadEff=Array.isArray(c.eff); if(!hadEff){ const g=CARD_APP?guessEffFor(c):guessEff(c.pieces);")
rep("if(m.effGuess){ const g=guessEff(m.pieces); if(g) m.eff=g; }", "if(m.effGuess){ const g=CARD_APP?guessEffFor(m):guessEff(m.pieces); if(g) m.eff=g; }")
# キャラ一覧の行：棒（と名札）を押すと育成候補、右上の札を押すとカード
rep("const go=()=>{ CH_OPEN=(CH_OPEN===b.dataset.open&&!CARD_APP)?null:b.dataset.open;",
    "const go=(ev)=>{ if(CARD_APP&&b.closest('#chTimeline')&&!(ev&&ev.target&&ev.target.closest&&ev.target.closest('.tl-mk'))){ candOpen(b.dataset.open,candSlotAt(b,ev)); return; } CH_OPEN=(CH_OPEN===b.dataset.open&&!CARD_APP)?null:b.dataset.open;")
rep("b.addEventListener('click',go); b.addEventListener('keydown',e=>{ if(b.tagName!=='BUTTON'&&(e.key==='Enter'||e.key===' ')){ e.preventDefault(); go(); } }); });",
    "b.addEventListener('click',go); b.addEventListener('keydown',e=>{ if(b.tagName!=='BUTTON'&&(e.key==='Enter'||e.key===' ')){ e.preventDefault(); go(); } }); });\n  if(CARD_APP) document.querySelectorAll('#chTimeline .tl-mk').forEach(m=>{ m.style.cursor='pointer'; const t=document.createElementNS('http://www.w3.org/2000/svg','title'); t.textContent='このキャラのカードを作成'; m.prepend(t); });")

CSS_INV = r"""
<style>
/* ===== 手持ちの聖遺物・育成候補（v2.3 試作） ===== */
.ia-list{display:grid; gap:8px; margin-top:10px}
.ia{display:grid; grid-template-columns:52px minmax(0,1fr) auto; gap:6px 14px; padding:10px 12px; border:1px solid var(--line); border-radius:8px; background:var(--inset)}
.ia.cur{border-color:rgba(255,255,255,.22)}
.ia{--ok:#7fd6a4; --okb:rgba(127,214,164,.55); --ng:#ff9b8a}
.ia-h{font-size:13px; color:var(--ink2); display:flex; flex-wrap:wrap; gap:2px 10px; align-items:baseline}
.ia-h b{color:var(--ink); font-size:14px} .ia-h .lv{font-variant-numeric:tabular-nums; color:var(--ink2)}
.ia-subs{display:grid; grid-template-columns:repeat(4,max-content); gap:6px 22px; font-size:12.5px}
.ia-sub{display:inline-flex; flex-direction:column; gap:3px; color:var(--muted); white-space:nowrap}
.ia-sub .tx{display:inline-flex; align-items:center; gap:6px}
.rb{display:flex; gap:5px; padding-left:11px}
.rg{display:flex; gap:2px}
.rg b,.rg s{display:block; width:8px; height:3px; border-radius:1px; background:rgba(255,255,255,.12); text-decoration:none}
.rg b{background:var(--muted)} .ia-sub.on .rg b{background:var(--ink)} .ia-sub.off .rb{opacity:.6}
.ia-sub i{width:5px; height:5px; border-radius:50%; flex:none; box-shadow:inset 0 0 0 1px currentColor; opacity:.6}
.ia-sub .v{font-variant-numeric:tabular-nums}
.ia-sub .rv{font-style:normal; font-size:10.5px; color:var(--muted); font-variant-numeric:tabular-nums; margin-left:-1px}
.ia-fb{display:flex; flex-wrap:wrap; gap:5px; flex-basis:100%; margin-bottom:2px}
.fb{display:inline-block; font-size:10.5px; line-height:1; padding:3px 6px; border-radius:4px; border:1px solid rgba(255,255,255,.14); color:var(--muted); letter-spacing:.02em; align-self:center; white-space:nowrap}
.fb.hi{color:var(--ink2); border-color:rgba(255,255,255,.3)}
.ia-sub.on{color:var(--ink)} .ia-sub.on i{background:var(--ink); box-shadow:none; opacity:1}
.ia-sub.off{opacity:.8} .ia-sub small{font-size:10.5px; color:var(--muted); border:1px dashed rgba(255,255,255,.25); border-radius:4px; padding:0 4px}
.ia.go{border-color:var(--okb)}
.ia-r{grid-column:3; grid-row:1 / span 2; text-align:right; font-size:12px; color:var(--muted); align-self:center; font-variant-numeric:tabular-nums}
.ia-r b{display:block; font-size:20px; color:var(--ink); line-height:1.2}
.ia-r .tier{font-weight:700}
.ia-r b.ok{color:var(--ok)}
.ia-ic{grid-column:1; grid-row:1 / span 2; width:52px; height:52px; border-radius:8px; align-self:start; background:linear-gradient(160deg,#6b4a3a,#b8763a 70%,#d29a52); box-shadow:inset 0 0 0 1px rgba(255,255,255,.12)}
.ia-h,.ia-subs{grid-column:2}
.ia-who{grid-column:1 / -1; font-size:12px; color:var(--muted)}
.cico{display:inline-block; width:22px; height:22px; border-radius:50%; flex:none; background:#1c2140 50% 20%/165% no-repeat; box-shadow:0 0 0 1px rgba(255,255,255,.18); vertical-align:middle}
.cico.s{width:18px; height:18px} .cico.l{width:34px; height:34px}
.cico.ini{display:inline-flex; align-items:center; justify-content:center; font-size:11px; color:var(--ink2); background:#1c2140}
.cd-hd{display:flex; align-items:center; gap:10px}
.ia-r .scl{display:block; margin-top:3px; color:var(--ink2); font-variant-numeric:tabular-nums}
.ia-r .cap{display:flex; align-items:center; justify-content:flex-end; gap:0; font-size:11px; letter-spacing:.08em; color:var(--muted); margin-bottom:2px}
.ia-r .big{display:grid; grid-template-columns:auto 156px; justify-content:end; align-items:center; gap:8px} .ia-r .big > b{text-align:right; white-space:nowrap}
.ia-r .rkw .rk{min-width:60px; justify-content:center} .ia-r .prk.dn{color:var(--muted)}
.rkw.est .rk{background:color-mix(in srgb,var(--rc) 12%,transparent); color:var(--rc); box-shadow:inset 0 0 0 1.5px color-mix(in srgb,var(--rc) 70%,transparent)}
.ia-r .big.est b{opacity:.68; font-weight:500}
.ia-r .prk{display:block; margin-top:2px; font-size:12px; color:var(--ink2)} .ia-r .prk b{display:inline; font-size:12px; color:var(--ink); font-weight:700}
.rkw{display:inline-flex; flex:none} .rkw.glow{filter:drop-shadow(0 0 6px color-mix(in srgb,var(--rc) 55%,transparent))}
.rk{display:inline-flex; align-items:center; height:22px; padding:0 13px 0 12px; font-size:12.5px; font-weight:800; letter-spacing:.08em; color:#0b0e22; background:var(--rc); background:linear-gradient(120deg,color-mix(in srgb,var(--rc) 70%,#fff) 0%,var(--rc) 45%,color-mix(in srgb,var(--rc) 72%,#000) 100%); clip-path:polygon(7px 0,100% 0,calc(100% - 7px) 100%,0 100%)}
.qwrap{position:relative; display:inline-block; margin-left:6px; vertical-align:middle}
.qm{width:17px; height:17px; border-radius:50%; border:1px solid rgba(255,255,255,.3); background:none; color:var(--ink2); font:700 11px/1 system-ui,sans-serif; cursor:pointer; padding:0}
.qm:hover,.qm:focus-visible{border-color:var(--ink); color:var(--ink)}
.itip{display:none; position:absolute; right:0; top:calc(100% + 6px); z-index:30; width:min(340px,82vw); background:#11152e; border:1px solid rgba(255,255,255,.18); border-radius:8px; padding:9px 12px; font-size:12px; line-height:1.6; color:var(--ink2); text-align:left; box-shadow:0 10px 28px rgba(0,0,0,.55); font-weight:400}
.ia-r .itip b{display:inline; font-size:inherit; line-height:inherit; color:var(--ink); font-weight:700}
.qwrap:hover .itip, .qwrap.open .itip, .qm:focus-visible + .itip{display:block}
.ia-who .tag2.cc{display:inline-flex; align-items:center; gap:6px; padding:2px 10px 2px 2px; font-size:12px}
.ia-who .tag2.cc .nm{color:var(--ink)} .ia-who .tag2.cc .st{color:var(--ink2)} .ia-who .tag2.cc .st b{color:var(--ink); font-variant-numeric:tabular-nums}
.ia-who .tag2.cc{position:relative}
.ia-who .tag2 .tip{display:none; position:absolute; left:0; bottom:calc(100% + 6px); z-index:30; width:max-content; max-width:min(560px,92vw); flex-direction:column; gap:3px; background:#11152e; border:1px solid rgba(255,255,255,.18); border-radius:8px; padding:8px 11px; font-size:12px; line-height:1.5; color:var(--ink2); text-align:left; white-space:normal; box-shadow:0 10px 28px rgba(0,0,0,.55); pointer-events:none}
.ia-who .tag2.cc:hover .tip, .ia-who .tag2.cc:focus-visible .tip{display:flex}
.ia-who .tag2 .tip > b{color:var(--ink); font-weight:700}
.ia-who .tag2 .tip .cmp{display:grid; grid-template-columns:auto auto auto auto; gap:1px 16px; margin:4px 0 2px; padding:6px 9px; background:rgba(255,255,255,.04); border-radius:6px; font-variant-numeric:tabular-nums}
.ia-who .tag2 .tip .cmp i{font-style:normal; color:var(--muted); text-align:right; white-space:nowrap} .ia-who .tag2 .tip .cmp i.k{text-align:left} .ia-who .tag2 .tip .cmp i.h{font-size:10.5px}
.ia-who .tag2 .tip .cmp i.on{color:var(--ink)} .ia-who .tag2 .tip .cmp i.ar{color:var(--muted); opacity:.7; padding:0 2px}
.ia-who .tag2 .tip .cmp i.up{color:var(--ok); font-weight:700} .ia-who .tag2 .tip .cmp i.dn{color:var(--ng); font-weight:700} .ia-who .tag2 .tip .cmp i.chg{color:#ffd27a}
.ia-who .fxl{display:block; margin:6px 0 1px; font-size:11px; letter-spacing:.06em; color:var(--muted)}
.ia-who .tag2.cc.fx{padding:1px 8px 1px 2px; font-size:11px; border-style:dashed} .ia-who .tag2.cc.fx .cico{width:20px; height:20px}
.ia-who .tag2.cc.alt .st{color:var(--muted)} .ia-who .tag2.cc.alt .nm{color:var(--ink2)}
.ia-who .tag2 .tip .cmp.c5{grid-template-columns:auto auto auto auto auto} .ia-who .tag2 .tip .cmp i.pr{color:var(--ink2); font-size:11.5px}
.ia-who .tag2 .tip .cmp i.up small,.ia-who .tag2 .tip .cmp i.dn small{color:inherit}
.ia-who .tag2 .tip .wn{color:#ffb4a6} .ia-who .tag2 .tip .mk{color:var(--ok)} .ia-who .tag2.cc .wn{color:#ffb4a6; font-size:12px; margin-left:-2px} .ia-who .tag2 .tip .cmp small{font-size:9.5px; color:var(--muted); margin-left:2px}
.ia-who .tag2 .tip .cur{display:flex; flex-wrap:wrap; gap:1px 10px; margin-top:2px; padding:5px 8px; background:rgba(255,255,255,.04); border-radius:6px}
.ia-who .tag2 .tip .cur .k{width:100%; font-size:10.5px; color:var(--muted)} .ia-who .tag2 .tip .cur em{font-style:normal; color:var(--muted); white-space:nowrap} .ia-who .tag2 .tip .cur em.on{color:var(--ink)}
.ia-who .tag2 .tip .tt{display:grid; grid-template-columns:auto repeat(3,auto); gap:2px 14px; margin:4px 0 2px; font-style:normal; font-variant-numeric:tabular-nums}
.ia-who .tag2 .tip .tt.t3{grid-template-columns:auto repeat(2,auto)} .ia-who .tag2 .tip .tt.t2{grid-template-columns:auto auto}
.ia-who .tag2 .tip .tt i{font-style:normal; text-align:right; color:var(--ink)} .ia-who .tag2 .tip .tt i.k{text-align:left; color:var(--muted)} .ia-who .tag2 .tip .tt i.h{color:var(--muted); font-size:11px}
.ia-who .tag2 .tip .tt i small{display:block; font-size:10.5px; font-weight:400; color:var(--muted)}
.ia-who .tag2 .tip .tt i.up{color:var(--ok); font-weight:700} .ia-who .tag2 .tip .tt i.dn{color:var(--ng)} .ia-who .tag2 .tip .up{color:var(--ok)} .ia-who .tag2 .tip .dn{color:var(--ng)} .ia-who .tag2 .tip .pb{color:var(--muted)}
@media (hover:none){ .ia-who .tag2 .tip{display:none!important} }
.ia-who .tag2.cc.hi{border-color:var(--okb)} .ia-who .tag2.cc.hi .st, .ia-who .tag2.cc.hi .st b{color:var(--ok)}
.ia-who .tag2.cc.ex{border-color:var(--line)} .ia-who .tag2.cc.ex .st{color:var(--ng)} .ia-who .tag2.cc.ex .nm{color:var(--ink2)} .ia-who .tag2.cc.ex .cico{opacity:.6} .ia-who .tag2.cc.own .st{color:var(--muted)}
.ia-who .tag2{display:inline-block; border:1px solid var(--line); border-radius:999px; padding:0 8px; margin:2px 4px 0 0; color:var(--ink2)}
.ia-who .tag2.ex{color:#ffb4a6; border-color:rgba(255,155,138,.5)}
.ia-who button.tag2{background:none; font:inherit; font-size:12px; cursor:pointer}
.ia-more{margin-top:10px}
.inv-f{display:flex; flex-wrap:wrap; gap:8px 14px; align-items:center; margin-top:10px}
.inv-f label{display:flex; gap:6px; align-items:center; font-size:12.5px; color:var(--muted)}
.inv-f select{max-width:16em}
.cd-tabs{display:flex; flex-wrap:wrap; gap:6px}
.cd-tabs button{display:inline-flex; align-items:baseline; gap:5px; padding:5px 12px; font-size:13px}
.cd-tabs button small{color:var(--muted); font-size:11px}
.cd-tabs button[aria-pressed="true"]{border-color:var(--gold); color:var(--gold-hi); background:rgba(233,211,154,.12)}
/* ページの切り替えが6つになったので、狭い画面では1行のまま横にずらせるように */
@media (max-width:560px){ .cnav{flex-wrap:nowrap; overflow-x:auto; scrollbar-width:none; max-width:100%} .cnav::-webkit-scrollbar{display:none} .cnav button{white-space:nowrap; flex:none; padding:6px 9px; font-size:12.5px} }
.inv-sum{display:flex; flex-wrap:wrap; gap:6px 18px; font-size:13px; color:var(--ink2)}
.inv-sum b{color:var(--ink); font-size:16px; font-variant-numeric:tabular-nums}
@media (max-width:560px){ .ia-r .cap{justify-content:flex-start} .ia-r .big{display:flex; justify-content:flex-start} .ia-r{position:relative} .qwrap{position:static} .itip{left:0; right:0; width:auto; top:calc(100% + 6px)} .ia-subs{grid-template-columns:repeat(2,minmax(0,max-content)); column-gap:18px} .ia{grid-template-columns:44px minmax(0,1fr)} .ia-ic{width:44px; height:44px; grid-row:1} .ia-subs{grid-column:1 / -1} .ia-r{grid-column:1 / -1; grid-row:auto; text-align:left} .ia-r b{display:inline; margin-right:8px} .ia-r .by{display:inline-flex; margin:0 0 0 10px; vertical-align:middle} }
</style>
"""

JS += r"""
/* ================= 単位（v2.3）：カードアプリでは日数をすべて MONTHS（30.4日＝1か月）・小数第1位で出す ================= */
function fmtMonths(d){ if(!isFinite(d)) return 'never'; const m=Math.max(0,d)/30.4; return m.toLocaleString('en-US',{minimumFractionDigits:1,maximumFractionDigits:1})+'\u2009MONTHS'; }
function moLabels(){ const o={}; for(const d of [7,30,90,365,1095,3650]) o[d]=fmtMonths(d).replace('\u2009',' '); return o; }
function moTicks(T){ return T.filter(t=>t[0]>=7).map(([d])=>[d,fmtMonths(d).replace('\u2009MONTHS',' MO')]); }
/* ================= 手持ちの聖遺物・育成候補（v2.3 試作） ================= */
var GOOD_NAMES=/*__GOOD_NAMES__*/{}, BUILDS=/*__BUILDS__*/{}, ICONS=/*__ICONS__*/{}, RELICS=/*__RELICS__*/{};
// 聖遺物のアイコン（src/icons/relic、tools/build_relic_icons.py）。Enka の部位の番号：1＝杯・2＝羽・3＝冠・4＝花・5＝砂
const RELIC_PART={goblet:1,plume:2,circlet:3,flower:4,sands:5};
function relicIcon(a){ const id=RELICS[a.set], n=RELIC_PART[a.slot]; return id&&n?`<img class="ia-ic" src="icons/relic/${id}_${n}.webp" alt="" loading="lazy" decoding="async">`:`<span class="ia-ic"></span>`; }
function charIcon(name,sz){ const f=ICONS[name]; return f?`<i class="cico${sz?' '+sz:''}" style="background-image:url(icons/${f})" aria-hidden="true"></i>`:`<i class="cico ini${sz?' '+sz:''}" aria-hidden="true">${esc(String(name||'？').slice(0,1))}</i>`; }
var INV=null, INV_IDX=null, INV_VIEW=null; const PF_MEMO=new Map();
const GOOD_STAT={hp:'HP',atk:'ATK',def:'DEF',hp_:'HP%',atk_:'ATK%',def_:'DEF%',enerRech_:'ER',eleMas:'EM',critRate_:'CR',critDMG_:'CD',heal_:'HEAL',physical_dmg_:'PHYS',pyro_dmg_:'DMG_炎',hydro_dmg_:'DMG_水',cryo_dmg_:'DMG_氷',electro_dmg_:'DMG_雷',anemo_dmg_:'DMG_風',geo_dmg_:'DMG_岩',dendro_dmg_:'DMG_草'};
const INV_GAME={'HP':'HP','ATK':'攻撃力','DEF':'防御力','HP%':'HP','ATK%':'攻撃力','DEF%':'防御力','ER':'元素チャージ効率','EM':'元素熟知','CR':'会心率','CD':'会心ダメージ'};
const INV_SUB={'HP':'HP','ATK':'攻撃力','DEF':'防御力','HP%':'HP%','ATK%':'攻撃力%','DEF%':'防御力%','ER':'元素チャージ','EM':'元素熟知','CR':'会心率','CD':'会心ダメ'};
const invPct=s=>/%$/.test(s)||s==='ER'||s==='CR'||s==='CD';
const goodChar=k=>!k?'':k.startsWith('Traveler')?'旅人':((GOOD_NAMES.chars||{})[k]||k);
const goodSet=k=>(GOOD_NAMES.sets||{})[k]||k;
const pctTxt=p=>p>=0.995?'ほぼ100%':p<0.01?'1%未満':Math.round(p*100)+'%';
function todayStr(){ const d=new Date(); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); }
/* ---- 有効OPの初期値（src/builds.csv） ---- */
function buildEff(c){ const b=c&&BUILDS[c.name]; return b&&b.eff&&b.eff.length?b.eff.slice():null; }
function guessEffFor(c){ const d=buildEff(c); if(d){ c.effDef=true; return d; } delete c.effDef; return guessEff(c.pieces); }
function buildsApply(){ let ch=false; for(const c of CHARS){ if(!c.effGuess||effOf(c)) continue; const d=buildEff(c); if(d&&(!c.effDef||d.join()!==(c.eff||[]).join())){ c.eff=d; c.effDef=true; ch=true; } } if(ch) saveChars(); }
/* ---- キャラの方針：使えるセット・メインOP・4+1（表 → いまの装備） ---- */
function planOf(c){ const b=BUILDS[c.name]||null; let sets=b&&b.sets&&b.sets.length?b.sets:null;
  if(!sets){ const ps=String(c.set||'').split('＋').map(x=>x.trim()).filter(Boolean);
    sets=ps.length===1&&/4$/.test(ps[0])?[[ps[0].slice(0,-1)]]:ps.length===1?[[ps[0].replace(/2$/,''),'どれでも']]:ps.length===2?[ps.map(x=>x.replace(/2$/,''))]:[]; }
  const okSet=new Set(sets.flat()), any=!sets.length||okSet.has('どれでも'), main={};
  for(const s of SLOTS) main[s]=(b&&b.main&&b.main[s]&&b.main[s].length)?b.main[s]:charMainKeys(c,s);
  return {sets,okSet,any,main,p41:!!(b&&b.p41),table:!!b,ok:!!(b&&b.ok)}; }
const planSetTxt=pl=>pl.any&&!pl.sets.length?'どれでも':pl.sets.map(o=>o.join('＋')).join('／');
/* ---- 手持ちの保存（lab:inv。GitHub Pages ではラボと同じ場所） ---- */
function invLoad(){ if(INV===null){ const v=store.get('inv',null); INV=v&&Array.isArray(v.arts)&&v.arts.length?v:false; } return INV||null; }
function invSave(v){ INV=v; INV_IDX=null; PF_MEMO.clear(); try{ localStorage.setItem('lab:inv',JSON.stringify(v)); return true; }catch(e){ return false; } }
function goodPiece(a){ const subs=(a.substats||[]).map(x=>({s:GOOD_STAT[x.key],v:String(x.value)})).concat((a.unactivatedSubstats||[]).map(x=>({s:GOOD_STAT[x.key],v:String(x.value),off:true})));
  while(subs.length<4) subs.push({s:'',v:''}); const p={main:GOOD_STAT[a.mainStatKey],subs:subs.slice(0,4)}; if(a.level<20) p.lv=a.level; return p; }
function goodParse(txt){ let d; try{ d=JSON.parse(String(txt)); }catch(e){ return null; } return d&&d.format==='GOOD'&&Array.isArray(d.artifacts)?d:null; }
// 手持ちを入れ替える。戻り値は知らせる文（失敗は null）
function invFromGood(txt){ const d=typeof txt==='string'?goodParse(txt):txt; if(!d) return null;
  const arts=d.artifacts.filter(a=>a&&a.rarity===5&&GOOD_STAT[a.mainStatKey]&&a.slotKey).map(a=>({set:goodSet(a.setKey),slot:a.slotKey,lk:!!a.lock,loc:goodChar(a.location),p:goodPiece(a)}));
  if(!arts.length) return '。★5の聖遺物がなかったので、手持ちは前のままです';
  const ok=invSave({at:todayStr(),src:d.source||'',arts}); const eq=arts.filter(a=>a.loc).length;
  return ok?`。手持ちとして★5の聖遺物 ${arts.length.toLocaleString()}個（装備中 ${eq}・装備なし ${(arts.length-eq).toLocaleString()}）を保存しました`:'。手持ちが大きすぎて、この端末に保存できませんでした（このページを開いている間だけ使えます）'; }
// GOODファイルから：装備中のキャラをキャラ一覧へ（動画の取り込みと同じ形）、★5すべてを手持ちへ
function goodImportFile(txt,box){ const d=goodParse(txt); if(!d){ box.textContent='GOOD形式のファイルではないようです（"format":"GOOD" が見つかりません）'; return; }
  const by=new Map(), notes={low:0,partial:0}, date=todayStr();
  for(const a of d.artifacts){ if(!a||!a.location) continue; if(a.rarity!==5){ notes.low++; continue; } if(!GOOD_STAT[a.mainStatKey]) continue; if(!by.has(a.location)) by.set(a.location,[]); by.get(a.location).push(a); }
  const chars=[]; for(const [key,list] of by){ const pieces={}, cnt={}; for(const a of list){ const p=goodPiece(a); if(p.lv!=null) notes.partial++; pieces[a.slotKey]=p; cnt[a.setKey]=(cnt[a.setKey]||0)+1; }
    const set=Object.entries(cnt).sort((x,y)=>y[1]-x[1]).filter(e=>e[1]>=2).map(e=>goodSet(e[0])+(e[1]>=4?'4':'2')).join('＋');
    chars.push({id:'scan-'+key,name:goodChar(key),set,pieces,date}); }
  let r=chars.length?moveImport(JSON.stringify({app:'genshin-lab-chars',v:1,chars})):'装備中のキャラは見つかりませんでした';
  const ex=[]; if(notes.partial) ex.push(`+20になっていない装備中の聖遺物 ${notes.partial}個は、いまの値で評価しています`); if(notes.low) ex.push(`装備中の★4以下 ${notes.low}個は外しました`);
  r+=(invFromGood(d)||'')+(ex.length?'。'+ex.join('。'):'')+'。';
  buildsApply(); importDone(box,r,chars.map(c=>c.name)); renderChars(); }
/* ---- 1個を+20まで上げたときの見込み（「1個を評価」と同じ数え方）：{cur（いまの有効RV%）, dist:[[10%単位, 確率]], rem} ---- */
function pieceFinal(p,eff){ const key=JSON.stringify([p.main,p.subs,p.lv,eff]); if(PF_MEMO.has(key)) return PF_MEMO.get(key); let r=null;
  const est=estPiece(p.main,p.subs,p.lv);
  if(est.ok){ const E=new Set(eff); let cur=0; for(const d of est.det) if(E.has(d.s)) cur+=d.u; const k=p.subs.filter(x=>x.s&&E.has(x.s)).length; let rem=Math.max(0,5-est.lv/4);
    if(est.pend){ rem=4; const o=p.subs.find(x=>x.off); if(o&&E.has(o.s)){ const m=matches(o.s,o.v), q=m&&m[1]; if(q&&q.cnt){ let eu=0,c=0; for(const [uu,cc] of q.rv){ eu+=uu*cc; c+=cc; } cur+=eu/c; } else cur+=8.5; } }
    let dist=new Map([[Math.round(cur),1]]); const add=(dm,q)=>{ const nd=new Map(); for(const [v,w] of dm){ if(q<1) nd.set(v,(nd.get(v)||0)+w*(1-q)); if(q>0) for(let t=0;t<4;t++) nd.set(v+7+t,(nd.get(v+7+t)||0)+w*q/4); } return nd; };
    for(let i=0;i<rem;i++) dist=add(dist,k/4);
    r={cur:Math.round(cur)*10,dist:[...dist.entries()],rem,lv:est.lv,pend:!!est.pend}; }
  PF_MEMO.set(key,r); return r; }
const pieceSig=p=>p?JSON.stringify([p.main,(p.subs||[]).filter(x=>x.s).map(x=>x.s+'='+x.v+(x.off?'*':''))]):'';
/* ---- キャラの1部位の候補 ---- */
function candFor(c,slot,opt,st){ const inv=invLoad(); if(!inv) return null; opt=opt||{}; st=st||charStats(c); const pl=planOf(c), mains=pl.main[slot]||[], eff=c.eff||[];
  const now=st.slots[slot].rv||0, nowU=Math.round(now/10), mine=pieceSig(c.pieces[slot]); const out=[];
  for(const a of inv.arts){ if(a.slot!==slot||!mains.includes(a.p.main)) continue; if(a.loc&&a.loc===c.name) continue; if(!a.loc&&mine&&pieceSig(a.p)===mine) continue;
    const inSet=pl.any||pl.okSet.has(a.set); if(!inSet&&!(opt.p41!=null?opt.p41:pl.p41)) continue; if(a.loc&&opt.noEquipped) continue;
    const f=pieceFinal(a.p,eff); if(!f) continue; let pb=0,gain=0,ex=0; for(const [v,q] of f.dist){ ex+=v*q; if(v>nowU){ pb+=q; gain+=(v-nowU)*q; } }
    if(pb<0.01) continue; out.push({a,f,pb,gain:gain*10,exp:ex*10,off:!inSet}); }
  return out.sort((x,y)=>y.gain-x.gain||y.pb-x.pb); }
// 聖遺物のページ用：1個ごとに「そのセットを4セットで使うキャラ」（表の使えるセット。メインOPも合うもの）を並べ、+20での素質（秘境何日分か）を出す
//   2＋2・「どれでも」・使えるセットが空欄のキャラは並べない（表に4セットで書いたキャラだけ）。4+1 は出さない（キャラ一覧の育成候補では出せる）
// 自由枠：いまの装備が「あるセットの4個＋ほかの1個（★4や空きも含む）」のとき、その1か所 {slot, four：4セットのセット, set：いま付けている1個のセット（なければ null）}
//   5部位とも同じセット・4セットが発動していないキャラは、自由枠なし（null）
function freeSlotOf(eq){ const cnt={}; for(const s of SLOTS) if(eq[s]) cnt[eq[s]]=(cnt[eq[s]]||0)+1; const four=Object.keys(cnt).find(k=>cnt[k]===4); if(!four) return null;
  const slot=SLOTS.find(s=>eq[s]!==four); return slot?{slot,four,set:eq[slot]||null}:null; }
function invUsers(c){ const b=BUILDS[c.name]; return b&&b.sets?b.sets.filter(o=>o.length===1).map(o=>o[0]):[]; }
function invIndex(){ const inv=invLoad(); if(!inv) return null; const sig=(dmgBennett()?'B':'-')+inv.at+'|'+inv.arts.length+'|'+CHARS.map(c=>c.id+':'+(c.eff||[]).join('')+':'+(c.date||'')+':'+SLOTS.map(s=>pieceSig(c.pieces&&c.pieces[s])).join('/')).join(',');
  if(INV_IDX&&INV_IDX.sig===sig) return INV_IDX;
  const eqBy=new Map(); for(const b of inv.arts) if(b.loc){ if(!eqBy.has(b.loc)) eqBy.set(b.loc,{}); eqBy.get(b.loc)[b.slot]=b.set; }
  const bySet=new Map(), bySlot=new Map(); for(const c of CHARS){ const pl=planOf(c), st=charStats(c), fs=freeSlotOf(eqBy.get(c.name)||{}), sets=invUsers(c);
    for(const set of sets){ if(!bySet.has(set)) bySet.set(set,[]); bySet.get(set).push({c,pl,st,fs}); }
    if(fs&&sets.includes(fs.four)){ if(!bySlot.has(fs.slot)) bySlot.set(fs.slot,[]); bySlot.get(fs.slot).push({c,pl,st,fs,sets}); } } // 自由枠は、いまの4セットが表の使えるセットのキャラだけ
  const info=new Map();
  for(const a of inv.arts){ const us=[], lv=a.p.lv==null?20:a.p.lv; let pot=null;
    // 表のセットで使うキャラ＋自由枠がこの部位のキャラ（表にないセットの1個は、自由枠で上回るときだけ。下で pb を見る）
    const cand=(bySet.get(a.set)||[]).map(x=>Object.assign({fx:false},x)).concat((bySlot.get(a.slot)||[]).filter(x=>!x.sets.includes(a.set)).map(x=>Object.assign({fx:true},x)));
    for(const {c,pl,st,fs,fx} of cand){ if(!(pl.main[a.slot]||[]).includes(a.p.main)) continue;
      const f=pieceFinal(a.p,c.eff||[]); if(!f) continue; const own=a.loc===c.name, now=st.slots[a.slot].rv, nowU=now==null?-1:Math.round(now/10);
      let pb=0,ex=0; for(const [v,q] of f.dist){ ex+=v*q; if(v>nowU) pb+=q; }
      if(fx&&!own&&(now==null||pb<0.01)) continue;
      const M=model(a.slot,[a.p.main],c.eff), days=ageOf(d=>M.mean(d),ex*10);
      let mxU=0, pMx=0; for(const [v,q] of f.dist) if(v>mxU){ mxU=v; pMx=q; } const daysMax=ageOf(d=>M.mean(d),mxU*10), sr=scoreRange(c,a.p,f);
      const dm=own?null:dmgCompare(c,a,f);
      us.push({c,own,now,pb:own?null:pb,dm,ex:ex*10,rvMax:mxU*10,sw:own?null:setSwap(c,a),fs:fs&&fs.slot===a.slot?fs:null,fx,days,daysMax,pMx,sr,scNow:st.slots[a.slot].sc,slotAge:st.slots[a.slot].age,cardAge:st.age,cardNew:own?st.age:ageOf(st.meanTot,Math.max(0,st.tot-(now||0)+ex*10))}); if(pot==null||days>pot.days) pot={days,ex:ex*10,c,sr,f,M}; }
    const ord=u=>u.own?2:u.fx?-3+u.pb/10:u.sw&&u.sw.alt?-1+u.pb/10:u.pb; us.sort((x,y)=>ord(y)-ord(x)); info.set(a,{us,pot,lv}); }
  INV_IDX={sig,info}; return INV_IDX; }
// いまのセットの状態と、この1個に替えたとき：
//   null＝ふつうの更新（いまこのセットの4セット、または替えると4セットになる＝mk）
//   {alt:true, label, desc}＝いまはこのセットの4セットではない（他の4セット／2セット＋2セット／4セット効果なし）。「更新」には数えない
//   手持ちに装備中の1個があればそれで数え、なければキャラのセットの欄（「X4」「A2＋B2」）から
function setSwap(c,a){ const inv=invLoad(), eq={}; if(inv) for(const b of inv.arts) if(b.loc===c.name) eq[b.slot]=b.set;
  const bon=n=>SET_BONUS2[n]||n; let four=null, twos=[];
  if(Object.keys(eq).length){ const cnt=o=>{ const m={}; for(const s of SLOTS) if(o[s]) m[o[s]]=(m[o[s]]||0)+1; return m; }, b=cnt(eq), af=cnt(Object.assign({},eq,{[a.slot]:a.set}));
    if((b[a.set]||0)>=4) return null; if((af[a.set]||0)>=4) return {mk:a.set};
    four=Object.keys(b).find(k=>b[k]>=4)||null; twos=Object.keys(b).filter(k=>b[k]>=2&&b[k]<4); if(four&&(af[four]||0)>=4) return null; }
  else { const ps=String(c.set||'').split('＋').map(x=>x.trim()).filter(Boolean); if(!ps.length) return null;
    const f=ps.map(x=>/^(.+?)4$/.exec(x)).find(Boolean); if(f){ if(f[1]===a.set) return null; four=f[1]; } else twos=ps.map(x=>x.replace(/2$/,'')); }
  if(four) return {alt:true,label:`現在、他セット装備中（${four}）`,desc:`${four}の4セット`};
  if(twos.length) return {alt:true,label:`現在、他セット装備中（${twos.map(bon).join('＋')}）`,desc:`${twos.map(bon).join('＋')}の${twos.length>1?'2セット＋2セット':'2セット'}`};
  return {alt:true,label:'現在、4セット発動なし',desc:'4セット効果なし'}; }
/* ---- ダメージの見積もり（v2.3 試作）：「この1個に替えたら、基準の技のダメージが何%変わるか」 ----
   ダメージそのものは求めない（天賦倍率・敵の耐性・防御は、どのサブOPでも同じだけ掛かるので、比べると消える）。
   キャラごとに、ステータスの効き方だけを式にする。数字は genshin-db 5.2.15、式は gcsim（b107b5d）の実装で照らし合わせた（docs/ROADMAP.md 2.7） */
const DMG_MODELS={
  'フリンズ':{skill:'雷霆のシンフォニー',            // 元素爆発（特殊）。月感電の直接ダメージ（攻撃力×倍率×3×(1+基礎ボーナス)×(1+熟知ボーナス+反応ボーナス)×会心）
    baseAtk:351.59+674.33,                          // Lv90 フリンズ＋Bloodsoaked Ruins
    cr:5+22.05, cd:50+38.4+28,                       // 基礎＋武器の会心率／基礎＋突破＋武器（月感電の後 +28%）
    react:0.36+0.20,                                 // 武器（元爆の後の月感電 +36%）＋固有天賦（昇輝の月感電 +20%）
    set:'天穹の顕現せし夜', set2:{EM:80}, set4:{CR:30,react:0.10}, // 2セット：熟知+80／4セット（昇輝）：会心率+30%・月反応+10%
    dmg(t){ const atk=t.atk, em=t.EM+Math.min(0.08*atk,160), base=Math.min(atk/100*0.007,0.14);
      return atk*(1+base)*(1+6*em/(em+2000)+t.react)*(1+Math.min(1,t.CR/100)*t.CD/100); } }
};
const BENNETT_ATK=1.19*(191.16+674.33); // ベネットの元素爆発（天賦13）：ベネットの基礎攻撃力（キャラ＋基礎攻撃力674の武器）の119%
const MAIN_NUM={HP:4780,ATK:311,'ATK%':46.6,'HP%':46.6,'DEF%':58.3,EM:186.5,ER:51.8,CR:31.1,CD:62.2,HEAL:35.9,PHYS:58.3};
const rollAvg=s=>ROLL[s]?ROLL[s].reduce((a,b)=>a+b,0)/4:0;
function dmgBennett(){ return !!store.get('dmgBennett',0); }
// いま付けている5部位（とセット）。部位のセットは手持ちの「装備中」から、分からなければキャラのセットのものとみなす
function dmgSetOf(c,slot){ const inv=invLoad(); const a=inv&&inv.arts.find(x=>x.loc===c.name&&x.slot===slot); return a?a.set:((DMG_MODELS[c.name]||{}).set||''); }
function dmgTotal(M,pieces,sets,bennett){ const t={atkP:0,atk:0,CR:M.cr,CD:M.cd,EM:0,react:M.react};
  for(const s of SLOTS){ const p=pieces[s]; if(!p||!p.main) continue; const mv=MAIN_NUM[p.main]!=null?MAIN_NUM[p.main]:(String(p.main).startsWith('DMG_')?46.6:0);
    const add=(k,v)=>{ if(k==='ATK%') t.atkP+=v; else if(k==='ATK') t.atk+=v; else if(k==='CR'||k==='CD'||k==='EM') t[k]+=v; };
    add(p.main,mv); for(const q of p.subs||[]){ if(!q.s||q.off) continue; add(q.s,parseFloat(q.v)||0); } }
  const n=SLOTS.filter(s=>sets[s]===M.set).length; if(n>=2) t.EM+=M.set2.EM; if(n>=4){ t.CR+=M.set4.CR; t.react+=M.set4.react; }
  t.atk=M.baseAtk*(1+t.atkP/100)+t.atk+(bennett?BENNETT_ATK:0); return t; }
// この1個（+20まで上げたときの伸び方を、強化が4行に入る回数の組み合わせごとに数える。伸び幅は平均）
function dmgCompare(c,a,f){ const M=DMG_MODELS[c.name]; if(!M||!f) return null; const ben=dmgBennett(), slot=a.slot;
  const sets={}; for(const s of SLOTS) sets[s]=dmgSetOf(c,s); const D0=M.dmg(dmgTotal(M,c.pieces,sets,ben)); if(!(D0>0)) return null;
  const sets2=Object.assign({},sets,{[slot]:a.set}), L=a.p.subs.filter(x=>x.s), rem=f.rem||0;
  const evalWith=adds=>{ const subs=L.map((x,i)=>({s:x.s,v:String((parseFloat(x.v)||0)+adds[i])})); /* off も付いた値として数える */ return M.dmg(dmgTotal(M,Object.assign({},c.pieces,{[slot]:{main:a.p.main,subs}}),sets2,ben))/D0-1; };
  const base=L.map(()=>0); // 4行目が+4で付くなら、付いた値はそのまま（subs の off を外して数える）
  let mean=0,pUp=0,best=-Infinity,pBest=0; const fact=n=>{ let r=1; for(let i=2;i<=n;i++) r*=i; return r; };
  (function rec(i,left,ns){ if(i===L.length-1){ ns.push(left); const pr=fact(rem)/ns.reduce((a,n)=>a*fact(n),1)/Math.pow(L.length,rem); const r=evalWith(ns.map((n,j)=>n*rollAvg(L[j].s)));
      mean+=pr*r; if(r>1e-9) pUp+=pr; ns.pop(); return; } for(let n=0;n<=left;n++){ ns.push(n); rec(i+1,left-n,ns); ns.pop(); } })(0,rem,[]);
  for(let j=0;j<L.length;j++){ const r=evalWith(L.map((x,k)=>k===j?rem*(ROLL[x.s]?ROLL[x.s][3]:0):0)); if(r>best+1e-12){ best=r; pBest=Math.pow(1/16,rem); } else if(Math.abs(r-best)<=1e-12) pBest+=Math.pow(1/16,rem); }
  if(!rem){ best=mean; pBest=1; }
  return {skill:M.skill,mean,pUp,max:best,pMax:pBest,ben}; }
/* ---- 1個のスコア（会心率×2＋会心ダメージ＋型の1項目。カードと同じ）：いま・+20で平均・+20で最大 ----
   平均＝残りの強化が4行に等しく入り、伸び幅も平均。最大＝残りの強化がすべて、スコアにいちばん効く行に最大の伸びで入ったとき */
function scoreRange(c,p,f){ const t=scoreType(c), W=s=>s==='CR'?2:s==='CD'?1:(t!=='CRIT'&&s===t?STYPES[t][2]:0), L=p.subs.filter(x=>x.s);
  const avg=s=>ROLL[s]?ROLL[s].reduce((a,b)=>a+b,0)/4:0, top=s=>ROLL[s]?ROLL[s][3]:0, now=pieceScore(p,t);
  const o=f.pend?p.subs.find(x=>x.off):null, add0=o?W(o.s)*(parseFloat(o.v)||0):0;
  const best=Math.max(0,...L.map(x=>W(x.s)*top(x.s))), nTop=L.filter(x=>best>0&&W(x.s)*top(x.s)===best).length; // 最大になる確率：残りの強化が毎回その行（同じ値の行が複数なら、どれか）に入り、伸び幅も最大（1/4）
  return {now, mean:now+add0+f.rem*L.reduce((a,x)=>a+W(x.s)*avg(x.s),0)/4, max:now+add0+f.rem*best, pMax:best>0?Math.pow(nTop/16,f.rem):1}; }
/* ---- キャラの札の吹き出し：この1個を+20まで上げて付けたら、部位とカード全体の秘境レベルが平均でどうなるか ---- */
// 右端の数字の「?」：何を表すかの説明（マウスを載せる・押す）
// ランクのバッジ：ランクの色の平行四辺形（★5・★5+ はその色でほのかに光る）
function rankBadge(t,est){ const i=TIERS.indexOf(t); return `<span class="rkw${i>=4&&!est?' glow':''}${est?' est':''}" style="--rc:${t[2]}"${est?' title="+20まで上げたときの見込み"':''}><span class="rk">${esc(t[1])}</span></span>`; }
// +20未満の1個：表示しているランク以上になる確率（+20での有効RVの分布を、ひとつずつ秘境の期間に直して数える）
function potRankP(p,t){ if(p.pr!=null) return p.pr; const M=p.M; let q=0; for(const [u,w] of p.f.dist) if(ageOf(d=>M.mean(d),u*10)>=t[0]) q+=w; return p.pr=q; }
function invQm(x,p){ const nm=esc(p.c.name), all=x.us.map(u=>esc(u.c.name)).join('・'), lv=x.lv;
  return `<span class="qwrap"><button class="qm" type="button" aria-label="この数字の説明">?</button><span class="itip" role="tooltip"><b>素質</b>：${lv<20?'この1個を+20まで上げたら、平均で':'この1個（+20）は、いま'}秘境何か月分の1個になるか。秘境だけで同じ有効RVの1個をそろえるのに、平均的な人がかかる期間です。${lv<20?'（+20での有効RVの平均を期間に直した値。だいたい「半々で上か下か」の真ん中です）。強化の当たり外れで大きく振れるので、ランクのバッジは透けた色にし、そのランク以上になる確率を添えています。':''}<br>${x.us.length>1?`このセットを使うキャラ（${all}）の有効OPでそれぞれ測り、いちばん高く出た<b>${nm}</b>の値です。`:`<b>${nm}</b>の有効OPで測った値です。`}★はカードと同じランクです。<br><b>スコア</b>：会心率×2＋会心ダメージ＋型の1項目（${nm}の型）。${lv<20?'+20まで上げたときの平均です。':'いまの値です。'}</span></span>`; }
const dmgPct=x=>(x>=0?'+':'')+(x*100).toFixed(1)+'%';
const dmgNote=d=>`<span class="pb">ダメージ＝${esc(d.skill)}（${d.ben?'ベネットのバフあり':'バフなし'}・試作）が何%変わるか。上がる確率 ${pctTxt(d.pUp)}</span>`;
const pRare=p=>p>=0.995?'ほぼ確実':p>=0.1?Math.round(p*100)+'%':p>=0.001?(p*100).toFixed(1)+'%':'約1/'+Math.round(1/p).toLocaleString();
function invTip(u,a){ const lv=a.p.lv==null?20:a.p.lv, sl=SLOT_JP[a.slot], sc=x=>x==null?'—':x.toFixed(1), ag=x=>x>0?fmtAge(x):'なし', cl=(x,y,k)=>{ const r=v=>Math.round((v||0)/(k||1)); return r(y)>r(x)?'up':r(y)<r(x)?'dn':''; }; // 見えている桁（MONTHS・スコアとも小数第1位）で比べる
  if(u.own) return `<span class="tip" role="tooltip"><b>${esc(u.c.name)}がいま付けている1個</b><span class="tt t2"><i></i><i class="h">いま</i><i class="k">${RANK_NAME}</i><i>${ag(u.slotAge)}</i><i class="k">スコア</i><i>${sc(u.scNow)}</i></span></span>`;
  const cur=u.c.pieces&&u.c.pieces[a.slot], E=new Set(u.c.eff||[]), A=a.p.subs.filter(q=>q.s), B=cur&&cur.subs?cur.subs.filter(q=>q.s):[];
  const ks=[...new Set([...B.map(q=>q.s),...A.map(q=>q.s)])].sort((x,y)=>(E.has(y)?1:0)-(E.has(x)?1:0));
  // この1個は+20まで上げたときの平均（残りの強化が4行に等しく入るとして、1回あたり平均の伸び＝4段階の平均）
  const f=lv<20?pieceFinal(a.p,u.c.eff||[]):null, rem=f?f.rem:0, num=(L,k)=>{ const q=L.find(z=>z.s===k); return q?parseFloat(q.v)||0:null; };
  const exp=k=>{ const v=num(A,k); return v==null?null:v+rem/4*(ROLL[k]?ROLL[k].reduce((x,y)=>x+y,0)/4:0); };
  const fv=(k,v)=>v==null?'—':'+'+(invPct(k)?v.toFixed(1)+'%':Math.round(v));
  // 行ごとの更新率：残りの強化が1/4ずつこの行に入り、伸びは最大の70/80/90/100%のどれか、として +20 でいまの装備のその行の値を上回る確率
  const upP=(k,c0)=>{ const b=num(A,k); if(b==null||!ROLL[k]) return null; const mx=ROLL[k][3]; let d=new Map([[0,1]]);
    for(let i=0;i<rem;i++){ const nd=new Map(); for(const [u,w] of d){ nd.set(u,(nd.get(u)||0)+w*0.75); for(let t=7;t<=10;t++) nd.set(u+t,(nd.get(u+t)||0)+w/16); } d=nd; }
    let up=0; for(const [u,w] of d) if(b+u/10*mx>(c0||0)+1e-6) up+=w; return up; };
  const rows=ks.map(k=>{ const on=E.has(k), c0=num(B,k), c1=exp(k), h=ROLL[k]?ROLL[k][3]/2:0, d=(c1||0)-(c0||0);
    const cls=!on?'':d>=h?'up':d<=-h?'dn':'', mk=cls==='up'?'<small>▲</small>':cls==='dn'?'<small>▼</small>':'', off=A.find(z=>z.s===k&&z.off)?'<small>+4で付く</small>':'';
    return `<i class="k${on?' on':''}">${INV_SUB[k]||k}</i><i class="${on?'on':''}">${fv(k,c0)}</i><i class="ar">→</i><i class="${on?'on ':''}${cls}">${fv(k,c1)}${mk}${off}</i>${rem?`<i class="pr">${on?(q=>q==null?'—':pctTxt(q))(upP(k,c0)):''}</i>`:''}`; }).join('');
  const mc=cur&&cur.main&&cur.main!==a.p.main;
  const cmp=`<span class="cmp${rem?' c5':''}"><i></i><i class="h">いまの${sl}${cur&&cur.lv!=null&&cur.lv<20?`（+${cur.lv}）`:''}</i><i></i><i class="h">${lv<20?`この1個（+20で平均）`:'この1個'}</i>${rem?'<i class="h">更新率</i>':''}`
    +`<i class="k">メイン</i><i class="${mc?'chg':''}">${cur&&cur.main?esc(MAIN_SHORT(cur.main)):'—'}</i><i class="ar">→</i><i class="${mc?'chg':''}">${esc(MAIN_SHORT(a.p.main))}</i>${rem?'<i></i>':''}${rows}</span>`;
  const notes=(u.sw&&u.sw.alt?`<span class="pb">いまは${esc(a.set)}の4セットではないので、「更新」には数えていません。下の表は、いまの${sl}との比べです</span>`:'')+(u.sw&&u.sw.mk?`<span class="mk">${esc(u.sw.mk)}が4セットになります</span>`:'')
    +(mc?`<span class="pb">メインOPが変わります（有効RVの比べ方はサブOPだけ）</span>`:'')+(u.fs&&!(u.sw&&u.sw.alt)?`<span class="pb">${sl}はいま自由枠（${esc(u.fs.set||'★5なし')}）。${esc(u.fs.four)}の4セットのまま、どのセットにも替えられます</span>`:'');
  const head=(u.sw&&u.sw.alt?`<b>${esc(u.c.name)}はいま${esc(u.sw.desc)}。${esc(a.set)}の4セットにするなら、${sl}はこの1個で</b>`:`<b>${esc(u.c.name)}の${sl}を、この1個に替えると</b>`)+cmp+notes, rvr=x=>x==null?'—':Math.round(x)+'%', now=u.slotAge||0, sn=u.scNow;
  if(lv>=20) return `<span class="tip" role="tooltip">${head}<span class="tt t3"><i></i><i class="h">いま</i><i class="h">替えたら</i><i class="k">有効RV</i><i>${rvr(u.now)}</i><i class="${cl(u.now||0,u.ex,10)}">${rvr(u.ex)}</i><i class="k">${RANK_NAME}</i><i>${ag(now)}</i><i class="${cl(now,u.days,3.04)}">${ag(u.days)}</i><i class="k">スコア</i><i>${sc(sn)}</i><i class="${cl(sn||0,u.sr.now,0.1)}">${sc(u.sr.now)}</i>${u.dm?`<i class="k">ダメージ</i><i>±0%</i><i class="${cl(0,u.dm.mean,0.001)}">${dmgPct(u.dm.mean)}</i>`:''}</span>${u.dm?dmgNote(u.dm):''}</span>`;
  return `<span class="tip" role="tooltip">${head}<span class="tt"><i></i><i class="h">いま</i><i class="h">平均</i><i class="h">最大</i><i class="k">有効RV</i><i>${rvr(u.now)}</i><i class="${cl(u.now||0,u.ex,10)}">${rvr(u.ex)}</i><i class="${cl(u.now||0,u.rvMax,10)}">${rvr(u.rvMax)}</i><i class="k">${RANK_NAME}</i><i>${ag(now)}</i><i class="${cl(now,u.days,3.04)}">${ag(u.days)}</i><i class="${cl(now,u.daysMax,3.04)}">${ag(u.daysMax)}<small>${pRare(u.pMx)}</small></i><i class="k">スコア</i><i>${sc(sn)}</i><i class="${cl(sn||0,u.sr.mean,0.1)}">${sc(u.sr.mean)}</i><i class="${cl(sn||0,u.sr.max,0.1)}">${sc(u.sr.max)}<small>${pRare(u.sr.pMax)}</small></i>${u.dm?`<i class="k">ダメージ</i><i>±0%</i><i class="${cl(0,u.dm.mean,0.001)}">${dmgPct(u.dm.mean)}</i><i class="${cl(0,u.dm.max,0.001)}">${dmgPct(u.dm.max)}<small>${pRare(u.dm.pMax)}</small></i>`:''}</span>${u.dm?dmgNote(u.dm):''}<span class="pb">${u.sw&&u.sw.alt?'いまの'+sl+'を上回る確率':'更新できる確率'} ${pctTxt(u.pb)}。平均・最大は+20まで上げたとき（いま+${lv}）。最大の下の小さな数字は、最大になる確率</span></span>`; }
/* ---- 1個の表示 ---- */
// ロールの棒：伸びた回数だけ「箱4つの組」を並べ、伸び幅の合計（70%＝箱1つ … 100%＝箱4つ）だけ塗る。合計は見積もり（RV÷10−6×回数）
function rollBar(n,u){ if(!n) return ''; const fill=Math.max(n,Math.min(4*n,Math.round(u-6*n))); let k=fill, g='';
  for(let i=0;i<n;i++){ const f=Math.floor(fill/n)+(i<fill%n?1:0); g+='<span class="rg">'+'<b></b>'.repeat(f)+'<s></s>'.repeat(4-f)+'</span>'; }
  return `<span class="rb" title="${n}回伸びた・合計 RV ${Math.round(u*10)}%（見積もり）">${g}</span>`; }
const EST_MEMO=new Map();
function estOf(p){ const k=JSON.stringify([p.main,p.subs,p.lv]); if(!EST_MEMO.has(k)) EST_MEMO.set(k,estPiece(p.main,p.subs,p.lv)); return EST_MEMO.get(k); }
// 1個の特色：W会心（会心率と会心ダメージが両方ある。+4で付く4行目も数える）・有効OPの行数・有効OPに入ったロールの平均の伸び（70〜100%）
function pieceFeat(p,eff){ const E=new Set(eff||[]), L=p.subs.filter(x=>x.s), est=estOf(p); let n=0,u=0;
  if(est.ok) for(const d of est.det) if(E.has(d.s)){ n+=d.n; u+=d.u; }
  return {w:L.some(x=>x.s==='CR')&&L.some(x=>x.s==='CD'), k:L.filter(x=>E.has(x.s)).length, avg:n?u/n*10:null}; }
function featBadges(f){ if(!f) return ''; const b=[];
  if(f.w) b.push(`<span class="fb hi" title="会心率と会心ダメージが両方ある">W会心</span>`);
  if(f.k!=null) b.push(`<span class="fb${f.k>=4?' hi':''}" title="4行のうち、有効OPの行の数">有効OP ${f.k}</span>`);
  if(f.avg!=null) b.push(`<span class="fb${f.avg>=90?' hi':''}" title="有効OPに入ったロールの、1回あたりの平均の伸び（最大100%）">平均RV ${Math.round(f.avg)}%</span>`);
  return b.join(''); }
// 特色は、並んだキャラのうちいちばんよく出るもの（有効OPの行の数 → 平均RV の順で比べる）
function featBest(p,effs){ let best=null; for(const e of effs){ const f=pieceFeat(p,e); if(!best||f.k>best.k||(f.k===best.k&&(f.avg||0)>(best.avg||0))) best=f; } return best; }
function invArtHTML(a,eff,right,who,cls,feat){ const E=new Set(eff||[]), p=a.p, est=estOf(p), det={}; if(est.ok) for(const d of est.det) det[d.s]=d;
  const subs=p.subs.filter(x=>x.s).map(x=>{ let n=0,u=0; if(x.off){ const m=matches(x.s,x.v), q=m&&m[1]; if(q&&q.cnt){ let e=0,c=0; for(const [uu,cc] of q.rv){ e+=uu*cc; c+=cc; } n=1; u=e/c; } } else if(det[x.s]){ n=det[x.s].n; u=det[x.s].u; }
    return `<span class="ia-sub${E.has(x.s)?' on':''}${x.off?' off':''}"${E.has(x.s)?' title="有効OP"':''}><span class="tx"><i></i>${INV_GAME[x.s]||x.s}<span class="v">+${esc(x.v)}${invPct(x.s)?'%':''}</span>${x.off?'<small>+4で付く</small>':''}</span>${rollBar(n,u)}</span>`; }).join('');
  return `<div class="ia${cls?' '+cls:''}">${relicIcon(a)}<div class="ia-h">${(()=>{ const fb=feat===undefined?featBadges(pieceFeat(p,eff)):featBadges(feat); return fb?`<span class="ia-fb">${fb}</span>`:''; })()}<b>${esc(a.set||'セット不明')}</b><span>${SLOT_JP[a.slot]||a.slot}・${esc(MAIN_SHORT(p.main))}</span><span class="lv">+${p.lv==null?20:p.lv}</span>${a.lk?'<span title="ロック中">🔒</span>':''}</div>
    <div class="ia-subs">${subs}</div>${right?`<div class="ia-r">${right}</div>`:''}${who?`<div class="ia-who">${who}</div>`:''}</div>`; }
/* ---- 育成候補（キャラ一覧の行を押したとき） ---- */
var CAND={id:null,slot:'flower',p41:null,eq:true,n:20};
function candSlotAt(row,ev){ try{ const svg=row.ownerSVGElement, r=row.querySelector('rect'); if(!svg||!r||!ev||ev.clientY==null||!ev.clientX) return null;
    const pt=svg.createSVGPoint(); pt.x=ev.clientX; pt.y=ev.clientY; const q=pt.matrixTransform(svg.getScreenCTM().inverse()); if(q.x<236) return null;
    const cy=+r.getAttribute('y')+(+r.getAttribute('height'))/2, k=Math.round((q.y-cy)/11)+2; return SLOTS[Math.max(0,Math.min(4,k))]; }catch(e){ return null; } }
function candOpen(id,slot){ const c=CHARS.find(x=>x.id===id); if(!c) return; CAND={id,slot:null,p41:null,eq:true,n:20};
  if(!slot&&invLoad()){ const st=charStats(c); let best=null; for(const s of SLOTS){ const L=candFor(c,s,{},st)||[]; if(L.length&&(!best||L[0].gain>best.g)) best={s,g:L[0].gain}; } slot=best?best.s:null; }
  CAND.slot=slot||'flower'; let ov=$('cdOv'); if(!ov){ ov=cardEl('div',{class:'uv-ov',id:'cdOv',role:'dialog','aria-modal':'true','aria-label':'育成候補'}); document.body.appendChild(ov);
    ov.addEventListener('click',e=>{ if(e.target===ov) candClose(); }); document.addEventListener('keydown',e=>{ if(e.key==='Escape'&&$('cdOv')) candClose(); }); }
  document.body.style.overflow='hidden'; candRender(); }
function candClose(){ const ov=$('cdOv'); if(ov) ov.remove(); document.body.style.overflow=''; }
function candRender(){ const ov=$('cdOv'), c=CHARS.find(x=>x.id===CAND.id); if(!ov||!c) return candClose(); const inv=invLoad(), st=charStats(c), pl=planOf(c), slot=CAND.slot, p41=CAND.p41==null?pl.p41:CAND.p41;
  const L=inv?(candFor(c,slot,{p41,noEquipped:!CAND.eq},st)||[]):[];
  const tabs=SLOTS.map(s=>{ const n=inv?(candFor(c,s,{p41,noEquipped:!CAND.eq},st)||[]).length:0; return `<button class="btn" data-cs="${s}" aria-pressed="${s===slot}">${SLOT_JP[s]}<small>${n}</small></button>`; }).join('');
  const x=st.slots[slot], mine=c.pieces[slot], effTxt=(c.eff||[]).map(q=>INV_SUB[q]||q).join('・')||'なし';
  let h=`<div class="uv-box"><div class="uv-h"><div class="cd-hd">${charIcon(c.name,'l')}<b>${esc(c.name||'（名前なし）')}</b><span class="note">育成候補</span></div><button class="rv-x" id="cdX" aria-label="閉じる">×</button></div>
    <p class="note" style="margin:0">有効OP：${effTxt}${c.effGuess?(c.effDef?'（初期値）':'（装備からの推定）'):''}／使えるセット：${esc(planSetTxt(pl))}／${SLOT_JP[slot]}のメインOP：${(pl.main[slot]||[]).map(m=>esc(MAIN_SHORT(m))).join('・')||'—'}${pl.table?'':'（初期値の表にないキャラなので、いまの装備から）'}</p>
    <div class="cd-tabs" role="group" aria-label="部位">${tabs}</div>`;
  if(!inv) h+=`<div class="empty">手持ちの聖遺物がまだありません。「取り込む」のページで、動画を読むか、GOOD形式のファイルを読み込むと、ここに候補が出ます。</div>`;
  else{ const stale=(c.date||'')>inv.at;
    h+=mine&&x.rv!=null?invArtHTML({set:'いま付けている1個',slot,lk:false,p:mine},c.eff,`<b style="color:${tierOf(x.age)[2]}">${fmtAge(x.age)}</b>いまの${SLOT_JP[slot]}<br>スコア ${x.sc==null?'—':x.sc.toFixed(1)}`,'','cur'):`<p class="note">いまこの部位は空です。どの1個でも上回ります。</p>`;
    h+=`<div class="inv-f"><label><input type="checkbox" id="cdP41" ${p41?'checked':''}>ほかのセットも出す（4+1）</label><label><input type="checkbox" id="cdEq" ${CAND.eq?'checked':''}>ほかのキャラが装備中の1個も出す</label></div>
      <p class="note" style="margin:0">手持ちは ${esc(inv.at)} の取り込みの時点です${stale?`。<b class="err">このキャラのデータ（${esc(c.date)}）のほうが新しいので、もう付け替えた1個や、強化した1個が古いまま出ているかもしれません</b>`:''}。</p>`;
    if(!L.length) h+=`<div class="empty">いまの${SLOT_JP[slot]}を超えうる1個は、手持ちにありません。</div>`;
    else{ h+=`<div class="ia-list">`+L.slice(0,CAND.n).map(r=>{ const a=r.a, who=[a.loc?`<span class="tag2">${esc(a.loc)}が装備中</span>`:'',r.off?'<span class="tag2 ex">ほかのセット（4+1）</span>':''].join('');
        const M=model(slot,[a.p.main],c.eff), dNew=ageOf(d=>M.mean(d),r.exp), sr=scoreRange(c,a.p,r.f), lvA=a.p.lv==null?20:a.p.lv; let mxU=0, pMx=0; for(const [v,q] of r.f.dist) if(v>mxU){ mxU=v; pMx=q; }
        const dm=dmgCompare(c,a,r.f), right=`<b class="${r.pb>=0.5?'ok':''}">更新 ${pctTxt(r.pb)}</b>${dm?`ダメージ 平均 ${dmgPct(dm.mean)}（上がる確率 ${pctTxt(dm.pUp)}）<br>`:''}${lvA<20?`平均 ${fmtAge(dNew)}・スコア ${sr.mean.toFixed(1)}<br>最大 ${fmtAge(ageOf(d=>M.mean(d),mxU*10))}（${pRare(pMx)}）・スコア ${sr.max.toFixed(1)}（${pRare(sr.pMax)}）`:`${fmtAge(dNew)}・スコア ${sr.now.toFixed(1)}`}`;
        return invArtHTML(a,c.eff,right,who,r.pb>=0.5?'go':''); }).join('')+`</div>`;
      if(L.length>CAND.n) h+=`<div class="ia-more"><button class="btn" id="cdMore">もっと見る（あと${L.length-CAND.n}個）</button></div>`; } }
  h+=`<p class="note" style="margin-top:4px">超える確率＝その1個を+20まで上げたとき、いまの${SLOT_JP[slot]}の有効RVを上回る確率（+20の1個は、付け替えるだけで上がるなら100%）。平均の伸び＝上回る分の平均。計算は「1個を評価」と同じで、サブOPの値からロール数を見積もります。並びは平均の伸びの大きい順。</p>
    <div class="btns"><button class="btn primary" id="cdCard">このキャラのカードを作成 ›</button><button class="btn" id="cdClose">閉じる</button></div></div>`;
  ov.innerHTML=h; ov.scrollTop=0;
  ov.querySelectorAll('[data-cs]').forEach(b=>b.addEventListener('click',()=>{ CAND.slot=b.dataset.cs; CAND.n=20; candRender(); }));
  const on=(id,ev,fn)=>{ const e=$(id); if(e) e.addEventListener(ev,fn); };
  on('cdX','click',candClose); on('cdClose','click',candClose); on('cdMore','click',()=>{ CAND.n+=30; const y=ov.scrollTop; candRender(); ov.scrollTop=y; });
  on('cdP41','change',e=>{ CAND.p41=e.target.checked; candRender(); }); on('cdEq','change',e=>{ CAND.eq=e.target.checked; candRender(); });
  on('cdCard','click',()=>{ candClose(); CH_OPEN=c.id; store.set('cardLast',c.id); renderChars(); cardShowPage('card'); }); }
/* ---- 聖遺物のページ ---- */
const INV_SORTS={pot:'素質の高い順',lv:'レベルの高い順',set:'セット順'};
function invInit(page){ INV_VIEW=Object.assign({set:'',slot:'',main:'',lv:'',eq:'free',cand:'',sort:'pot',n:50},store.get('invView',{})||{}); if(!INV_SORTS[INV_VIEW.sort]) INV_VIEW.sort='pot'; if(!['','go','yes','no'].includes(INV_VIEW.cand)) INV_VIEW.cand=''; INV_VIEW.n=50; page.innerHTML=`<div class="panel" style="margin-top:14px" id="invBox"></div>`; }
function invRender(){ const box=$('invBox'); if(!box) return; const inv=invLoad();
  if(!inv){ box.innerHTML=`<h2>手持ちの聖遺物</h2><div class="empty">まだありません。「取り込む」のページで、動画を読むか、GOOD形式のファイルを読み込むと、ここに★5の聖遺物が並びます（UIDやスクショからは手持ちは作れません）。</div><div class="btns"><button class="btn primary" id="invGo">取り込むのページへ</button></div>`; $('invGo').addEventListener('click',()=>cardShowPage('scan')); return; }
  box.innerHTML=`<h2>手持ちの聖遺物</h2><p class="note">計算しています…</p>`;
  setTimeout(()=>{ const t0=performance.now(); const idx=invIndex(); invRenderList(box,inv,idx,performance.now()-t0); },30); }
function invRenderList(box,inv,idx,ms){ const V=INV_VIEW, arts=inv.arts, I=idx.info, used=a=>I.get(a).us.length>0, lvOf=a=>I.get(a).lv;
  const free=arts.filter(a=>!a.loc), nNo=free.filter(a=>!used(a)).length, nNo0=free.filter(a=>!used(a)&&lvOf(a)===0).length;
  const sets=[...new Set(arts.map(a=>a.set))].sort((a,b)=>a.localeCompare(b,'ja')), mains=[...new Set(arts.filter(a=>!V.slot||a.slot===V.slot).map(a=>a.p.main))];
  const opt=(v,list)=>list.map(([k,l])=>`<option value="${esc(k)}"${k===v?' selected':''}>${esc(l)}</option>`).join('');
  let L=arts.filter(a=>(!V.set||a.set===V.set)&&(!V.slot||a.slot===V.slot)&&(!V.main||a.p.main===V.main)&&(V.eq==='all'||(V.eq==='free'?!a.loc:!!a.loc)));
  if(V.lv==='0') L=L.filter(a=>lvOf(a)===0); else if(V.lv==='mid') L=L.filter(a=>lvOf(a)>0&&lvOf(a)<20); else if(V.lv==='20') L=L.filter(a=>lvOf(a)===20);
  const goA=a=>I.get(a).us.some(u=>!u.own&&(u.now==null||u.pb>=0.5)); if(V.cand==='go') L=L.filter(goA); else if(V.cand==='yes') L=L.filter(used); else if(V.cand==='no') L=L.filter(a=>!used(a));
  const pot=a=>{ const p=I.get(a).pot; return p?(isFinite(p.days)?p.days:1e15):-1; };
  if(V.sort==='pot') L.sort((a,b)=>pot(b)-pot(a)); else if(V.sort==='lv') L.sort((a,b)=>lvOf(b)-lvOf(a)||pot(b)-pot(a)); else L.sort((a,b)=>a.set.localeCompare(b.set,'ja')||SLOTS.indexOf(a.slot)-SLOTS.indexOf(b.slot)||pot(b)-pot(a));
  const stale=CHARS.filter(c=>(c.date||'')>inv.at).length;
  let h=`<h2>手持ちの聖遺物</h2><div class="inv-sum"><span>★5 <b>${arts.length.toLocaleString()}</b>個</span><span>装備なし <b>${free.length.toLocaleString()}</b></span><span>使うキャラがいない（装備なし） <b>${nNo.toLocaleString()}</b>（うち+0 ${nNo0.toLocaleString()}）</span></div>
    <p class="note" style="margin-top:6px">${esc(inv.at)} の取り込みの時点${inv.src?`（${esc(inv.src)}）`:''}。読み込み直すと、まるごと入れ替わります。${stale?`<b class="err">そのあとで更新したキャラが ${stale}人います。付け替え・強化した分は、ここには入っていません。</b>`:''}</p>
    <div class="inv-f"><label>セット<select data-iv="set"><option value="">すべて</option>${opt(V.set,sets.map(x=>[x,x]))}</select></label>
      <label>部位<select data-iv="slot"><option value="">すべて</option>${opt(V.slot,SLOTS.map(s=>[s,SLOT_JP[s]]))}</select></label>
      <label>メインOP<select data-iv="main"><option value="">すべて</option>${opt(V.main,mains.map(m=>[m,MAIN_SHORT(m)]))}</select></label>
      <label>レベル<select data-iv="lv">${opt(V.lv,[['','すべて'],['0','+0'],['mid','途中'],['20','+20']])}</select></label>
      <label>装備<select data-iv="eq">${opt(V.eq,[['free','装備なし'],['eq','装備中'],['all','すべて']])}</select></label>
      <label>使うキャラ<select data-iv="cand">${opt(V.cand,[['','すべて'],['go','更新できる見込みが高い（緑の枠）'],['yes','いる'],['no','いない（餌の候補）']])}</select></label>
      <label>並び<select data-iv="sort">${opt(V.sort,Object.entries(INV_SORTS))}</select></label>
      <label title="ダメージの見積もりは、いまはフリンズ（雷霆のシンフォニー）だけの試作です"><input type="checkbox" id="invBen" ${dmgBennett()?'checked':''}>ダメージの見積もりにベネットのバフを入れる（試作・フリンズのみ）</label></div>
    <p class="note" style="margin-top:8px">${L.length.toLocaleString()}個${ms>800?`（計算 ${(ms/1000).toFixed(1)}秒）`:''}。<b>右の大きな数字</b>＝その1個の素質（+20まで上げたら、秘境で何日分の1個になるか）。<b>キャラの札</b>＝このセットを4セットで使うキャラ（初期値の表）と、いまの部位を<b>更新</b>できる確率。札にマウスを載せると、付け替えたときに部位の${RANK_NAME}とスコアがどうなるか（いま・+20で平均・最大）が出ます。押すと、そのキャラの育成候補が開きます。</p><div class="ia-list">`;
  h+=L.slice(0,V.n).map(a=>{ const x=I.get(a), p=x.pot, t=p?tierOf(p.days):null;
    const est=x.lv<20, right=p?`<span class="cap">${est?'+20で平均的に伸びたら':'いまの実力'}${invQm(x,p)}</span><span class="big${est?' est':''}">${t?rankBadge(t,est):''}<b title="${est?'+20で平均の有効RV':'有効RV'} ${Math.round(p.ex)}%" style="color:${t?t[2]:'inherit'}">${fmtAge(p.days)}</b></span>${t?(est?`<span class="prk">${esc(t[1])}${TIERS.indexOf(t)<TIERS.length-1?'以上':''}になる確率 <b>${pctTxt(potRankP(p,t))}</b></span>`:`<span class="prk dn">+20まで強化済み</span>`):''}<span class="scl">スコア ${est?'平均 ':''}${(est?p.sr.mean:p.sr.now).toFixed(1)}</span>`:'<span>使うキャラなし</span>';
    const who=(a.loc&&!x.us.some(u=>u.own)?`<span class="tag2">${esc(a.loc)}が装備中</span>`:'')+(x.us.length?x.us.map((u,i)=>{ const st=u.own?['own',u.fs?'装備中（自由枠）':'装備中']:u.sw&&u.sw.alt?['alt',esc(u.sw.label)]:u.now==null?['hi','空き部位']:u.pb<0.01?['ex','いまが上']:[u.pb>=0.5?'hi':'',`更新 <b>${pctTxt(u.pb)}</b>`];
      return (u.fx&&!(i&&x.us[i-1].fx)?`<span class="fxl">${x.us.some(v=>!v.fx)?'自由枠でも使えるキャラ':'4セットで使うキャラはいません。自由枠でなら使えるキャラ'}</span>`:'')+`<button class="tag2 cc ${st[0]}${u.fx?' fx':''}" data-cand="${u.c.id}" data-cslot="${a.slot}" aria-label="${esc(u.c.name)}の育成候補を開く">${charIcon(u.c.name)}<span class="nm">${esc(u.c.name)}</span><span class="st">${st[1]}</span>${invTip(u,a)}</button>`; }).join(''):`<span class="tag2 ex">使うキャラなし（餌の候補）</span>`);
    return invArtHTML(a,p?p.c.eff:null,right,who,x.us.some(u=>!u.own&&!(u.sw&&u.sw.alt)&&(u.now==null||u.pb>=0.5))?'go':'',x.us.length?featBest(a.p,x.us.map(u=>u.c.eff||[])):{w:pieceFeat(a.p,[]).w,k:null,avg:null}); }).join('')+`</div>`;
  if(L.length>V.n) h+=`<div class="ia-more"><button class="btn" id="invMore">もっと見る（あと${(L.length-V.n).toLocaleString()}個）</button></div>`;
  box.innerHTML=h;
  box.querySelectorAll('[data-iv]').forEach(el=>el.addEventListener('change',()=>{ V[el.dataset.iv]=el.value; if(el.dataset.iv==='slot') V.main=''; V.n=50; store.set('invView',Object.assign({},V,{n:undefined})); invRenderList(box,inv,idx,0); }));
  box.querySelectorAll('[data-cand]').forEach(el=>el.addEventListener('click',()=>candOpen(el.dataset.cand,el.dataset.cslot)));
  { const bn=$('invBen'); if(bn) bn.addEventListener('change',()=>{ store.set('dmgBennett',bn.checked?1:0); INV_IDX=null; invRender(); }); }
  box.querySelectorAll('.qm').forEach(b=>b.addEventListener('click',e=>{ e.stopPropagation(); const w=b.parentElement, on=!w.classList.contains('open'); box.querySelectorAll('.qwrap.open').forEach(q=>q.classList.remove('open')); w.classList.toggle('open',on); }));
  const m=$('invMore'); if(m) m.addEventListener('click',()=>{ V.n+=100; invRenderList(box,inv,idx,0); }); }
"""

s = s.replace("<div class=\"wrap\">", CSS_INV + "<div class=\"wrap\">", 1)
rep("showTab((CHARS_ONLY||CARD_APP)?'chars'", JS + "\nshowTab((CHARS_ONLY||CARD_APP)?'chars'")
import os, json as _json
_t = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'enka_tables.json'), encoding='utf-8').read(); _json.loads(_t)
assert s.count('__ENKA_TABLES__') == 1
s = s.replace('__ENKA_TABLES__', _t)
_pp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'portraits', 'portraits.json')
_pj = open(_pp, encoding='utf-8').read() if os.path.exists(_pp) else '{}'
_json.loads(_pj)
# 同梱の立ち絵の描かれている範囲（不透明な部分の外接、割合）を測って bb に入れる（カードの「丸ごと」の立ち絵の大きさと位置に使う。v2.9）
try:
    from PIL import Image as _Im
    _pd = _json.loads(_pj)
    for _k, _v in _pd.items():
        _f = os.path.join(os.path.dirname(_pp), _v.get('file', ''))
        if _v.get('bb') or not _v.get('file') or not os.path.exists(_f): continue  # 測ってあるもの（portraits.json の bb）はそのまま
        _im = _Im.open(_f).convert('RGBA'); _W, _H = _im.size; _sm = _im.copy(); _sm.thumbnail((400, 400))
        _a = _sm.getchannel('A'); _w, _h = _sm.size; _px = _a.load(); _xs = []; _ys = []
        for _y in range(_h):
            for _x in range(_w):
                if _px[_x, _y] >= 60: _xs.append(_x); _ys.append(_y)
        if len(_xs) < 50: continue
        _xs.sort(); _ys.sort(); _q = lambda v, f: v[min(len(v) - 1, int(len(v) * f))]
        _v['bb'] = [round(_q(_xs, .005) / _w, 4), round(_q(_ys, .005) / _h, 4), round((_q(_xs, .995) + 1) / _w, 4), round((_q(_ys, .995) + 1) / _h, 4), round(_W / _H, 4)]
    _pj = _json.dumps(_pd, ensure_ascii=False)
except ImportError:
    pass  # Pillow がない環境では測らない（カードの側で測る）
assert s.count('__PORTRAITS__') == 1
s = s.replace('__PORTRAITS__', _pj)
_sb = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'set_bonus.json'), encoding='utf-8').read(); _json.loads(_sb)
assert s.count('/*__SET_BONUS__*/{}') == 1
s = s.replace('/*__SET_BONUS__*/{}', _sb.strip())  # 2セット効果の表（v2.2）
# 手持ち・育成候補（v2.3）：GOOD 形式のキャラ名・セット名（src/scanner/data.js）と、育成の方針の初期値（src/builds.csv）を埋め込む
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_dj = open(os.path.join(_root, 'src', 'scanner', 'data.js'), encoding='utf-8').read()
_gd, _ = _json.JSONDecoder().raw_decode(_dj, _dj.index('{', _dj.index('GSCAN_DATA')))
_gn = {'chars': {k: v for k, v in _gd['chars'].items()}, 'sets': {k: v['n'] for k, v in _gd['sets'].items()}}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import csv as _csv, io as _io, check_builds as _cb
_rows = [(i + 2, r) for i, r in enumerate(_csv.DictReader(_io.StringIO(open(_cb.CSV, encoding='utf-8-sig').read())))]
_ch, _st = _cb.load_data(); _errs = _cb.check(_rows, _ch, _st, False)
assert not _errs, 'src/builds.csv に書き間違いがあります（python3 tools/check_builds.py）：\n' + '\n'.join(_errs)
_CODE = {'会心率': 'CR', '会心ダメージ': 'CD', '攻撃力%': 'ATK%', 'HP%': 'HP%', '防御力%': 'DEF%', '元素熟知': 'EM', '元素チャージ効率': 'ER',
         '攻撃力': 'ATK', 'HP': 'HP', '防御力': 'DEF', '治癒効果': 'HEAL', '物理ダメージ': 'PHYS'}
for _e in _cb.ELEMS: _CODE[_e + '元素ダメージ'] = 'DMG_' + _e
_lst = lambda v: [_CODE[x] for x in v.split('・') if x]
_builds = {}
for _, _r in _rows:
    _builds[_r['キャラ'].strip()] = {'eff': _lst(_r['有効OP']), 'sets': [o.split('＋') for o in _r['使えるセット'].split('／') if o],
        'main': {k: _lst(_r[j]) for k, j in (('sands', '砂'), ('goblet', '杯'), ('circlet', '冠'))}, 'p41': _r['4+1'].strip() == '○', 'ok': _r['確認済み'].strip() == '○'}
_ip = os.path.join(_root, 'src', 'icons', 'icons.json'); _icons = open(_ip, encoding='utf-8').read() if os.path.exists(_ip) else '{}'; _json.loads(_icons)
assert s.count('/*__ICONS__*/{}') == 1
s = s.replace('/*__ICONS__*/{}', _icons.strip())
_rp = os.path.join(_root, 'src', 'icons', 'relic', 'relic.json'); _relics = open(_rp, encoding='utf-8').read() if os.path.exists(_rp) else '{}'; _json.loads(_relics)
assert s.count('/*__RELICS__*/{}') == 1
s = s.replace('/*__RELICS__*/{}', _relics.strip())  # 聖遺物のアイコン（セット名 → Enka のセットの番号）
assert s.count('/*__GOOD_NAMES__*/{}') == 1 and s.count('/*__BUILDS__*/{}') == 1
s = s.replace('/*__GOOD_NAMES__*/{}', _json.dumps(_gn, ensure_ascii=False)).replace('/*__BUILDS__*/{}', _json.dumps(_builds, ensure_ascii=False))
# --- カードのデザインの見直し（試作・docs/ROADMAP.md の 2.9）：constellationCardSVG(c,st,'v2') ---
#     五角形・右上の見出しと物差し・右の5行を描かず、代わりに下の V2 の部分を描く（名前・有効OP・立ち絵・下の一文・外枠は今のまま）
#     決まり：①ランクの色は全体の★と部位の★の札だけ ②★の表記は「★5」 ③1か所に主役は1つ ④物差しには上限（百年級・有史以来） ⑤有効OPの色はサブOPの文字だけ
rep("mode=mode||'tick';", "const V2=mode==='v2'; mode=V2?'tick':(mode||'tick');")
rep("  // 星の位置\n", "  if(!V2){\n  // 星の位置\n")
rep("  // キャラ名は左上（星図の外側）", "  }\n  if(!V2){\n  // キャラ名は左上（星図の外側）")
rep("  const rx=676, RE=W-56;", "  }\n  const rx=676, RE=W-56;")
rep("  // 右上の見出し（CC_HDR）", "  if(!V2){\n  // 右上の見出し（CC_HDR）")
rep("  // 下の一文：秘境レベルの定義", "  }\n" + r"""  if(V2){
    const EST=new Set(); { const sl={}; let tot=0; for(const s of SLOTS){ const x=st.slots[s], p=c.pieces[s]; let y=x;
        if(p&&p.lv!=null&&+p.lv<20&&x.rv!=null&&typeof pieceFinal==='function'){ const f=pieceFinal(p,c.eff||[]); if(f&&f.rem>0){ let ex=0; for(const [v,q] of f.dist) ex+=v*q; const rv=ex*10; y=Object.assign({},x,{rv,age:ageOf(d=>x.M.mean(d),rv),cur:x.rv}); EST.add(s); } }
        sl[s]=y; tot+=y.rv||0; }
      if(EST.size) st=Object.assign({},st,{slots:sl,tot,age:ageOf(st.meanTot,tot)}); } /* +20になっていない部位は「+20で平均的に伸びたら」の見込み（バッジは透けた色）。全体もその見込みで組み直す */
    const LV=window.CC2_LEFT||'A', RNK=d=>d>0?tierOf(d):null, MOP=d=>{ const m=d/30.4; return m<10?m.toFixed(1):Math.round(m).toLocaleString('en-US'); };
    const mixH=(a,b,f)=>{ const q=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)), A=q(a), B=q(b); return '#'+A.map((v,i)=>Math.round(v+(B[i]-v)*f).toString(16).padStart(2,'0')).join(''); };
    const C2DEFS=`${TIERS.map((t,k)=>`<linearGradient id="c2Mt${k}" x1="0" y1="0" x2="1" y2=".55"><stop offset="0" stop-color="${mixH(t[2],'#ffffff',.38)}"/><stop offset=".32" stop-color="${t[2]}"/><stop offset=".5" stop-color="${mixH(t[2],'#ffffff',.22)}"/><stop offset=".68" stop-color="${mixH(t[2],'#000000',.08)}"/><stop offset="1" stop-color="${mixH(t[2],'#000000',.26)}"/></linearGradient><linearGradient id="c2MtSide${k}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="${mixH(t[2],'#000000',.5)}"/><stop offset="1" stop-color="${mixH(t[2],'#000000',.62)}"/></linearGradient>`).join('')}<linearGradient id="c2MtSheen" x1="0" y1="0" x2="1" y2="1"><stop offset=".3" stop-color="#fff" stop-opacity="0"/><stop offset=".44" stop-color="#fff" stop-opacity=".32"/><stop offset=".5" stop-color="#fff" stop-opacity=".08"/><stop offset=".58" stop-color="#fff" stop-opacity="0"/></linearGradient>${TIERS.map((t,k)=>`<linearGradient id="c2Rk${k}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${mixH(t[2],'#ffffff',.3)}"/><stop offset=".45" stop-color="${t[2]}"/><stop offset="1" stop-color="${mixH(t[2],'#000000',.28)}"/></linearGradient><filter id="c2Gw${k}" x="-30%" y="-60%" width="160%" height="220%"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="${t[2]}" flood-opacity=".6"/></filter>`).join('')}<filter id="c2Halo" x="-20%" y="-40%" width="140%" height="180%"><feMorphology in="SourceAlpha" operator="dilate" radius="1.4" result="d"/><feGaussianBlur in="d" stdDeviation="1.8" result="b"/><feFlood flood-color="#04050b" flood-opacity=".9"/><feComposite in2="b" operator="in" result="s"/><feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter><linearGradient id="c2Panel" x1="0" x2="1"><stop offset="0" stop-color="#05060d" stop-opacity=".72"/><stop offset=".8" stop-color="#05060d" stop-opacity=".5"/><stop offset="1" stop-color="#05060d" stop-opacity="0"/></linearGradient>`; g+=`<defs>${C2DEFS}</defs>`;
    // ランクの札。ランクの色を使うのは、この札（全体と5部位）だけ。見た目は window.CC2_BADGE（12通り。#card2 の「バッジ一覧」で見比べる）
    let BS=window.CC2_BADGE||'p'; const DK='#0b0e22';
    const BADGE=(xr,yc,h,d,o={})=>{ const t=RNK(d); if(!t) return {s:'',w:0}; const k=TIERS.indexOf(t), ML=MYTH(d), fill=ML?'url(#ccPrism)':`url(#c2Rk${k})`, col=t[2], gl=k>=4||ML?` filter="url(#c2Gw${k})"`:'', n=[...t[1]].length, num=esc(t[1].slice(1)), f1=v=>(+v).toFixed(1);
      const TG=window.CC2_TIGHT?.55:1, W0=(fs,pad)=>Math.round(pad*TG+fs*(1+.62*(n-1))), at=w=>o.left?xr:xr-w;
      const TXT=(cx,fs,c,ex='')=>`<text x="${f1(cx)}" y="${f1(yc+fs*.36)}" text-anchor="middle" font-family='${sans}' font-size="${f1(fs)}" font-weight="800" letter-spacing=".03em" fill="${c}"${ex}>${t[1]}</text>`;
      const POLY=(pts,fl,ex='')=>`<polygon points="${pts.map(q=>q.map(f1).join(',')).join(' ')}" fill="${fl}"${ex}/>`;
      if(BS==='g'){ const fs=h*.95, w=Math.round(fs*(1+.6*(n-1))), x0=at(w); return {w, s:`<text x="${x0}" y="${f1(yc+fs*.36)}" font-family='${sans}' font-size="${f1(fs)}" font-weight="800" fill="${fill}" paint-order="stroke" stroke="#05060d" stroke-width="${f1(fs*.06)}" stroke-opacity=".8"${gl}>★<tspan dx="${f1(fs*.04)}">${num}</tspan></text>`}; }
      if(BS==='e'||BS==='medal'||BS==='hex'||BS==='shield'||BS==='diamond'){ // 形の中に数字（＋は右肩）
        const R0=h*.6, w=Math.round(2*R0+(n>2?R0*.55:0)), cx=at(w)+R0, cy=yc; let shp='';
        if(BS==='e') shp=POLY([...Array(10)].map((_,i)=>{ const a=-Math.PI/2+i*Math.PI/5, r=i%2?R0*.5:R0; return [cx+r*Math.cos(a),cy+R0*.08+r*Math.sin(a)]; }),fill,` stroke="#fff" stroke-opacity=".5" stroke-width=".8" stroke-linejoin="round"${gl}`);
        if(BS==='medal') shp=`<circle cx="${f1(cx)}" cy="${f1(cy)}" r="${f1(R0)}" fill="${DK}" stroke="${fill}" stroke-width="${f1(h*.09)}"${gl}/><circle cx="${f1(cx)}" cy="${f1(cy)}" r="${f1(R0*.74)}" fill="none" stroke="${fill}" stroke-opacity=".45" stroke-width=".8"/>`;
        if(BS==='hex') shp=POLY([...Array(6)].map((_,i)=>{ const a=-Math.PI/2+i*Math.PI/3; return [cx+R0*Math.cos(a),cy+R0*Math.sin(a)]; }),fill,gl);
        if(BS==='shield') shp=`<path d="M${f1(cx-R0*.85)},${f1(cy-R0*.85)} H${f1(cx+R0*.85)} V${f1(cy+R0*.05)} Q${f1(cx+R0*.85)},${f1(cy+R0*.7)} ${f1(cx)},${f1(cy+R0*1.05)} Q${f1(cx-R0*.85)},${f1(cy+R0*.7)} ${f1(cx-R0*.85)},${f1(cy+R0*.05)} Z" fill="${fill}"${gl}/>`;
        if(BS==='diamond') shp=POLY([[cx,cy-R0],[cx+R0,cy],[cx,cy+R0],[cx-R0,cy]],fill,gl);
        const tc=BS==='medal'?fill:DK, fs=R0*(BS==='e'?.62:BS==='diamond'?.72:.9), ty=cy+(BS==='e'?R0*.08:BS==='shield'?-R0*.05:0);
        const star=BS==='medal'||BS==='diamond'?`<text x="${f1(cx)}" y="${f1(cy-R0*.38)}" text-anchor="middle" font-family='${sans}' font-size="${f1(R0*.32)}" fill="${BS==='diamond'?DK:fill}">★</text>`:'';
        return {w, s:shp+star+`<text x="${f1(cx)}" y="${f1(ty+fs*.36+(BS==='medal'||BS==='diamond'?R0*.12:0))}" text-anchor="middle" font-family='${mono}' font-size="${f1(fs)}" font-weight="800" fill="${tc}">${num.slice(0,1)}</text>`+(n>2?`<text x="${f1(cx+R0*.95)}" y="${f1(cy-R0*.3)}" font-family='${mono}' font-size="${f1(R0*.75)}" font-weight="800" fill="${fill}"${gl}>+</text>`:'')}; }
      if(BS==='pill'){ const fs=h*.5, w=W0(fs,h*1.25), x0=at(w); return {w, s:`<rect x="${x0}" y="${f1(yc-h*.42)}" width="${w}" height="${f1(h*.84)}" rx="${f1(h*.42)}" fill="${col}" fill-opacity=".12" stroke="${col}" stroke-opacity=".55" stroke-width="1"/><circle cx="${f1(x0+h*.38)}" cy="${yc}" r="${f1(h*.1)}" fill="${fill}"${gl}/>`+TXT(x0+w/2+h*.12,fs,fill)}; }
      if(BS==='split'){ const fs=h*.56, a=h*.95, w=Math.round(a+fs*(.62*(n-1))+h*.7), x0=at(w); return {w, s:`<rect x="${x0}" y="${f1(yc-h/2)}" width="${w}" height="${h}" rx="3" fill="${DK}" stroke="${fill}" stroke-width="1"/><rect x="${f1(x0+a)}" y="${f1(yc-h/2)}" width="${f1(w-a)}" height="${h}" rx="3" fill="${fill}"${gl}/><text x="${f1(x0+a/2)}" y="${f1(yc+fs*.36)}" text-anchor="middle" font-family='${sans}' font-size="${f1(fs)}" fill="${fill}">★</text><text x="${f1(x0+a+(w-a)/2)}" y="${f1(yc+fs*.38)}" text-anchor="middle" font-family='${mono}' font-size="${f1(fs*1.05)}" font-weight="800" fill="${DK}">${num}</text>`}; }
      if(BS==='under'){ const fs=h*.7, w=W0(fs,4), x0=at(w); return {w, s:TXT(x0+w/2,fs,'#f3ead6')+`<rect x="${x0}" y="${f1(yc+fs*.5)}" width="${w}" height="${f1(Math.max(2.5,h*.12))}" rx="1" fill="${fill}"${gl}/>`}; }
      if(BS==='glass'){ const fs=h*.56, w=W0(fs,h*.95), x0=at(w); return {w, s:`<rect x="${x0}" y="${f1(yc-h/2)}" width="${w}" height="${h}" rx="${f1(h*.28)}" fill="#fff" fill-opacity=".08" stroke="#fff" stroke-opacity=".22" stroke-width="1"/><line x1="${f1(x0+h*.3)}" x2="${f1(x0+w-h*.3)}" y1="${f1(yc-h/2+1.2)}" y2="${f1(yc-h/2+1.2)}" stroke="#fff" stroke-opacity=".35" stroke-width="1"/>`+TXT(x0+w/2,fs,fill,gl)}; }
      const fs=h*.58, w=W0(fs,h*.95), x0=at(w), tx=TXT(x0+w/2,fs,BS==='f'?fill:DK);
      if(BS==='f'){ const c=h*.22, y0=yc-h/2, y1=yc+h/2, oct=e=>[[x0+c+e,y0+e],[x0+w-c-e,y0+e],[x0+w-e,y0+c+e],[x0+w-e,y1-c-e],[x0+w-c-e,y1-e],[x0+c+e,y1-e],[x0+e,y1-c-e],[x0+e,y0+c+e]];
        return {w, s:POLY(oct(0),DK,` fill-opacity=".6" stroke="${fill}" stroke-width="1.4"${gl}`)+POLY(oct(3),'none',` stroke="${fill}" stroke-opacity=".45" stroke-width=".7"`)+tx}; }
      if(BS==='card'&&o.est){ const fsC=h*.56, w=Math.round(h*2.45), x0=at(w), y0=yc-h/2, r=Math.max(2,h*.13), cl=ML?'url(#ccPrism)':col; /* 見込み：透けたカード（色の淡い面＋色の細い縁＋色の文字）。厚みと光沢は付けない */
        return {w, s:`<rect x="${f1(x0+.6)}" y="${f1(y0+.6)}" width="${f1(w-1.2)}" height="${f1(h-1.2)}" rx="${f1(r)}" fill="${cl}" fill-opacity=".13" stroke="${cl}" stroke-opacity=".8" stroke-width="1.2" stroke-dasharray="${f1(h*.18)} ${f1(h*.1)}"/>`+TXT(x0+w/2,fsC,cl,' letter-spacing=".02em"')}; }
      if(BS==='card'){ const fsC=h*.56, w=Math.round(h*2.45), x0=at(w), y0=yc-h/2, r=Math.max(2,h*.13), th=Math.max(.9,h*.045), mt=ML?'url(#ccPrism)':`url(#c2Mt${k})`, sd=ML?'#6b5a8c':`url(#c2MtSide${k})`; /* 長方形のカード：金属の斜めのグラデーション＋光沢の帯、上の縁に明るい線、下に側面をのぞかせて厚みを。横幅はすべてのランクで同じ */
        return {w, s:`<g${gl}><rect x="${x0}" y="${f1(y0+th)}" width="${w}" height="${h}" rx="${f1(r)}" fill="${sd}"/><rect x="${x0}" y="${f1(y0)}" width="${w}" height="${h}" rx="${f1(r)}" fill="${mt}"/><rect x="${x0}" y="${f1(y0)}" width="${w}" height="${h}" rx="${f1(r)}" fill="url(#c2MtSheen)"/><rect x="${f1(x0+.6)}" y="${f1(y0+.6)}" width="${f1(w-1.2)}" height="${f1(h-1.2)}" rx="${f1(r-.5)}" fill="none" stroke="#fff" stroke-opacity=".38" stroke-width=".8"/><line x1="${f1(x0+r)}" x2="${f1(x0+w-r)}" y1="${f1(y0+.9)}" y2="${f1(y0+.9)}" stroke="#fff" stroke-opacity=".6" stroke-width=".8"/></g>`+TXT(x0+w/2,fsC,'#0b0e22',' letter-spacing=".02em"')}; }
      const sk=h*.3; return {w, s:`<g${gl}>${POLY([[x0+sk,yc-h/2],[x0+w,yc-h/2],[x0+w-sk,yc+h/2],[x0,yc+h/2]],fill)}</g>${tx}`}; };
    if(LV==='SHEET'){ // バッジ一覧（12通り × ランク）。カードの代わりにこの絵を返す
      const KS=[['card','カード（金属）'],['p','平行四辺形'],['g','金の文字'],['e','星の紋章'],['f','箔押し'],['medal','メダル'],['hex','六角形'],['pill','小さな札'],['split','二分割'],['under','下線'],['glass','すりガラス'],['shield','盾'],['diamond','ひし形']], DS=[3,15,60,200,600,3000,60000], H2=60+KS.length*62;
      const defs=(g.match(/<linearGradient id="ccPrism"[\s\S]*?<\/linearGradient>/)||[''])[0]+C2DEFS;
      let o=`<rect width="${W}" height="${H2}" fill="#070914"/>`+DS.map((d,j)=>`<text x="${250+j*130}" y="34" text-anchor="middle" font-family='${sans}' font-size="12" fill="#8a93a6">${j<6?TIERS[j][1]:'百年級'}</text>`).join('');
      KS.forEach(([k,lab],i)=>{ BS=k; const y=80+i*62; o+=`<text x="40" y="${y+5}" font-family='${sans}' font-size="14" fill="#cfd4e6">${lab}</text>`; DS.forEach((d,j)=>{ const bb=BADGE(0,0,30,d); o+=`<g transform="translate(${(250+j*130-bb.w/2).toFixed(1)},${y})">`+BADGE(0,0,30,d,{left:1}).s+`</g>`; }); });
      return `<svg viewBox="0 0 ${W} ${H2}" role="img" aria-label="バッジ一覧" style="display:block;width:100%;height:auto;border-radius:10px"><defs>${defs}</defs>${o}</svg>`; }
    // 上限つきの物差し：★1〜★5+ の6段に、百年級（1,200 MONTHS〜）・有史以来（60,000 MONTHS〜）の2段を足す。段の幅は等しく、段の中は日数の対数
    const EB=[...TIERS.map(t=>t[0]),36500,1825000,18250000], EN=EB.length-1, ES5=TIERS.length/EN, ELB=[...TIERS.map(t=>t[1]),'百年級','有史以来'], EMO=EB.slice(1,EN).map(d=>d===36500?'1,200':d===1825000?'60,000':MOP(d));
    const ES=d=>{ if(!(d>0)) return 0; if(!isFinite(d)) return 1; let k=0; for(let i=0;i<EN;i++) if(d>=EB[i]) k=i; const lo=Math.log(Math.max(1,EB[k])), hi=Math.log(EB[k+1]); return Math.min(1,(k+Math.max(0,Math.min(1,(Math.log(Math.max(1,d))-lo)/(hi-lo))))/EN); };
    const REL=Math.max(1,(Date.now()-Date.UTC(2020,8,28))/864e5); // 原神のリリースの日（2020-09-28）から今日まで、毎日秘境を回った日数
    let HALO=0; const HAL=()=>HALO?' paint-order="stroke" stroke="#05060d" stroke-width="3" stroke-opacity=".9" stroke-linejoin="round"':'';
    const TX=(x,y,t,o={})=>`<text${HAL()} x="${(+x).toFixed(1)}" y="${(+y).toFixed(1)}" text-anchor="${o.a||'start'}" font-family='${o.m?mono:sans}' font-size="${o.fs||9}" font-weight="${o.fw||400}" fill="${o.c||'#8a93a6'}"${o.op?` opacity="${o.op}"`:''}>${t}</text>`;
    const LN=(x1,y1,x2,y2,c,op,w,ex='')=>`<line x1="${(+x1).toFixed(1)}" y1="${(+y1).toFixed(1)}" x2="${(+x2).toFixed(1)}" y2="${(+y2).toFixed(1)}" stroke="${c}" stroke-opacity="${op}" stroke-width="${w}"${ex}/>`;
    const CREAM='#e6dfcf', RELC='#a9bddc', age=st.age>0?st.age:0;
    /* 年月表記の試作（window.CC2_OPT.un）：mo＝MONTHS（本番）／ym1＝「3.2か月」「7年 + 4.0か月」／ym2＝「12日」「3.2か月」「7年4か月」。右寄せなので「か月」の縦の線はそろう。「年」の部分だけ淡い金 */
    const UN=(window.CC2_OPT||{}).un||'mo', YM=(d,fs)=>{ const u=f=>`<tspan font-size="${(fs*.62).toFixed(1)}" font-family='${sans}' dx="1.5">${f}</tspan>`;
      if(!isFinite(d)) return '上限'; const m=d/30.4;
      if(UN==='ym2'&&m<1) return `${Math.max(1,Math.round(d))}${u('日')}`;
      if(m<12) return `${m.toFixed(1)}${u('か月')}`;
      const y=Math.floor(m/12), r=m-y*12, yp=`<tspan fill="#f6e2a8">${y.toLocaleString('en-US')}${u('年')}</tspan>`;
      return UN==='ym1'?`${yp}<tspan font-size="${(fs*.62).toFixed(1)}" fill="#8a93a6" dx="3">+</tspan><tspan dx="3">${r.toFixed(1)}</tspan>${u('か月')}`:`${yp}<tspan dx="3">${Math.floor(r)}</tspan>${u('か月')}`; },
      /* ym3（持ち主の案）：1か月未満は「0.8か月」、1か月以上は「2か月」、1年以上は「1年9か月」（小数なし）。x を渡すと、月の部分を x に右寄せ、年の部分を月の欄（「00か月」ぶん）の左に右寄せ＝「年」の縦の位置もそろう */
      YM3=(d,fs,x)=>{ const u=f=>`<tspan font-size="${(fs*.62).toFixed(1)}" font-family='${sans}' dx="1.5">${f}</tspan>`; if(!isFinite(d)) return '上限'; const m=d/30.4;
        /* 1か月未満は「0.9か月」、1か月以上は「3か月」、1年以上は「1年0か月」（月が0でも書く）。0.95か月以上は「1か月」（「1.0か月」にしない） */
        const M=Math.round(m), y=m<.95?0:Math.floor(M/12), ms=m<.95?m.toFixed(1):String(M-y*12), yp=y?`<tspan fill="#f6e2a8">${y.toLocaleString('en-US')}${u('年')}</tspan>`:'', YK=(window.CC2_OPT||{}).yk||'R4';
        if(x==null) return y?`${yp}<tspan dx="3">${ms}</tspan>${u('か月')}`:`${ms}${u('か月')}`;
        /* 行の組み方（window.CC2_OPT.yk。2.10 の詰め）：「年」の右端はどの行でも同じ位置、月は右寄せ（「か月」の右端もそろう）。年と月のすき間を段階で詰める：
           R0＝月の欄を「0.9か月」「11か月」の広いほうの幅＋すき間0.15字／R1＝欄を「10か月」「11か月」の幅に（「0.9か月」は年のない行だけなので、欄に入れなくてよい）／R2＝R1＋すき間0.03字／R3＝R2＋2桁の月（10・11）だけ数字の字間を0.06字詰めて欄を細く／R4＝字間を0.13字（「1」の両脇の余白ぶん）・すき間0。これ以上は「10か月」「11か月」が欄に入らない（残る空き＝1桁と2桁の差、ほぼ「1」の幅）。now＝前の形 */
        if(YK==='now'){ const colW=fs*.6*2+fs*.62*2+1.5+fs*.3; return y?`<tspan x="${(x-colW).toFixed(1)}">${yp}</tspan><tspan x="${x}">${ms}${u('か月')}</tspan>`:`${ms}${u('か月')}`; }
        const fm=`600 ${fs}px ${mono}`, fu=`600 ${(fs*.62).toFixed(1)}px ${sans}`, LS=YK==='R4'?-fs*.13:YK==='R3'?-fs*.06:0, wMo=t=>MW4(t,fm)+(t.length-1)*(/^\d\d$/.test(t)?LS:0)+1.5+MW4('か月',fu),
          colW=YK==='R0'?Math.max(wMo('0.9'),wMo('11')):Math.max(wMo('10'),wMo('11')), gap=fs*(YK==='R0'||YK==='R1'?.15:YK==='R4'?0:.03), c0=x-colW, ls=LS&&/^\d\d$/.test(ms)?` letter-spacing="${LS.toFixed(2)}"`:'';
        return (y?`<tspan x="${(c0-gap).toFixed(1)}">${yp}</tspan>`:'')+`<tspan x="${x}"${ls}>${ms}</tspan>${u('か月')}`; },
      /* ym4（持ち主の案2）：1か月未満は「29日」、1か月以上は「11か月」、1年以上は「1年3か月」（すべて整数）。行では「年」の右端の位置をそろえ、月は「年」のすぐ右に詰める（「11か月」がちょうど右端に来る位置） */
      MW4=(t,f)=>{ try{ const cx=(window.CC2_MCTX=window.CC2_MCTX||document.createElement('canvas').getContext('2d')); cx.font=f; return cx.measureText(t).width; }catch(e){ return t.length*10; } },
      YM4=(d,fs,x)=>{ const u=f=>`<tspan font-size="${(fs*.62).toFixed(1)}" font-family='${sans}' dx="1.5">${f}</tspan>`; if(!isFinite(d)) return '上限'; const m=d/30.4;
        if(m<1) return `${Math.max(1,Math.round(d))}${u('日')}`; const M=Math.floor(m), y=Math.floor(M/12), r=M-y*12; if(!y) return `${M}${u('か月')}`;
        const yp=`<tspan fill="#f6e2a8">${y.toLocaleString('en-US')}${u('年')}</tspan>`; if(x==null) return `${yp}<tspan dx="2">${r}</tspan>${u('か月')}`;
        const fm=`600 ${fs}px ${mono}`, fu=`600 ${(fs*.62).toFixed(1)}px ${sans}`, wMo=t=>MW4(t,fm)+1.5+MW4('か月',fu), yEnd=x-wMo('11')-3;
        return `<tspan x="${yEnd.toFixed(1)}">${yp}</tspan><tspan x="${(yEnd+3+wMo(String(r))).toFixed(1)}">${r}${u('か月')}</tspan>`; },
      VAL=(d,fs,x)=>UN==='mo'?UHT(fmtAge(d),fs,null):UN==='ym3'?YM3(d,fs,x):UN==='ym4'?YM4(d,fs,x):YM(d,fs);
    // 分析の表（1か月で更新できる見込み＋有効OPの伸び）の置き場（G）：br＝右下へ全部（5行を詰める。左は立ち絵とグラフだけ）／left＝左の表。row（各行に添える）・strip（右下に帯）は試してやめた
    const f1r=v=>(+v).toFixed(1);
    const UPM=LV==='G'?((window.CC2_OPT||{}).up||'br'):'left', BRH=UPM==='br'?148:0, PA=upProbAll(st,30), PS=SLOTS.map(s=>upProb(st.slots[s],30)), PSB=Math.max(...PS), FPc=p0=>p0>=.995?'>99%':p0<.005?(p0<=0?'0%':'<1%'):Math.round(p0*100)+'%';
    // ---- 右上：部位の見出し（全体の★と値は左の物差しへ移した） ----
    const CHIP=(t,x,y,fs)=>{ fs=fs||9.5; let w; try{ const cx=(window.CC2_MCTX=window.CC2_MCTX||document.createElement('canvas').getContext('2d')); cx.font=`700 ${fs}px ${sans}`; w=cx.measureText(t).width+t.length*fs*.12; }catch(e){ w=[...t].length*fs*1.1; } /* 見出しのチップ：細い金の枠とごく淡い面だけ */
      return `<rect x="${x}" y="${(y-fs*1.17).toFixed(1)}" width="${(w+fs*1.68).toFixed(1)}" height="${(fs*1.6).toFixed(1)}" rx="${(fs*.38).toFixed(1)}" fill="#e9d39a" fill-opacity=".05" stroke="#e9d39a" stroke-opacity=".38" stroke-width=".8"/><text x="${(x+fs*.9).toFixed(1)}" y="${y}" font-family='${sans}' font-size="${fs}" font-weight="700" letter-spacing=".12em" fill="#cfd4e6">${t}</text>`; };
    if(LV==='G') g+=CHIP(RANK_NAME,rx,58,11); else g+=TX(rx,58,(window.CC2_OPT||{}).ov==='hdr'&&/^[EF]$/.test(LV)?RANK_NAME:'部位ごとの'+RANK_NAME,{fs:12,c:'#9aa6bb'}).replace('<text ','<text letter-spacing=".15em" ');
    g+=`<text x="${RE}" y="58" text-anchor="end" font-family='${sans}' font-size="12" fill="#9aa6bb">${UPM==='row'?`1か月で更新 <tspan font-family='${mono}' fill="#f3ead6" font-size="14">${FPc(PA)}</tspan>　`:''}有効RV <tspan font-family='${mono}' fill="#f3ead6" font-size="14">${Math.round(st.tot)}%</tspan>　スコア <tspan font-family='${mono}' fill="#f3ead6" font-size="14">${st.score.toFixed(1)}</tspan></text>`;
    // ---- 右：5部位の行（2秒目＝部位の★の札、3秒目＝値と棒、最後＝サブOP） ----
    const NEXTD=Math.min(...SLOTS.map(s=>{ const x=st.slots[s]; return x.rv!=null&&x.age>0&&isFinite(x.age)?x.age:Infinity; }));
    const SUBN={'HP':'HP','ATK':'攻撃','DEF':'防御','HP%':'HP%','ATK%':'攻撃%','DEF%':'防御%','ER':'チャージ','EM':'熟知','CR':'会心率','CD':'会心ダメ'}, effS=new Set(c.eff), BARS=true, RT=(window.CC2_OPT||{}).ov==='hdr'&&/^[EF]$/.test(LV)||LV==='G'?132:96, RH=(H-50-RT-(UPM==='strip'?40:0)-BRH)/5, SX=rx+44, bx0=SX, bx1=RE, BX=d=>bx0+ES(d)*(bx1-bx0), bw=(bx1-bx0)/EN;
    { const top=[st.age,...SLOTS.map(s=>st.slots[s].age)].filter(d=>d>0).reduce((m,d)=>{ let k0=0; for(let i=0;i<EN;i++) if(d>=EB[i]) k0=i; return Math.max(m,k0); },0); /* 百年級・有史以来は隠し要素：届いた部位か全体があるときだけ段の名前を出す（棒の点線の延長は残す） */
      if(BARS) for(let k=0;k<EN;k++) if(k<TIERS.length||k<=top) g+=TX(bx0+(k+.5)*bw,RT-1,ELB[k],{a:'middle',fs:8.5,fw:700,c:'#646d80'}); }
    SLOTS.forEach((s,k)=>{ const Y=RT+k*RH, x=st.slots[s], p=c.pieces[s], d=x.rv!=null&&x.age>0?x.age:0, eq=p&&p.main&&(p.subs||[]).some(q=>q.v!==''), lo=!eq&&c.low&&c.low[s]&&c.low[s].main?c.low[s]:null, pim=c.pimg&&c.pimg[s], y1=Y+(BRH?25:33);
      g+=LN(rx,Y+4,RE,Y+4,'#c9b98f',.12,1);
      const pp=eq?p:lo, rid=typeof RELICS!=='undefined'&&pp?(pp.setId||(pp.set&&RELICS[pp.set])||null):null, /* 部位ごとのセットが分かるときだけ絵を出す（4セットの名前からの推測はしない：自由枠の1個まで4セットに見えてしまうため） */ rimg=rid&&typeof RELIC_PART!=='undefined'?`icons/relic/${rid}_${RELIC_PART[s]}.webp`:null;
      g+=`<g transform="translate(${rx+16},${y1-5})">${pim?`<image href="${pim}" x="-15" y="-15" width="30" height="30" preserveAspectRatio="xMidYMid slice" clip-path="url(#ccP${k})"/>`:rimg?`<image href="${rimg}" x="-19" y="-19" width="38" height="38" preserveAspectRatio="xMidYMid meet"/>`:slotIcon(s,0,0,18,'#8a93a6')}${rimg&&!pim?'':`<circle r="15" fill="none" stroke="#c9b98f" stroke-opacity=".4" stroke-width="1"/>`}</g>`;
      g+=`<text x="${SX}" y="${y1}" font-family='${sans}' font-size="11" fill="#9aa6bb">${SLOT_JP[s]}<tspan dx="8" font-size="15" font-weight="700" fill="${eq?'#e6dfcf':lo?'#8a93a6':'#ff9b8a'}">${eq?esc(MAIN_SHORT(p.main)):lo?esc(MAIN_SHORT(lo.main)):'未装備'}</tspan>${UPM==='row'&&eq?`<tspan dx="14" font-size="10" fill="#8a93a6">1か月で更新 <tspan font-family='${mono}' font-size="11.5" font-weight="${PS[k]===PSB&&PSB>0?700:400}" fill="${PS[k]===PSB&&PSB>0?'#f3ead6':'#cfd4e6'}">${FPc(PS[k])}</tspan></tspan>`:''}</text>`;
      { const mt=eq?MAIN_SHORT(p.main):lo?MAIN_SHORT(lo.main):'未装備', MW=(t,f,fb)=>{ try{ const cx=(window.CC2_MCTX=window.CC2_MCTX||document.createElement('canvas').getContext('2d')); cx.font=f; return cx.measureText(t).width; }catch(e){ return fb; } }, /* 文字の実際の幅を測る（メインOPの右に注意書きを同じすき間で置くため） */
          tw=MW(SLOT_JP[s],`400 11px ${sans}`,[...SLOT_JP[s]].length*11)+8+MW(mt,`700 15px ${sans}`,[...mt].reduce((a2,ch)=>a2+(/[ -~]/.test(ch)?9:15),0)), wx=SX+tw+10, LVc='#ff6b5e';
        if(eq&&p.lv!=null&&+p.lv<20){ const ty=y1-4.5; g+=`<path d="M${f1r(wx+5)},${f1r(ty-5)} L${f1r(wx+10.4)},${f1r(ty+4.6)} L${f1r(wx-.4)},${f1r(ty+4.6)} Z" fill="${LVc}" stroke="${LVc}" stroke-width=".9" stroke-linejoin="round"/><text x="${f1r(wx+5)}" y="${f1r(ty+3.7)}" text-anchor="middle" font-family='${sans}' font-size="7.2" font-weight="900" fill="#14110a">!</text><text x="${f1r(wx+14.5)}" y="${y1}" font-family='${sans}' font-size="10" font-weight="700" fill="${LVc}">Lv.${+p.lv}${EST.has(s)?'（Lv.20の見込み）':''}</text>`; } /* +20未満の注意：赤い三角に「!」（書体に頼らず図形で）＋Lv.○（Lv.20の見込み） */
        if(lo) g+=`<text x="${f1r(wx)}" y="${y1}" font-family='${sans}' font-size="11" font-weight="700" fill="#8a93a6">★4<tspan dx="4" font-weight="400" font-size="10" fill="#6f7a8e">Lv.${lo.lv!=null?lo.lv:16}</tspan></text>`; }
      const BH0=22, b=lo?{s:`<text x="${RE}" y="${y1}" text-anchor="end" font-family='${sans}' font-size="10.5" fill="#6f7a8e">★4の聖遺物（${RANK_NAME}の対象外）</text>`,w:-1}:BADGE(RE,y1-5,BH0,d,{est:EST.has(s)}); g+=b.s; /* バッジの大きさ：全体と5部位で同じ。★4は対象外の一文だけ */
      { // 部位の秘境レベル（MONTHS）。window.CC2_OPT.mv：plain＝そのまま／type＝見出しの MONTHS と同じ字面に／next＝いちばん短い部位（次の狙い）に金の下線と札／both＝両方
        if(lo){} else { const MV=(window.CC2_OPT||{}).mv||'plain', TY=MV==='type'||MV==='both', NX=(MV==='next'||MV==='both')&&d>0&&d===NEXTD, fsV=TY?16.5:14, vx=RE-(b.w?b.w+10:0), vt=d>0?fmtAge(d):'—';
        g+=`<text x="${vx}" y="${y1}" text-anchor="end" font-family='${mono}' font-size="${fsV}" font-weight="${TY?700:600}" fill="${NX?'#f6e2a8':TY?'#f3ead6':'#d8d2c2'}">${d>0?VAL(d,fsV,vx):'—'}</text>`;
        if(NX){ const w=UTW(vt,fsV*.6,fsV); g+=LN(vx-w,y1+4,vx,y1+4,'#e9d39a',.9,1.2)+`<text x="${f1r(vx-w-8)}" y="${y1-1}" text-anchor="end" font-family='${sans}' font-size="9" font-weight="800" letter-spacing=".1em" fill="#e9d39a">次の狙い</text>`; } } }
      if(BARS){ const yb=y1+(BRH?14:19), xm=bx0+ES5*(bx1-bx0);
        g+=LN(bx0,yb,xm,yb,'#fff',.13,3,' stroke-linecap="round"')+LN(xm,yb,bx1,yb,'#fff',.22,1,' stroke-dasharray="2 3"');
        if(d>0) g+=LN(bx0,yb,BX(d),yb,CREAM,.78,3,' stroke-linecap="round"');
        for(let i=1;i<EN;i++){ const xt=bx0+i*bw; if(xt<=xm+.5) g+=LN(xt,yb-2.5,xt,yb+2.5,'#05060d',1,1.6); }
        if(d>0) g+=`<circle cx="${BX(d).toFixed(1)}" cy="${yb}" r="3.4" fill="#fff"/>`; }
      if(eq){ const subs=p.subs.filter(q=>q.s).map((q,i)=>[q,i]).sort((a2,b2)=>(effS.has(b2[0].s)-effS.has(a2[0].s))||(a2[1]-b2[1])).map(a2=>a2[0]), det=x.est&&x.est.ok?x.est.det:null, CW=(RE-SX)/4, ys=y1+(BRH?33:46);
        subs.forEach((q,i)=>{ const on=effS.has(q.s), dd=det&&det.find(z=>z.s===q.s), up=dd?dd.n-1:0, val=FLAT.has(q.s)?q.v:((parseFloat(q.v)||0).toFixed(1)+'%'); let xx=SX+i*CW;
          // 名前と値の下に、そのサブOPに入った回数ぶんの横長の箱：白抜き1個＝付いた（最初の1回）、塗った箱＝伸びた（強化）。右下の表の「付いた／伸びた」と同じ数え方
          g+=`<text x="${xx.toFixed(1)}" y="${ys}" font-family='${sans}' font-size="10.5" fill="${on?'#b8a77c':'#5f6879'}"${q.off?' opacity=".5"':''}>${SUBN[q.s]||q.s}<tspan dx="5" font-family='${mono}' font-size="11.5" fill="${on?'#e2d3a8':'#7a8396'}">${val}</tspan></text>`;
          if(dd){ const bc=on?'#d9c48e':'#6f7a8e', by=ys+5; for(let j=0;j<dd.n;j++){ const bx=xx+j*11; g+=j===0?`<rect x="${(bx+.5).toFixed(1)}" y="${by+.5}" width="8" height="3.2" rx=".6" fill="none" stroke="${bc}" stroke-opacity="${on?.85:.6}" stroke-width="1"/>`:`<rect x="${bx.toFixed(1)}" y="${by}" width="9" height="4.2" rx=".8" fill="${bc}" fill-opacity="${on?.95:.55}"/>`; } } }); } });
    if(UPM==='br'){ // 右下へ全部：左に「1か月で更新できる見込み」、右に「有効OPごとの伸び」
      /* 2.10 の試作（window.CC2_OPT.pb）：now＝左に「1か月で更新できる見込み」（本番）／U＝左に「パラメータの実際の値」（UID で取り込んだキャラ全体の値 uidStat＝ゲームのキャラ画面の値。行＝有効OPに対応する値＋そのキャラの元素ダメ。式が登録されたら、ここに理想を重ねる）。
         聖遺物の分の値の合計（A）・右の表に合計の列（C）は試してやめた（値の合計はノイズ） */
      const PB=(window.CC2_OPT||{}).pb||'now';
      const y0=H-50-BRH+16, /* 5部位の行とのあいだに余白（区切りの線はやめ、見出しのチップで区切る） */ LX=rx, LX1=rx+226, TXa=RE-226, TXb=RE, /* 左右の段を同じ幅（226）に、真ん中の縦線は中央 */ SECr=(t,x,y)=>CHIP(t,x,y), BARr=(x0,x1,y,f)=>LN(x0,y,x1,y,'#fff',.12,2,' stroke-linecap="round"')+(f>0?LN(x0,y,x0+(x1-x0)*Math.min(1,f),y,CREAM,.8,2,' stroke-linecap="round"'):'');
      g+=LN((rx+RE)/2,y0+8,(rx+RE)/2,H-56,'#c9b98f',.12,1);
      if(['B2','B3','P2','P1','PX','BX'].includes(PB)){ /* 横棒（2.10 の試作）：単位は「サブOP何回分」（伸びた量 ÷ サブOP 1回の最大の伸び）。会心率：会心ダメ＝1：2 が同じ長さになる。
          全体＝UID のキャラ画面の値から最初からある分（会心率5%・会心ダメ50%・チャージ100%）を引く。HP・攻撃・防御は「基礎の何%増えたか」。元素ダメは攻撃%と同じ 5.83 で割る。
          棒の内訳：聖遺物（5部位のメイン＋サブ。B3 はサブだけ色を変える＝右の表と同じ量）／それ以外（武器・突破・セット効果など＝全体−聖遺物） */
        /* 2026-11-23：仕上げ（PX・BX）は**聖遺物の分だけ**（5部位のメインOP＋サブOP。UID は要らない）。8種類（HP%・攻撃%・防御%・熟知・チャージ・元素ダメ・会心率・会心ダメ）を
           サブOP 1回の最大の伸びで割って回数に直し、割合にする（メインOP +20 はどれもちょうど8回分。元素ダメのメイン 46.6 は攻撃%と同じなので 5.83 で割る）。実数（HP・攻撃・防御）は入れない。
           出すのは有効OPに入っている%のパラメータ＋そのキャラの元素ダメ。武器・突破・セット効果は、理想（c.idealRoll）の計算の側で吸収する（docs/HANDOFF_BALANCE.md） */
        const ART=PB==='PX'||PB==='BX', IN=14, us=c.uidStat, fp=(us&&us.fp)||(ART?{}:null), bs=(us&&us.base)||{}; g+=SECr(ART?'聖遺物のパラメータの割合':PB[0]==='P'?'パラメータの割合':'パラメータ（サブOP何回分）',LX+IN,y0+18);
        if(!fp) g+=`<text x="${LX+IN}" y="${y0+62}" font-family='${sans}' font-size="10.5" fill="#6f7a8e">UIDで取り込むと、ここに</text><text x="${LX+IN}" y="${y0+78}" font-family='${sans}' font-size="10.5" fill="#6f7a8e">キャラ全体の釣り合い（武器・突破込み）</text>`;
        else { const EL=typeof skyElem==='function'?skyElem(c):'?', MAP={'HP%':'HP',HP:'HP','ATK%':'ATK',ATK:'ATK','DEF%':'DEF',DEF:'DEF',CR:'CR',CD:'CD',ER:'ER',EM:'EM'}, ORD=['HP','ATK','DEF','CR','CD','ER','EM'],
            U1={HP:5.83,ATK:5.83,DEF:7.29,CR:3.89,CD:7.77,ER:6.48,EM:23.31}, B0={CR:5,CD:50,ER:100,EM:0}, ks=ART?ORD.filter(k=>(c.eff||[]).includes(['HP','ATK','DEF'].includes(k)?k+'%':k)):ORD.filter(k=>(c.eff||[]).some(e=>MAP[e]===k)); if(ART||fp['DMG_'+EL]!=null) ks.push('DMG_'+EL);
          const art=k=>{ let m=0,u=0; SLOTS.forEach(s2=>{ const pc=c.pieces[s2]; if(!pc||!pc.main) return; const F3=['HP','ATK','DEF'].includes(k), add=(key,v,sub)=>{ const r=key===k+'%'?v:key===k?(F3?(ART?null:bs[k]?v/bs[k]*100:0):v):null; /* HP・攻撃・防御の実数は基礎の%に直す */ if(r!=null){ if(sub) u+=r; else m+=r; } };
              add(pc.main,MAIN_NUM[pc.main]!=null?MAIN_NUM[pc.main]:(String(pc.main).startsWith('DMG_')?46.6:0),0); (pc.subs||[]).forEach(q=>{ if(q.s&&!q.off) add(q.s,parseFloat(q.v)||0,1); }); }); return {m,u}; };
          const rows=ks.map(k=>{ const dm=k.startsWith('DMG_'), u1=dm?5.83:U1[k], a=art(k), tot=ART?a.m+a.u:dm?fp[k]:['HP','ATK','DEF'].includes(k)?(bs[k]?(fp[k]/bs[k]-1)*100:null):(fp[k]||0)-B0[k];
            return {k,tot:tot==null?null:tot/u1,m:a.m/u1,u:a.u/u1}; });
          /* 理想：c.idealRoll＝理想の配分を同じ単位（サブOP何回分）で。仕上げ（PX・BX）では聖遺物の分だけの理想（武器・突破・セット効果は理想の計算の側で吸収）。B2・B3 はキャラ全体の理想。キーがないパラメータ（アタッカーのチャージなど）は図から外す。
             いまは見本だけ（値は仮）。window.CC2_OPT.ib：tick＝棒に縦の目印／ghost＝理想の長さの枠 */
          const ID=c.idealRoll||null, IB=(window.CC2_OPT||{}).ib||'tick';
          if(PB==='PX'||PB==='BX'){ /* 仕上げの試作（2.10）：PX＝円（今の輪＋外の軌道に理想の境目を星で）／BX＝100%の帯（今の帯＋上の細い線に理想の境目を星で、星から今の境目へ細い線）。割合だけを事実として。
              理想（c.idealRoll）がないキャラは、今の輪／帯と今の割合だけ（チャージも入れる。役割が分からないため）。
              window.CC2_OPT.ie＝理想の目立たせ方：n＝控えめ／s＝星を大きく光らせ、線と理想の数字を明るく／r＝s に加えて理想の割合を細い輪（帯）でも描く */
            const IE=(window.CC2_OPT||{}).ie||'s', ST=ID&&IE!=='n', RG=ID&&IE==='r';
            const PR=rows.filter(r=>r.tot!=null&&(!ID||ID[r.k]!=null)), sum=PR.reduce((a,r)=>a+Math.max(0,r.tot),0)||1, isum=ID?PR.reduce((a,r)=>a+ID[r.k],0)||1:1, GD='#e9d39a',
              COL={HP:'#7cc6a8',ATK:'#e0866a',DEF:'#c2b08a',CR:'#f2dfa0',CD:'#d39a4c',ER:'#9aa8e6',EM:'#a5cf7e'}, colOf=k=>COL[k]||(typeof SKY_EL!=='undefined'&&SKY_EL[k.slice(4)])||'#8a93a6',
              NM={HP:'HP',ATK:'攻撃',DEF:'防御',CR:'会心率',CD:'会心ダメ',ER:'チャージ',EM:'熟知'}, nm=k=>NM[k]||(k.startsWith('DMG_')?k.slice(4)+'ダメ':k), /* 狭いので元素ダメは「水ダメ」の形に */
              STAR=(x,y,r,col,op)=>`<path d="M${f1r(x)},${f1r(y-r)} Q${f1r(x)},${f1r(y)} ${f1r(x+r)},${f1r(y)} Q${f1r(x)},${f1r(y)} ${f1r(x)},${f1r(y+r)} Q${f1r(x)},${f1r(y)} ${f1r(x-r)},${f1r(y)} Q${f1r(x)},${f1r(y)} ${f1r(x)},${f1r(y-r)} Z" fill="${col}" fill-opacity="${op==null?1:op}"/>`,
              ISTAR=(x,y)=>ST?`<circle cx="${f1r(x)}" cy="${f1r(y)}" r="6.5" fill="${GD}" opacity=".45" filter="url(#c2PG)"/>`+STAR(x,y,6.4,'#05060d')+STAR(x,y,5.4,'#fff6d8'):STAR(x,y,4.6,'#05060d')+STAR(x,y,3.6,GD),
              LOP=ST?.9:.5, LW=ST?1.1:.8, ICOL=ST?GD:GD, IOP=ST?1:.85, IFS=ST?11:10;
            let a=0, ai=0; PR.forEach(r=>{ r.f=Math.max(0,r.tot)/sum; r.fi=ID?ID[r.k]/isum:0; r.a0=a; r.i0=ai; a+=r.f; ai+=r.fi; });
            g+=`<defs><filter id="c2PG" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3.2"/></filter></defs>`;
            const PCT=(v,fs,col)=>`${Math.round(v*100)}<tspan font-size="${(fs*.66).toFixed(1)}" font-weight="400" fill="${col||'#8a93a6'}" dx=".5">%</tspan>`;
            if(PB==='PX'){ const cx=LX+IN+40, cy=y0+90, R0=33, RW=9, RO=46, TAU=Math.PI*2, P=(r,t)=>[cx+r*Math.sin(t*TAU), cy-r*Math.cos(t*TAU)], gap=.012,
                arc=(r,t0,t1,w,col,op)=>{ if(t1-t0<=gap) return ''; const [x0,y0b]=P(r,t0+gap/2), [x1,y1b]=P(r,t1-gap/2); return `<path d="M${f1r(x0)},${f1r(y0b)} A${r},${r} 0 ${t1-t0>.5?1:0} 1 ${f1r(x1)},${f1r(y1b)}" fill="none" stroke="${col}" stroke-opacity="${op}" stroke-width="${w}"/>`; };
              /* 外の軌道（文字盤のような細い線と5%ごとの目盛り） */
              g+=`<circle cx="${cx}" cy="${cy}" r="${RO}" fill="none" stroke="${GD}" stroke-opacity="${ST?.38:.22}" stroke-width=".8"/>`+(RG?'':`<circle cx="${cx}" cy="${cy}" r="${R0-RW/2-4}" fill="none" stroke="${GD}" stroke-opacity=".12" stroke-width=".6"/>`);
              for(let i=0;i<20;i++){ const L=i%5===0?3.2:1.6, [xa,ya]=P(RO,i/20), [xb,yb2]=P(RO+L,i/20); g+=`<path d="M${f1r(xa)},${f1r(ya)} L${f1r(xb)},${f1r(yb2)}" stroke="${GD}" stroke-opacity="${i%5===0?.45:.25}" stroke-width=".8"/>`; }
              /* 今の輪：ぼかした光＋本体＋外側のつや */
              PR.forEach(r=>{ const col=colOf(r.k); g+=`<g filter="url(#c2PG)" opacity=".55">${arc(R0,r.a0,r.a0+r.f,RW,col,1)}</g>`+arc(R0,r.a0,r.a0+r.f,RW,col,.95)+arc(R0+RW/2-1,r.a0,r.a0+r.f,1.4,'#fff',.28); });
              if(RG) PR.forEach(r=>{ g+=arc(R0-RW/2-5,r.i0,r.i0+r.fi,3,colOf(r.k),.8); }); /* 内側に理想の細い輪 */
              /* 理想の境目：軌道の上に星、輪の外側まで細い線 */
              if(ID) PR.forEach(r=>{ const t=r.i0, [xs,ys]=P(RO,t), [xa,ya]=P(R0+RW/2+1,t); g+=`<path d="M${f1r(xa)},${f1r(ya)} L${f1r(xs)},${f1r(ys)}" stroke="${GD}" stroke-opacity="${LOP}" stroke-width="${LW}"/>`+ISTAR(xs,ys); });
              g+=`<text x="${cx}" y="${cy+(ID&&!RG?-1:3)}" text-anchor="middle" font-family='${sans}' font-size="${RG?6:7}" font-weight="700" letter-spacing="${RG?'.14em':'.22em'}" fill="${GD}" fill-opacity=".8">BALANCE</text>`+(ID&&!RG?`<text x="${cx}" y="${cy+10}" text-anchor="middle" font-family='${sans}' font-size="7.5" fill="#8a93a6">輪＝今</text>`:'');
              const lx=LX+IN+94, ly0=y0+52, LRS=PR.length>5?14:PR.length>4?16:19, xn=ID?LX1-36:LX1-6;
              if(ID) g+=`<text x="${xn}" y="${y0+35}" text-anchor="end" font-family='${sans}' font-size="8" letter-spacing=".1em" fill="#6f7a8e">今</text>`+STAR(LX1-27,y0+32,ST?3.6:3,GD,ST?1:.8)+`<text x="${LX1-6}" y="${y0+35}" text-anchor="end" font-family='${sans}' font-size="8" fill="${ST?GD:'#6f7a8e'}">理想</text>`;
              PR.forEach((r,ri)=>{ const y=ly0+ri*LRS; g+=`<rect x="${lx}" y="${y-8}" width="2.6" height="10" rx="1.3" fill="${colOf(r.k)}"/><text x="${lx+7}" y="${y}" font-family='${sans}' font-size="10" font-weight="700" fill="#e6dfcf">${nm(r.k)}</text><text x="${xn}" y="${y}" text-anchor="end" font-family='${mono}' font-size="12.5" font-weight="700" fill="#f3ead6">${PCT(r.f,12.5)}</text>`+(ID?`<text x="${LX1-6}" y="${y}" text-anchor="end" font-family='${mono}' font-size="${IFS}" font-weight="${ST?700:400}" fill="${ICOL}" fill-opacity="${IOP}">${PCT(r.fi,IFS,'#8a7d5c')}</text>`:''); }); }
            else { const x0=LX+IN, x1=LX1-6, W=x1-x0, yh=y0+42, yb=y0+58, BH=11, X=t=>x0+t*W, gp=1.2;
              g+=`<defs><clipPath id="c2BC"><rect x="${x0}" y="${yb}" width="${W}" height="${BH}" rx="${BH/2}"/></clipPath><clipPath id="c2BI"><rect x="${x0}" y="${yh-1.5}" width="${W}" height="3" rx="1.5"/></clipPath></defs>`;
              if(ID){ /* 上の細い線（理想）：左右の端に小さな目盛り、境目に星。星から今の境目へ細い線。r は細い線の代わりに理想の割合の細い帯 */
                g+=RG?`<g clip-path="url(#c2BI)">`+PR.map(r=>`<rect x="${f1r(X(r.i0)+(r.i0>0?.6:0))}" y="${yh-1.5}" width="${f1r(Math.max(0,X(r.i0+r.fi)-X(r.i0)-1.2))}" height="3" fill="${colOf(r.k)}" fill-opacity=".85"/>`).join('')+`</g>`:LN(x0,yh,x1,yh,GD,ST?.5:.3,.8)+LN(x0,yh-2.5,x0,yh+2.5,GD,.4,.8)+LN(x1,yh-2.5,x1,yh+2.5,GD,.4,.8);
                PR.slice(1).forEach(r=>{ const xi=X(r.i0), xa=X(r.a0); g+=`<path d="M${f1r(xi)},${yh+3} C${f1r(xi)},${yh+9} ${f1r(xa)},${yb-8} ${f1r(xa)},${yb-1.5}" fill="none" stroke="${GD}" stroke-opacity="${LOP}" stroke-width="${LW}"/>`; }); }
              g+=`<g filter="url(#c2PG)" opacity=".5">`+PR.map(r=>`<rect x="${f1r(X(r.a0))}" y="${yb+1}" width="${f1r(X(r.a0+r.f)-X(r.a0))}" height="${BH-2}" fill="${colOf(r.k)}"/>`).join('')+`</g>`; /* 帯の後ろのぼかした光 */
              g+=`<g clip-path="url(#c2BC)">`+PR.map(r=>{ const col=colOf(r.k), xa=X(r.a0)+(r.a0>0?gp/2:0), xb=X(r.a0+r.f)-(r.a0+r.f<.999?gp/2:0); return xb>xa?`<rect x="${f1r(xa)}" y="${yb}" width="${f1r(xb-xa)}" height="${BH}" fill="${col}" fill-opacity=".95"/><rect x="${f1r(xa)}" y="${yb}" width="${f1r(xb-xa)}" height="${(BH*.42).toFixed(1)}" fill="#fff" fill-opacity=".16"/>`:''; }).join('')+`</g>`;
              if(ID) PR.slice(1).forEach(r=>{ g+=ISTAR(X(r.i0),yh); });
              g+=`<text x="${x0}" y="${yh-(ST?9:6)}" font-family='${sans}' font-size="7" font-weight="700" letter-spacing=".22em" fill="${GD}" fill-opacity=".8">BALANCE</text>`+(ID?STAR(x1-52,yh-(ST?11.5:8.5),ST?3.6:3,GD,ST?1:.8)+`<text x="${x1-32}" y="${yh-(ST?9:6)}" text-anchor="end" font-family='${sans}' font-size="8" fill="${ST?GD:'#6f7a8e'}">理想</text><text x="${x1}" y="${yh-(ST?9:6)}" text-anchor="end" font-family='${sans}' font-size="8" fill="#6f7a8e">帯＝今</text>`:'');
              /* 帯の下：2列の凡例（色・名前・今・理想） */
              const ly0=yb+BH+22, LRS=PR.length>4?16:18;
              PR.forEach((r,ri)=>{ const x=x0+(ri%2?112:0), y=ly0+Math.floor(ri/2)*LRS, xr=ri%2?x1:x0+102, xn=ID?xr-23:xr; g+=`<rect x="${x}" y="${y-8}" width="2.6" height="10" rx="1.3" fill="${colOf(r.k)}"/><text x="${x+7}" y="${y}" font-family='${sans}' font-size="10" font-weight="700" fill="#e6dfcf">${nm(r.k)}</text><text x="${xn}" y="${y}" text-anchor="end" font-family='${mono}' font-size="12" font-weight="700" fill="#f3ead6">${PCT(r.f,12)}</text>`+(ID?`<text x="${xr}" y="${y}" text-anchor="end" font-family='${mono}' font-size="${IFS-.5}" font-weight="${ST?700:400}" fill="${ICOL}" fill-opacity="${IOP}">${PCT(r.fi,IFS-.5,'#8a7d5c')}</text>`:''); }); }
          } else if(PB[0]==='P'){ /* 円グラフ（2.10 の試作）：振り分けの割合だけ（量や運は消える）。P2＝二重の輪（外＝今、内＝理想）／P1＝今の輪に理想の境目を金の刻みで。
              割合は「サブOP何回分（全体）」の合計に対する各パラメータの割合。理想があるときは理想に入っているパラメータだけ（チャージはアタッカーでは外す）。勧めの言葉は出さず、事実（今と理想の割合）だけ */
            const PR=rows.filter(r=>r.tot!=null&&(!ID||ID[r.k]!=null)), sum=PR.reduce((a,r)=>a+Math.max(0,r.tot),0)||1, isum=ID?PR.reduce((a,r)=>a+ID[r.k],0)||1:1,
              COL={HP:'#7ec4a4',ATK:'#d77a5f',DEF:'#b0a27a',CR:'#f3e2a8',CD:'#c98a3d',ER:'#8c9bd6',EM:'#9cc77a'}, colOf=k=>COL[k]||(typeof SKY_EL!=='undefined'&&SKY_EL[k.slice(4)])||'#8a93a6',
              cx=LX+IN+36, cy=y0+88, TAU=Math.PI*2, gap=.035, arc=(r,a0,a1,w,col,op)=>{ if(a1-a0<=gap) return ''; const b0=a0+gap/2, b1=a1-gap/2, P=a=>`${(cx+r*Math.sin(a)).toFixed(1)},${(cy-r*Math.cos(a)).toFixed(1)}`; return `<path d="M${P(b0)} A${r},${r} 0 ${b1-b0>Math.PI?1:0} 1 ${P(b1)}" fill="none" stroke="${col}" stroke-opacity="${op}" stroke-width="${w}"/>`; };
            let a=0, ai=0; const NM={HP:'HP',ATK:'攻撃',DEF:'防御',CR:'会心率',CD:'会心ダメ',ER:'チャージ',EM:'熟知'};
            PR.forEach(r=>{ const f=Math.max(0,r.tot)/sum, fi=ID?ID[r.k]/isum:0, col=colOf(r.k);
              if(PB==='P2'){ g+=arc(41,a*TAU,(a+f)*TAU,8,col,.95); if(ID) g+=arc(29,ai*TAU,(ai+fi)*TAU,5,col,.55); }
              else g+=arc(37,a*TAU,(a+f)*TAU,11,col,.95);
              r.f=f; r.fi=fi; a+=f; ai+=fi; });
            if(PB==='P1'&&ID){ let t=0; PR.forEach(r=>{ t+=r.fi; const A=t*TAU, P=rr=>`${(cx+rr*Math.sin(A)).toFixed(1)},${(cy-rr*Math.cos(A)).toFixed(1)}`; g+=`<path d="M${P(28)} L${P(48)}" stroke="#05060d" stroke-width="3.2"/><path d="M${P(28)} L${P(48)}" stroke="#e9d39a" stroke-width="1.4"/>`; }); }
            if(ID) g+=`<text x="${cx}" y="${cy+3}" text-anchor="middle" font-family='${sans}' font-size="8" fill="#8a93a6">${PB==='P2'?'外 今':'輪 今'}</text><text x="${cx}" y="${cy+14}" text-anchor="middle" font-family='${sans}' font-size="8" fill="#8a93a6">${PB==='P2'?'内 理想':'刻み 理想'}</text>`;
            const lx=cx+52, ly0=y0+51, LRS=PR.length>4?16:18;
            if(ID) g+=`<text x="${LX1-34}" y="${y0+36}" text-anchor="end" font-family='${sans}' font-size="8.5" fill="#6f7a8e">今</text><text x="${LX1-6}" y="${y0+36}" text-anchor="end" font-family='${sans}' font-size="8.5" fill="#6f7a8e">理想</text>`;
            PR.forEach((r,ri)=>{ const y=ly0+ri*LRS; g+=`<circle cx="${lx+3}" cy="${y-4}" r="3" fill="${colOf(r.k)}"/><text x="${lx+11}" y="${y}" font-family='${sans}' font-size="10" font-weight="700" fill="#d9c48e">${NM[r.k]||(r.k.startsWith('DMG_')?r.k.slice(4)+'元素ダメ':r.k)}</text><text x="${ID?LX1-34:LX1-6}" y="${y}" text-anchor="end" font-family='${mono}' font-size="12" font-weight="700" fill="#f3ead6">${Math.round(r.f*100)}<tspan font-size="8.5" font-weight="400" fill="#8a93a6">%</tspan></text>`+(ID?`<text x="${LX1-6}" y="${y}" text-anchor="end" font-family='${mono}' font-size="10.5" fill="#9aa6bb">${Math.round(r.fi*100)}<tspan font-size="8" fill="#6f7a8e">%</tspan></text>`:''); });
          } else {
          const mx=Math.max(10,...rows.map(r=>r.tot||0),...(ID?rows.map(r=>ID[r.k]||0):[])), top=Math.ceil(mx/5)*5, NM={HP:'HP',ATK:'攻撃',DEF:'防御',CR:'会心率',CD:'会心ダメ',ER:'チャージ',EM:'熟知'}, RS=rows.length>5?15:17, bx0c=LX+IN+58, bx1c=LX1-(ID?64:38), BXc=v=>bx0c+Math.min(1,Math.max(0,v)/top)*(bx1c-bx0c);
          const CO='#5f6c86', CM='#b8a77c', CU=CREAM, y1r=y0+(rows.length>5?47:51);
          for(let t=5;t<top;t+=5) g+=LN(BXc(t),y1r-9,BXc(t),y1r+(rows.length-1)*RS+3,'#fff',.08,1);
          g+=`<text x="${bx1c}" y="${y0+33}" text-anchor="end" font-family='${mono}' font-size="8.5" fill="#6f7a8e">${top}回</text>`;
          rows.forEach((r,ri)=>{ const y=y1r+ri*RS, yb=y-4; g+=`<text x="${LX+IN}" y="${y}" font-family='${sans}' font-size="11" font-weight="700" fill="#d9c48e">${NM[r.k]||(r.k.startsWith('DMG_')?r.k.slice(4)+'元素ダメ':r.k)}</text>`;
            if(r.tot==null){ g+=`<text x="${LX1-6}" y="${y}" text-anchor="end" font-family='${sans}' font-size="9.5" fill="#6f7a8e">取り込み直すと出ます</text>`; return; }
            const a=Math.min(r.tot,r.m+r.u), o=Math.max(0,r.tot-a), xa=BXc(o), BW=6, seg=(x0,x1,col,op)=>x1-x0>.3?`<rect x="${x0.toFixed(1)}" y="${(yb-BW/2).toFixed(1)}" width="${(x1-x0).toFixed(1)}" height="${BW}" fill="${col}" fill-opacity="${op}"/>`:'';
            g+=LN(bx0c,yb,bx1c,yb,'#fff',.07,BW);
            g+=seg(bx0c,xa,CO,.9); if(PB==='B3'){ const xm=BXc(o+Math.min(a,r.m)); g+=seg(xa,xm,CM,.85)+seg(xm,BXc(r.tot),CU,.95); } else g+=seg(xa,BXc(r.tot),CU,.9);
            const iv=ID?ID[r.k]:null, GD='#e9d39a';
            if(iv!=null){ const xi=BXc(iv); g+=IB==='ghost'?`<rect x="${bx0c-1.5}" y="${(yb-BW/2-2).toFixed(1)}" width="${(xi-bx0c+3).toFixed(1)}" height="${BW+4}" rx="1.5" fill="none" stroke="${GD}" stroke-opacity=".85" stroke-width="1"/>`:LN(xi,yb-6,xi,yb+6,'#05060d',1,3.6)+LN(xi,yb-6,xi,yb+6,GD,1,1.8); }
            g+=`<text x="${ID?LX1-34:LX1-6}" y="${y}" text-anchor="end" font-family='${mono}' font-size="12" font-weight="700" fill="${ID&&iv==null?'#8a93a6':'#f3ead6'}">${r.tot.toFixed(1)}</text>`;
            if(iv!=null){ const df=r.tot-iv, ok=Math.abs(df)<.5; g+=`<text x="${LX1-4}" y="${y}" text-anchor="end" font-family='${mono}' font-size="10" font-weight="700" fill="${ok?GD:df<0?'#ff9b8a':'#8a93a6'}">${ok?'±0':(df>0?'+':'−')+Math.abs(df).toFixed(1)}</text>`; } });
          const ly=y1r+(rows.length-1)*RS+16, LG=(x,col,t)=>`<rect x="${x}" y="${ly-6}" width="8" height="5" fill="${col}"/><text x="${x+11}" y="${ly}" font-family='${sans}' font-size="8.5" fill="#8a93a6">${t}</text>`;
          g+=LG(LX+IN,CO,'聖遺物以外')+(PB==='B3'?LG(LX+IN+62,CM,'メイン')+LG(LX+IN+104,CU,'サブ'):LG(LX+IN+62,CU,'聖遺物'))
            +(ID?(IB==='ghost'?`<rect x="${LX+IN+142}" y="${ly-7}" width="10" height="7" rx="1" fill="none" stroke="#e9d39a" stroke-width="1"/>`:LN(LX+IN+147,ly-8,LX+IN+147,ly+1,'#e9d39a',1,1.8))+`<text x="${LX+IN+156}" y="${ly}" font-family='${sans}' font-size="8.5" fill="#8a93a6">理想（無凸餅）</text>`:''); } } }
      else if(PB==='U'){ const IN=14, us=c.uidStat, fp=us&&us.fp;
        g+=SECr('パラメータ（実際の値）',LX+IN,y0+18);
        if(!fp) g+=`<text x="${LX+IN}" y="${y0+62}" font-family='${sans}' font-size="10.5" fill="#6f7a8e">UIDで取り込むと、ここに</text><text x="${LX+IN}" y="${y0+78}" font-family='${sans}' font-size="10.5" fill="#6f7a8e">キャラ全体の値（武器・突破込み）</text>`;
        else { const EL=typeof skyElem==='function'?skyElem(c):'?', MAP={'HP%':'HP',HP:'HP','ATK%':'ATK',ATK:'ATK','DEF%':'DEF',DEF:'DEF',CR:'CR',CD:'CD',ER:'ER',EM:'EM'}, ORD=['HP','ATK','DEF','CR','CD','ER','EM'];
          const ks=ORD.filter(k=>(c.eff||[]).some(e=>MAP[e]===k)), rows=ks.map(k=>[k,fp[k]||0]); if(fp['DMG_'+EL]!=null) rows.push(['DMG_'+EL,fp['DMG_'+EL]]);
          const NM={HP:'HP上限',ATK:'攻撃力',DEF:'防御力',CR:'会心率',CD:'会心ダメージ',ER:'元素チャージ効率',EM:'元素熟知'}, fmt=(k,v)=>['HP','ATK','DEF','EM'].includes(k)?Math.round(v).toLocaleString('en-US'):(+v).toFixed(1)+'%', RS=rows.length>5?15:17;
          rows.forEach(([k,v],ri)=>{ const y=y0+(rows.length>5?47:51)+ri*RS; g+=`<text x="${LX+IN}" y="${y}" font-family='${sans}' font-size="11" font-weight="700" fill="#d9c48e">${NM[k]||(k.startsWith('DMG_')?k.slice(4)+'元素ダメージ':k)}</text><text x="${LX1-6}" y="${y}" text-anchor="end" font-family='${mono}' font-size="12.5" font-weight="700" fill="#f3ead6">${fmt(k,v)}</text>`; }); } }
      else { // 左の列：大きな確率（どこか1部位でも）。右の列：5部位を縦に（アイコン・確率・棒）、右の表と同じ行の間隔
        const IN=14, RY=j=>y0+51+j*17, cx2=LX+IN+88, bx0b=cx2+48, bx1b=LX1-6; /* チップと大きな確率を少し右へ、棒は短く（段の右端はそのまま） */
        g+=SECr('1か月で更新できる見込み',LX+IN,y0+18)+`<text x="${LX+IN}" y="${y0+66}" font-family='${mono}' font-size="30" font-weight="700" fill="#f3ead6">${FPc(PA)}</text><text x="${LX+IN}" y="${y0+84}" font-family='${sans}' font-size="9.5" fill="#8a93a6">どこか1部位でも</text>`;
        SLOTS.forEach((s2,j)=>{ const y=RY(j), b=PS[j]===PSB&&PSB>0; g+=slotIcon(s2,cx2+6,y-4,11,b?'#f3ead6':'#8a93a6')+`<text x="${cx2+42}" y="${y}" text-anchor="end" font-family='${mono}' font-size="11" font-weight="${b?700:400}" fill="${b?'#f3ead6':'#9aa6bb'}">${FPc(PS[j])}</text>`+BARr(bx0b,bx1b,y-4,PS[j]); }); }
      { // 有効OPごとの伸び：合計・付いた（そのサブOPが付いた部位／付きうる部位。メインOPと同じ部位は付かない）・伸びた（強化で伸びた回数。最初の1回は除く）・1回の伸び。初期の運（どれが付いたか）と強化の運（どこが伸びたか）を別々に数える
        const effL=(c.eff||[]).filter(k=>ROLL[k]).slice(0,4), effAll=(c.eff||[]).filter(k=>ROLL[k]), cols=[TXa,null,TXa+112,TXa+168,TXb]; /* サブOPの名前と「付いた」の間を詰める */ let UP=0,UA=0,NA=0,UU=0,AT=0,AM=0; /* cols[1] は使わない（合計の列はやめた：伸びた値の合計はノイズ） */
        SLOTS.forEach(s2=>{ const x=st.slots[s2], pc=c.pieces[s2]; if(x.est&&x.est.ok) UA+=x.est.four?5:4; if(pc&&pc.main&&pc.subs&&pc.subs.some(q=>q.v!=='')){ AM+=Math.min(4,effAll.filter(k=>k!==pc.main).length); AT+=effAll.filter(k=>pc.subs.some(q=>q.s===k&&!q.off)).length; } });
        g+=SECr('有効OPごとの伸び（5部位の合計）',TXa,y0+18)+[['付いた',cols[2]],['伸びた',cols[3]],['1回の伸び',cols[4]]].map(([t,x])=>`<text x="${f1r(x)}" y="${y0+33}" text-anchor="end" font-family='${sans}' font-size="8.5" fill="#6f7a8e">${t}</text>`).join('');
        effL.forEach((k,ri)=>{ let v=0,n=0,u=0,up=0,at=0,am=0; SLOTS.forEach(s2=>{ const pc=c.pieces[s2], x=st.slots[s2]; if(!pc||!pc.subs||!pc.main) return; if(pc.main!==k) am++; const q=pc.subs.find(z=>z.s===k&&!z.off); if(q){ v+=parseFloat(q.v)||0; at++; } const dd=x.est&&x.est.ok&&x.est.det.find(z=>z.s===k); if(dd){ n+=dd.n; u+=dd.u; up+=dd.n-1; } });
          UP+=up; NA+=n; UU+=u; const y=y0+51+ri*17, vt=!FLAT.has(k)?v.toFixed(1)+'%':Math.round(v).toLocaleString('en-US');
          g+=`<text x="${cols[0]}" y="${y}" font-family='${sans}' font-size="11.5" font-weight="700" fill="#d9c48e">${SUBN[k]||k}</text><text x="${f1r(cols[2])}" y="${y}" text-anchor="end" font-family='${mono}' font-size="12" font-weight="700" fill="#f3ead6">${at}<tspan font-weight="400" fill="#6f7a8e">/${am}</tspan></text><text x="${f1r(cols[3])}" y="${y}" text-anchor="end" font-family='${mono}' font-size="12" font-weight="700" fill="#f3ead6">${up}<tspan font-weight="400" font-size="10" fill="#8a93a6">回</tspan></text><text x="${cols[4]}" y="${y}" text-anchor="end" font-family='${mono}' font-size="11.5" fill="#cfd4e6">${n?Math.round(u*10/n)+'%':'—'}</text>`; });
        const yt=y0+51+effL.length*17+6; g+=LN(TXa,yt-12,TXb,yt-12,'#fff',.15,1)+`<text x="${TXa}" y="${yt}" font-family='${sans}' font-size="11" font-weight="700" fill="#9aa6bb">合計</text><text x="${f1r(cols[2])}" y="${yt}" text-anchor="end" font-family='${mono}' font-size="11.5" font-weight="700" fill="#f3ead6">${AT}<tspan font-weight="400" fill="#8a93a6">/${AM}</tspan></text><text x="${f1r(cols[3])}" y="${yt}" text-anchor="end" font-family='${mono}' font-size="11.5" font-weight="700" fill="#f3ead6">${UP}<tspan font-weight="400" fill="#8a93a6">/${UA}回</tspan></text><text x="${cols[4]}" y="${yt}" text-anchor="end" font-family='${mono}' font-size="11.5" font-weight="700" fill="#f3ead6">${NA?Math.round(UU*10/NA)+'%':'—'}</text>`
; } } /* 表の下の説明2行はやめた（アプリの説明へ） */
    if(UPM==='strip'){ // 右下に1行の帯：これから1か月で更新できる見込み（全体の確率＋部位ごと）
      const y0=H-50-38, cw=(RE-(rx+236))/5; g+=LN(rx,y0+4,RE,y0+4,'#c9b98f',.12,1)+`<text x="${rx}" y="${y0+27}" font-family='${sans}' font-size="11" fill="#9aa6bb">1か月で更新できる見込み<tspan dx="10" font-family='${mono}' font-size="20" font-weight="700" fill="#f3ead6">${FPc(PA)}</tspan></text>`;
      SLOTS.forEach((s2,j)=>{ const x=rx+236+j*cw, b=PS[j]===PSB&&PSB>0; g+=slotIcon(s2,x+7,y0+22,13,b?'#f3ead6':'#8a93a6')+`<text x="${x+18}" y="${y0+27}" font-family='${mono}' font-size="12" font-weight="${b?700:400}" fill="${b?'#f3ead6':'#9aa6bb'}">${FPc(PS[j])}</text>`; }); }
    // ---- 左：全体＝秘境レベルの物差し（上限つき）と、その印の横に全体の★と値（1秒目）。印・線は白系 ----
    const MARK=(x,y)=>`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="7" fill="#fff" opacity=".35" filter="url(#ccGl)"/><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.6" fill="#fff"/>`;
    const REL_T=`原神のリリースから毎日回ると <tspan font-family='${mono}' font-weight="700" fill="${RELC}">${UHT(fmtAge(REL),8.5,null)}</tspan>`;
    g+=`<defs><filter id="c2Blur" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="9"/></filter></defs>`;
    // 全体のかたまり：★の札＋値（MONTHS）。x0＝左端、yc＝札の中心。下に激レアの呼び名
    const OVR=(x0,yc,noML)=>{ const b=BADGE(x0,yc,25,age,{left:1,est:EST.size>0}), txt=fmtAge(st.age), nx=x0+(b.w?b.w+12:0), nw=UTW(txt,34*.58,34)*.97, ML=MYTH(age), W2=nx-x0+nw;
      return {w:W2, s:(noML?'':`<rect x="${x0-14}" y="${yc-34}" width="${W2+28}" height="${ML?84:68}" rx="16" fill="#05060d" opacity=".72" filter="url(#c2Blur)"/>`)+b.s+`<text x="${nx}" y="${(yc+12).toFixed(1)}" font-family='${mono}' font-size="34" font-weight="600" fill="#f3ead6" paint-order="stroke" stroke="#05060d" stroke-width="3" stroke-opacity=".6">${age>0?VAL(age,34):UHT(txt,34,null)}</text>`+(ML&&!noML?MTX(x0,yc+40,ML,'start'):'')}; };
    if(LV==='E'||LV==='F'||LV==='G'){ // 2次元のグラフ（G は立ち絵を左上・分析を右隣・グラフを左下に横長）：横＝秘境を回った期間、縦＝有効RV。平均的な人の手持ちの最高が伸びていく曲線（E は5部位を積み上げ、F は全体だけ）
      // 切り替え（window.CC2_OPT）：ov＝全体の★と値の置き場（pt 点のそば／hdr 右上／ttl グラフの見出し／axis 横軸の読み）、xs＝横軸（band 段ごとに等幅／log 対数／lin 線形）、pz＝立ち絵との重なり（none／fade 溶かす／glass すりガラスの板／side 立ち絵を右へ）
      const O=window.CC2_OPT||{}, G3=LV==='G', OV=G3?'hdr':(O.ov||'pt'), XS=O.xs||'band', PZ=G3?'grid':(O.pz||'none'), WH=G3&&O.fl===2, f1=v=>(+v).toFixed(1);
      const GX0=PZ==='side'?62:G3?62:70, GX1=PZ==='side'?372:G3?(WH&&UPM!=='br'?398:616):606, GY0=PZ==='side'?(OV==='ttl'?236:196):G3?(WH?422:436):318, GY1=OV==='axis'?552:G3?587:578, /* G：グラフを左下へ（縦軸の数字の分だけ左を空け、MONTHS の2行と札が下の一文に重ならない所まで下げる） */ ymax=Math.max(st.ceil||0,st.tot||0,1), GYp=r=>GY1-Math.min(1,r/ymax)*(GY1-GY0);
      const ESI=f=>{ const x=Math.min(EN-1e-9,Math.max(0,f*EN)), k=Math.floor(x), lo=Math.log(Math.max(1,EB[k])), hi=Math.log(EB[k+1]); return Math.exp(lo+(x-k)*(hi-lo)); };
      const kA0=age>0?(()=>{ let k0=0; for(let i=0;i<EN;i++) if(age>=EB[i]) k0=i; return k0; })():0, ENg=EN, HID=k=>G3&&k>=TIERS.length&&k>kA0; /* G：グラフ本体はいつも上限まで描く（形を変えない）。百年級・有史以来は隠し要素なので、その段に届いたキャラのときだけ文字（段の名前・境目の数字）を出す */
      const LMX=Math.log(EB[ENg]), DMX=Math.max(REL,isFinite(age)?age:0,1095)*1.25;
      const XF=XS==='log'?(d=>d>0?Math.min(1,Math.log(Math.max(1,d))/LMX):0):XS==='lin'?(d=>Math.min(1,Math.max(0,d)/DMX)):(d=>Math.min(1,ES(d)*EN/ENg)), XI=XS==='log'?(f=>Math.exp(f*LMX)):XS==='lin'?(f=>Math.max(1e-3,f*DMX)):(f=>ESI(f*ENg/EN)), GXp=d=>GX0+XF(d)*(GX1-GX0);
      // 立ち絵との重なり
      if(PZ==='side'){ g=g.replace(/(<image id="ccArtImg"[^>]*? x=")([-\d.]+)"/,(m,a,x)=>a+(+x+130)+'"').replace('<stop offset=".33" stop-color="#05060d" stop-opacity="0"/><stop offset=".56"','<stop offset=".45" stop-color="#05060d" stop-opacity="0"/><stop offset=".6"'); }
      if(PZ==='glass'){ const px0=GX0-52, py0=GY0-(OV==='ttl'?96:40), pw=GX1-px0+22, ph=GY1+(OV==='axis'?70:46)-py0, im=(g.match(/<image id="ccArtImg"[^>]*\/>/)||[''])[0];
        g+=`<defs><clipPath id="c2Glass"><rect x="${px0}" y="${py0}" width="${pw}" height="${ph}" rx="14"/></clipPath><filter id="c2Frost" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="10"/></filter></defs>`+(im?`<g clip-path="url(#c2Glass)">${im.replace(' id="ccArtImg"','').replace(/filter="[^"]*"/,'filter="url(#c2Frost)"')}</g>`:'')+`<rect x="${px0}" y="${py0}" width="${pw}" height="${ph}" rx="14" fill="#0b0e22" fill-opacity=".62" stroke="#e9d39a" stroke-opacity=".22"/>`; }
      else if(PZ!=='grid'){ const strong=PZ==='fade'||PZ==='side'; g+=`<defs><linearGradient id="c2Fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05060d" stop-opacity="0"/><stop offset="${strong?.42:.3}" stop-color="#05060d" stop-opacity="${strong?.94:.72}"/><stop offset="1" stop-color="#05060d" stop-opacity="${strong?.96:.88}"/></linearGradient></defs>`+(PZ==='side'?'':`<rect x="22" y="${GY0-(strong?150:90)}" width="626" height="${H-50-GY0+(strong?152:92)}" fill="url(#c2Fade)"/>`);
        if(PZ==='side') g+=`<defs><linearGradient id="c2FadeX" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#05060d" stop-opacity=".9"/><stop offset=".7" stop-color="#05060d" stop-opacity=".75"/><stop offset="1" stop-color="#05060d" stop-opacity="0"/></linearGradient></defs><rect x="22" y="${GY0-50}" width="${GX1+20}" height="${H-50-GY0+50}" fill="url(#c2FadeX)"/>`; }
      let G0=-1;
      if(G3){ // 立ち絵は左上の枠に収める。右隣に分析（次の★まで／1か月で更新できる見込み／有効OPごとの伸び）
        if(WH){ // 丸ごと：同梱の立ち絵（1600×800、背景は透明で端は絵そのものがぼけている）を切り出さずに、名前の下の横長の場所（622×311 ≒ 2:1）へそのまま。分析の表はグラフの横へ
          const AJ=window.CC2_ADJ||{x:0,y:0,s:1}, BW=622, BH=370, BX0=24, BY0=96, bb=window.CC2_BB||{x0:0,y0:0,x1:1,y1:1,ar:2}, IA=bb.ar||2, k0=Math.min(BH/(bb.y1-bb.y0),1.3*BW/((bb.x1-bb.x0)*IA)), IH=k0*AJ.s, IW=IH*IA, PW=IW, PH=IH, PO=window.CC2_POS||{dx:0,dy:0}, PX0=BX0+BW/2-((bb.x0+bb.x1)/2)*IW+AJ.x*BW, PY0=BY0+BH/2-((bb.y0+bb.y1)/2)*IH+AJ.y*BH, PX=PX0+(PO.dx||0), PY=PY0+(PO.dy||0), src=window.CC2_WHOLE; /* 絵の中の描かれている範囲（bb、割合）が場所（622×370：名前の下から、下のグラフと表に少しかぶるところまで）の高さいっぱいになるよう拡大（横に広い絵は横がはみ出し、端で溶かす。拡大は横幅の1.3倍まで）。端は少し溶かす */
          const tag=src?`<image id="ccArtImg" data-bx="${f1(PX0)}" data-by="${f1(PY0)}" href="${src}" x="${f1(PX)}" y="${f1(PY)}" width="${f1(PW)}" height="${f1(PH)}" preserveAspectRatio="none" filter="url(#c2ArtW)" opacity=".95" clip-path="url(#c2Card)" mask="url(#c2WM)"/>`:'';
          g=g.replace(/<image id="ccArtImg"[^>]*\/>/,tag).replace(/<image href="[^"]*" x="[-\d.]+" y="[-\d.]+" width="860" height="430"[^>]*\/>/,tag).replace(`<rect width="${W}" height="${H}" fill="url(#ccVig)"/>`,'').replace(`<rect x="0" y="0" width="${W}" height="${H}" fill="url(#ccFadeR)"/>`,'');
          const VX0=Math.max(PX,22), VX1=Math.min(PX+PW,648), VY0=Math.max(PY,86), VY1=PY+PH, ex=Math.min(.45,58/Math.max(1,VX1-VX0)), ey=Math.min(.45,62/Math.max(1,VY1-VY0)), /* 溶かしは「見えている範囲」の端に（大きな絵が場所からはみ出しても、場所の境目で四角く切れないように）。上は名前と有効OPの札の下（86）から */ GR=(id,x1,y1,x2,y2,e)=>`<linearGradient id="${id}" gradientUnits="userSpaceOnUse" x1="${f1(x1)}" y1="${f1(y1)}" x2="${f1(x2)}" y2="${f1(y2)}"><stop offset="0" stop-color="#000"/><stop offset="${e.toFixed(4)}" stop-color="#fff"/><stop offset="${(1-e).toFixed(4)}" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>`;
          g+=`<defs><clipPath id="c2Card"><rect x="21" y="86" width="627" height="395"/></clipPath><filter id="c2ArtW" x="0" y="0" width="1" height="1"><feColorMatrix type="saturate" values=".82"/><feComponentTransfer><feFuncR type="linear" slope=".78"/><feFuncG type="linear" slope=".78"/><feFuncB type="linear" slope=".86"/></feComponentTransfer></filter>${GR('c2WX',VX0,0,VX1,0,ex)}${GR('c2WY',0,VY0,0,VY1,ey)}<mask id="c2WMy" maskUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}"><rect width="${W}" height="${H}" fill="url(#c2WY)"/></mask><mask id="c2WM" maskUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}"><g mask="url(#c2WMy)"><rect width="${W}" height="${H}" fill="url(#c2WX)"/></g></mask><linearGradient id="c2Low" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05060d" stop-opacity="0"/><stop offset=".16" stop-color="#05060d" stop-opacity=".74"/><stop offset="1" stop-color="#05060d" stop-opacity=".86"/></linearGradient><linearGradient id="c2LowX" gradientUnits="userSpaceOnUse" x1="21" x2="648" y1="0" y2="0"><stop offset=".9" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient><mask id="c2LowM" maskUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}"><rect x="21" y="0" width="627" height="${H}" fill="url(#c2LowX)"/></mask></defs><rect x="21" y="368" width="627" height="${H-21-368}" fill="url(#c2Low)" mask="url(#c2LowM)"/>`; } else {
        const FL=!!(window.CC2_OPT||{}).fl, AJ=window.CC2_ADJ||{x:0,y:0,s:1}, BW=FL?407:306, BH=FL?380:286, BX0=FL?24:30, BY0=FL?100:116, PW=BW*AJ.s, PH=BH*AJ.s, PX=BX0+BW/2-PW/2+AJ.x*BW, PY=BY0+BH/2-PH/2+AJ.y*BH; if(window.CC2_FIT2) g=g.replace(/(<image id="ccArtImg"[^>]*? href=")[^"]*"/,(m,a)=>a+window.CC2_FIT2+'"'); /* 枠：306×286 の枠にちょうど収める（切り出した立ち絵の画像と同じ縦横比 600:560）／枠なし：左端はカードの枠の内側にそろえ、名前の下から縦いっぱい。右（表の下）と下（グラフの上）へのはみ出しは3割の濃さに落とす。立ち絵は fitCardArt で人物の高さいっぱい・600:560 にそろっているので、キャラごとの調整は要らない */ g=g.replace(/(<image id="ccArtImg"[^>]*? x=")[-\d.]+(" y=")[-\d.]+(" width=")600(" height=")560"/,(m,a,b2,c2,d2)=>`${a}${PX}${b2}${PY}${c2}${PW}${d2}${PH}"${FL?'':' clip-path="url(#c2Por)"'}`).replace(`<rect width="${W}" height="${H}" fill="url(#ccVig)"/>`,''); if(FL) g=g.replace(/<image id="ccArtImg"[^>]*\/>/,m=>`<g mask="url(#c2MY)"><g mask="url(#c2MX)">${m}</g></g>`);
        if(FL) g+=`<defs><linearGradient id="c2GX" gradientUnits="userSpaceOnUse" x1="0" x2="${W}" y1="0" y2="0"><stop offset="${(22/W).toFixed(4)}" stop-color="#000"/><stop offset="${(48/W).toFixed(4)}" stop-color="#fff"/><stop offset="${(330/W).toFixed(4)}" stop-color="#fff"/><stop offset="${(362/W).toFixed(4)}" stop-color="#4d4d4d"/><stop offset="${(420/W).toFixed(4)}" stop-color="#4d4d4d"/><stop offset="${(446/W).toFixed(4)}" stop-color="#000"/></linearGradient><linearGradient id="c2GY" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="${H}"><stop offset="${(102/H).toFixed(4)}" stop-color="#000"/><stop offset="${(116/H).toFixed(4)}" stop-color="#fff"/><stop offset="${(424/H).toFixed(4)}" stop-color="#fff"/><stop offset="${(440/H).toFixed(4)}" stop-color="#4d4d4d"/><stop offset="${(470/H).toFixed(4)}" stop-color="#4d4d4d"/><stop offset="${(486/H).toFixed(4)}" stop-color="#000"/></linearGradient><mask id="c2MX" maskUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}"><rect x="21" y="21" width="${W-42}" height="${H-42}" fill="url(#c2GX)"/></mask><mask id="c2MY" maskUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}"><rect x="21" y="21" width="${W-42}" height="${H-42}" fill="url(#c2GY)"/></mask></defs>`;
        else g+=`<defs><clipPath id="c2Por"><rect x="30" y="116" width="306" height="286" rx="10"/></clipPath></defs><rect x="30" y="116" width="306" height="286" rx="10" fill="none" stroke="#e9d39a" stroke-opacity=".22"/>`;
        }
        G0=g.length; const IX=WH&&UPM!=='left'?412:352, IX1=WH&&UPM!=='left'?640:636, SEC=(t,y)=>`<text x="${IX}" y="${y}" font-family='${sans}' font-size="9.5" font-weight="700" letter-spacing=".12em" fill="#9aa6bb">${t}</text>`, BAR=(x0,x1,y,f,w=3)=>LN(x0,y,x1,y,'#fff',.12,w,' stroke-linecap="round"')+(f>0?LN(x0,y,x0+(x1-x0)*Math.min(1,f),y,CREAM,.8,w,' stroke-linecap="round"'):'');
        // 1. これから1か月で更新できる見込み（どこか1部位でも／部位ごと）。部位の秘境レベルの言い直しに近いが、「次にどこを回るか」の向きの数字として残す
        if(UPM==='left'){ const pa=upProbAll(st,30), ps=SLOTS.map(s2=>upProb(st.slots[s2],30)), cw=(IX1-IX)/5, FP=p0=>p0>=.995?'>99%':p0<.005?(p0<=0?'0%':'<1%'):Math.round(p0*100)+'%';
          g+=SEC('これから1か月で更新できる見込み',134)+`<text x="${IX}" y="164" font-family='${mono}' font-size="24" font-weight="700" fill="#f3ead6">${FP(pa)}<tspan dx="10" font-family='${sans}' font-size="10" font-weight="400" fill="#8a93a6">どこか1部位でも、いまより良い1個が出る確率</tspan></text>`;
          SLOTS.forEach((s2,j)=>{ const x=IX+j*cw, best=ps[j]===Math.max(...ps)&&ps[j]>0; g+=slotIcon(s2,x+6,186,11,best?'#f3ead6':'#8a93a6')+`<text x="${x+15}" y="190" font-family='${mono}' font-size="10" font-weight="${best?700:400}" fill="${best?'#f3ead6':'#9aa6bb'}">${FP(ps[j])}</text>`+BAR(x+2,x+cw-8,200,ps[j],2); }); }
        // 2. 有効OPごとの伸び（5部位のサブOPの合計値・強化で伸びた回数（最初の1回は除く。右の行の点と同じ）・1回あたりの伸び）。最後に合計の行
        if(UPM!=='br'){ const effL=(c.eff||[]).filter(k=>ROLL[k]), cols=[IX,IX+(IX1-IX)*.5,IX+(IX1-IX)*.75,IX1], TY=UPM==='left'?0:(WH?186:-94); let UP=0, UA=0, NA=0, UU=0;
          SLOTS.forEach(s2=>{ const x=st.slots[s2]; if(x.est&&x.est.ok) UA+=x.est.four?5:4; });
          g+=SEC('有効OPごとの伸び（5部位の合計）',228+TY)+[['合計',cols[1]],['伸びた回数',cols[2]],['1回の伸び',cols[3]]].map(([t,x])=>`<text x="${x}" y="${245+TY}" text-anchor="end" font-family='${sans}' font-size="8.5" fill="#6f7a8e">${t}</text>`).join('');
          const rows=effL.slice(0,4); rows.forEach((k,ri)=>{ let v=0,n=0,u=0,up=0; SLOTS.forEach(s2=>{ const pc=c.pieces[s2], x=st.slots[s2]; if(!pc||!pc.subs) return; const q=pc.subs.find(z=>z.s===k&&!z.off); if(q) v+=parseFloat(q.v)||0; const dd=x.est&&x.est.ok&&x.est.det.find(z=>z.s===k); if(dd){ n+=dd.n; u+=dd.u; up+=dd.n-1; } });
            UP+=up; NA+=n; UU+=u; const y=266+TY+ri*20, pct=!FLAT.has(k), vt=pct?v.toFixed(1)+'%':Math.round(v).toLocaleString('en-US');
            g+=`<text x="${IX}" y="${y}" font-family='${sans}' font-size="12" fill="#d8d2c2">${SUBN[k]||k}</text><text x="${cols[1]}" y="${y}" text-anchor="end" font-family='${mono}' font-size="13" font-weight="700" fill="#f3ead6">+${vt}</text><text x="${cols[2]}" y="${y}" text-anchor="end" font-family='${mono}' font-size="12" fill="#cfd4e6">${up}回</text><text x="${cols[3]}" y="${y}" text-anchor="end" font-family='${mono}' font-size="12" fill="#cfd4e6">${n?Math.round(u*10/n)+'%':'—'}</text>`; });
          const yt=266+TY+rows.length*20+8; g+=LN(IX,yt-14,IX1,yt-14,'#fff',.15,1)+`<text x="${IX}" y="${yt}" font-family='${sans}' font-size="11" font-weight="700" fill="#9aa6bb">合計${IX1-IX<260?'':`<tspan dx="6" font-size="8.5" font-weight="400" fill="#6f7a8e">強化のうち有効OPに入った回数</tspan>`}</text>${IX1-IX<260?`<text x="${cols[2]}" y="${yt+13}" text-anchor="end" font-family='${sans}' font-size="8" fill="#6f7a8e">強化のうち有効OPに入った回数</text>`:''}<text x="${cols[2]}" y="${yt}" text-anchor="end" font-family='${mono}' font-size="12" font-weight="700" fill="#f3ead6">${UP}<tspan font-weight="400" fill="#8a93a6">/${UA}回</tspan></text><text x="${cols[3]}" y="${yt}" text-anchor="end" font-family='${mono}' font-size="12" font-weight="700" fill="#f3ead6">${NA?Math.round(UU*10/NA)+'%':'—'}</text>`; } }
      if(WH&&G0>=0&&UPM==='left'){ const k=.8, part=g.slice(G0); g=g.slice(0,G0)+`<g transform="translate(${f1(414-352*k)},${f1(384-122*k)}) scale(${k})">${part}</g>`; } // 丸ごとのときは、分析の表を縮めてグラフの右へ
      HALO=WH?1:0;
      const N=160, fs=[...Array(N+1)].map((_,i)=>i/N), ds=fs.map(XI), sl=SLOTS.map(s=>ds.map(d=>st.slots[s].M.mean(d))), cum=[]; let acc=ds.map(()=>0);
      sl.forEach(a=>{ acc=acc.map((v,i)=>v+a[i]); cum.push(acc); });
      const PL=arr=>arr.map((r,i)=>`${f1(GX0+fs[i]*(GX1-GX0))},${f1(GYp(r))}`);
      // 目盛り：段の境目（縦の細線、★5+より先は点線）、上限（横の点線）、RVの目盛り。G は文字を大きく、段ごとの淡い縞・曲線の下の金の光・読み取りの札で「目を引く」形に（色はカードの枠と同じ金だけ）
      const BG=G3, GS=BG?((window.CC2_OPT||{}).gs||'bold'):'calm', /* グラフ本体の見た目（G）：bold＝華やか／mid＝中間／calm＝控えめ（前の形）。文字・読み取りの札・あなたの点は変えない */ FA=BG?9.5:7.5, FLb=BG?10.5:8, FB=BG?11.5:9, FE=BG?9:7, ACC='#e9d39a', py0=age>0?GYp(st.tot):null;
      const BX=[...Array(ENg+1)].map((_,i)=>GX0+XF(EB[i])*(GX1-GX0)); BX[0]=GX0;
      if(BG){ g+=`<defs><linearGradient id="c2Area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${ACC}" stop-opacity=".26"/><stop offset="1" stop-color="${ACC}" stop-opacity="0"/></linearGradient><linearGradient id="c2Curve" gradientUnits="userSpaceOnUse" x1="${GX0}" x2="${GX1}" y1="0" y2="0"><stop offset="0" stop-color="#cfd4e6"/><stop offset="1" stop-color="#f6e2a8"/></linearGradient></defs>`;
        if(GS==='bold') for(let k=0;k<ENg;k+=2){ const a=BX[k], b=Math.min(GX1,BX[k+1]); if(b>a) g+=`<rect x="${f1(a)}" y="${GY0}" width="${f1(b-a)}" height="${GY1-GY0}" fill="#fff" fill-opacity=".03"/>`; } }
      for(let i=1;i<ENg;i++) if(BX[i]<GX1-1) g+=LN(BX[i],GY0,BX[i],GY1,'#fff',i>TIERS.length-1?.1:.07,1,i>TIERS.length-1?' stroke-dasharray="2 3"':'');
      const nearY=y=>false;
      const stp=BG?2000:([100,200,500,1000,2000,5000].find(v=>ymax/v<=5)||10000); for(let r=stp;r<ymax*.999;r+=stp) g+=LN(GX0,GYp(r),GX1,GYp(r),'#fff',.05,1)+(nearY(GYp(r))||(!BG&&GYp(r)-GY0<12)?'':TX(GX0-6,GYp(r)+3.5,r.toLocaleString('en-US'),{a:'end',fs:FA,c:'#7d869a',m:1}));
      g+=LN(GX0,GY0,GX1,GY0,'#fff',.35,1,' stroke-dasharray="3 3"')+(BG?CHIP(RANK_NAME+'の物差し',GX0-12,GY0-26)+TX(GX0,GY0-6,`<tspan fill="#9aa6bb">有効RV %</tspan><tspan dx="14">上限</tspan> <tspan font-family='${mono}' font-weight="700" fill="#cfd4e6">${Math.round(ymax).toLocaleString('en-US')}</tspan>`,{fs:FLb,c:'#9aa6bb'}):(nearY(GY0)?'':TX(GX0-6,GY0+3.5,Math.round(ymax).toLocaleString('en-US'),{a:'end',fs:FA,c:'#9aa6bb',m:1}))+TX(GX0+4,GY0-6,'上限（この装備で届く有効RVの最大）',{fs:FLb,c:'#9aa6bb'}));
      g+=LN(GX0,GY1,GX1,GY1,'#fff',.3,1)+LN(GX0,GY0,GX0,GY1,'#fff',.2,1)+(BG?'':TX(GX0-6,GY0-16,'有効RV %',{a:'end',fs:FLb,c:'#9aa6bb'})); /* G：有効RV % は上限の行にまとめる */
      // 横軸の文字：読みのかたまり（axis）・読み取りの札と重なるものは出さない
      const px=age>0?GXp(age):null, o0=OVR(0,0), axL=OV==='axis'&&px!=null?Math.max(GX0-20,Math.min(GX1+20-o0.w,px-o0.w/2)):null, xc=BG&&px!=null?{w:UTW(fmtAge(age),10.5*.6,10.5)+18}:null, xcL=xc?Math.max(GX0-30,Math.min(GX1+24-xc.w,px-xc.w/2)):null,
        hideX=x=>axL!=null&&x>axL-14&&x<axL+o0.w+14, hideXE=x=>hideX(x)||(xcL!=null&&x>xcL-16&&x<xcL+xc.w+16); // 横軸の札は目盛りの数字の行に置くので、★の段の名前は消さず、数字だけ消す
      const kAge=age>0?(()=>{ let k0=0; for(let i=0;i<EN;i++) if(age>=EB[i]) k0=i; return k0; })():-1; // あなたの点が入っている段（G では札と同じ金で着色）
      for(let k=0;k<ENg;k++){ const a=BX[k], b=Math.min(GX1,BX[k+1]); if(b-a>16&&!hideX((a+b)/2)&&!HID(k)) g+=TX((a+b)/2,GY1+(BG?16:14),ELB[k],{a:'middle',fs:FB,fw:700,c:BG&&k===kAge?ACC:'#9aa6bb'}); }
      { let last=-99; for(let i=1;i<ENg;i++){ const x=BX[i]; if(x>GX1-1||x-last<(BG?26:20)||hideXE(x)) continue; last=x; g+=TX(x,GY1+(BG?29:25),EMO[i-1],{a:'middle',fs:FE,c:BG?'#b4bccb':'#6f7a8e',m:1}); } }
      if(XS==='lin'&&!hideXE(GX1)) g+=TX(GX1,GY1+(BG?29:25),MOP(DMX),{a:'end',fs:FE,c:'#6f7a8e',m:1});
      else if(BG&&XS!=='lin'&&!hideXE(GX1)) g+=TX(GX1,GY1+(BG?29:25),'∞',{a:'middle',fs:FE+2,c:'#b4bccb'}); /* 右端は描画の端（理論値ではない）。本当の理論値は平均的な人がいつまでも追いつかない＝無限なので ∞ */
      if(BG) g+=`<text x="${GX0}" y="${GY1+29}" text-anchor="middle" font-family='${sans}' font-size="8.5" font-weight="700" letter-spacing=".06em" fill="#9aa6bb">MONTHS</text><text x="${GX0}" y="${GY1+40}" text-anchor="middle" font-family='${sans}' font-size="7.5" fill="#7d869a">（秘境を回る月数）</text>`; /* 目盛りの数字の行の左端（数字を読み始める所）に単位 */
      if(!BG) g+=TX(GX1,GY1+(BG?53:36),BG?'秘境を回った期間'+(XS==='log'?'（対数）':XS==='lin'?'（線形）':''):'秘境を回った期間（MONTHS）'+(XS==='log'?'・対数':XS==='lin'?'・線形':''),{a:'end',fs:BG?9.5:7.5,c:'#7d869a'});
      // 曲線
      if(LV==='E'||G3){ cum.forEach((top,j)=>{ const bot=j?cum[j-1]:ds.map(()=>0); g+=`<polygon points="${PL(top).join(' ')} ${PL(bot).reverse().join(' ')}" fill="${CREAM}" fill-opacity="${j%2?.13:.07}"/>`; if(j<4) g+=`<polyline points="${PL(top).join(' ')}" fill="none" stroke="${CREAM}" stroke-opacity=".22" stroke-width=".7"/>`;
          const yt=GYp(top[N]), yb=GYp(bot[N]); if(yb-yt>9) g+=slotIcon(SLOTS[j],GX1-10,(yt+yb)/2,Math.min(BG?14:12,yb-yt-2),'#cfc6ae'); }); }
      else g+=`<polygon points="${PL(cum[4]).join(' ')} ${f1(GX1)},${GY1} ${GX0},${GY1}" fill="${CREAM}" fill-opacity=".08"/>`;
      if(BG&&GS==='bold') g+=`<polygon points="${PL(cum[4]).join(' ')} ${f1(GX1)},${GY1} ${GX0},${GY1}" fill="url(#c2Area)"/><polyline points="${PL(cum[4]).join(' ')}" fill="none" stroke="${ACC}" stroke-opacity=".35" stroke-width="6" stroke-linejoin="round" filter="url(#ccSoft)"/><polyline points="${PL(cum[4]).join(' ')}" fill="none" stroke="url(#c2Curve)" stroke-width="2.4" stroke-linejoin="round"/>`;
      else if(BG&&GS==='mid') g+=`<polygon points="${PL(cum[4]).join(' ')} ${f1(GX1)},${GY1} ${GX0},${GY1}" fill="url(#c2Area)" opacity=".4"/><polyline points="${PL(cum[4]).join(' ')}" fill="none" stroke="url(#c2Curve)" stroke-width="1.8" stroke-linejoin="round"/>`;
      else g+=`<polyline points="${PL(cum[4]).join(' ')}" fill="none" stroke="${CREAM}" stroke-opacity=".9" stroke-width="1.6"/>`;
      // 原神のリリースから毎日回った線
      if(!(BG&&+((window.CC2_OPT||{}).fw||0)>0&&age>0&&isFinite(age))){ const x=GXp(REL), lf=x+(BG?190:165)>GX1; g+=LN(x,GY0,x,GY1,RELC,.6,1,' stroke-dasharray="3 2.5"')+`<text${HAL()} x="${f1(lf?x-4:x+4)}" y="${BG?GY0+14:GY1-6}"${lf?' text-anchor="end"':''} font-family='${sans}' font-size="${BG?9.5:8}" fill="${RELC}">${REL_T}</text>`; }
      // あなた：有効RVの横線が曲線とぶつかる点 → 真下が秘境レベル。G は縦軸・横軸に読み取りの札
      if(age>0){ const py=py0; g+=LN(GX0,py,px,py,'#fff',BG?.7:.55,1,' stroke-dasharray="2 2.5"')+LN(px,py,px,OV==='axis'?GY1+8:BG?GY1+19:GY1,'#fff',BG?.7:.55,1,' stroke-dasharray="2 2.5"');
        const FW=BG?+((window.CC2_OPT||{}).fw||0):0; /* これからの帯（G）：あなたの点から FW 日先まで。対数の横軸では、同じ期間でも右へ行くほど帯が細くなり、帯の中の伸びも小さくなる＝潮時が見える */
        if(FW>0&&isFinite(age)){ // 標語は帯の上に題字のように、伸びる分（あなたの有効RVの線と曲線のあいだ）を金で塗り、伸びの数字はごほうびらしく光らせて到達点の上に
          const x2=Math.min(GX1,GXp(age+FW)), y2=GYp(st.meanTot(age+FW)), gain=Math.max(0,st.meanTot(age+FW)-st.tot), lab=FW>=365?'ONE MORE YEAR':FW>=180?'SIX MORE MONTHS':'THREE MORE MONTHS';
          const wedge=fs.map((f,i)=>[GX0+f*(GX1-GX0),GYp(cum[4][i])]).filter(([x])=>x>=px&&x<=x2);
          g+=`<defs><linearGradient id="c2Gain" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${ACC}" stop-opacity=".55"/><stop offset="1" stop-color="${ACC}" stop-opacity=".12"/></linearGradient><filter id="c2GainGl" x="-30%" y="-80%" width="160%" height="260%"><feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="${ACC}" flood-opacity=".75"/></filter></defs>`;
          g+=`<rect x="${f1(px)}" y="${GY0}" width="${f1(Math.max(1.5,x2-px))}" height="${GY1-GY0}" fill="${ACC}" fill-opacity=".05"/>`+LN(x2,GY0,x2,GY1,ACC,.45,1);
          if(wedge.length>1) g+=`<polygon points="${f1(px)},${f1(py)} ${wedge.map(([x,y])=>`${f1(x)},${f1(y)}`).join(' ')} ${f1(x2)},${f1(y2)} ${f1(x2)},${f1(py)}" fill="url(#c2Gain)"/>`;
          g+=`<circle cx="${f1(x2)}" cy="${f1(y2)}" r="3.4" fill="#fff6dc" stroke="${ACC}" stroke-width="1.2"/>`;
          { // 拡大の窓：横はあなたの点〜その期間の先、縦はあなたの有効RV〜到達点。帯の部分だけを縦に引き伸ばして、伸び方と伸びの量（RV）を見せる。帯が左半分なら右下、右半分なら左上
            const WW=170, WH2=92, right=true, wx=GX1-WW-28, wy=GY1-WH2-14, /* いつも右下。あなたの点の真下の破線とかぶっても、MONTHS は横軸の札で読める */ ix0=wx+38, ix1=wx+WW-12, iy0=wy+38, iy1=wy+WH2-12; /* 帯が左上の窓の下に来るなら右下へ */
            const yTop=Math.max(st.tot+Math.max(gain,ymax*.02),st.tot+1), IX=d=>ix0+(Math.log(Math.max(1,d))-Math.log(Math.max(1,age)))/Math.max(1e-9,Math.log(age+FW)-Math.log(Math.max(1,age)))*(ix1-ix0), IY=r=>iy1-(r-st.tot)/(yTop-st.tot)*(iy1-iy0);
            const M=24, seg=[...Array(M+1)].map((_,k)=>{ const d=Math.max(1,age)*Math.pow((age+FW)/Math.max(1,age),k/M); return [IX(d),IY(st.meanTot(d))]; });
            { // 拡大の囲み：グラフの上で拡大している範囲（あなたの点〜到達点）を金の四角で囲み、四角の角と窓の角を金の線で結ぶ（窓は四角の中身の拡大）
              const sx0=px, sx1=Math.max(px+4,x2), sy0=Math.min(py-3,y2-3), sy1=py+3, wc=right?[[wx,wy],[wx,wy+WH2]]:[[wx+WW,wy],[wx+WW,wy+WH2]], sc=right?[[sx1,sy0],[sx1,sy1]]:[[sx0,sy0],[sx0,sy1]];
              g+=LN(sc[0][0],sc[0][1],wc[0][0],wc[0][1],ACC,.6,1)+LN(sc[1][0],sc[1][1],wc[1][0],wc[1][1],ACC,.6,1);
              g+=`<rect x="${f1(sx0)}" y="${f1(sy0)}" width="${f1(sx1-sx0)}" height="${f1(sy1-sy0)}" rx="2" fill="${ACC}" fill-opacity=".12" stroke="${ACC}" stroke-width="1.3" filter="url(#c2GainGl)"/>`; }
            g+=`<rect x="${wx}" y="${wy}" width="${WW}" height="${WH2}" rx="6" fill="#0b0e22" fill-opacity=".92" stroke="${ACC}" stroke-opacity=".5" stroke-width="1"/>`;
            g+=`<text x="${wx+8}" y="${wy+14}" font-family='${sans}' font-size="8.5" font-weight="800" letter-spacing=".2em" fill="${ACC}">${lab}</text>`;
            g+=LN(ix0,iy1,ix1,iy1,'#fff',.25,1)+LN(ix0,iy0,ix1,iy0,'#fff',.12,1,' stroke-dasharray="2 2"')+LN(ix0,iy0,ix0,iy1,'#fff',.2,1);
            g+=`<polygon points="${f1(ix0)},${f1(iy1)} ${seg.map(([x,y])=>`${f1(x)},${f1(y)}`).join(' ')} ${f1(ix1)},${f1(iy1)}" fill="${ACC}" fill-opacity=".18"/><polyline points="${seg.map(([x,y])=>`${f1(x)},${f1(y)}`).join(' ')}" fill="none" stroke="url(#c2Curve)" stroke-width="1.8"/>`;
            g+=`<circle cx="${f1(ix0)}" cy="${f1(iy1)}" r="3" fill="#fff"/><circle cx="${f1(ix1)}" cy="${f1(seg[M][1])}" r="2.8" fill="#fff6dc" stroke="${ACC}" stroke-width="1"/>`;
            g+=`<text x="${f1(ix0-4)}" y="${f1(iy1+3)}" text-anchor="end" font-family='${mono}' font-size="8" fill="#cfd4e6">${Math.round(st.tot).toLocaleString('en-US')}</text><text x="${f1(ix0-4)}" y="${f1(iy0+3)}" text-anchor="end" font-family='${mono}' font-size="8" fill="#cfd4e6">${Math.round(yTop).toLocaleString('en-US')}</text>`;
            const gt=gain<.5?'≈ +0':'+'+Math.round(gain).toLocaleString('en-US'); g+=`<text x="${wx+WW-12}" y="${wy+31}" text-anchor="end" font-family='${mono}' font-size="14" font-weight="800" fill="#f3ead6">${gt}<tspan dx="3" font-family='${sans}' font-size="8.5" font-weight="700" fill="#9aa6bb">RV</tspan></text>`; }
          }
        if(BG){ const CH=(x,y,w,t)=>`<rect x="${f1(x)}" y="${f1(y-9.5)}" width="${f1(w)}" height="19" rx="4" fill="#0b0e22" stroke="${ACC}" stroke-opacity=".75" stroke-width="1"/><text x="${f1(x+w/2)}" y="${f1(y+4)}" text-anchor="middle" font-family='${mono}' font-size="10.5" font-weight="700" fill="#f3ead6">${t}</text>`, yt=Math.round(st.tot).toLocaleString('en-US')+'%', yw=yt.length*6.6+14;
          g+=`<circle cx="${f1(px)}" cy="${f1(py)}" r="14" fill="${ACC}" opacity=".22" filter="url(#ccSoft)"/><circle cx="${f1(px)}" cy="${f1(py)}" r="8" fill="none" stroke="${ACC}" stroke-opacity=".8" stroke-width="1.2"/><circle cx="${f1(px)}" cy="${f1(py)}" r="4.2" fill="#fff"/>`+TX(FW>0?px-12:px+12,py-10,'あなた',{fs:10.5,fw:700,c:'#f3ead6',a:FW>0?'end':'start'});
          g+=CH(xcL,GY1+29,xc.w,UHT(fmtAge(age),10.5,null)); /* 縦軸の札（有効RV）はやめた：右上の有効RVと同じ数字なので */ }
        else g+=MARK(px,py)+TX(GX0+4,py-4,`あなたの有効RV ${Math.round(st.tot)}%`,{fs:8,c:'#cfd4e6'});
        if(OV==='pt'){ const below=py+78<GY1, x0=below?Math.max(40,Math.min(630-o0.w,px+16)):Math.max(40,Math.min(630-o0.w,px-o0.w/2)), yc=below?py+42:Math.max(150,py-(MYTH(age)?72:52)); g+=OVR(x0,yc).s; }
        if(OV==='ttl') g+=OVR(GX0-8,GY0-(MYTH(age)?66:52)).s;
        if(OV==='axis') g+=`<path d="M${f1(px-6)},${GY1+8} L${f1(px)},${GY1+2} L${f1(px+6)},${GY1+8} Z" fill="#fff" fill-opacity=".8"/>`+OVR(axL,GY1+32).s;
        if(OV==='hdr') g+=OVR(rx+8,90,1).s+(MYTH(age)?MTX(rx+86,58,MYTH(age),'start'):''); } }
    HALO=0;
    if(LV==='A'){ // 縦の物差し（左端）。全体のかたまりは印の右に
      const LT=150, LB=600, AX=46, LY=d=>LB-ES(d)*(LB-LT), bh=(LB-LT)/EN, ym=LB-ES5*(LB-LT), yb=age>0?Math.max(LT+24,Math.min(LB-30,LY(age))):null, near=y=>yb!=null&&Math.abs(y-yb)<38;
      g+=`<g filter="url(#c2Halo)">`+LN(AX,LB,AX,ym,'#fff',.22,2,' stroke-linecap="round"')+LN(AX,ym,AX,LT,'#fff',.3,1,' stroke-dasharray="2 3"');
      if(age>0) g+=LN(AX,LB,AX,LY(age),CREAM,.85,3,' stroke-linecap="round"');
      for(let i=1;i<EN;i++){ const y=LB-i*bh; g+=LN(AX-4,y,AX+4,y,'#fff',.35,1); if(!near(y)) g+=TX(AX+8,y+3,EMO[i-1],{fs:7.5,c:'#6f7a8e',m:1}); }
      for(let k=0;k<EN;k++){ const y=LB-(k+.5)*bh; if(!near(y)) g+=TX(AX+8,y+3.5,ELB[k],{fs:9.5,fw:700,c:'#8a93a6'}); }
      g+=TX(AX-4,LB+16,'MONTHS',{fs:7,c:'#6f7a8e',m:1});
      const yr=LY(REL); g+=LN(AX-6,yr,AX+30,yr,RELC,.75,1,' stroke-dasharray="3 2.5"')+(near(yr)?'':`<text x="${AX+40}" y="${(yr+3).toFixed(1)}" font-family='${sans}' font-size="8.5" fill="${RELC}">${REL_T}</text>`);
      g+=`</g>`;
      if(age>0){ const y=LY(age); g+=LN(AX,y,AX+14,yb,'#fff',.5,1)+MARK(AX,y)+OVR(AX+24,yb).s; } }
    if(LV==='B'){ // 横の物差し（立ち絵の下）。全体のかたまりは印の上に
      const X0=50, X1=616, HY=598, HX=d=>X0+ES(d)*(X1-X0), bwl=(X1-X0)/EN, xm=X0+ES5*(X1-X0);
      g+=`<g filter="url(#c2Halo)">`+LN(X0,HY,xm,HY,'#fff',.22,2,' stroke-linecap="round"')+LN(xm,HY,X1,HY,'#fff',.3,1,' stroke-dasharray="2 3"');
      if(age>0) g+=LN(X0,HY,HX(age),HY,CREAM,.85,3,' stroke-linecap="round"');
      for(let i=1;i<EN;i++){ const x=X0+i*bwl; g+=LN(x,HY-4,x,HY+4,'#fff',.35,1)+TX(x,HY+16,EMO[i-1],{a:'middle',fs:7.5,c:'#6f7a8e',m:1}); }
      for(let k=0;k<EN;k++) g+=TX(X0+(k+.5)*bwl,HY+16,ELB[k],{a:'middle',fs:9.5,fw:700,c:'#8a93a6'});
      g+=TX(X1,HY+28,'MONTHS',{a:'end',fs:7,c:'#6f7a8e',m:1});
      const xr=HX(REL); g+=LN(xr,HY-6,xr,HY+5,RELC,.85,1.2)+`<text x="${xr.toFixed(1)}" y="${HY+29}" text-anchor="middle" font-family='${sans}' font-size="8.5" fill="${RELC}">${REL_T}</text>`;
      g+=`</g>`;
      if(age>0){ const x=HX(age), o0=OVR(0,0), x0=Math.max(44,Math.min(626-o0.w,x-o0.w/2)), yc=HY-(MYTH(age)?62:40); g+=LN(x,HY,x,yc+20,'#fff',.5,1)+MARK(x,HY)+OVR(x0,yc).s; } }
    // ---- 左上：元素アイコン＋名前、名前の右に有効OP（枠なしの淡い金の文字＝サブOPの有効OPと同じ色）、その下にセット名。色を足さない ----
    { const big=[...nm].length>6, fsN=big?32:40, EI=(window.CC2_ELEM||{})[el], IS=EI?Math.round(fsN*.85):0, NX=44+(IS?IS+8:0);
      g+=(EI?`<image href="${EI}" x="44" y="${(78-fsN*.36-IS/2).toFixed(1)}" width="${IS}" height="${IS}"/>`:'')+`<text x="${NX}" y="78" font-family='${disp}' font-size="${fsN}" font-weight="800" fill="#f3ead6" paint-order="stroke" stroke="#05060d" stroke-width="4" stroke-opacity=".6">${esc(nm)}</text>`;
      const nmW=[...nm].reduce((a,c2)=>a+(/[ -~]/.test(c2)?.55:1),0)*fsN, x0=NX+nmW+22, EJ={'HP%':'HP%','ATK%':'攻撃力%','DEF%':'防御力%','ER':'元素チャージ','EM':'元素熟知','CR':'会心率','CD':'会心ダメージ'}, tw=t=>[...t].reduce((a,c2)=>a+(/[ -~]/.test(c2)?8.6:13.4),0);
      let ex=x0+52, ey=60; g+=`<text x="${x0}" y="${ey}" font-family='${sans}' font-size="11" fill="#8a93a6" letter-spacing=".12em" paint-order="stroke" stroke="#05060d" stroke-width="3" stroke-opacity=".6">有効OP</text>`;
      const items=(c.effGuess?[['推定','#ffb4a6']]:[]).concat((c.eff||[]).map(k=>[EJ[k]||k,'#d9c48e']));
      items.forEach(([t,col],i)=>{ const w=tw(t); if(ex+w>630&&ex>x0+60){ ex=x0+52; ey+=20; } g+=`<text x="${ex}" y="${ey}" font-family='${sans}' font-size="13" font-weight="700" fill="${col}" paint-order="stroke" stroke="#05060d" stroke-width="3" stroke-opacity=".6">${t}</text>`; if(i<items.length-1) g+=`<text x="${(ex+w+9).toFixed(1)}" y="${ey}" text-anchor="middle" font-family='${sans}' font-size="12" fill="#6f7a8e">・</text>`; ex+=w+(i<items.length-1?18:0); });
      if(c.set) g+=`<text x="${x0}" y="${ey+21}" font-family='${sans}' font-size="11" fill="#8a93a6" letter-spacing=".12em" paint-order="stroke" stroke="#05060d" stroke-width="3" stroke-opacity=".6">セット<tspan dx="14" letter-spacing="0" font-size="13" fill="#cfd4e6">${esc(setKeyOf(c.set))}</tspan></text>`; }
  }
""" + "  // 下の一文：秘境レベルの定義")
import base64 as _b64
_ed = os.path.join(_root, 'src', 'icons', 'element'); _EN = {'炎': 'pyro', '水': 'hydro', '風': 'anemo', '雷': 'electro', '草': 'dendro', '氷': 'cryo', '岩': 'geo'}
_elem = {k: 'data:image/webp;base64,' + _b64.b64encode(open(os.path.join(_ed, v + '.webp'), 'rb').read()).decode() for k, v in _EN.items() if os.path.exists(os.path.join(_ed, v + '.webp'))}
assert s.count('/*__ELEM_ICONS__*/{}') == 1
s = s.replace('/*__ELEM_ICONS__*/{}', _json.dumps(_elem))  # 元素アイコン（カードの左上。保存する画像にも写るよう埋め込む）
# --- 本番のカード（v2.9）：命ノ星座カードのアプリでは 'SK' を新しいカード（cardV2）で描く。保存する画像には外の画像を埋め込む ---
rep("function cardSVG(c,st,v){ if(v==='SK'||v==='SKB') return", "function cardSVG(c,st,v){ if(CARD_APP&&v==='SK'&&typeof cardV2==='function') return cardV2(c,st); if(v==='SK'||v==='SKB') return")
rep("clone.setAttribute('xmlns',NS); clone.setAttribute('xmlns:xlink','http://www.w3.org/1999/xlink'); clone.setAttribute('width',W); clone.setAttribute('height',H); clone.removeAttribute('style');",
    "clone.setAttribute('xmlns',NS); clone.setAttribute('xmlns:xlink','http://www.w3.org/1999/xlink'); clone.setAttribute('width',W); clone.setAttribute('height',H); clone.removeAttribute('style'); if(typeof svgInlineImages==='function') await svgInlineImages(clone);")
open(dst, 'w', encoding='utf-8').write(s)
print('wrote', dst, len(s))
