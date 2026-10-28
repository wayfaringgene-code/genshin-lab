# このリポジトリについて（Claude 向け）

- 最初に `MAINTENANCE.md` を読む。どこに何があるか・公開の流れ・困ったときの確認手順がまとまっている。次に何をやるかは `docs/ROADMAP.md`
- 正は `src/lab.html`（ラボの元）。命ノ星座カードは `tools/build_card.py` がラボの元に差分を当てて組み立てる。公開ページは `tools/build_pages.py` が `_site/` に組み立て、`main` への push で GitHub Actions が GitHub Pages に公開する
- 変更したら `python3 tools/build_pages.py` が通ることと、`python3 -m http.server 8000 --directory _site` で開いて動くことを確かめてから push する。push 後は Actions の成功まで見届ける
- 立ち絵の登録は `docs/PORTRAITS.md` の手順（`tools/build_portraits.py`）。見本の立ち絵やカードの見た目を変えたら `src/og.png` も `tools/make_og.mjs` で作り直す
- 中継（`proxy/enka-proxy.js`）は Cloudflare に手で貼って反映する。リポジトリを変えただけでは中継は変わらない
- 公開リポジトリなので、秘密の情報や利用者の Enka の応答データは入れない
- 大きなファイルの書き換えより差分（`build_card.py` の `rep()` の追加）を好む。カードアプリの版番号は `build_card.py` の「命ノ星座カード vX.Y」と `MAINTENANCE.md` の版の記録を一緒に更新する
