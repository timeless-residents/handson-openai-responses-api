"""
AI連携ヘルパー: OpenAI Responses APIとの連携機能をまとめたエントリーポイント
"""

# 各モジュールからの機能をインポート
from .ai_core import client, MOCK_MODE, logger, DEFAULT_MODEL
from .ai_content import (
    generate_learning_content,
    generate_learning_plan,
    get_default_plan_items,
    summarize_text,
)
from .ai_quiz import generate_quiz_questions
from .ai_flashcards import generate_flashcards
from .ai_chat import ask_ai_tutor

# このモジュールからエクスポートする機能
__all__ = [
    "generate_learning_content",
    "generate_quiz_questions",
    "generate_flashcards",
    "generate_learning_plan",
    "summarize_text",
    "ask_ai_tutor",
]