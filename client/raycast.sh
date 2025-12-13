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

# 1. AppleScriptを使って「Cmd+C」をシミュレートし、選択テキストをコピー
system("osascript -e 'tell application \"System Events\" to keystroke \"c\" using {command down}'")

# コピーが完了するまで少し待つ（これがないと古いクリップボードを読み込んでしまう）
sleep 0.1

# 2. クリップボードの中身を取得
content = `pbpaste`.strip

if content.empty?
  puts "⚠️ No text selected"
  exit 1
end

# 3. 送信データの準備
category = ARGV[0] || "uncategorized"
uri = URI.parse("http://localhost:3000/api/save")
header = {'Content-Type': 'application/json'}
payload = {
  content: content,
  category: category
}

# 4. サーバーへPOST送信
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