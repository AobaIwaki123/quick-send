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
├── docs/                          # ドキュメント
│   ├── JSON.md                   # JSON仕様
│   └── arch-prompt.md            # アーキテクチャプロンプト
├── img/                           # 画像リソース
│   └── demo.png                  # デモ画像
├── creds/                         # 認証情報 (gitignore推奨)
├── compose.yml                    # Docker Compose設定
├── Makefile                       # Make コマンド定義
├── pyproject.toml                 # Python依存関係管理
├── .env.example                   # 環境変数テンプレート
├── ARCHITECTURE.md                # アーキテクチャドキュメント
├── workflow.md                    # ワークフロー説明
└── README.md                      # このファイル
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