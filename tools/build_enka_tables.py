# Enka.Network の公式リポジトリ（EnkaNetwork/API-docs）から、カードアプリで使う小さな対応表を抜き出す。
# 使い方: python3 build_enka_tables.py <API-docs のフォルダ> <出力の enka_tables.json>
#   avatar：avatarId → 日本語のキャラ名
#   avatar_en：avatarId → 英語のキャラ名（立ち絵のファイル名を英語で付けたときの照合用）
#   set   ：setId → 日本語のセット名
#   affix ：★5のサブOPの伸び1回のID → [ラボのOPキー, 段（0〜3＝70/80/90/100%）]
# 新キャラ・新セットが出たら、API-docs を取り直してこれを実行し、build_card.py を回し直す。
import json, os, sys

src, dst = sys.argv[1], sys.argv[2]
G = os.path.join(src, 'store', 'gi')
ld = lambda f: json.load(open(os.path.join(G, f), encoding='utf-8'))
locs = ld('locs.json'); ja = locs['ja']; en = locs['en']
PT = {2: 'HP', 3: 'HP%', 5: 'ATK', 6: 'ATK%', 8: 'DEF', 9: 'DEF%', 20: 'CR', 22: 'CD', 23: 'ER', 28: 'EM'}

avatar, avatar_en = {}, {}
for k, v in ld('avatars.json').items():
    n = ja.get(str(v.get('NameTextMapHash')))
    if n: avatar[k] = n
    e = en.get(str(v.get('NameTextMapHash')))
    if e: avatar_en[k] = e
sets = {}
for k, v in ld('relics.json')['Sets'].items():
    n = ja.get(str(v.get('Name')))
    if n: sets[k] = n
affix = {}
for k, v in ld('affixes.json').items():
    if k.startswith('501') and v['PropType'] in PT:   # ★5のサブOP
        affix[k] = [PT[v['PropType']], int(v['Position']) - 1]
assert len(affix) == 40, len(affix)
json.dump({'avatar': avatar, 'avatar_en': avatar_en, 'set': sets, 'affix': affix}, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('wrote', dst, len(avatar), len(sets), len(affix), os.path.getsize(dst), 'bytes')
