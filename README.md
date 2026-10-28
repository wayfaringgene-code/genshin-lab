# 聖遺物ラボ

原神の聖遺物を「秘境を何日回ると届くか」で測る、非公式のファンツール群です（HoYoverse とは関係ありません）。

| ページ | URL | 中身 |
|---|---|---|
| 命ノ星座カード | `/` | 入口。UIDを入れると、キャラごとの聖遺物を秘境レベル（平均的な人が秘境だけで揃えるのにかかる日数）で測ってカードにする。動画・スクショからの取り込みも |
| 聖遺物ラボ：キャラ | `/lab/` | くわしい分析。手持ちのキャラの装備を、秘境レベルで並べる |

保守のしかた（どこに何があるか、困ったときの確認手順）は **[MAINTENANCE.md](MAINTENANCE.md)** にまとめています。

## フォルダ

- `src/lab.html` … **ラボの元**。計算・取り込み・カード描画のコードはすべてここ。ラボを直すときはこのファイルを直す
- `src/scanner/` … 聖遺物ビデオスキャナーの元
- `src/fonts/` … カード画像に埋め込むフォント（Murecho・M PLUS 1p。fontsource の分割 woff2 を JSON にしたもの）
- `tools/build_pages.py` … 公開するページ一式を `_site/` に組み立てる（GitHub Actions が push のたびに実行）
- `tools/build_card.py` … ラボの元から命ノ星座カードを組み立てる
- `tools/build_scan.py` … スキャナーをカードの「取り込む」ページ用に組み立てる
- `tools/build_enka_tables.py` / `tools/enka_tables.json` … Enka.Network の公式リポジトリ（EnkaNetwork/API-docs）から抜き出した、キャラ名・セット名・サブOPの伸び幅の対応表。新キャラ・新セットが出たら作り直す
- `proxy/` … 「UIDで取得」用の Enka.Network 中継（Cloudflare Workers）。置き方は `proxy/README.md`
- `src/portraits/` … 同梱の立ち絵（`tools/build_portraits.py` で登録。集め方は `docs/PORTRAITS.md`）
- `src/og.png` … X などにURLを貼ったときの画像（`tools/make_og.mjs` で作る）
- `tools/patch_lab_cardlink.py` … ラボのキャラの詳細のカードを、命ノ星座カードへのリンクに置き換える（`src/lab.html` には適用済み）

## 手元で組み立てる

```
python3 tools/build_pages.py
python3 -m http.server 8000 --directory _site
```

## 公開

`main` に push すると、`.github/workflows/pages.yml` が組み立てて GitHub Pages に公開します（Settings → Pages の Source は「GitHub Actions」）。

## 使っているもの

- 確率の出典：KQM「Genshin Impact Artifacts Guide」、Genshin Impact Wiki（Fandom）「Artifact/Distribution」
- UID からの取り込み：Enka.Network
- 動画の読み取り：Tesseract.js（Apache-2.0）と日本語の認識データ（tessdata、Apache-2.0）
- 聖遺物の名前・数値データ：Genshin Optimizer（MIT）
- フォント：Murecho、M PLUS 1p（SIL Open Font License）
