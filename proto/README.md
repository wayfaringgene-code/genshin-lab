# 試作のページ（公開しない）

`tools/build_pages.py` は、このフォルダを公開しない。claude.ai の artifact（自分だけが見られる版）で触って確かめるためのもの。

| ファイル | 中身 | artifact |
|---|---|---|
| `subop-guide.html` | サブOPの効き方：前提（メインOP・回数・厳選の現実度・バフ）→ 答え（いちばん良い配分・1%以内の幅・育てる順番）→ くわしく（配分の山・三角の地図・次の1回）、GOODファイルでの診断、計算式とバフ（手入力のバフ・指数） | https://claude.ai/artifact/CFUMGFekRLv9ane18QeoX3 |
| `types.html` | 型くらべ：キャラ×型を「箱」の欄から組み立てて、育てる順番の図と有効OPを比べる。箱の一覧つき | https://claude.ai/artifact/RbFLEmz3CLQRj4sE9QyUcm |

- どちらも1つのHTMLで完結している（計算のコードも中に入っている）。`subop-guide.html` の計算は `tools/build_card.py` の `DMG_MODELS` から写したもの
- GOODファイルの中身は入れていない（ページで読み込むだけ）
- 考え方と経緯は `docs/ROADMAP.md` の 2.8・2.9
