# Raycast × MemosでAI感のある雑な文章を収集する

## Abstract

RaycastとMemosを組み合わせた文章収集ツール

`cmd + i` など、設定したショートカットキーで選択したテキストをMemosに転送する

<img src="img/demo.png" alt="demo" width="800">

## Purpose

AI感のある雑な文章を効率的に収集し、アンチパターンとしてAIに投入できるようにする。

## Architecture

```mermaid
graph LR
    A[Raycast] -->|収集| B[Memos]
    A -->|分析| C[Cloud Functions]
    C -->|AI分析| D[Google AI]
    D -->|結果| B
    B --> E[(Firestore)]
    E -->|学習| F[ADK Agents]
    F -->|改善| B
```

```mermaid
sequenceDiagram
    participant Raycast
    participant Memos
    participant Firestore
    participant AI as Google AI
    participant Agent as ADK Agents
    Raycast->>Memos: テキストを送信
    Memos->>Firestore: テキストを保存
    Raycast->>AI: 収集したテキストの分析依頼
    AI->>Memos: テキストの分析結果を投稿
    Memos->>Firestore: 分析結果を保存
    Note over Agent: 定期実行
    Agent->>Firestore: 分析後のデータを取得
    Agent->>Agent: パターン学習
    Agent->>Memos: アンチパターンをまとめたプロンプトを投稿
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

## Reference

- [Memos - GitHub](https://github.com/usememos/memos)