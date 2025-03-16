"""
設定ファイル: アプリケーションの設定を管理
"""

import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# サポートする科目とレベル
SUBJECTS = [
    ("python", "Python プログラミング"),
    ("javascript", "JavaScript プログラミング"),
    ("math", "数学"),
    ("science", "科学"),
    ("history", "歴史"),
    ("language", "言語と文学"),
]

# サポートする難易度レベル
LEVELS = [
    ("beginner", "初級"),
    ("intermediate", "中級"),
    ("advanced", "上級"),
]

# OpenAI モデル設定
DEFAULT_MODEL = "gpt-4o-2024-08-06"  # Responses APIで使用可能なモデル（json_schemaサポート）
# 代替モデル (必要に応じて使用)
# DEFAULT_MODEL = "gpt-4-turbo"  # 古いモデル（必要に応じて使用）
EMBEDDING_MODEL = "text-embedding-3-small"


# アプリケーション設定
class Config:
    # パスを絶対パスで指定
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "instance", "learning_assistant.db")

    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy_key_for_testing")

    # セッション設定
    SESSION_TYPE = "filesystem"

    # その他の設定
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB アップロード制限
