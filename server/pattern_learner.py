#!/usr/bin/env python3
"""
パターン学習モジュール
"""

import json
from typing import Dict, List

from .config import DATA_DIR, PROMPTS_DIR
from .gemini import gemini_client
from .nl_api import nl_client
from .firestore_client import firestore_client


class PatternLearner:
    """データセットからパターンを学習"""
    
    def __init__(self, db_client=firestore_client):
        self.db_client = db_client

    def load_dataset(self) -> Dict[str, List[str]]:
        """データセットを読み込み、ラベルごとに分類"""
        if self.db_client and self.db_client.db:
            data = self.db_client.load_collected_texts()
        else:
            # Fallback to local
            print("⚠️ Loading from local JSON (Fallback)")
            dataset_path = DATA_DIR / "collected_texts.json"
            if not dataset_path.exists():
                return {"ai_bad": [], "good": []}
            with open(dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        return {
            "ai_bad": [item["text"] for item in data if item["label"] == "ai_bad"],
            "good": [item["text"] for item in data if item["label"] == "good"]
        }

    def learn_patterns(self, dataset: Dict[str, List[str]]) -> Dict:
        """
        データセットからパターンを学習（3ステップ構成）

        Step 1: AI感がある文章からパターンを抽出
        Step 2: 良い文章からパターンを抽出  
        Step 3: 両者を比較・分析し、改善アドバイスを生成
        最後にPythonコードでマージ（情報欠落を防ぐ）
        """
        # 1. NL API で特徴抽出（感情分析）
        features = {"ai_bad": [], "good": []}

        for label in ["ai_bad", "good"]:
            for text in dataset[label]:
                sentiment = nl_client.analyze_sentiment(text)
                features[label].append({
                    "text": text,
                    "sentiment_score": sentiment.score if sentiment else 0,
                    "sentiment_magnitude": sentiment.magnitude if sentiment else 0
                })

        # 2. 特徴量の統計を計算
        stats = {
            "ai_bad": self._calc_stats(features["ai_bad"]),
            "good": self._calc_stats(features["good"])
        }

        # Step 1: AI感がある文章のパターン抽出
        print("🔍 Step 1: Extracting patterns from ai_bad texts...")
        bad_patterns = self._extract_patterns(dataset["ai_bad"], mode="bad")

        # Step 2: 良い文章のパターン抽出
        print("🔍 Step 2: Extracting patterns from good texts...")
        good_patterns = self._extract_patterns(dataset["good"], mode="good")

        # Step 3: 比較・分析
        print("🔍 Step 3: Analyzing and comparing patterns...")
        analysis = self._analyze_patterns(bad_patterns, good_patterns)

        # Pythonコードでマージ（情報欠落なし）
        patterns = {
            "version": "2.0",
            "patterns": {
                "ai_bad": bad_patterns.get("patterns", []),
                "good": good_patterns.get("patterns", [])
            },
            "analysis": analysis
        }

        # メタデータを追加
        patterns["metadata"] = {
            "ai_bad_count": len(dataset["ai_bad"]),
            "good_count": len(dataset["good"]),
            "ai_bad_patterns_count": len(patterns["patterns"]["ai_bad"]),
            "good_patterns_count": len(patterns["patterns"]["good"]),
            "sentiment_stats": stats,
            "model": gemini_client.model_name,
            "nl_api_enabled": nl_client.enabled
        }

        return patterns

    def _extract_patterns(self, texts: List[str], mode: str) -> Dict:
        """
        Step 1/2: テキストからパターンを抽出

        Args:
            texts: 分析対象のテキストリスト
            mode: "bad" または "good"

        Returns:
            抽出されたパターンのJSON
        """
        if not texts:
            return {"patterns": []}

        # プロンプトを読み込み
        prompt_path = PROMPTS_DIR / "extract_patterns.md"
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
            prompt = prompt_template.format(
                examples=self._format_examples(texts)
            )
        else:
            prompt = f"""
以下の文章から共通するパターンを詳細に抽出してください。要約せず、具体例を含めてください。

{self._format_examples(texts)}

JSON形式で出力してください。
"""

        # モードに応じたシステム指示
        if mode == "bad":
            system_instruction = "あなたは「AI感がある」文章のパターンを分析する専門家です。ユーザーがラベル付けしたデータから、AIらしさの特徴を網羅的に抽出してください。"
        else:
            system_instruction = "あなたは「自然で良い」文章のパターンを分析する専門家です。ユーザーがラベル付けしたデータから、良い文章の特徴を網羅的に抽出してください。"

        return gemini_client.generate_json(prompt, system_instruction)

    def _analyze_patterns(self, bad_patterns: Dict, good_patterns: Dict) -> Dict:
        """
        Step 3: パターンを比較・分析

        Args:
            bad_patterns: AI感があるパターン
            good_patterns: 良いパターン

        Returns:
            比較分析結果（comparison, advice）
        """
        # プロンプトを読み込み
        prompt_path = PROMPTS_DIR / "analyze_patterns.md"
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
            prompt = prompt_template.format(
                bad_patterns=json.dumps(bad_patterns.get("patterns", []), ensure_ascii=False, indent=2),
                good_patterns=json.dumps(good_patterns.get("patterns", []), ensure_ascii=False, indent=2)
            )
        else:
            prompt = f"""
以下の2つのパターンリストを比較し、改善アドバイスを生成してください。
パターンリスト自体は出力せず、analysisオブジェクトのみを返してください。

AI感があるパターン:
{json.dumps(bad_patterns.get("patterns", []), ensure_ascii=False, indent=2)}

良いパターン:
{json.dumps(good_patterns.get("patterns", []), ensure_ascii=False, indent=2)}
"""

        system_instruction = "あなたは文章改善のアドバイザーです。2つのパターンリストを比較し、具体的で実践的な改善アドバイスを提供してください。"

        return gemini_client.generate_json(prompt, system_instruction)

    def run(self) -> Dict:
        """学習処理を実行"""
        dataset = self.load_dataset()

        if not dataset["ai_bad"] and not dataset["good"]:
            return {"error": "ラベル付きデータがありません。先にデータを収集してください。"}

        patterns = self.learn_patterns(dataset)

        # 保存
        if self.db_client and self.db_client.db:
            self.db_client.save_patterns(patterns)
        else:
             print("⚠️ Saving to local JSON (Fallback)")
             DATA_DIR.mkdir(parents=True, exist_ok=True)
             output_path = DATA_DIR / "learned_patterns.json"
             with open(output_path, "w", encoding="utf-8") as f:
                 json.dump(patterns, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "version": patterns.get("version", "2.0"),
            "ai_bad_patterns_count": len(patterns.get("patterns", {}).get("ai_bad", [])),
            "good_patterns_count": len(patterns.get("patterns", {}).get("good", [])),
            "patterns": patterns.get("patterns", {}),
            "analysis": patterns.get("analysis", {}),
            "ai_bad_count": len(dataset["ai_bad"]),
            "good_count": len(dataset["good"])
        }

    @staticmethod
    def _calc_stats(items: List[Dict]) -> Dict:
        """特徴量の統計を計算"""
        if not items:
            return {"avg_score": 0, "avg_magnitude": 0}
        scores = [i["sentiment_score"] for i in items]
        magnitudes = [i["sentiment_magnitude"] for i in items]
        return {
            "avg_score": sum(scores) / len(scores),
            "avg_magnitude": sum(magnitudes) / len(magnitudes)
        }

    def _build_prompt(self, dataset: Dict[str, List[str]], stats: Dict) -> str:
        """プロンプトを構築"""
        prompt_path = PROMPTS_DIR / "pattern_learning.md"
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            prompt = prompt_template.format(
                ai_bad_examples=self._format_examples(dataset["ai_bad"]),
                good_examples=self._format_examples(dataset["good"])
            )

            # 感情分析の統計情報を追加
            prompt += f"\n\n## 感情分析の統計 (Natural Language AI API)\n"
            prompt += f"- AI感がある文章: 平均スコア={stats['ai_bad']['avg_score']:.2f}, 強度={stats['ai_bad']['avg_magnitude']:.2f}\n"
            prompt += f"- 良い文章: 平均スコア={stats['good']['avg_score']:.2f}, 強度={stats['good']['avg_magnitude']:.2f}\n"
        else:
            prompt = f"""
以下のデータを分析し、「AI感がある」文章のパターンを抽出してください。

AI感がある文章:
{self._format_examples(dataset["ai_bad"])}

良い文章:
{self._format_examples(dataset["good"])}

JSON形式で出力してください。
"""
        return prompt

    @staticmethod
    def _format_examples(texts: List[str], max_examples: int = 20) -> str:
        """サンプルテキストをフォーマット"""
        if not texts:
            return "(データなし)"
        examples = texts[:max_examples]
        formatted = [f"{i+1}. {text}" for i, text in enumerate(examples)]
        if len(texts) > max_examples:
            formatted.append(f"\n... 他 {len(texts) - max_examples} 件")
        return "\n".join(formatted)

    @staticmethod
    def _load_system_instruction() -> str | None:
        """システム指示を読み込み"""
        system_prompt_path = PROMPTS_DIR / "system.md"
        if system_prompt_path.exists():
            with open(system_prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return None


# シングルトンインスタンス
pattern_learner = PatternLearner()
