"""
アプリケーション初期化: Flaskアプリケーションとその依存関係を初期化
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flaskアプリケーションの初期化
app = Flask(__name__)

# 設定の読み込み
from .config import Config

app.config.from_object(Config)

# データベースの初期化
db = SQLAlchemy(app)

# ログインマネージャーの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "この機能を利用するにはログインが必要です。"
login_manager.login_message_category = "info"

# モデルのインポート
from .models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ルートのインポートと登録
def register_blueprints(app):
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.learning import learning_bp
    from .routes.plans import plans_bp
    from .routes.notes import notes_bp
    from .routes.quizzes import quizzes_bp
    from .routes.flashcards import flashcards_bp
    from .routes.stats import stats_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(plans_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(quizzes_bp)
    app.register_blueprint(flashcards_bp)
    app.register_blueprint(stats_bp)


# データベース初期化関数
def init_db():
    """データベースを初期化し、初期データを登録する"""
    from .config import SUBJECTS, Config
    from .models import Subject
    import os

    # データベースファイルのディレクトリが存在することを確認
    db_dir = os.path.dirname(Config.db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"データベースディレクトリを作成しました: {db_dir}")

    with app.app_context():
        db.create_all()
        logger.info(f"データベーステーブルを作成しました: {Config.db_path}")

        # サポートする科目を登録
        for code, name in SUBJECTS:
            if not Subject.query.filter_by(code=code).first():
                subject = Subject(code=code, name=name)
                db.session.add(subject)

        db.session.commit()

    logger.info("データベースを初期化しました。")


# アプリケーション作成
def create_app():
    # Blueprintの登録
    register_blueprints(app)

    # Userモデルが定義される前に必要なインポートを行うため
    # このメソッド内で初期化処理を行う
    from .routes import (
        auth,
        dashboard,
        learning,
        plans,
        notes,
        quizzes,
        flashcards,
        stats,
    )

    return app


# アプリケーションの初期化
create_app()
