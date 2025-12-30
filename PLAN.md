# Cloud Run 移行と Firestore 統合計画

Local ファイルシステムに依存している `quick-send` API サーバーのデータを Google Cloud Firestore に移行し、Memos データを Cloud SQL に移行することで、Cloud Run 上でのステートレスな運用を実現します。

## アーキテクチャの変更

### 変更前 (Current: Local Docker Compose)
現状は全てのデータがローカルファイルシステム上に存在します。

```mermaid
graph LR
    subgraph "Local Machine"
        direction TB
        subgraph "Docker Compose"
            M[Memos Service]
            API[API Server]
        end
        
        subgraph "Local Storage (Host Mounted)"
            SQLite[(memos_prod.db<br/>SQLite)]
            JSON[("collected_texts.json<br/>learned_patterns.json")]
        end
    end
    
    M -->|Read/Write| SQLite
    API -->|Read/Write| JSON
    API -->|API Call| M
```

### 変更後 (Proposed: Cloud Run)
Cloud Run はステートレス（再起動でデータが消える）な環境であるため、データの保存先を外部のマネージドサービスに切り替える必要があります。

```mermaid
graph LR
    subgraph "Google Cloud Platform"
        direction TB
        subgraph "Cloud Run"
            M_RUN[Memos Service]
            API_RUN[API Server]
        end
        
        subgraph "Managed Databases"
            SQL[(Cloud SQL<br/>PostgreSQL)]
            FS[(Firestore)]
        end
    end
    
    M_RUN -->|Read/Write| SQL
    API_RUN -->|Read/Write| FS
    API_RUN -->|API Call| M_RUN
```

## 5. Memos サービスの Cloud Run 移行計画

API サーバーの Firestore 化に加え、Memos 本体を Cloud Run + Cloud SQL に移行します。

### Memos の構成変更
- **Docker Image**: 公式イメージ `neosmemo/memos:stable` または現在のカスタムイメージ `iwakiaoba/aoba-memos:v1.0.0` を使用。
- **Database**: SQLite から PostgreSQL (Cloud SQL) に変更。
- **Environment Variables**:
    - `DRIVER`: `postgres`
    - `DSN`: `postgresql://[USER]:[PASSWORD]@localhost/[DB_NAME]?host=/cloudsql/[PROJECT_ID]:[REGION]:[INSTANCE_NAME]`

### Cloud SQL (PostgreSQL) の構成
- **Edition**: Enterprise (または開発用に Micro インスタンス)
- **Version**: PostgreSQL 15, 16 など最新の安定版
- **Connection**: Cloud Run からは Unix Socket 経由で接続

### データ移行戦略
1.  **新規作成**: PostgreSQL で新規データベースとして開始する（推奨）。蓄積済みのメモは手動で再登録、または Memos のエクスポート/インポート機能を利用する。
2.  **SQLite からの移行**: `pgloader` 等のツールを使って SQLite ファイルを PostgreSQL にダンプする、あるいは Memos のバックアップ機能で JSON エクスポートし、新しい環境で復元する。

---

## 提案される変更 (詳細: API Server)

### Python API サーバー (`server/`)

`DataCollector` と `PatternLearner` におけるローカル JSON ファイル操作を、Firestore クライアント経由のアクセスに置き換えます。

#### [NEW] [firestore_client.py](file:///Users/aobaiwaki/quick-send/server/firestore_client.py)
- Firestore とのやり取りをカプセル化します。
    - `save_collected_texts`: Memos から取得したデータを保存
    - `load_collected_texts`: 分析のためにデータを取得
    - `save_patterns`: 生成されたパターンを保存
    - `load_patterns`: フロントエンド表示用に取得

#### [MODIFY] [data_collector.py](file:///Users/aobaiwaki/quick-send/server/data_collector.py)
- `_save_dataset` (JSON保存) を削除・置換。
- `FirestoreClient` を使用してデータを保存。

#### [MODIFY] [pattern_learner.py](file:///Users/aobaiwaki/quick-send/server/pattern_learner.py)
- `load_dataset` (JSON読み込み) を削除・置換。
- `FirestoreClient` から学習データを取得し、結果を保存。

#### [MODIFY] [api_handler.py](file:///Users/aobaiwaki/quick-send/server/api_handler.py)
- データ取得ロジックを Firestore 経由に変更。

#### [MODIFY] [pyproject.toml](file:///Users/aobaiwaki/quick-send/pyproject.toml)
- `google-cloud-firestore` を依存関係に追加。

### インフラストラクチャ

#### [NEW] [Dockerfile](file:///Users/aobaiwaki/quick-send/Dockerfile)
- API サーバー専用の Dockerfile を作成。

## 検証計画

### 自動テスト
- 現状テストスイートがないため、手動検証を中心に行います。

### 手動検証
1.  **ビルド**: Docker ビルドが成功することを確認します。
2.  **ローカル実行 (Firestore モック/Dev)**:
    - Google Cloud クレデンシャルを使用して、ローカルの Python スクリプトが実際の Firestore プロジェクト（またはエミュレータ）に書き込めるか確認します。
