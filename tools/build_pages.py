# GitHub Pages に出すページ一式を組み立てる（GitHub Actions が push のたびに実行する。手元でも実行できる）。
# 使い方: python3 tools/build_pages.py [出力のフォルダ（既定 _site）]
#
#   src/lab.html     ラボの元（聖遺物厳選ラボ。artifact に公開しているものと同じ）← ラボを直すときはここ
#   src/scanner/     聖遺物ビデオスキャナーの元
#   src/fonts/       カード画像に埋め込むフォント（fontsource の Murecho・M PLUS 1p を分割したJSON）
#   tools/           組み立てスクリプトと Enka の対応表
#
# 出力：
#   index.html           命ノ星座カード（build_card.py。ホームから始まる。OGP付き）
#   scan/                ビデオスキャナー（build_scan.py）
#   fonts/               カード画像に埋め込むフォント
#   portraits/           同梱の立ち絵（src/portraits があれば）
#   og.png               X などにURLを貼ったときの画像（src/og.png があれば）
#   lab/index.html       聖遺物ラボ：キャラ（LAB_MODE='chars'）
#   card/index.html      以前の /card/ からトップへの転送
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '_site'))
SRC = os.path.join(ROOT, 'src')
TOOLS = os.path.join(ROOT, 'tools')
ARTIFACT_CARD_URL = 'https://claude.ai/artifact/CWeeXV4M4vmh2rh7JRabbP'

def read(p): return open(p, encoding='utf-8').read()
def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

def pages_head(s, title, app, icon, mode_script=''):
    """artifact の公開時に付く頭（<!doctype>〜<body>）を、ホーム画面に追加できる頭に差し替える。
    頭の小さなリセット（[hidden] の扱いなど）はそのまま残す。<title> は1つ目だけを差し替える。"""
    m = re.match(r'<!doctype html><html><head>(.*?)</head><body>\s*<title>[^<]*</title>', s, re.S | re.I)
    assert m, 'artifact の頭が見つからない'
    reset = re.search(r'<style>.*?</style>', m.group(1), re.S).group(0)
    head = ('<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
            f'<meta name="apple-mobile-web-app-title" content="{app}">\n<meta name="theme-color" content="#05060d">\n'
            f'<link rel="apple-touch-icon" href="{icon}">\n<link rel="icon" type="image/png" href="{icon}">\n'
            f'{reset}\n{mode_script}<title>{title}</title>\n</head>\n<body>\n')
    return head + s[m.end():]

if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
lab = read(os.path.join(SRC, 'lab.html'))

SITE = 'https://wayfaringgene-code.github.io/genshin-lab/'
OGP = (f'<meta name="description" content="原神の聖遺物が「秘境を何日回った人のレベル」かを測って、カードにします。UIDを入れるだけ・ログイン不要。">\n'
       f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="命ノ星座カード">\n'
       f'<meta property="og:title" content="命ノ星座カード｜あなたの聖遺物は、秘境を何日回った人のレベル？">\n'
       f'<meta property="og:description" content="UIDを入れるだけで、キャラごとの聖遺物の「秘境レベル」をカードにします。ログイン不要。非公式のファンツールです。">\n'
       f'<meta property="og:url" content="{SITE}">\n<meta property="og:image" content="{SITE}og.png">\n'
       f'<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
       f'<meta name="twitter:card" content="summary_large_image">\n')

# 命ノ星座カード（ルート）。ホームから始まる。スキャナー・フォント・同梱の立ち絵もルートに置く
with tempfile.TemporaryDirectory() as td:
    tmp = os.path.join(td, 'card.html')
    subprocess.run([sys.executable, os.path.join(TOOLS, 'build_card.py'), os.path.join(SRC, 'lab.html'), tmp], check=True)
    write(os.path.join(OUT, 'index.html'), pages_head(read(tmp), '命ノ星座カード', '命ノ星座カード', 'apple-touch-icon.png', OGP))
subprocess.run([sys.executable, os.path.join(TOOLS, 'build_scan.py'), os.path.join(SRC, 'scanner'), os.path.join(OUT, 'scan')], check=True)
shutil.copytree(os.path.join(SRC, 'fonts'), os.path.join(OUT, 'fonts'))
if os.path.isdir(os.path.join(SRC, 'portraits')):
    shutil.copytree(os.path.join(SRC, 'portraits'), os.path.join(OUT, 'portraits'))
if os.path.exists(os.path.join(SRC, 'og.png')):
    shutil.copy(os.path.join(SRC, 'og.png'), OUT)

# 聖遺物ラボ：キャラ（/lab/）。カードへのリンクは、サイトのトップ（../）に向ける
chars = pages_head(lab, '聖遺物ラボ：キャラ', '聖遺物ラボ', '../apple-touch-icon.png', "<script>window.LAB_MODE='chars';</script>\n")
assert chars.count(ARTIFACT_CARD_URL) == 1
write(os.path.join(OUT, 'lab', 'index.html'), chars.replace(ARTIFACT_CARD_URL, '../').replace(' target="_blank" rel="noopener" style="text-decoration:none">命ノ星座カードを開く', ' style="text-decoration:none">命ノ星座カードを開く'))

# 以前の /card/ は、トップへ転送する（ブックマーク・共有済みのリンクのため）
write(os.path.join(OUT, 'card', 'index.html'), '<!doctype html>\n<html lang="ja"><head><meta charset="utf-8"><title>命ノ星座カード</title>\n'
      '<meta http-equiv="refresh" content="0; url=../"><link rel="canonical" href="../">\n'
      '<script>location.replace("../"+location.hash)</script></head>\n<body><p><a href="../">命ノ星座カードはこちらに移りました</a></p></body></html>\n')

shutil.copy(os.path.join(ROOT, 'apple-touch-icon.png'), OUT)
open(os.path.join(OUT, '.nojekyll'), 'w').close()
print('wrote', OUT)
