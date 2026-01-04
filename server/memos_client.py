#!/usr/bin/env python3
"""
Memos API クライアント
"""

from typing import Dict, List

import requests

from .config import MEMOS_URL, MEMOS_ACCESS_TOKEN, MEMOS_LEARN_AGENT_TOKEN


class MemosClient:
    """Memos API との通信を担当"""

    def __init__(self, url: str = MEMOS_URL, token: str = MEMOS_ACCESS_TOKEN, learn_token: str = MEMOS_LEARN_AGENT_TOKEN):
        self.url = url
        self.token = token
        self.learn_token = learn_token

    def create_memo(self, content: str, visibility: str = "PUBLIC") -> Dict:
        """メモを作成"""
        headers = {"Authorization": f"Bearer {self.learn_token}"}
        data = {"content": content, "visibility": visibility}
        response = requests.post(f"{self.url}/api/v1/memos", headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def fetch_memos(self) -> List[Dict]:
        """Memosから全てのメモを取得"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.url}/api/v1/memos", headers=headers)
        response.raise_for_status()
        return response.json().get("memos", [])

    @staticmethod
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


# シングルトンインスタンス
memos_client = MemosClient()
