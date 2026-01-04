#!/usr/bin/ruby

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Quick Send
# @raycast.mode silent
# @raycast.packageName Data Collector

# Optional parameters:
# @raycast.icon ⚡
# @raycast.argument1 { "type": "dropdown", "placeholder": "Category", "data": [{"title": "👎 AI感", "value": "ai_bad"}, {"title": "👍 好き", "value": "good"}] }

# Documentation:
# @raycast.description Memosへテキストを保存します

require 'json'
require 'net/http'
require 'uri'

# --- 設定項目: ここにMemosのアクセストークンを貼ってください ---
ACCESS_TOKEN = "PLACE_HOLDER" # make cp-raycast-scriptで自動補完される
MEMOS_URL = "https://memos-976586712956.asia-northeast1.run.app/api/v1/memos"
# -------------------------------------------------------

# 1. 選択テキストの取得
sleep 0.5
system("pbcopy < /dev/null") # clipboardをクリア
system("osascript -e 'tell application \"System Events\" to keystroke \"c\" using {command down}'") # 選択テキストをコピー
sleep 0.5
content = `pbpaste`.strip # clipboardからテキストを取得

# テキストの存在チェック
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
  http.use_ssl = (uri.scheme == "https")
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