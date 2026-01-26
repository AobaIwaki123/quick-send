#!/usr/bin/env python3
"""
設定管理モジュール
"""

import os
from pathlib import Path

# サーバー設定
PORT = 8080

# Memos API 設定
MEMOS_URL = os.getenv("MEMOS_URL", "http://localhost:5230")
MEMOS_ACCESS_TOKEN = os.getenv("MEMOS_ACCESS_TOKEN", "")

# パス設定 (Docker 内では /app がルート)
PROJECT_ROOT = Path("/app") if Path("/app").exists() else Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "memos_data"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
