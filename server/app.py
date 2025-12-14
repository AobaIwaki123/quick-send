#!/usr/bin/env python3
"""
API サーバー - データ収集とパターン学習を提供
"""

from http.server import HTTPServer

from .config import PORT, MEMOS_URL, DATA_DIR
from .api_handler import APIHandler


def main():
    server = HTTPServer(("0.0.0.0", PORT), APIHandler)
    print(f"🚀 API Server running on http://0.0.0.0:{PORT}")
    print(f"")
    print(f"Endpoints:")
    print(f"  POST /collect  - Memosからデータ収集")
    print(f"  POST /learn    - データ収集 + パターン学習")
    print(f"  GET  /patterns - 学習済みパターンを取得")
    print(f"  GET  /health   - ヘルスチェック")
    print(f"")
    print(f"Environment:")
    print(f"  MEMOS_URL: {MEMOS_URL}")
    print(f"  DATA_DIR:  {DATA_DIR}")
    server.serve_forever()


if __name__ == "__main__":
    main()
