#!/usr/bin/env python3
"""
Memosからラベル付きデータを収集してJSON形式で保存する
"""

import os
import json
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

MEMOS_URL = os.getenv("MEMOS_URL", "http://localhost:5230")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


def fetch_memos() -> List[Dict]:
    """Memosから全てのメモを取得"""
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(f"{MEMOS_URL}/api/v1/memos", headers=headers)
    response.raise_for_status()
    return response.json().get("memos", [])


def parse_memo(memo: Dict) -> Dict:
    """メモからテキストとラベルを抽出"""
    content = memo.get("content", "")
    
    # ハッシュタグからラベルを抽出
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


def save_dataset(data: List[Dict], output_path: str = "data/collected_texts.json"):
    """データセットをJSON形式で保存"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {len(data)} items to {output_path}")


def main():
    print("📥 Fetching memos...")
    memos = fetch_memos()
    
    print(f"📝 Processing {len(memos)} memos...")
    dataset = [parse_memo(memo) for memo in memos]
    
    # ラベル付きデータのみフィルタ
    labeled_data = [d for d in dataset if d["label"] is not None]
    
    print(f"🏷️  Found {len(labeled_data)} labeled items:")
    print(f"   - AI感: {sum(1 for d in labeled_data if d['label'] == 'ai_bad')}")
    print(f"   - 好き: {sum(1 for d in labeled_data if d['label'] == 'good')}")
    
    save_dataset(labeled_data)


if __name__ == "__main__":
    main()