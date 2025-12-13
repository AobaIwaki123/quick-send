#!/usr/bin/ruby

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Save Selected Text
# @raycast.mode silent
# @raycast.packageName Data Collector

# Optional parameters:
# @raycast.icon 🤖
# @raycast.argument1 { "type": "dropdown", "placeholder": "Category", "data": [{"title": "🤮 不快なAI", "value": "ai_bad"}, {"title": "✨ 良文", "value": "good"}, {"title": "👻 不気味", "value": "uncanny"}] }

# Documentation:
# @raycast.description 選択中のテキストを自動コピーして送信します

require 'json'
require 'net/http'
require 'uri'

# --- 修正ポイント 1 ---
# Raycastのウィンドウが閉じて、元のアプリにフォーカスが戻るまで少し待つ
sleep 0.5 

# --- 修正ポイント 2 ---
# 現在のクリップボードの中身を一旦退避（空にする）
# これにより「コピーが失敗したのに前のデータを送ってしまう」事故を防ぐ
system("pbcopy < /dev/null")

# Cmd+C を送信 (System Events経由)
system("osascript -e 'tell application \"System Events\" to keystroke \"c\" using {command down}'")

# --- 修正ポイント 3 ---
# OSがコピー処理を完了するのを確実に待つ (0.1秒だと失敗することがある)
sleep 0.5

# クリップボードの中身を取得
content = `pbpaste`.strip

# エラーハンドリング: 中身が空なら通知を出して終了
if content.empty?
  puts "⚠️ Copy failed. Try again."
  exit 1
end

# 送信処理
category = ARGV[0] || "uncategorized"
uri = URI.parse("http://localhost:3000/api/save")
header = {'Content-Type': 'application/json'}
payload = {
  content: content,
  category: category
}

begin
  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Post.new(uri.request_uri, header)
  request.body = payload.to_json
  response = http.request(request)

  if response.code == "200"
    puts "✅ Saved: #{category}"
  else
    puts "❌ Error: #{response.code}"
  end
rescue => e
  puts "❌ Connection Failed"
end