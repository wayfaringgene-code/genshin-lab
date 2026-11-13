#!/usr/bin/env python3
# キャラのスプラッシュアート（ゲーム公式のガチャの絵。背景が透明）を Enka.Network から取ってきて、同梱の立ち絵（src/portraits/）に登録する。
#   使い方：python3 tools/build_splash.py <EnkaNetwork/API-docs の store/characters.json> [--wait 秒（既定3）]
#   - 名前と英語のキーの決め方は tools/build_icons.py と同じ（Enka のキャラ表が先、新キャラはスキャナーの表から推測）
#   - すでに立ち絵が登録してあるキャラ（手で集めたものを含む）は取らない。旅人は取らない
#   - Enka に負担をかけないよう、既定で3秒に1枚。User-Agent にこのリポジトリを書く
#   - build_portraits.py と同じく、長い辺1600pxの WebP（透明を保つ）にして src/portraits/ に置き、portraits.json に登録する
#     （ファイル名は avatarId。Enka の対応表にまだない新キャラは英語のキー。カードは名前でも探す）
# ネットワーク：enka.network に接続できる環境で動かす（Claude の作業環境「genshin-lab」は許可済み）
import io, json, os, sys, time, urllib.request
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_icons as bi

DST = os.path.join(bi.ROOT, 'src', 'portraits')
MAX = 1600

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    wait = float(sys.argv[sys.argv.index('--wait') + 1]) if '--wait' in sys.argv else 3.0
    if '--wait' in sys.argv: args = [a for a in args if a != sys.argv[sys.argv.index('--wait') + 1]]
    if not args: print('使い方：python3 tools/build_splash.py <characters.json>'); sys.exit(1)
    want = bi.targets(json.load(open(args[0], encoding='utf-8')))
    man_path = os.path.join(DST, 'portraits.json')
    man = json.load(open(man_path, encoding='utf-8')) if os.path.exists(man_path) else {}
    have = {v.get('name') for v in man.values()}
    todo = [(nm, key, aid) for nm, (key, how, aid) in want.items() if nm not in have and nm != '旅人']
    print(f'取る {len(todo)}人（{wait}秒に1枚。登録済み {len(have)}人は飛ばす）', flush=True)
    got, miss = [], []
    for i, (nm, key, aid) in enumerate(todo):
        url = 'https://enka.network/ui/UI_Gacha_AvatarImg_' + key + '.png'
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': bi.UA}), timeout=60) as r:
                im = Image.open(io.BytesIO(r.read())).convert('RGBA')
            k = min(1.0, MAX / max(im.size))
            if k < 1: im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
            mk = aid or key; out = mk + '.webp'
            im.save(os.path.join(DST, out), 'WEBP', quality=88, method=6)
            ent = man.get(mk, {}); ent.update({'file': out, 'name': nm}); man[mk] = ent
            got.append(nm)
            json.dump(dict(sorted(man.items())), open(man_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)  # 途中で止まっても、取った分は残す
        except Exception as e:
            miss.append(f'{nm}（UI_Gacha_AvatarImg_{key}：{e}）')
        print(f'  {i + 1}/{len(todo)} {nm} {"ok" if got and got[-1] == nm else "x"}', flush=True)
        time.sleep(wait)
    print(f'取った {len(got)}・取れなかった {len(miss)}・登録 {len(man)}人')
    for m in miss: print('  取れなかった：', m)

if __name__ == '__main__': main()
