#!/usr/bin/env python3
"""
学習結果のJSONをMemos投稿用フォーマットに変換
3つの投稿に分割: analysis, ai_bad, good
"""

from typing import Dict, List

# Memos APIの文字数制限
MAX_CONTENT_LENGTH = 8000  # 8192だが余裕を持たせる

# 表示件数の設定
NUM_AI_BAD = 5
NUM_GOOD = 5
NUM_EXAMPLES = 3
NUM_PRIORITY_IMPROVEMENTS = 3
NUM_GENERAL_TIPS = 5

# 個別フィールドの文字数制限
MAX_NAME_LENGTH = 50
MAX_DESCRIPTION_LENGTH = 150
MAX_EXAMPLE_LENGTH = 100
MAX_PROBLEM_LENGTH = 150
MAX_SOLUTION_LENGTH = 200
MAX_BEFORE_AFTER_LENGTH = 80


def format_patterns_for_posts(learn_result: Dict) -> List[str]:
    """
    学習結果のJSONをMemos投稿用のMarkdownリストに変換
    
    Args:
        learn_result: pattern_learner.run() の戻り値
        
    Returns:
        Memos投稿用のMarkdown文字列のリスト（最大3件）
    """
    patterns = learn_result.get("patterns", {})
    analysis = learn_result.get("analysis", {})
    
    posts = []
    
    # 1. Analysis (改善アドバイス)
    advice = analysis.get("advice", {})
    if advice:
        analysis_content = _format_analysis_post(advice)
        posts.append(_truncate_content(analysis_content))
    
    # 2. AI Bad Patterns
    ai_bad = patterns.get("ai_bad", [])
    if ai_bad:
        ai_bad_content = _format_ai_bad_post(ai_bad)
        posts.append(_truncate_content(ai_bad_content))
    
    # 3. Good Patterns
    good = patterns.get("good", [])
    if good:
        good_content = _format_good_post(good)
        posts.append(_truncate_content(good_content))
    
    return posts


def _truncate_content(content: str) -> str:
    """コンテンツ全体を文字数制限内に収める"""
    if len(content) <= MAX_CONTENT_LENGTH:
        return content
    # オーバーフロー時は切り捨てて...を付加
    return content[:MAX_CONTENT_LENGTH - 20] + "\n\n...(省略)\n\n#learn"


def _truncate(text: str, max_len: int) -> str:
    """文字列を指定長で切り捨て"""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def _format_analysis_post(advice: Dict) -> str:
    """改善アドバイスの投稿をフォーマット"""
    lines = ["# 🔧 改善アドバイス", ""]
    
    # Summary (最初に表示)
    summary = advice.get("summary", "")
    if summary:
        lines.append(f"**まとめ:** {_truncate(summary, 300)}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Priority improvements
    priority = advice.get("priority_improvements", [])
    for i, item in enumerate(priority[:NUM_PRIORITY_IMPROVEMENTS], 1):
        title = _truncate(item.get("title", "改善ポイント"), MAX_NAME_LENGTH)
        problem = _truncate(item.get("problem", ""), MAX_PROBLEM_LENGTH)
        solution = _truncate(item.get("solution", ""), MAX_SOLUTION_LENGTH)
        before = _truncate(item.get("before_example", ""), MAX_BEFORE_AFTER_LENGTH)
        after = _truncate(item.get("after_example", ""), MAX_BEFORE_AFTER_LENGTH)
        
        lines.append(f"## {i}. {title}")
        if problem:
            lines.append(f"**問題:** {problem}")
        if solution:
            lines.append(f"**解決策:** {solution}")
        lines.append("")
        
        if before and after:
            lines.append("| Before | After |")
            lines.append("|--------|-------|")
            lines.append(f"| {before} | {after} |")
            lines.append("")
    
    # General tips
    tips = advice.get("general_tips", [])
    if tips:
        lines.append("## 一般的なTips")
        for tip in tips[:NUM_GENERAL_TIPS]:
            lines.append(f"- {_truncate(tip, 150)}")
        lines.append("")
    
    lines.append("#learn #analysis")
    
    return "\n".join(lines)


def _format_ai_bad_post(ai_bad: List[Dict]) -> str:
    """AI Badパターンの投稿をフォーマット"""
    lines = ["# ⚠️ 避けるべきパターン (AI感)", ""]
    
    for i, pattern in enumerate(ai_bad[:NUM_AI_BAD], 1):
        lines.extend(_format_pattern(i, pattern))
    
    lines.append("#learn")
    
    return "\n".join(lines)


def _format_good_post(good: List[Dict]) -> str:
    """Goodパターンの投稿をフォーマット"""
    lines = ["# ✅ 良いパターン", ""]
    
    for i, pattern in enumerate(good[:NUM_GOOD], 1):
        lines.extend(_format_pattern(i, pattern))
    
    lines.append("#learn")
    
    return "\n".join(lines)


def _format_pattern(index: int, pattern: Dict) -> List[str]:
    """パターンをMarkdown形式にフォーマット"""
    lines = []
    
    name = _truncate(pattern.get("name", f"パターン{index}"), MAX_NAME_LENGTH)
    description = _truncate(pattern.get("description", ""), MAX_DESCRIPTION_LENGTH)
    examples = pattern.get("examples", [])[:NUM_EXAMPLES]
    
    lines.append(f"## {index}. {name}")
    if description:
        lines.append(description)
    lines.append("")
    
    if examples:
        lines.append("**具体例:**")
        for ex in examples:
            ex_oneline = ex.replace("\n", " ")
            ex_truncated = _truncate(ex_oneline, MAX_EXAMPLE_LENGTH)
            lines.append(f"- {ex_truncated}")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    return lines


# 後方互換性のため旧関数も残す
def format_patterns_for_post(learn_result: Dict) -> str:
    """
    学習結果のJSONをMemos投稿用のMarkdownに変換（単一投稿版）
    後方互換性のため残存。新規実装は format_patterns_for_posts を使用。
    """
    posts = format_patterns_for_posts(learn_result)
    if posts:
        return posts[0]  # 最初の投稿（analysis）を返す
    return "# 📚 学習完了\n\nパターンが抽出されました。\n\n#learn"
