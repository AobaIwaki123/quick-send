#!/usr/bin/env python3
"""
Natural Language AI API クライアント
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

from google.cloud import language_v1


@dataclass
class SentimentResult:
    """感情分析の結果"""
    score: float  # -1.0 (negative) to 1.0 (positive)
    magnitude: float  # 感情の強さ


@dataclass
class TextFeatures:
    """テキストから抽出した特徴量"""
    sentiment: Optional[SentimentResult] = None
    entities: Optional[List[Dict]] = None  # 将来の拡張用
    syntax: Optional[Dict] = None  # 将来の拡張用


class NLAPIClient:
    """Natural Language AI API クライアント"""
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_NL_API", "false").lower() == "true"
        if self.enabled:
            self.client = language_v1.LanguageServiceClient()
    
    def analyze_sentiment(self, text: str) -> Optional[SentimentResult]:
        """
        テキストの感情分析を実行
        
        Returns:
            SentimentResult or None if API is disabled
        """
        if not self.enabled:
            return self._mock_sentiment(text)
        
        document = language_v1.Document(
            content=text,
            type_=language_v1.Document.Type.PLAIN_TEXT,
            language="ja"
        )
        
        response = self.client.analyze_sentiment(
            request={"document": document}
        )
        
        return SentimentResult(
            score=response.document_sentiment.score,
            magnitude=response.document_sentiment.magnitude
        )
    
    def _mock_sentiment(self, text: str) -> SentimentResult:
        """モック: 感情分析"""
        # シンプルなヒューリスティック
        positive_words = ["良い", "素晴らしい", "嬉しい", "好き"]
        negative_words = ["悪い", "ダメ", "嫌い", "問題"]
        
        score = 0.0
        for word in positive_words:
            if word in text:
                score += 0.2
        for word in negative_words:
            if word in text:
                score -= 0.2
        
        score = max(-1.0, min(1.0, score))
        return SentimentResult(score=score, magnitude=abs(score))
    
    def analyze_entities(self, text: str) -> Optional[List[Dict]]:
        """
        エンティティ抽出（将来の拡張用）
        
        現在はモック実装
        """
        # TODO: 実装
        return None
    
    def analyze_syntax(self, text: str) -> Optional[Dict]:
        """
        構文解析（将来の拡張用）
        
        現在はモック実装
        """
        # TODO: 実装
        return None
    
    def extract_features(self, text: str) -> TextFeatures:
        """
        テキストから全ての特徴量を抽出
        """
        return TextFeatures(
            sentiment=self.analyze_sentiment(text),
            entities=self.analyze_entities(text),
            syntax=self.analyze_syntax(text)
        )


# シングルトンインスタンス
nl_client = NLAPIClient()
