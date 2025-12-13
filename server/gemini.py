#!/usr/bin/env python3
"""
Gemini API クライアント
"""

import json
import os
from typing import Dict, Optional

import google.generativeai as genai


# 利用可能なモデル
MODELS = {
    "2.0-flash": "gemini-2.0-flash",
    "2.5-flash": "gemini-2.5-flash", 
    "2.5-pro": "gemini-2.5-pro-preview-06-05",
    "3.0-pro": "gemini-3.0-pro-preview",
}

DEFAULT_MODEL = "2.5-flash"


class GeminiClient:
    """Gemini API クライアント"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model_key = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            genai.configure(api_key=self.api_key)
    
    @property
    def model_name(self) -> str:
        """現在のモデル名を取得"""
        return MODELS.get(self.model_key, MODELS[DEFAULT_MODEL])
    
    def set_model(self, model_key: str):
        """モデルを切り替え"""
        if model_key in MODELS:
            self.model_key = model_key
        else:
            raise ValueError(f"Unknown model: {model_key}. Available: {list(MODELS.keys())}")
    
    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """
        テキスト生成
        
        Args:
            prompt: プロンプト
            system_instruction: システム指示
            
        Returns:
            生成されたテキスト
        """
        if not self.enabled:
            return self._mock_generate(prompt)
        
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction
        )
        
        response = model.generate_content(prompt)
        return response.text
    
    def generate_json(self, prompt: str, system_instruction: str = None) -> Dict:
        """
        JSON形式で生成
        
        Args:
            prompt: プロンプト
            system_instruction: システム指示
            
        Returns:
            パースされたJSON
        """
        if not self.enabled:
            return self._mock_generate_json(prompt)
        
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        response = model.generate_content(prompt)
        return json.loads(response.text)
    
    def _mock_generate(self, prompt: str) -> str:
        """モック: テキスト生成"""
        return "[MOCK] Generated response for prompt"
    
    def _mock_generate_json(self, prompt: str) -> Dict:
        """モック: JSON生成"""
        return {
            "patterns": [
                {
                    "id": "pattern_1",
                    "name": "過度な丁寧語の使用",
                    "description": "「〜させていただく」などの丁寧語が頻出",
                    "strength": "strong",
                    "frequency": 0.75,
                    "examples_from_data": ["ご説明させていただきます"],
                    "synthetic_examples": ["ご確認させていただきたく存じます"],
                    "detection_rule": "「させていただく」が頻出する場合"
                }
            ],
            "summary": {
                "total_patterns": 1,
                "strong_indicators": ["過度な丁寧語の使用"],
                "common_features": {
                    "lexical": ["させていただく"],
                    "syntactic": ["箇条書き"],
                    "semantic": ["過度に形式的"]
                }
            },
            "insights": ["ユーザーは形式的すぎる文章をAI感があると判断する傾向"]
        }
    
    def status(self) -> Dict:
        """クライアントの状態を取得"""
        return {
            "enabled": self.enabled,
            "model": self.model_name,
            "model_key": self.model_key,
            "available_models": list(MODELS.keys())
        }


# シングルトンインスタンス
gemini_client = GeminiClient()
