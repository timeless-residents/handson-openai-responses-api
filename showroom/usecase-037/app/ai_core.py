"""
AI連携コア機能: OpenAI APIクライアントとコア設定の初期化
"""

import os
import logging
from typing import List, Dict, Any, Tuple, Optional, Union
import openai
from .config import DEFAULT_MODEL, EMBEDDING_MODEL

# OpenAI クライアントの初期化
client = openai.Client(api_key=os.getenv("OPENAI_API_KEY", "dummy_key_for_testing"))

# テスト環境でのダミーレスポンス用
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

# ロギングの設定
logger = logging.getLogger(__name__)
