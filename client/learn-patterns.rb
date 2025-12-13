#!/usr/bin/ruby

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Learn Patterns
# @raycast.mode silent
# @raycast.packageName Data Collector

# Optional parameters:
# @raycast.icon 🧠

# Documentation:
# @raycast.description パターン学習を実行します

require 'json'
require 'net/http'
require 'uri'

API_URL = "http://localhost:8080/learn"

begin
  uri = URI.parse(API_URL)
  http = Net::HTTP.new(uri.host, uri.port)
  http.read_timeout = 60  # 学習に時間がかかる場合を考慮
  
  request = Net::HTTP::Post.new(uri.request_uri)
  request['Content-Type'] = 'application/json'
  
  response = http.request(request)
  result = JSON.parse(response.body)
  
  if response.code == "200" && result["success"]
    count = result["patterns_count"] || "?"
    puts "✅ 学習完了 (#{count} パターン)"
  else
    puts "❌ Error: #{result['error'] || response.code}"
  end
rescue => e
  puts "❌ Connection Failed: #{e.message}"
end
