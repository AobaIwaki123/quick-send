#!/usr/bin/env python3
"""
API サーバー - データ収集とパターン学習を提供
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, List

import requests

# 設定
PORT = 8080
MEMOS_URL = os.getenv("MEMOS_URL", "http://localhost:5230")
MEMOS_ACCESS_TOKEN = os.getenv("MEMOS_ACCESS_TOKEN", "")

# パス設定 (Docker 内では /app がルート)
PROJECT_ROOT = Path("/app") if Path("/app").exists() else Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "memos_data"
PROMPTS_DIR = PROJECT_ROOT / "prompts"


# =============================================================================
# データ収集
# =============================================================================

def fetch_memos() -> List[Dict]:
    """Memosから全てのメモを取得"""
    headers = {"Authorization": f"Bearer {MEMOS_ACCESS_TOKEN}"}
    response = requests.get(f"{MEMOS_URL}/api/v1/memos", headers=headers)
    response.raise_for_status()
    return response.json().get("memos", [])


def parse_memo(memo: Dict) -> Dict:
    """メモからテキストとラベルを抽出"""
    content = memo.get("content", "")
    
    label = None
    text = content
    
    if "#ai_bad" in content:
        label = "ai_bad"
        text = content.replace("#ai_bad", "").strip()
    elif "#good" in content:
        label = "good"
        text = content.replace("#good", "").strip()
    
    return {
        "id": memo.get("name", ""),
        "text": text,
        "label": label,
        "created_at": memo.get("createTime", ""),
        "updated_at": memo.get("updateTime", "")
    }


def collect_data() -> Dict:
    """Memosからデータを収集して保存"""
    memos = fetch_memos()
    dataset = [parse_memo(memo) for memo in memos]
    labeled_data = [d for d in dataset if d["label"] is not None]
    
    # 保存
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / "collected_texts.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(labeled_data, f, ensure_ascii=False, indent=2)
    
    ai_bad_count = sum(1 for d in labeled_data if d["label"] == "ai_bad")
    good_count = sum(1 for d in labeled_data if d["label"] == "good")
    
    return {
        "total": len(labeled_data),
        "ai_bad": ai_bad_count,
        "good": good_count
    }


# =============================================================================
# パターン学習
# =============================================================================

def load_dataset() -> Dict[str, List[str]]:
    """データセットを読み込み、ラベルごとに分類"""
    dataset_path = DATA_DIR / "collected_texts.json"
    if not dataset_path.exists():
        return {"ai_bad": [], "good": []}
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return {
        "ai_bad": [item["text"] for item in data if item["label"] == "ai_bad"],
        "good": [item["text"] for item in data if item["label"] == "good"]
    }


def learn_patterns(dataset: Dict[str, List[str]]) -> Dict:
    """
    データセットからパターンを学習
    
    TODO: 実際の実装では、ここでADKやVertex AIのAPIを呼び出す
    """
    # デモ用のダミーパターン
    patterns = {
        "patterns": [
            {
                "id": "pattern_1",
                "name": "過度な丁寧語の使用",
                "description": "「〜させていただく」「〜でございます」などの丁寧語が頻出し、不自然に礼儀正しい印象を与える",
                "strength": "strong",
                "frequency": 0.75,
                "examples_from_data": [
                    "本日はお忙しい中ご参加いただきありがとうございます",
                    "ご説明させていただきます"
                ],
                "synthetic_examples": [
                    "こちらの資料をご覧いただけますでしょうか",
                    "ご確認させていただきたく存じます"
                ],
                "detection_rule": "「させていただく」が1文中に2回以上、または文章全体で頻出する場合"
            },
            {
                "id": "pattern_2",
                "name": "機械的な箇条書き構造",
                "description": "「まず」「次に」「最後に」の定型的な展開が多用される",
                "strength": "medium",
                "frequency": 0.60,
                "examples_from_data": [
                    "まず、背景について説明します。次に、具体的な手順を示します。最後にまとめます。"
                ],
                "synthetic_examples": [
                    "第一に〜、第二に〜、第三に〜",
                    "1つ目は〜、2つ目は〜、3つ目は〜"
                ],
                "detection_rule": "「まず/次に/最後に」または番号付けが連続して出現"
            }
        ],
        "summary": {
            "total_patterns": 2,
            "strong_indicators": ["過度な丁寧語の使用"],
            "common_features": {
                "lexical": ["させていただく", "ございます", "存じます"],
                "syntactic": ["箇条書き", "番号付けリスト"],
                "semantic": ["過度に形式的", "個人的視点の欠如"]
            }
        },
        "insights": [
            "ユーザーは形式的すぎる文章をAI感があると判断する傾向",
            "具体例や個人的な視点がある文章は「良い」と評価される"
        ],
        "metadata": {
            "ai_bad_count": len(dataset["ai_bad"]),
            "good_count": len(dataset["good"])
        }
    }
    
    return patterns


def run_learn() -> Dict:
    """学習処理を実行"""
    dataset = load_dataset()
    
    if not dataset["ai_bad"] and not dataset["good"]:
        return {"error": "ラベル付きデータがありません。先にデータを収集してください。"}
    
    patterns = learn_patterns(dataset)
    
    # 保存
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / "learned_patterns.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)
    
    return {
        "success": True,
        "patterns_count": len(patterns["patterns"]),
        "ai_bad_count": len(dataset["ai_bad"]),
        "good_count": len(dataset["good"])
    }


# =============================================================================
# API サーバー
# =============================================================================

class APIHandler(BaseHTTPRequestHandler):
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
            result = collect_data()
            self.send_json({"success": True, **result})
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def handle_learn(self):
        """学習処理（collect + learn）"""
        try:
            # 1. データ収集
            collect_result = collect_data()
            
            # 2. パターン学習
            learn_result = run_learn()
            
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
