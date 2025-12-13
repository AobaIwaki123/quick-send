#!/usr/bin/env python3
"""
Vertex AIを使ったモデルのファインチューニング

収集したデータを使って、AI感検出精度を向上させる
"""

import json
from pathlib import Path
from typing import List, Dict
from google.cloud import aiplatform

# Google Cloud設定
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
DATASET_PATH = Path(__file__).parent.parent / "data" / "collected_texts.json"


def load_training_data() -> List[Dict]:
    """学習データを読み込む"""
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def prepare_training_examples(data: List[Dict]) -> List[Dict]:
    """
    Vertex AI形式の学習データに変換
    
    JSONL形式:
    {"input_text": "...", "output_text": "..."}
    """
    examples = []
    
    for item in data:
        text = item["text"]
        label = item["label"]
        
        # ラベルに応じて出力を生成
        if label == "ai_bad":
            output = json.dumps({
                "has_ai_feel": True,
                "assessment": "この文章にはAI感があります"
            }, ensure_ascii=False)
        elif label == "good":
            output = json.dumps({
                "has_ai_feel": False,
                "assessment": "自然で読みやすい文章です"
            }, ensure_ascii=False)
        else:
            continue
        
        examples.append({
            "input_text": f"以下の文章を分析してください:\n{text}",
            "output_text": output
        })
    
    return examples


def save_training_data(examples: List[Dict], output_path: str = "data/training.jsonl"):
    """学習データをJSONL形式で保存"""
    with open(output_path, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    print(f"✅ Saved {len(examples)} training examples to {output_path}")


def create_tuning_job(training_data_uri: str):
    """
    Vertex AIでファインチューニングジョブを作成
    
    注意: これは簡略化した例です。実際のコードは使用するモデルや
    APIバージョンに合わせて調整が必要です。
    """
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
    
    # ファインチューニングジョブの設定例
    # 実際のパラメータは使用するモデル (Gemini など) に依存
    tuning_job = aiplatform.PipelineJob(
        display_name="ai-feel-detector-tuning",
        template_path="gs://your-bucket/tuning_pipeline.json",
        parameter_values={
            "training_data_uri": training_data_uri,
            "base_model": "gemini-1.5-flash",
            "tuned_model_display_name": "ai-feel-detector-v1"
        }
    )
    
    tuning_job.run(sync=True)
    print(f"✅ Tuning job completed: {tuning_job.resource_name}")


def main():
    print("📊 Loading training data...")
    data = load_training_data()
    
    print(f"📝 Preparing {len(data)} examples...")
    examples = prepare_training_examples(data)
    
    print(f"💾 Saving training data...")
    save_training_data(examples)
    
    print("\n" + "="*60)
    print("次のステップ:")
    print("1. data/training.jsonl を Google Cloud Storage にアップロード")
    print("2. Vertex AI Console でファインチューニングジョブを作成")
    print("3. または create_tuning_job() を実装して自動化")
    print("="*60)


if __name__ == "__main__":
    main()