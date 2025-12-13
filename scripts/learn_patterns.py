#!/usr/bin/env python3
"""
ユーザーがラベル付けしたデータからパターンを学習する

このスクリプトは:
1. collected_texts.json からラベル付きデータを読み込む
2. AIにパターン抽出を依頼
3. 学習したパターンを patterns.json として保存
"""

import json
import os
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# パス設定
DATA_DIR = Path(__file__).parent.parent / "data"
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
DATASET_PATH = DATA_DIR / "collected_texts.json"
PATTERNS_PATH = DATA_DIR / "learned_patterns.json"


class PromptLoader:
    """プロンプト読み込みユーティリティ"""
    
    @staticmethod
    def load(filename: str) -> str:
        path = PROMPTS_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    
    @staticmethod
    def load_with_vars(filename: str, **kwargs) -> str:
        template = PromptLoader.load(filename)
        return template.format(**kwargs)


def load_dataset() -> Dict[str, List[str]]:
    """データセットを読み込み、ラベルごとに分類"""
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    ai_bad_texts = [item["text"] for item in data if item["label"] == "ai_bad"]
    good_texts = [item["text"] for item in data if item["label"] == "good"]
    
    return {
        "ai_bad": ai_bad_texts,
        "good": good_texts
    }


def format_examples(texts: List[str], max_examples: int = 20) -> str:
    """例文をフォーマット"""
    if not texts:
        return "(データなし)"
    
    examples = texts[:max_examples]
    formatted = []
    for i, text in enumerate(examples, 1):
        formatted.append(f"{i}. {text}")
    
    if len(texts) > max_examples:
        formatted.append(f"\n... 他 {len(texts) - max_examples} 件")
    
    return "\n".join(formatted)


def learn_patterns(dataset: Dict[str, List[str]]) -> Dict:
    """
    データセットからパターンを学習
    
    実際の実装では、ここでADKやVertex AIのAPIを呼び出す
    """
    # プロンプトの準備
    prompt = PromptLoader.load_with_vars(
        "pattern_learning.md",
        ai_bad_examples=format_examples(dataset["ai_bad"]),
        good_examples=format_examples(dataset["good"])
    )
    
    print("📝 プロンプトを生成しました")
    print(f"   AI感がある文章: {len(dataset['ai_bad'])} 件")
    print(f"   良い文章: {len(dataset['good'])} 件")
    print()
    
    # 実際の実装では、ここでAIを呼び出す
    # response = call_ai_api(prompt)
    # patterns = json.loads(response)
    
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
        ]
    }
    
    return patterns


def save_patterns(patterns: Dict, output_path: Path = PATTERNS_PATH):
    """学習したパターンを保存"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)
    
    print(f"✅ パターンを保存しました: {output_path}")


def print_summary(patterns: Dict):
    """学習結果のサマリーを表示"""
    print("\n" + "="*60)
    print("📊 学習結果サマリー")
    print("="*60)
    
    summary = patterns.get("summary", {})
    print(f"\n抽出されたパターン数: {summary.get('total_patterns', 0)}")
    
    print("\n【強い指標】")
    for indicator in summary.get("strong_indicators", []):
        print(f"  - {indicator}")
    
    print("\n【共通特徴】")
    features = summary.get("common_features", {})
    for category, items in features.items():
        print(f"  {category}: {', '.join(items)}")
    
    print("\n【洞察】")
    for insight in patterns.get("insights", []):
        print(f"  • {insight}")
    
    print("\n" + "="*60)


def main():
    print("🔍 パターン学習を開始します\n")
    
    # データセット読み込み
    print("📚 データセットを読み込んでいます...")
    dataset = load_dataset()
    
    if not dataset["ai_bad"] and not dataset["good"]:
        print("❌ エラー: ラベル付きデータが見つかりません")
        print("   先に collect_from_memos.py を実行してください")
        return
    
    # パターン学習
    print("\n🤖 パターンを学習しています...")
    patterns = learn_patterns(dataset)
    
    # 結果保存
    save_patterns(patterns)
    
    # サマリー表示
    print_summary(patterns)
    
    print("\n次のステップ:")
    print("  1. data/learned_patterns.json を確認")
    print("  2. python src/agent.py で新しい文章を評価")


if __name__ == "__main__":
    main()