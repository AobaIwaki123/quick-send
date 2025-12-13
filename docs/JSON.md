# JSON フォーマット仕様

## collected_texts.json

Memos から収集したラベル付きデータ。

```json
[
  {
    "id": "memos/123",
    "text": "収集した文章の本文",
    "label": "ai_bad",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }
]
```

| フィールド   | 型     | 説明                     |
| ------------ | ------ | ------------------------ |
| `id`         | string | Memos のメモ ID          |
| `text`       | string | ラベルタグを除去した本文 |
| `label`      | string | `"ai_bad"` or `"good"`   |
| `created_at` | string | 作成日時 (ISO 8601)      |
| `updated_at` | string | 更新日時 (ISO 8601)      |

---

## learned_patterns.json

学習されたパターン情報。

```json
{
  "patterns": [
    {
      "id": "pattern_1",
      "name": "パターン名",
      "description": "パターンの詳細説明",
      "strength": "strong",
      "frequency": 0.75,
      "examples_from_data": ["実データからの例1", "例2"],
      "synthetic_examples": ["生成した例1", "例2"],
      "detection_rule": "検出ルールの説明"
    }
  ],
  "summary": {
    "total_patterns": 2,
    "strong_indicators": ["強い指標となるパターン名"],
    "common_features": {
      "lexical": ["語彙レベルの特徴"],
      "syntactic": ["構文レベルの特徴"],
      "semantic": ["意味レベルの特徴"]
    }
  },
  "insights": [
    "データから得られた洞察1",
    "洞察2"
  ],
  "metadata": {
    "ai_bad_count": 3,
    "good_count": 4
  }
}
```

### patterns[]

| フィールド           | 型       | 説明                             |
| -------------------- | -------- | -------------------------------- |
| `id`                 | string   | パターン ID                      |
| `name`               | string   | パターン名                       |
| `description`        | string   | 詳細な説明                       |
| `strength`           | string   | `"strong"`, `"medium"`, `"weak"` |
| `frequency`          | number   | 出現頻度 (0.0-1.0)               |
| `examples_from_data` | string[] | 実データからの例                 |
| `synthetic_examples` | string[] | 生成した例文                     |
| `detection_rule`     | string   | 検出ルール                       |

### summary

| フィールド          | 型       | 説明                                  |
| ------------------- | -------- | ------------------------------------- |
| `total_patterns`    | number   | 抽出されたパターン数                  |
| `strong_indicators` | string[] | 強い指標のリスト                      |
| `common_features`   | object   | 共通特徴 (lexical/syntactic/semantic) |

### metadata

| フィールド     | 型     | 説明               |
| -------------- | ------ | ------------------ |
| `ai_bad_count` | number | AI感ありのデータ数 |
| `good_count`   | number | 良い文章のデータ数 |

---

# API レスポンス

## POST /collect

データ収集のレスポンス。

```json
{
  "success": true,
  "total": 7,
  "ai_bad": 3,
  "good": 4
}
```

| フィールド | 型      | 説明               |
| ---------- | ------- | ------------------ |
| `success`  | boolean | 成功フラグ         |
| `total`    | number  | 収集したデータ総数 |
| `ai_bad`   | number  | AI感ありのデータ数 |
| `good`     | number  | 良い文章のデータ数 |

---

## POST /learn

データ収集 + パターン学習のレスポンス。

```json
{
  "success": true,
  "collected": {
    "total": 7,
    "ai_bad": 3,
    "good": 4
  },
  "learned": {
    "success": true,
    "patterns_count": 2,
    "ai_bad_count": 3,
    "good_count": 4
  }
}
```

| フィールド  | 型      | 説明       |
| ----------- | ------- | ---------- |
| `success`   | boolean | 成功フラグ |
| `collected` | object  | 収集結果   |
| `learned`   | object  | 学習結果   |

### collected

| フィールド | 型     | 説明               |
| ---------- | ------ | ------------------ |
| `total`    | number | 収集したデータ総数 |
| `ai_bad`   | number | AI感ありのデータ数 |
| `good`     | number | 良い文章のデータ数 |

### learned

| フィールド       | 型      | 説明               |
| ---------------- | ------- | ------------------ |
| `success`        | boolean | 成功フラグ         |
| `patterns_count` | number  | 抽出したパターン数 |
| `ai_bad_count`   | number  | AI感ありのデータ数 |
| `good_count`     | number  | 良い文章のデータ数 |

---

## GET /patterns

学習済みパターンを取得。レスポンスは [learned_patterns.json](#learned_patternsjson) と同じ形式。

---

## GET /health

ヘルスチェック。

```json
{
  "status": "ok"
}
```

---

## エラーレスポンス

エラー時の共通形式。

```json
{
  "error": "エラーメッセージ"
}
```
