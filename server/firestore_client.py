#!/usr/bin/env python3
"""
Firestore クライアント
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from google.cloud import firestore
from google.oauth2 import service_account

from .config import DATA_DIR


class FirestoreClient:
    """Firestore との通信を担当"""

    def __init__(self):
        # ローカル開発などでクレデンシャルファイルがある場合に使用
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        # プロジェクトIDの取得（環境変数またはクレデンシャルから自動）
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

        try:
            if credentials_path and os.path.exists(credentials_path):
                self.db = firestore.Client.from_service_account_json(credentials_path)
            else:
                # Cloud Run 環境など、デフォルトのクレデンシャルを使用
                # プロジェクトIDが指定されていない場合は自動検出を試みる
                self.db = firestore.Client(project=self.project_id) if self.project_id else firestore.Client()
                
            print(f"🔥 Firestore initialized (project: {self.db.project})")
        except Exception as e:
            print(f"⚠️ Failed to initialize Firestore: {e}")
            self.db = None

    def save_collected_texts(self, data: List[Dict]) -> bool:
        """収集したテキストデータを保存"""
        if not self.db:
            return False

        batch = self.db.batch()
        collection_ref = self.db.collection("collected_texts")

        count = 0
        for item in data:
            # IDをドキュメントIDとして使用
            doc_ref = collection_ref.document(str(item["id"]))
            batch.set(doc_ref, item)
            count += 1
            
            # バッチ制限（500）ごとにコミット
            if count >= 400:
                batch.commit()
                batch = self.db.batch()
                count = 0
        
        if count > 0:
            batch.commit()
            
        return True

    def load_collected_texts(self) -> List[Dict]:
        """収集したテキストデータを全て取得"""
        if not self.db:
            return []

        docs = self.db.collection("collected_texts").stream()
        return [doc.to_dict() for doc in docs]

    def save_patterns(self, patterns: Dict) -> bool:
        """学習済みパターンを保存"""
        if not self.db:
            return False

        # 最新のパターンとして保存（上書きまたは履歴管理）
        # ここではシンプルに単一のドキュメント 'latest' を更新し、
        # 履歴として timestamp 付きのドキュメントも作成する
        
        patterns["created_at"] = datetime.now()
        
        # latest
        self.db.collection("patterns").document("latest").set(patterns)
        
        # history
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.db.collection("patterns_history").document(timestamp).set(patterns)
        
        return True

    def load_patterns(self) -> Optional[Dict]:
        """最新の学習済みパターンを取得"""
        if not self.db:
            return None

        doc_ref = self.db.collection("patterns").document("latest")
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None

# シングルトンインスタンス
firestore_client = FirestoreClient()
