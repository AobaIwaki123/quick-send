#!/usr/bin/env python3
"""
API リクエストハンドラ
"""

import json
from http.server import BaseHTTPRequestHandler

from .config import DATA_DIR
from .data_collector import data_collector
from .pattern_learner import pattern_learner


class APIHandler(BaseHTTPRequestHandler):
    """HTTP API リクエストハンドラ"""

    def do_GET(self):
        if self.path == "/health":
            self.send_json({"status": "ok"})
        elif self.path == "/patterns":
            self.handle_get_patterns()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/collect":
            self.handle_collect()
        elif self.path == "/learn":
            self.handle_learn()
        else:
            self.send_error(404)

    def handle_collect(self):
        """データ収集"""
        try:
            result = data_collector.collect_and_save()
            self.send_json({"success": True, **result})
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_learn(self):
        """学習処理（collect + learn）"""
        try:
            # 1. データ収集
            collect_result = data_collector.collect_and_save()

            # 2. パターン学習
            learn_result = pattern_learner.run()

            if "error" in learn_result:
                self.send_json(learn_result, status=400)
            else:
                self.send_json({
                    "success": True,
                    "collected": collect_result,
                    "learned": learn_result
                })
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_get_patterns(self):
        """学習済みパターンを取得"""
        patterns_path = DATA_DIR / "learned_patterns.json"
        if patterns_path.exists():
            with open(patterns_path, "r", encoding="utf-8") as f:
                patterns = json.load(f)
            self.send_json(patterns)
        else:
            self.send_json({"error": "パターンがありません"}, status=404)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")
