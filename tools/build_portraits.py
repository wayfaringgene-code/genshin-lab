# 集めた立ち絵を、カードアプリの同梱の立ち絵（src/portraits/）に変換して登録する。
# 使い方: python3 tools/build_portraits.py <集めた画像のフォルダ> [出力のフォルダ（既定 src/portraits）]
#
# ・ファイル名は「ゲーム内のキャラ名」か「avatarId」（例：フリーナ.png、10000089.png）。旅人は名前が同じなので avatarId で（空 10000005／蛍 10000007）
# ・英語名で始まる名前でもよい（例：Skirk_Wish.webp、Raiden_Shogun_Card.png）。記号と大文字小文字は無視し、いちばん長く一致する英語名を使う
# ・背景が透明な画像（キャラだけ切り抜かれたもの）がいちばんきれいに入る。背景つきでも使えるが、横長の枠でそのまま貼る形になる
# ・長い辺 1600px に縮めて WebP（透明を保つ）で保存し、portraits.json に登録する。すでに登録済みのキャラは画像だけ差し替え、
#   portraits.json に手で書いた zoom（大きさ、%）・pos（位置 {dx,dy}）はそのまま残す
# ・名前が分からないファイルは、何もせずに一覧で知らせる
# 要るもの：Pillow（pip install pillow）
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'src', 'portraits')
os.makedirs(dst, exist_ok=True)
tables = json.load(open(os.path.join(ROOT, 'tools', 'enka_tables.json'), encoding='utf-8'))
avatar = tables['avatar']                      # avatarId → 名前
by_name = {}
for k, v in avatar.items(): by_name.setdefault(v, []).append(k)
import re
norm = lambda t: re.sub(r'[^0-9a-z]', '', t.lower())
by_en = {}
for k, v in tables.get('avatar_en', {}).items():
    if k.isdigit(): by_en.setdefault(norm(v), set()).add(k)
def en_match(stem):
    st = norm(stem); best = None
    for n, ids in by_en.items():
        if n and st.startswith(n) and (best is None or len(n) > len(best[0])): best = (n, ids)
    return best
man_path = os.path.join(dst, 'portraits.json')
manifest = json.load(open(man_path, encoding='utf-8')) if os.path.exists(man_path) else {}

MAX = 1600
done, unknown, ambiguous, opaque = [], [], [], []
for fn in sorted(os.listdir(src)):
    stem, ext = os.path.splitext(fn)
    if ext.lower() not in ('.png', '.webp', '.jpg', '.jpeg'): continue
    stem = stem.strip()
    if stem.isdigit() and stem in avatar: aid = stem
    elif stem in by_name and len(by_name[stem]) == 1: aid = by_name[stem][0]
    elif stem in by_name: ambiguous.append(f'{fn}（候補：{", ".join(by_name[stem])}）'); continue
    elif en_match(stem) and len(en_match(stem)[1]) == 1: aid = next(iter(en_match(stem)[1]))
    elif en_match(stem): ambiguous.append(f'{fn}（候補：{", ".join(sorted(en_match(stem)[1]))}）'); continue
    else: unknown.append(fn); continue
    im = Image.open(os.path.join(src, fn)).convert('RGBA')
    k = min(1.0, MAX / max(im.size))
    if k < 1: im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    a = im.getchannel('A')
    if a.getextrema()[0] >= 250: opaque.append(f'{fn}（{avatar[aid]}）')
    out = f'{aid}.webp'
    im.save(os.path.join(dst, out), 'WEBP', quality=88, method=6)
    ent = manifest.get(aid, {})
    ent.update({'file': out, 'name': avatar[aid]})
    manifest[aid] = ent
    done.append(f'{avatar[aid]}（{aid}）{im.width}×{im.height}')

json.dump(dict(sorted(manifest.items())), open(man_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'登録した立ち絵：{len(done)}人（合計 {len(manifest)}人）')
for x in done: print('  ', x)
if opaque: print('背景が透明でない画像（使えるが、横長の枠でそのまま貼る形になる）：\n  ' + '\n  '.join(opaque))
if ambiguous: print('同じ名前のキャラが複数いるので、avatarId のファイル名にしてください：\n  ' + '\n  '.join(ambiguous))
if unknown: print('名前が分からないファイル（ゲーム内のキャラ名か avatarId にしてください。新キャラなら tools/enka_tables.json の更新が先）：\n  ' + '\n  '.join(unknown))
