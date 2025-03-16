"""
メインアプリケーション実行ファイル: アプリケーションを起動するためのエントリーポイント
"""

from app import app, init_db

if __name__ == "__main__":
    # データベースの初期化
    init_db()
    
    # サーバーを起動（別のポートを使用）
    app.run(debug=True, port=5001)