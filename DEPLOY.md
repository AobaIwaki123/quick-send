# Cloud Run デプロイガイド

このガイドでは、`Makefile` を使用して API サーバーを Cloud Run にデプロイする手順を説明します。

## 事前準備

1.  **GCP プロジェクトの設定**: [MANUAL.md](./MANUAL.md) の手順が完了していることを確認してください。
2.  **gcloud CLI**: インストール済みで、認証が完了していること (`gcloud auth login`)。
3.  **プロジェクト設定**: `gcloud config set project [YOUR_PROJECT_ID]`。

## API Server のデプロイ

### 1. コンテナイメージのビルド

Docker イメージをビルドし、Cloud Build を使用して Google Container Registry (GCR) にプッシュします。

```sh
# 'your-project-id' を実際のプロジェクトIDに置き換えてください
make gcp-build PROJECT_ID=th-zenn-ai-hackathon
```

### 2. Cloud Run へのデプロイ

イメージを Cloud Run にデプロイします。

```sh
make gcp-deploy PROJECT_ID=th-zenn-ai-hackathon REGION=asia-northeast1
```

**デプロイ設定**:
`Makefile` を更新したので、デプロイ時に環境変数を直接指定できます：

```sh
make gcp-deploy \
  PROJECT_ID=th-zenn-ai-hackathon \
  REGION=asia-northeast1 \
  MEMOS_URL=https://memos-xxxxx-an.a.run.app \
  MEMOS_ACCESS_TOKEN=your-memos-access-token \
  GEMINI_API_KEY=your-gemini-api-key \
  GEMINI_MODEL=2.5-flash
```

もちろん、Cloud Console から後で設定することも可能です。

---

## Memos のデプロイ (Cloud SQL 使用)

Memos 本体を Cloud Run にデプロイします。こちらは Dockerfile のビルドは不要で、公式イメージを使用します。

### 1. Cloud SQL 接続情報の確認
以下の情報を用意してください（`MANUAL.md` で作成したもの）。
- **接続名**: `Project-ID:Region:Instance-ID` (例: `th-zenn-ai-hackathon:asia-northeast1:memos-db`)
- **DBユーザー**: `memos`
- **DBパスワード**: `[PASSWORD]`
- **DB名**: `memos`

### 2. デプロイコマンドの実行

以下のコマンドを実行してデプロイします。`MEMOS_DB_PASS` にはデータベース作成時に設定したパスワードを指定してください。

```sh
make gcp-deploy-memos \
  PROJECT_ID=th-zenn-ai-hackathon \
  MEMOS_DB_INSTANCE=th-zenn-ai-hackathon:asia-northeast1:memos-db \
  MEMOS_DB_PASS=your-strong-password
```

*解説*:
- `--add-cloudsql-instances`: Cloud Run サイドカーとして Cloud SQL Proxy を起動し、Unix Socket 経由で接続できるようにします。
- `MEMOS_DSN`: Memos が接続するための接続文字列です。`@localhost` となっていますが、Cloud SQL Proxy 経由で接続されます。
