#!/usr/bin/env python3
# 聖遺物のアイコン（ゲーム公式の部位ごとの絵）を Enka.Network から取ってきて、src/icons/relic/ に登録する。
#   使い方：python3 tools/build_relic_icons.py [--all]
#   - 対象は聖遺物ビデオスキャナーの表（src/scanner/data.js）で★5のあるセット。セットの番号は Enka の対応表（tools/enka_tables.json の set）
#   - Enka の絵の名前は UI_RelicIcon_{セットの番号}_{部位}（部位：1＝杯・2＝羽・3＝冠・4＝花・5＝砂）
#   - すでに絵があるセットは取らない（新しいセットだけ取る）。取り直すときは --all
#   - Enka に負担をかけないよう、1秒に1枚ずつ。User-Agent にこのリポジトリを書く
#   - 96px の WebP（透明を保つ）にして src/icons/relic/{セットの番号}_{部位}.webp に置き、
#     src/icons/relic/relic.json（セット名 → セットの番号）を書き直す。カードのページは組み立てのときにこの表を埋め込む
# ネットワーク：enka.network に接続できる環境で動かす（Claude の作業環境「genshin-lab」は許可済み）
# 新しいセットが出たら：Enka の対応表（tools/build_enka_tables.py）とスキャナーの表に入ったあとで、これを動かす
import io, json, os, sys, time, urllib.request
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'src', 'icons', 'relic')
UA = 'genshin-lab-icons/1.0 (one-time fetch; https://github.com/wayfaringgene-code/genshin-lab)'
SIZE = 96
PART = {'goblet': 1, 'plume': 2, 'circlet': 3, 'flower': 4, 'sands': 5}

def five_star_sets():
    s = open(os.path.join(ROOT, 'src', 'scanner', 'data.js'), encoding='utf-8').read()
    d, _ = json.JSONDecoder().raw_decode(s, s.index('{', s.index('GSCAN_DATA')))
    return [v['n'] for v in d['sets'].values() if 5 in v.get('r', [])]

def fetch(sid, n):
    url = f'https://enka.network/ui/UI_RelicIcon_{sid}_{n}.png'
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r:
        return Image.open(io.BytesIO(r.read())).convert('RGBA')

def main():
    ids = {v: k for k, v in json.load(open(os.path.join(ROOT, 'tools', 'enka_tables.json'), encoding='utf-8'))['set'].items()}
    os.makedirs(OUT, exist_ok=True)
    reg_path = os.path.join(OUT, 'relic.json')
    reg = json.load(open(reg_path, encoding='utf-8')) if os.path.exists(reg_path) and '--all' not in sys.argv else {}
    got, miss = [], []
    for nm in five_star_sets():
        sid = ids.get(nm)
        if not sid: miss.append(f'{nm}（Enka の対応表にない）'); continue
        if reg.get(nm) == sid and all(os.path.exists(os.path.join(OUT, f'{sid}_{n}.webp')) for n in PART.values()): continue
        ok = True
        for n in PART.values():
            try: im = fetch(sid, n)
            except Exception as e: miss.append(f'{nm}（UI_RelicIcon_{sid}_{n}：{e}）'); ok = False; time.sleep(1); break
            im.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(OUT, f'{sid}_{n}.webp'), 'WEBP', quality=80, method=6)
            time.sleep(1)
        if ok: reg[nm] = sid; got.append(nm)
    used = {f'{sid}_{n}.webp' for sid in reg.values() for n in PART.values()}
    for f in os.listdir(OUT):                               # どのセットにも使っていない絵は消す
        if f.endswith('.webp') and f not in used: os.remove(os.path.join(OUT, f))
    json.dump(dict(sorted(reg.items())), open(reg_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'取った {len(got)}セット・登録 {len(reg)}セット・取れなかった {len(miss)}')
    for m in miss: print('  取れなかった：', m)

if __name__ == '__main__': main()
