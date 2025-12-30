# 移行ノート

## Firestore 統合とフォールバックメカニズム

Cloud Run への移行に伴い、クラウド環境（ステートレス）とローカル環境（ステートフル/ファイルベース）の両方で API サーバーが動作するように、**ハイブリッド / フォールバック戦略**を実装しました。これにより、クラウド環境のセットアップが完了する前でも、ローカルでの開発を継続できます。

### フォールバックロジック

`FirestoreClient` は初期化時に Google Cloud のクレデンシャル（認証情報）を確認します。
- **クレデンシャルがある場合**: Firestore に接続します。
- **クレデンシャルがない場合**: DB接続を行わずに初期化します。

`DataCollector`（メモ収集）と `PatternLearner`（パターン学習）の両方がこのクライアントを使用します。
- **書き込み操作**: Firestore が利用できない場合、データはローカルファイルシステムの `memos_data/*.json` に保存されます。
- **読み込み操作**: Firestore が利用できない、またはデータが空の場合、システムはローカルの `memos_data/*.json` ファイルからの読み込みを試みます。

この仕組みにより、Google Cloud 環境が完全に構成される前でも、既存の JSON データを使用してローカルでの開発を継続できます。

### 主な変更ファイル
- `server/firestore_client.py`: 接続とフォールバックチェックを処理する新しいクライアント。
- `server/data_collector.py`: Firestore への保存を試み、失敗時は `_save_dataset_local` にフォールバックします。
- `server/pattern_learner.py`: Firestore からの読み書きを試み、失敗時は JSON にフォールバックします。
- `server/api_handler.py`: Firestore からパターンを提供し、失敗時はローカル JSON にフォールバックします。

## Memos データベース移行 (SQLite -> Cloud SQL)

Cloud Run で Memos を運用する場合、データベースをローカルの SQLite (`memos_prod.db`) から Cloud SQL (PostgreSQL) に切り替える必要があります。

### 推奨される移行手順

データベースの構造が異なるため、ファイルを直接コピーすることはできません。

1.  **フレッシュスタート（推奨）**:
    - 新しいデータベースで運用を開始し、必要なメモだけ手動で転記します。開発用データしかないのであれば、これが最も簡単です。

2.  **Memos のバックアップ機能**:
    - ローカルの Memos で `Settings` > `System` > `Export & Import` からデータをエクスポートします。
    - Cloud SQL で新しい Memos を立ち上げ、同じ画面からインポートします。
    - *注意*: バージョン間の互換性に依存するため、同じバージョンの Memos を使用してください。

3.  **pgloader (上級者向け)**:
    - ツール `pgloader` を使用して SQLite データを PostgreSQL に変換して流し込みます。
    - 手順が複雑になるため、データ量が大量にある場合以外は推奨しません。
