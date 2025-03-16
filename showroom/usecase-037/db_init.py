#!/usr/bin/env python3
"""
データベース再初期化スクリプト: テーブルの作り直しを行うためのスクリプト
"""

import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'learning_assistant.db')

# データベースディレクトリが存在しない場合は作成
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# データベースに接続
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# すべてのテーブルを取得
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"既存のテーブル: {tables}")

# topic テーブルが存在する場合は変更
if ('topic',) in tables:
    # 既存のカラムを取得
    cursor.execute("PRAGMA table_info(topic)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"トピックテーブルの既存カラム: {columns}")
    
    # 新しいカラムを追加
    if 'content_cache' not in columns:
        cursor.execute('ALTER TABLE topic ADD COLUMN content_cache TEXT')
        print("content_cache カラムを追加しました")
    
    if 'examples_cache' not in columns:
        cursor.execute('ALTER TABLE topic ADD COLUMN examples_cache TEXT')
        print("examples_cache カラムを追加しました")
    
    if 'summary_cache' not in columns:
        cursor.execute('ALTER TABLE topic ADD COLUMN summary_cache TEXT')
        print("summary_cache カラムを追加しました")
    
    if 'assessment_cache' not in columns:
        cursor.execute('ALTER TABLE topic ADD COLUMN assessment_cache TEXT')
        print("assessment_cache カラムを追加しました")
    
    if 'cache_updated_at' not in columns:
        cursor.execute('ALTER TABLE topic ADD COLUMN cache_updated_at TIMESTAMP')
        print("cache_updated_at カラムを追加しました")

    # 変更をコミット
    conn.commit()
    print("データベースの変更をコミットしました")
else:
    print("topic テーブルが見つかりません")

# 接続を閉じる
conn.close()

print("データベース操作が完了しました。")