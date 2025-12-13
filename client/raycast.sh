#!/usr/bin/ruby

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Save to Memos
# @raycast.mode silent
# @raycast.packageName Data Collector

# Optional parameters:
# @raycast.icon 📝
# @raycast.argument1 { "type": "dropdown", "placeholder": "Category", "data": [{"title": "🤮 不快なAI", "value": "ai_bad"}, {"title": "✨ 良文", "value": "good"}, {"title": "👻 不気味", "value": "uncanny"}] }

# Documentation:
# @raycast.description Memosへテキストを保存します

require 'json'
require 'net/http'
require 'uri'

# --- 設定項目: ここにMemosのアクセストークンを貼ってください ---
ACCESS_TOKEN = "PLACE_HOLDER" # envファイルからmake cmdで自動補完される
MEMOS_URL = "http://localhost:5230/api/v1/memos"
# -------------------------------------------------------

# 1. 選択テキストの取得 (前回と同じ処理)
sleep 0.5
system("pbcopy < /dev/null")
system("osascript -e 'tell application \"System Events\" to keystroke \"c\" using {command down}'")
sleep 0.5
content = `pbpaste`.strip

if content.empty?
  puts "⚠️ No text selected"
  exit 1
end

# 2. タグの形成 (Memosはハッシュタグ形式 #tag で管理します)
tag_key = ARGV[0] || "uncategorized"
final_content = "#{content}\n\n##{tag_key}"

# 3. Memos APIへ送信
uri = URI.parse(MEMOS_URL)
header = {
  'Content-Type': 'application/json',
  'Authorization': "Bearer #{ACCESS_TOKEN}"
}
payload = {
  content: final_content,
  visibility: "PRIVATE" # 公開範囲
}

begin
  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Post.new(uri.request_uri, header)
  request.body = payload.to_json
  response = http.request(request)

  if response.code == "200"
    puts "✅ Saved to Memos"
  else
    # エラー詳細を表示
    puts "❌ Error: #{response.code} #{response.body}"
  end
rescue => e
  puts "❌ Connection Failed"
end