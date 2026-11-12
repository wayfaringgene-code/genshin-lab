#!/usr/bin/env python3
# 育成の方針の初期値（src/builds.csv）を確かめる。
#   使い方：python3 tools/check_builds.py            … 表を読み、書き間違いがあれば行番号つきで出す（あれば終了コード1）
#           python3 tools/check_builds.py --fix      … 別名（「会心ダメ」「攻撃%」など）を正式な書き方にそろえて書き戻す
# キャラ名・セット名は聖遺物ビデオスキャナーの表（src/scanner/data.js）と同じ日本語名で書く。
import csv, io, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / 'src' / 'builds.csv'
COLS = ['キャラ', '有効OP', '使えるセット', '砂', '杯', '冠', '4+1', '確認済み', 'メモ']

# 正式な書き方（ラボの表示と同じ）と、受け付ける別名
STAT = {'会心率': [], '会心ダメージ': ['会心ダメ'], '攻撃力%': ['攻撃%', '攻撃力％', '攻撃％'], 'HP%': ['HP％', 'ＨＰ%'], '防御力%': ['防御%', '防御力％', '防御％'],
        '元素熟知': ['熟知'], '元素チャージ効率': ['チャージ', '元チャ', '元素チャージ'], '攻撃力': [], 'HP': [], '防御力': []}
ELEMS = ['炎', '水', '氷', '雷', '風', '岩', '草']
MAIN_EXTRA = {'治癒効果': ['治癒', '与える治療効果'], '物理ダメージ': ['物理']}
for e in ELEMS: MAIN_EXTRA[e + '元素ダメージ'] = [e + '元素', e + 'ダメ', e]
SUB_OK = ['会心率', '会心ダメージ', '攻撃力%', 'HP%', '防御力%', '元素熟知', '元素チャージ効率', '攻撃力', 'HP', '防御力']
MAIN_OK = {
  '砂': ['HP%', '攻撃力%', '防御力%', '元素熟知', '元素チャージ効率'],
  '杯': ['HP%', '攻撃力%', '防御力%', '元素熟知', '物理ダメージ'] + [e + '元素ダメージ' for e in ELEMS],
  '冠': ['HP%', '攻撃力%', '防御力%', '元素熟知', '会心率', '会心ダメージ', '治癒効果'],
}
ALIAS = {}
for k, v in {**STAT, **MAIN_EXTRA}.items():
  ALIAS[k] = k
  for a in v: ALIAS[a] = k
ANY = 'どれでも'

def load_data():
  s = (ROOT / 'src' / 'scanner' / 'data.js').read_text(encoding='utf-8')
  d, _ = json.JSONDecoder().raw_decode(s, s.index('{', s.index('GSCAN_DATA')))
  chars = [v for k, v in d['chars'].items() if not k.startswith('Traveler')] + ['旅人']
  return chars, {v['n'] for v in d['sets'].values()}

split = lambda s, seps: [x.strip() for x in re.split(seps, s or '') if x.strip()]

def check(rows, chars, sets, fix):
  errs, seen = [], set()
  def stats(v, ok, where, n):
    out = []
    for x in split(v, r'[・/／、]'):
      y = ALIAS.get(x)
      if y is None or y not in ok: errs.append(f'{n}行目 {where}：「{x}」は使えません（使える書き方：{"・".join(ok)}）'); out.append(x)
      else: out.append(y)
    if len(out) != len(set(out)): errs.append(f'{n}行目 {where}：同じものが2回あります')
    return '・'.join(out)
  for n, r in rows:
    name = (r.get('キャラ') or '').strip()
    if not name: errs.append(f'{n}行目：キャラ名が空です'); continue
    if name not in chars: errs.append(f'{n}行目：「{name}」というキャラが見つかりません（ゲームの日本語名で）')
    if name in seen: errs.append(f'{n}行目：「{name}」が2回出てきます')
    seen.add(name)
    r['有効OP'] = stats(r.get('有効OP'), SUB_OK, '有効OP', n)
    for slot in ['砂', '杯', '冠']: r[slot] = stats(r.get(slot), MAIN_OK[slot], slot, n)
    out = []
    for opt in split(r.get('使えるセット'), r'[/／]'):
      parts = split(opt, r'[＋+]')
      if len(parts) > 2: errs.append(f'{n}行目 使えるセット：「{opt}」は3つ以上に分かれています（4セットは名前だけ、2＋2は「A＋B」）')
      for p in parts:
        if p != ANY and p not in sets: errs.append(f'{n}行目 使えるセット：「{p}」というセットが見つかりません')
      if parts == [ANY] or (len(parts) == 2 and parts[0] == parts[1]): errs.append(f'{n}行目 使えるセット：「{opt}」は書けません')
      out.append('＋'.join(parts))
    r['使えるセット'] = '／'.join(out)
    for col in ['4+1', '確認済み']:
      v = (r.get(col) or '').strip()
      if v not in ('', '○'): errs.append(f'{n}行目 {col}：「○」か空欄で書きます（「{v}」になっています）')
  return errs

def main():
  fix = '--fix' in sys.argv
  chars, sets = load_data()
  text = CSV.read_text(encoding='utf-8-sig')
  rd = csv.DictReader(io.StringIO(text))
  if rd.fieldnames != COLS: print('1行目（見出し）は次のとおりにしてください：\n' + ','.join(COLS)); sys.exit(1)
  rows = [(i + 2, r) for i, r in enumerate(rd)]
  errs = check(rows, chars, sets, fix)
  for e in errs: print(e)
  if fix:
    buf = io.StringIO(); w = csv.DictWriter(buf, COLS, lineterminator='\n'); w.writeheader()
    for _, r in rows: w.writerow({k: (r.get(k) or '').strip() for k in COLS})
    CSV.write_text(buf.getvalue(), encoding='utf-8')
  done = sum(1 for _, r in rows if (r.get('確認済み') or '').strip() == '○')
  filled = sum(1 for _, r in rows if (r.get('有効OP') or '').strip())
  print(f'{len(rows)}人（有効OPあり {filled}人・確認済み {done}人）' + ('：問題なし' if not errs else f'：直すところ {len(errs)}件'))
  sys.exit(1 if errs else 0)

if __name__ == '__main__': main()
