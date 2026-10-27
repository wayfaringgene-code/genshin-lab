# GitHub Pages に出すページ一式を組み立てる（GitHub Actions が push のたびに実行する。手元でも実行できる）。
# 使い方: python3 tools/build_pages.py [出力のフォルダ（既定 _site）]
#
#   src/lab.html     ラボの元（聖遺物厳選ラボ。artifact に公開しているものと同じ）← ラボを直すときはここ
#   src/scanner/     聖遺物ビデオスキャナーの元
#   src/fonts/       カード画像に埋め込むフォント（fontsource の Murecho・M PLUS 1p を分割したJSON）
#   tools/           組み立てスクリプトと Enka の対応表
#
# 出力：
#   index.html           聖遺物ラボ：キャラ（LAB_MODE='chars'。ホーム画面に追加できる頭を付ける）
#   card/index.html      命ノ星座カード（build_card.py）
#   card/scan/           ビデオスキャナー（build_scan.py）
#   card/fonts/          フォント
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

# 聖遺物ラボ：キャラ（ルート）。カードへのリンクは、同じサイトの card/ に向ける
chars = pages_head(lab, '聖遺物ラボ：キャラ', '聖遺物ラボ', 'apple-touch-icon.png', "<script>window.LAB_MODE='chars';</script>\n")
assert chars.count(ARTIFACT_CARD_URL) == 1
write(os.path.join(OUT, 'index.html'), chars.replace(ARTIFACT_CARD_URL, 'card/').replace(' target="_blank" rel="noopener" style="text-decoration:none">命ノ星座カードを開く', ' style="text-decoration:none">命ノ星座カードを開く'))

# 命ノ星座カード
with tempfile.TemporaryDirectory() as td:
    tmp = os.path.join(td, 'card.html')
    subprocess.run([sys.executable, os.path.join(TOOLS, 'build_card.py'), os.path.join(SRC, 'lab.html'), tmp], check=True)
    write(os.path.join(OUT, 'card', 'index.html'), pages_head(read(tmp), '命ノ星座カード', '命ノ星座カード', '../apple-touch-icon.png'))
subprocess.run([sys.executable, os.path.join(TOOLS, 'build_scan.py'), os.path.join(SRC, 'scanner'), os.path.join(OUT, 'card', 'scan')], check=True)
shutil.copytree(os.path.join(SRC, 'fonts'), os.path.join(OUT, 'card', 'fonts'))

shutil.copy(os.path.join(ROOT, 'apple-touch-icon.png'), OUT)
open(os.path.join(OUT, '.nojekyll'), 'w').close()
print('wrote', OUT)
