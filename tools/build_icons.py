#!/usr/bin/env python3
# キャラのアイコン（ゲーム公式の正面のアイコン）を Enka.Network から取ってきて、src/icons/ に登録する。
#   使い方：python3 tools/build_icons.py <EnkaNetwork/API-docs の store/characters.json>
#   - characters.json の SideIconName（例 UI_AvatarIcon_Side_Flins）から、正面版（UI_AvatarIcon_Flins）の名前を作って取る
#   - characters.json にまだ載っていない新キャラは、聖遺物ビデオスキャナーの表（src/scanner/data.js）の英語のキー
#     （例 Sandrone）から UI_AvatarIcon_Sandrone を推測して取る（取れなければ一覧で知らせる）
#   - すでにアイコンがあるキャラは取らない（新キャラだけ取る）。取り直すときは --all
#   - Enka に負担をかけないよう、1秒に1枚ずつ。User-Agent にこのリポジトリを書く
#   - 128px の WebP（透明を保つ）にして src/icons/{英語のキー}.webp に置き、src/icons/icons.json（日本語名 → ファイル名）を書き直す
# ネットワーク：enka.network に接続できる環境で動かす（Claude の作業環境「genshin-lab」は許可済み）
import io, json, os, sys, time, urllib.request
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'src', 'icons')
UA = 'genshin-lab-icons/1.0 (one-time fetch; https://github.com/wayfaringgene-code/genshin-lab)'
SIZE = 128

def scanner_chars():
    s = open(os.path.join(ROOT, 'src', 'scanner', 'data.js'), encoding='utf-8').read()
    d, _ = json.JSONDecoder().raw_decode(s, s.index('{', s.index('GSCAN_DATA')))
    return {k: ('旅人' if k.startswith('Traveler') else v) for k, v in d['chars'].items()}

def targets(enka):
    """取る候補：日本語名 → (Enka での英語のキー, 'Enka'|'推測', avatarId か None)。
    Enka のキャラ表（characters.json の SideIconName）が先、表にまだない新キャラはスキャナーの英語のキーで推測。build_splash.py も使う"""
    tbl = json.load(open(os.path.join(ROOT, 'tools', 'enka_tables.json'), encoding='utf-8'))['avatar']
    sc = scanner_chars(); sc_low = {k.lower(): v for k, v in sc.items()}
    want = {}
    for aid, c in sorted(enka.items()):
        side = c.get('SideIconName') or ''
        if not aid.isdigit() or not side.startswith('UI_AvatarIcon_Side_'): continue
        key = side[len('UI_AvatarIcon_Side_'):]
        nm = tbl.get(aid) or sc_low.get(key.lower())
        if nm and nm not in want: want[nm] = (key, 'Enka', aid if tbl.get(aid) == nm else None)
    for key, nm in sc.items():
        if nm not in want and not key.startswith('Traveler'): want[nm] = (key, '推測', None)
    return want

def fetch(key):
    url = 'https://enka.network/ui/UI_AvatarIcon_' + key + '.png'
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r:
        return Image.open(io.BytesIO(r.read())).convert('RGBA')

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args: print('使い方：python3 tools/build_icons.py <characters.json>'); sys.exit(1)
    enka = json.load(open(args[0], encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)
    reg_path = os.path.join(OUT, 'icons.json')
    reg = json.load(open(reg_path, encoding='utf-8')) if os.path.exists(reg_path) and '--all' not in sys.argv else {}
    want = targets(enka)
    got, miss = [], []
    for nm, (key, how, _aid) in want.items():
        if nm in reg and os.path.exists(os.path.join(OUT, reg[nm])): continue
        try: im = fetch(key)
        except Exception as e: miss.append(f'{nm}（UI_AvatarIcon_{key}・{how}：{e}）'); time.sleep(1); continue
        fn = key + '.webp'; im.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(OUT, fn), 'WEBP', quality=80, method=6)
        reg[nm] = fn; got.append(nm); time.sleep(1)
    used = set(reg.values())
    for f in os.listdir(OUT):                               # どの名前にも使っていない画像は消す
        if f.endswith('.webp') and f not in used: os.remove(os.path.join(OUT, f))
    json.dump(dict(sorted(reg.items())), open(reg_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'取った {len(got)}・登録 {len(reg)}人・取れなかった {len(miss)}')
    for m in miss: print('  取れなかった：', m)

if __name__ == '__main__': main()
