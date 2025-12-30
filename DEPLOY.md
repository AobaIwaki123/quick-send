# Cloud Run デプロイガイド

このガイドでは、`Makefile` を使用して API サーバーを Cloud Run にデプロイする手順を説明します。

## 事前準備

1.  **GCP プロジェクトの設定**: [MANUAL.md](./MANUAL.md) の手順が完了していることを確認してください。
2.  **gcloud CLI**: インストール済みで、認証が完了していること (`gcloud auth login`)。
3.  **プロジェクト設定**: `gcloud config set project [YOUR_PROJECT_ID]`。

## デプロイ手順

`Makefile` を使用して、ビルドとデプロイを簡単に行えます。デフォルトの変数（`PROJECT_ID`, `REGION` など）は、コマンドライン引数で上書き可能です。

### 1. コンテナイメージのビルド

Docker イメージをビルドし、Cloud Build を使用して Google Container Registry (GCR) にプッシュします。

```sh
# 'your-project-id' を実際のプロジェクトIDに置き換えてください
make gcp-build PROJECT_ID=quick-send-prod
```

### 2. Cloud Run へのデプロイ

イメージを Cloud Run にデプロイします。

```sh
make gcp-deploy PROJECT_ID=quick-send-prod REGION=asia-northeast1
```

**注意**:
- 初回のデプロイ時に、サービスエージェントの作成許可を求められる場合があります（`y` を入力）。
- このコマンドには `--allow-unauthenticated` が含まれており、API が一般公開されます。アクセス制限を行いたい場合は、このフラグを削除してください。

### 3. デプロイの確認

デプロイ完了後、サービス URL が出力されます（例: `https://quick-send-api-xxxxx-an.a.run.app`）。

ステータスを確認します：
```sh
curl https://[YOUR-SERVICE-URL]/health
```

## 環境変数

`make gcp-deploy` コマンドは基本的な環境変数を設定します。`MEMOS_URL` や `GEMINI_API_KEY` など、その他の変数は Cloud Console やコマンドラインから追加設定する必要があります。

**方法 A: Cloud Console (推奨)**
1.  Cloud Run > `quick-send-api` > **新しいリビジョンの編集とデプロイ** に移動します。
2.  **変数とシークレット** タブを開きます。
3.  `MEMOS_URL` (Memos サービスの URL) を追加します。
4.  `GEMINI_API_KEY` を追加します（セキュリティ向上のため Secret Manager の利用を推奨）。

**方法 B: コマンドライン**
`Makefile` を修正して `--set-env-vars` を追加するか、手動でコマンドを実行します：
```sh
gcloud run services update quick-send-api \
  --set-env-vars MEMOS_URL=http://your-memos-url,GEMINI_API_KEY=your-key \
  --region asia-northeast1
```
