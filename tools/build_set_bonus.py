# 聖遺物セットの2セット効果の短い名前（「攻撃力+18%」など）の表を作る。
# 2セット＋2セットのキャラを「攻撃力+18%＋攻撃力+18%」のように表し、有効OPを「名前＋セット」で見分けるのに使う（v2.2）。
# 使い方: python3 tools/build_set_bonus.py <genshin-db の data.min.json> [出力（既定 tools/set_bonus.json）]
#   genshin-db は npm の公開パッケージ（https://www.npmjs.com/package/genshin-db）。取り方：
#     curl -sSLO https://registry.npmjs.org/genshin-db/-/genshin-db-<版>.tgz && tar xzf genshin-db-<版>.tgz
#     → package/src/min/data.min.json
# セット名は Enka の対応表（tools/enka_tables.json の set）に合わせる。表にないセット・効果が長すぎるセットは入れない
# （そのセットは「セット名＋2」のまま表示する）。新しいセットが出たら、Enka の対応表を作り直したあとにこれも作り直す。
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'tools', 'set_bonus.json')
MAX_LEN = 16  # これより長い効果（条件つきなど）は、効果ではなくセット名で表す

data = json.load(open(src, encoding='utf-8'))['data']['Japanese']['artifacts']
by_id = {str(v.get('id')): v for v in data.values()}
sets = json.load(open(os.path.join(ROOT, 'tools', 'enka_tables.json'), encoding='utf-8'))['set']

out, skipped = {}, []
for sid, name in sets.items():
    v = by_id.get(sid)
    t = (v or {}).get('effect2Pc') or ''
    t = re.sub(r'[。\s]+$', '', t.replace('重擊', '重撃')).strip()
    if not t or len(t) > MAX_LEN:
        skipped.append(name)
        continue
    out[name] = t
json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
print('wrote', dst, len(out), '件。効果で表さないセット：', '・'.join(skipped) or 'なし')
