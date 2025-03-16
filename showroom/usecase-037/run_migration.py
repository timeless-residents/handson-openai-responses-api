#!/usr/bin/env python3
"""
データベースマイグレーションスクリプト: 新しいカラムを追加するためのスクリプト
"""

from app import app, db
from app.models import Topic

# アプリケーションコンテキストで実行
with app.app_context():
    # 既存のテーブルを変更してキャッシュカラムを追加
    db.engine.execute('ALTER TABLE topic ADD COLUMN content_cache TEXT')
    db.engine.execute('ALTER TABLE topic ADD COLUMN examples_cache TEXT')
    db.engine.execute('ALTER TABLE topic ADD COLUMN summary_cache TEXT')
    db.engine.execute('ALTER TABLE topic ADD COLUMN assessment_cache TEXT')
    db.engine.execute('ALTER TABLE topic ADD COLUMN cache_updated_at DATETIME')
    
    print("データベースマイグレーションが完了しました。")