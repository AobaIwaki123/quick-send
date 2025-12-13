#!/usr/bin/env python3
"""
API サーバー - Raycast から学習処理を呼び出すためのエンドポイント
"""

import json
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "memos_data"


class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/patterns":
            self.handle_get_patterns()
        elif self.path == "/health":
            self.send_json({"status": "ok"})
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/learn":
            self.handle_learn()
        else:
            self.send_error(404)

    def handle_learn(self):
        """学習処理を実行"""
        try:
            # 1. データ収集
            print("📥 Collecting data from Memos...")
            result = subprocess.run(
                ["python", "scripts/collect_from_memos.py"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.send_json({"error": result.stderr}, status=500)
                return

            # 2. パターン学習
            print("🤖 Learning patterns...")
            result = subprocess.run(
                ["python", "scripts/learn_patterns.py"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.send_json({"error": result.stderr}, status=500)
                return

            # 3. 結果を返す
            patterns_path = DATA_DIR / "learned_patterns.json"
            if patterns_path.exists():
                with open(patterns_path, "r", encoding="utf-8") as f:
                    patterns = json.load(f)
                self.send_json({
                    "success": True,
                    "message": "学習完了",
                    "patterns_count": len(patterns.get("patterns", []))
                })
            else:
                self.send_json({"success": True, "message": "学習完了"})

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
            self.send_json({"error": "No patterns found"}, status=404)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[API] {args[0]}")


def main():
    server = HTTPServer(("0.0.0.0", PORT), APIHandler)
    print(f"🚀 API Server running on http://localhost:{PORT}")
    print(f"   POST /learn    - 学習処理を実行")
    print(f"   GET  /patterns - 学習済みパターンを取得")
    print(f"   GET  /health   - ヘルスチェック")
    server.serve_forever()


if __name__ == "__main__":
    main()
