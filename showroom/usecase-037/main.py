"""
個人向け学習アシスタント: OpenAI APIを活用して個人学習を支援するWebアプリケーション

このアプリケーションは、以下の機能を提供します：
- 学習者のレベルに応じたコンテンツ生成
- インタラクティブな質問応答
- パーソナライズされた学習計画の作成
- 学習の進捗状況の追跡
- 知識の確認のためのクイズ生成
"""

# リファクタリングにより、コードは以下のように再編成されました：
# - app/__init__.py: アプリケーション初期化
# - app/config.py: 設定
# - app/models.py: データベースモデル
# - app/forms.py: フォーム定義
# - app/utils.py: ユーティリティ関数
# - app/ai_helpers.py: OpenAI API連携
# - app/routes/: 機能別のルート
# - run.py: アプリケーション実行エントリーポイント

# 直接このファイルを実行した場合は、run.pyを呼び出す
if __name__ == "__main__":
    from app import app, init_db

    # データベースを初期化
    init_db()

    # アプリケーションを実行（別のポートを使用）
    app.run(debug=True, port=8090)
