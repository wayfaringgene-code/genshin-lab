# Enka.Network 中継（Cloudflare Workers）

Enka.Network はブラウザからの直接の呼び出しを許していない（CORS）ので、命ノ星座カードの「UIDで取得」はこの中継を通して Enka に問い合わせる。

- `GET /uid/{UID}` → `https://enka.network/api/uid/{UID}/` の応答をそのまま返す
- 受け付けるのは `enka-proxy.js` の `ALLOW` に書いたページだけ（GitHub Pages と、手元で試すときの `http://localhost:8000`）
- Enka の決まりに合わせて独自の `User-Agent` を付ける。応答の `ttl` の間は、使える環境ならキャッシュを返す
- 無料プランの範囲（1日10万回まで）で足りる

## 置き方（Cloudflare のダッシュボードで貼り付ける）

1. Cloudflare のアカウントを作り、ダッシュボードの **Workers & Pages** を開く
2. **Create application**（作成）から、「Hello World」の Worker を作る。名前は `enka-proxy` など。作るとそのまま公開される
3. できた Worker の **Edit code**（コードを編集）を開き、中身を全部消して `enka-proxy.js` の中身を貼り付け、**Deploy**
4. Worker の URL（`https://enka-proxy.〇〇.workers.dev`）を控える
5. `tools/build_card.py` の `ENKA_PROXY` に、その URL に `/uid/` を付けたもの（例：`https://enka-proxy.〇〇.workers.dev/uid/`）を入れて push

## 確かめ方

ブラウザで `https://enka-proxy.〇〇.workers.dev/uid/{自分のUID}` を開いて、文字だらけのJSONが出れば動いている。

## 直すとき

`enka-proxy.js` を直したら、ダッシュボードの **Edit code** に貼り直して **Deploy**。`ALLOW` を増やすのは、別の場所にページを置いたとき。
