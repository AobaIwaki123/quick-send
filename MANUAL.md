# 手動セットアップ手順

Cloud Run にデプロイする前に、Google Cloud 環境の構成が必要です。

## 1. Google Cloud プロジェクトのセットアップ

1.  **プロジェクトの作成**: [Google Cloud Console](https://console.cloud.google.com/) にアクセスし、新しいプロジェクトを作成します（例: `quick-send-prod`）。
2.  **請求の有効化**: プロジェクトで請求機能が有効になっていることを確認してください。

## 2. API の有効化

「API とサービス」>「ライブラリ」から、以下の API を有効にしてください：
- **Cloud Run API**
- **Artifact Registry API** (Docker イメージの保存用)
- **Cloud Build API** (クラウド上でビルドする場合、オプション)
- **Firestore API**
- **Cloud SQL Admin API** (Cloud SQL を使用する場合)

## 3. Firestore のセットアップ

1.  Cloud Console で **Firestore** に移動します。
2.  **データベースの作成** をクリックします。
3.  **ネイティブ モード** を選択します（Webアプリにはこちらが推奨されます）。
4.  **ロケーション** を選択します（例: 東京なら `asia-northeast1`）。
5.  **セキュリティ ルール**: 初期の検証用に「テスト モード」（全公開）で開始するか、本番公開前に「本番モード」（ロックダウン）に切り替えて適切なルールを設定してください。
    - このシステムはバックエンドサービスが Admin SDK 経由で Firestore にアクセスするため、ルールはバイパスされます。したがって、SDK 利用のみであれば「本番モード（デフォルト拒否）」でも問題ありません。

## 4. Cloud SQL (PostgreSQL) のセットアップ

Memos 本体をデプロイする場合に必要です。

1.  Cloud Console で **SQL** に移動します。
2.  **インスタンスを作成** をクリックし、**PostgreSQL** を選択します。
3.  **インスタンス ID** は任意の名前（例: `memos-db`）。
4.  **パスワード** を生成し、必ず控えておいてください。
5.  **Database version**: PostgreSQL 15 (または 16)。
6.  **Configuration**:
    - **本番**: Enterprise Edition を選択。
    - **開発/テスト**: "Shared core" の `db-f1-micro` (月額 ~$15) を選択するとコストを抑えられますが、SLAはありません。
7.  **Region**: Cloud Run と同じ場所 (`asia-northeast1`) を選択。
8.  インスタンス作成完了まで数分待ちます。

### データベースとユーザーの作成

1.  インスタンスの詳細画面 > **Databases** > **Create Database**。
    - 名前: `memos`
2.  **Users** > **Add User Account**。
    - ユーザー名: `memos` (デフォルトの postgres でも可)
    - パスワード: 強力なパスワードを設定

## 5. ローカル用の認証情報（ローカルテスト用）

Firestore をローカル環境でテストしたい場合：

1.  **IAM と管理** > **サービス アカウント** に移動します。
2.  サービス アカウントを作成します（例: `local-dev`）。
3.  ロール **Cloud Datastore ユーザー**（または Firestore ユーザー）を付与します。
4.  **キー** (JSON) を作成してダウンロードします。
5.  環境変数を設定します：
    ```sh
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/key.json"
    export GOOGLE_CLOUD_PROJECT="your-project-id"
    ```
