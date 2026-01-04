# Raycast × MemosでAI感のある雑な文章を収集する

## Abstract

RaycastとMemosを組み合わせた文章収集ツール

`cmd + i` など、設定したショートカットキーで選択したテキストをMemosに転送する

<img src="img/demo.png" alt="demo" width="800">

## Purpose

AI感のある雑な文章を効率的に収集し、アンチパターンとしてAIに投入できるようにする。

## ディレクトリ構成

```sh
.
├── client/                        # Raycast用クライアントスクリプト
│   ├── raycast.rb                # Memosへテキスト送信
│   └── learn-patterns.rb         # パターン学習スクリプト
├── server/                        # バックエンドサーバー
│   ├── app.py                    # FastAPI アプリケーション
│   ├── gemini.py                 # Gemini API連携
│   └── nl_api.py                 # Natural Language API
├── memos_data/                    # Memosデータ格納
│   ├── collected_texts.json      # 収集したラベル付きデータ
│   ├── learned_patterns.json     # 学習済みパターン
│   └── memos_prod.db             # Memos SQLiteデータベース
├── prompts/                       # プロンプトテンプレート
│   ├── system.md                 # システムプロンプト
│   └── pattern_learning.md       # パターン学習用プロンプト
```

## Quick Start

```sh
$ make up
Memos: http://lomakecalhost:5230
```

### Memosのアクセストークンを取得する

Memos左下の「Settings」→「My Account」→「Access Tokens」を選択。

`.env.example`を参考に、`.env`を作成する。

Raycastに拡張スクリプトを追加 (自己責任でお願いします)

```sh
$ make cp-raycast-script
```

## Troubleshooting

### macOS

1. システム設定 を開く。
2. プライバシーとセキュリティ -> アクセシビリティ を開く。
   1. Raycast が ON になっているか確認。
3. プライバシーとセキュリティ -> オートメーション を開く。
   1. Raycast の項目を展開し、System Events が ON になっているか確認。

## Cloud Deployment Setup

Cloud Run にデプロイする場合のセットアップ手順です。

### 1. Google Cloud プロジェクトのセットアップ

1.  **プロジェクトの作成**: [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成。
2.  **API の有効化**:
    - Cloud Run API
    - Artifact Registry API
    - Firestore API
    - Cloud SQL Admin API

### 2. Firestore のセットアップ

1.  Cloud Console で **Firestore** を作成（ネイティブモード推奨）。
2.  **ロケーション**: `asia-northeast1` (東京) など。

### 3. Cloud SQL (PostgreSQL) のセットアップ

Memos 本体をデプロイする場合に必要です。

1.  Cloud Console で **SQL** (PostgreSQL) インスタンスを作成。
2.  データベース `memos` とユーザーを作成。

### 4. ローカル開発用認証情報

Firestore をローカルから接続する場合：

1.  サービスアカウントを作成し、`Cloud Datastore User` ロールを付与。
2.  キー (JSON) をダウンロードし、環境変数設定：
    ```sh
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
    export GOOGLE_CLOUD_PROJECT="your-project-id"
    ```

## Database Migration (SQLite -> Cloud SQL)

Cloud Run 運用へ移行する際、SQLite (`memos_prod.db`) から Cloud SQL への移行が必要です。

推奨手順:
1.  **フレッシュスタート**: 新しいデータベースで開始し、必要なメモだけ手動移行。
2.  **Memos エクスポート/インポート**: Memos の `Settings` > `System` > `Export & Import` 機能を使用。

## Reference

- [Memos - GitHub](https://github.com/usememos/memos)