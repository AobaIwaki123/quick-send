# Architecture

## 概要

ユーザーがラベル付けした文章データから、「AI感」を感じる文章の特徴を抽出・言語化するシステム。

## システム構成

```mermaid
graph LR
    subgraph "Raycast"
        R1[Quick Send<br/>テキスト保存]
        R2[Learn Patterns<br/>学習呼び出し]
    end
    
    subgraph "Docker"
        M[Memos<br/>:5230]
        API[API Server<br/>:8080]
    end
    
    subgraph "Google AI"
        NL[Natural Language API<br/>感情分析]
        G[Gemini API<br/>パターン生成]
    end
    
    subgraph "データ"
        D[(memos_data/)]
    end
    
    R1 -->|"テキスト + ラベル"| M
    R2 -->|POST /learn| API
    API -->|GET /api/v1/memos| M
    API -->|感情分析| NL
    API -->|パターン生成| G
    API -->|JSON| D
```

## 学習パイプライン

```mermaid
sequenceDiagram
    participant API as API Server
    participant NL as Natural Language API
    participant Gemini
    
    API->>API: Memosからデータ収集
    
    loop 各テキスト
        API->>NL: 感情分析
        NL-->>API: score, magnitude
    end
    
    API->>API: 特徴量を集計
    API->>Gemini: プロンプト + 特徴量
    Gemini-->>API: パターン (JSON)
    API->>API: learned_patterns.json 保存
```

## ディレクトリ構成

```
quick-send/
├── client/
│   ├── raycast.rb          # テキスト保存 (Raycast)
│   └── learn-patterns.rb   # 学習呼び出し (Raycast)
├── server/
│   ├── app.py              # API サーバー
│   ├── nl_api.py           # Natural Language API クライアント
│   └── gemini.py           # Gemini API クライアント
├── prompts/
│   ├── system.md
│   └── pattern_learning.md
├── memos_data/
│   ├── collected_texts.json
│   └── learned_patterns.json
└── compose.yml
```

## API エンドポイント

| メソッド | パス        | 説明                      |
| -------- | ----------- | ------------------------- |
| POST     | `/collect`  | Memos からデータ収集      |
| POST     | `/learn`    | データ収集 + パターン学習 |
| GET      | `/patterns` | 学習済みパターンを取得    |
| GET      | `/health`   | ヘルスチェック            |

## 環境変数

| 変数名               | 説明                     | デフォルト     |
| -------------------- | ------------------------ | -------------- |
| `MEMOS_URL`          | Memos API エンドポイント | localhost:5230 |
| `MEMOS_ACCESS_TOKEN` | Memos アクセストークン   | -              |
| `GEMINI_API_KEY`     | Gemini API キー          | -              |
| `GEMINI_MODEL`       | 使用モデル               | 2.5-flash      |
| `ENABLE_NL_API`      | NL API を有効化          | false          |

## Gemini モデル

| キー      | モデル名                     |
| --------- | ---------------------------- |
| 2.0-flash | gemini-2.0-flash             |
| 2.5-flash | gemini-2.5-flash             |
| 2.5-pro   | gemini-2.5-pro-preview-06-05 |
| 3.0-pro   | gemini-3.0-pro-preview       |

## コマンド

| コマンド                  | 説明                       |
| ------------------------- | -------------------------- |
| `make up`                 | 起動                       |
| `make down`               | 停止                       |
| `make logs`               | API ログ表示               |
| `make collect`            | データ収集                 |
| `make learn`              | パターン学習               |
| `make patterns`           | パターン表示               |
| `make cp-raycast-scripts` | Raycast スクリプトをコピー |
