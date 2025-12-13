#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Save AI Snippet
# @raycast.mode silent
# @raycast.packageName Data Collector

# Optional parameters:
# @raycast.icon 🤖
# @raycast.argument1 { "type": "dropdown", "placeholder": "Category", "data": [{"title": "🤮 不快なAI", "value": "ai_bad"}, {"title": "✨ 良文", "value": "good"}, {"title": "👻 不気味", "value": "uncanny"}] }

# Documentation:
# @raycast.description 選択中のテキストをローカルサーバーに送信します
# @raycast.author User

# 選択中のテキストを取得 (macOS標準機能)
SELECTED_TEXT=$(pbpaste)

# もし選択テキストがなければエラー終了
if [ -z "$SELECTED_TEXT" ]; then
  echo "⚠️ Clipboard is empty"
  exit 1
fi

# エスケープ処理 (JSON用)
JSON_CONTENT=$(jq -n --arg txt "$SELECTED_TEXT" --arg cat "$1" '{content: $txt, category: $cat}')

# サーバーへ送信
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "$JSON_CONTENT" http://localhost:3000/api/save)

# 結果通知
echo "✅ Saved to Collection"