# 聖遺物厳選ラボ：キャラの詳細の「カード（ラフ）」を画面から外し、命ノ星座カードへのリンクに置き換える。
# 使い方: python3 patch_lab_cardlink.py <ラボのHTML> <出力のHTML>
# カードの描画コードとDOMはラボに残す（命ノ星座カードはラボのコードから build_card.py で組み立てるため）。
# LAB_MODE が 'card'（命ノ星座カード）のときは、今までどおりカードを表示する。
import sys

CARD_URL = 'https://claude.ai/artifact/CWeeXV4M4vmh2rh7JRabbP'
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()

def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, (old[:80], n)
    s = s.replace(old, new)

OPEN = '<div class="chdetail" style="border-top:1px solid var(--line)"><div class="row" style="justify-content:space-between;margin-bottom:8px"><h3 style="margin:0;font-size:14px">カード（ラフ）</h3>'
LINK = ('${window.LAB_MODE===\'card\'?\'\':`<div class="chdetail labcardlink" style="border-top:1px solid var(--line)">'
        '<div class="row" style="justify-content:space-between;gap:8px 14px"><div style="min-width:0"><h3 style="margin:0 0 2px;font-size:14px">カードを作る</h3>'
        '<p class="note">カード画像は「命ノ星座カード」で作れます。データは別々に保存されるので、下の「データの引っ越し」で書き出して、命ノ星座カードの「設定 → データの引っ越し」で読み込んでください。</p></div>'
        '<a class="btn primary" href="' + CARD_URL + '" target="_blank" rel="noopener" style="text-decoration:none">命ノ星座カードを開く</a></div></div>`}')
rep(OPEN, LINK + OPEN.replace('<div class="chdetail" style=', '<div class="chdetail${window.LAB_MODE===\'card\'?\'\':\' labcard-off\'}" style=', 1))
rep('.chdetail{border-top', '.labcard-off{display:none!important}\n.chdetail{border-top')
open(dst, 'w', encoding='utf-8').write(s)
print('wrote', dst, len(s))
