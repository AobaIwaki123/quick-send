#!/usr/bin/env python3
"""
パターン学習モジュール
"""

import json
from typing import Dict, List

from .config import DATA_DIR, PROMPTS_DIR
from .gemini import gemini_client
from .nl_api import nl_client


class PatternLearner:
    """データセットからパターンを学習"""

    def load_dataset(self) -> Dict[str, List[str]]:
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

    def learn_patterns(self, dataset: Dict[str, List[str]]) -> Dict:
        """
        データセットからパターンを学習

        1. NL API で各テキストの感情分析を実行
        2. Gemini でパターンを抽出・言語化
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

        # 3. プロンプトを構築
        prompt = self._build_prompt(dataset, stats)

        # 4. Gemini でパターン生成
        system_instruction = self._load_system_instruction()
        patterns = gemini_client.generate_json(prompt, system_instruction)

        # メタデータを追加
        patterns["metadata"] = {
            "ai_bad_count": len(dataset["ai_bad"]),
            "good_count": len(dataset["good"]),
            "sentiment_stats": stats,
            "model": gemini_client.model_name,
            "nl_api_enabled": nl_client.enabled
        }

        return patterns

    def run(self) -> Dict:
        """学習処理を実行"""
        dataset = self.load_dataset()

        if not dataset["ai_bad"] and not dataset["good"]:
            return {"error": "ラベル付きデータがありません。先にデータを収集してください。"}

        patterns = self.learn_patterns(dataset)

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
