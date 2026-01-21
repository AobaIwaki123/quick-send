#!/usr/bin/env python3
"""
学習結果のJSONをMemos投稿用フォーマットに変換
"""

from typing import Dict, List

NUM_AI_BAD = 5
NUM_GOOD = 3
NUM_EXAMPLES = 3
NUM_PRIORITY_IMPROVEMENTS = 5
NUM_GENERAL_TIPS = 5

def format_patterns_for_post(learn_result: Dict) -> str:
    """
    学習結果のJSONをMemos投稿用のMarkdownに変換
    
    Args:
        learn_result: pattern_learner.run() の戻り値
        
    Returns:
        Memos投稿用のMarkdown文字列
    """
    patterns = learn_result.get("patterns", {})
    analysis = learn_result.get("analysis", {})
    
    lines = ["# 📚 文章改善ガイド", ""]
    
    # AI Bad Patterns
    ai_bad = patterns.get("ai_bad", [])
    if ai_bad:
        lines.append("## ⚠️ 避けるべきパターン (AI感)")
        lines.append("")
        for i, pattern in enumerate(ai_bad[:NUM_AI_BAD], 1): # 最大NUM_AI_BAD件
            lines.extend(_format_pattern(i, pattern))
    
    # Good Patterns
    good = patterns.get("good", [])
    if good:
        lines.append("## ✅ 良いパターン")
        lines.append("")
        for i, pattern in enumerate(good[:NUM_GOOD], 1): # 最大NUM_GOOD件
            lines.extend(_format_pattern(i, pattern))
    
    # Advice
    advice = analysis.get("advice", {})
    if advice:
        lines.extend(_format_advice(advice))
    
    # Tags
    lines.append("#learn #writing_guide")
    
    return "\n".join(lines)


def _format_pattern(index: int, pattern: Dict) -> List[str]:
    """パターンをMarkdown形式にフォーマット"""
    lines = []
    
    name = pattern.get("name", f"パターン{index}")
    description = pattern.get("description", "")
    examples = pattern.get("examples", [])[:NUM_EXAMPLES]  # 最大NUM_EXAMPLES件
    
    lines.append(f"### {index}. {name}")
    if description:
        lines.append(description)
    lines.append("")
    
    if examples:
        lines.append("**具体例:**")
        for ex in examples:
            # 改行を含む例は1行に圧縮
            ex_oneline = ex.replace("\n", " ")
            lines.append(f"- {ex_oneline}")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    return lines


def _format_advice(advice: Dict) -> List[str]:
    """改善アドバイスをMarkdown形式にフォーマット"""
    lines = ["## 🔧 改善アドバイス", ""]
    
    # Priority improvements
    priority = advice.get("priority_improvements", [])
    for item in priority[:NUM_PRIORITY_IMPROVEMENTS]:  # 最大NUM_PRIORITY_IMPROVEMENTS件
        title = item.get("title", "改善ポイント")
        problem = item.get("problem", "")
        solution = item.get("solution", "")
        before = item.get("before_example", "")
        after = item.get("after_example", "")
        
        lines.append(f"### {title}")
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
        lines.append("### 一般的なTips")
        for tip in tips[:NUM_GENERAL_TIPS]:  # 最大NUM_GENERAL_TIPS件
            lines.append(f"- {tip}")
        lines.append("")
    
    # Summary
    summary = advice.get("summary", "")
    if summary:
        lines.append("---")
        lines.append("")
        lines.append(f"**まとめ:** {summary}")
        lines.append("")
    
    return lines
