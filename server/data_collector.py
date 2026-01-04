#!/usr/bin/env python3
"""
データ収集モジュール
"""

import json
from typing import Dict


from .config import DATA_DIR
from .memos_client import memos_client
from .firestore_client import firestore_client


class DataCollector:
    """Memosからのデータ収集と保存を担当"""

    def __init__(self, client=memos_client, db_client=firestore_client):
        self.client = client
        self.db_client = db_client

    def collect_and_save(self) -> Dict:
        """Memosからデータを収集して保存"""
        memos = self.client.fetch_memos()
        dataset = [self.client.parse_memo(memo) for memo in memos]
        labeled_data = [d for d in dataset if d["label"] is not None]

        # Firestoreに保存
        if self.db_client and self.db_client.db:
            success = self.db_client.save_collected_texts(labeled_data)
            if not success:
                print("⚠️ Firestore save failed, falling back to local file (if implemented) or ignoring.")
        else:
             # ローカルフォールバック (Firestoreが無効な場合)
             # 本来はここでもエラーにするか、開発用としてJSON保存を残すか検討
             # 今回は開発用としてJSON保存も残しておく（移行期間中）
             self._save_dataset_local(labeled_data)

        ai_bad_count = sum(1 for d in labeled_data if d["label"] == "ai_bad")
        good_count = sum(1 for d in labeled_data if d["label"] == "good")

        return {
            "total": len(labeled_data),
            "ai_bad": ai_bad_count,
            "good": good_count
        }

    def _save_dataset_local(self, data: list) -> None:
        """データセットをファイルに保存 (Fallback)"""
        print("💾 Saving to local JSON (Fallback)")
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DATA_DIR / "collected_texts.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# シングルトンインスタンス
data_collector = DataCollector()
