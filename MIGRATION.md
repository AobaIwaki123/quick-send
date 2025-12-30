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
