## 指示

以下のmermaidを参考に、アーキテクチャの図を作成してください。
全体的な色合いを意識し、ぱっと見で役割がわかるようにしてください
アイコンがあるものは元々の色を保持してください
矢印は直線でお願いします
灰色、紫は使わないでください
異なるブロックは異なる色を使用してください
背景は無地で真っ白ではない白色にしてください
色合いの組み合わせが補色にならようにしてください
それぞれのブロックと関係性のわかりやすさを意識してください。

## 注意

`A[`のような生成時の文字列が混入することがあるため、必ず除去してください

## アイコン画像

以下を参考にしてください
全体的にシンプルにお願いします

### Raycast

https://www.raycast.com/uploads/redesign/new-appicon.png

### Memos

カラフルでモダンなメモアプリのアイコンを作成してください

## Firestore

https://soichisumi.net/images/firestore.png

### Cloud Functions

https://blog.usize-tech.com/contents/uploads/2022/07/eyecatch-cloudfunctions.png

### Vertex AI

シンプルにしてください


https://ai-market.jp/wp-content/uploads/2024/02/googlecloud-vertexai-960x504-1.webp

### Gemin API

https://images.ctfassets.net/ct0aopd36mqt/wp-thumbnail-6a331d7c70f1897ca2ef1ad4cbe7c6bf/78c556633ae5115aa065636cc4a1160a/eyecatch_gemini?w=1920&fm=webp

### Natural Language API

https://devio2023-media.developers.io/wp-content/uploads/2022/09/googlecloud-cloud-natural-language-api.png

### ADK Agent System

エージェントの数が多いので、それぞれのエージェントはシンプルにしてください
エージェント同士の関係性がわかるようにしてください

### Agent Engine Runtime

Agent Engine Runtimeに沿ったシンプルなアイコンを作成してください

## アーキテクチャ

```mermaid
graph TB
    subgraph "フロントエンド"
        A[Raycast Extension]
        B[Memos UI]
    end
    
    subgraph "Firebase"
        C[(Firestore)]
        D[Cloud Functions]
    end
    
    subgraph "Google AI Services"
        E[Natural Language API]
        F[Gemini API]
        G[Vertex AI Embeddings]
    end
    
    subgraph "ADK Agent System"
        H[Pattern Analyzer Agent]
        I[Evaluator Agent]
        J[Prompt Optimizer Agent]
        K[Root Agent]
    end
    
    subgraph "Vertex AI"
        L[Agent Engine Runtime]
        M[Vector Search]
    end
    
    A -->|1. 選択テキスト送信| B
    B -->|2. 保存| C
    
    A -->|3. 分析コマンド実行| D
    D -->|4. 即座にACK応答| A
    D -->|5. メモ取得| C
    D -->|6. 感情・エンティティ分析| E
    D -->|7. AI感検出・分類| F
    D -->|8. ベクトル化| G
    G -->|9. インデックス登録| M
    D -->|10. 分析結果/エラー| B
    B -->|11. Memosに投稿| C
    
    C -->|12. 定期実行| K
    K -->|パターン分析| H
    K -->|品質評価| I
    K -->|プロンプト生成| J
    H -->|類似検索| M
    H & I & J -->|分析結果/エラー| B
    B -->|Memosに投稿| C
    
    K -.->|デプロイ| L
    
    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#fff4e6
    style D fill:#fff4e6
    style E fill:#e8f5e9
    style F fill:#e8f5e9
    style G fill:#e8f5e9
    style H fill:#f3e5f5
    style I fill:#f3e5f5
    style J fill:#f3e5f5
    style K fill:#f3e5f5
    style L fill:#fce4ec
    style M fill:#fce4ec
```

## 生成後

プロンプトに従えたかどうかを自己評価し、できていない場合はその点を列挙してください