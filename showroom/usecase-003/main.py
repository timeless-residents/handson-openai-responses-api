#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenAI Responses API - ユースケース003: ストリーミングによるリアルタイム応答表示

このスクリプトは、OpenAI Responses APIのストリーミング機能を使用して、
モデルの応答をリアルタイムで取得し表示する方法を示します。
ストリーミングでは、生成中の内容を逐次的に受け取ることができ、
ユーザー体験の向上やより対話的なアプリケーションの構築が可能になります。
"""

import os
import sys
import time
import json
from dotenv import load_dotenv
import openai


def setup_environment():
    """環境設定を行い、APIキーを取得します。"""
    # プロジェクトルートへのパスを追加
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(root_path)

    # プロジェクトルートの.envファイルから環境変数を読み込む
    load_dotenv(os.path.join(root_path, '.env'))

    # OpenAI API キーを環境変数から取得
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 環境変数が設定されていません")

    return api_key


def create_streaming_response(client, prompt_text, instructions=None):
    """ストリーミングレスポンスを生成します。

    Args:
        client: OpenAIクライアントインスタンス
        prompt_text: 入力テキスト
        instructions: オプションのシステムプロンプト

    Returns:
        ストリーミングレスポンスイテレータ
    """
    # ストリーミングを有効にしてレスポンスを生成
    params = {
        "model": "gpt-4o",
        "input": prompt_text,
        "stream": True,  # ストリーミングを有効化
    }
    
    # instructionsが指定されている場合は追加
    if instructions:
        params["instructions"] = instructions
    
    return client.responses.create(**params)


def process_streaming_response(stream, demo_name):
    """ストリーミングレスポンスを処理して表示します。

    このデモンストレーションでは、ストリーミングイベントの種類に基づいて
    異なる処理を行い、リアルタイムでテキストを表示します。

    Args:
        stream: ストリーミングレスポンスイテレータ
        demo_name: デモの名前（表示用）
    """
    print(f"\n===== {demo_name} =====")
    print("ストリーミングレスポンス開始:")
    
    full_text = ""
    start_time = time.time()
    
    # イベントカウンター（統計用）
    event_counts = {}
    
    for event in stream:
        # イベントタイプをカウント
        event_type = event.type
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # 特定のイベントタイプに応じた処理
        if event_type == "response.output_text.delta":
            # テキスト増分を取得して表示
            delta_text = event.delta
            full_text += delta_text
            print(delta_text, end="", flush=True)
        
        # その他のイベントタイプを扱いたい場合はここに追加
    
    # 処理時間の計算
    elapsed_time = time.time() - start_time
    
    print("\n\n処理完了")
    print(f"総処理時間: {elapsed_time:.2f}秒")
    print(f"受信イベント統計: {json.dumps(event_counts, indent=2)}")
    print("=" * 80)
    
    return full_text


def main():
    """メイン関数: ストリーミングレスポンスの3つのデモンストレーション"""
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)
        
        # デモ1: 短い質問への回答（基本的なストリーミング）
        prompt1 = "AIの主な応用分野を5つ挙げて、各分野を簡潔に説明してください。"
        stream1 = create_streaming_response(client, prompt1)
        process_streaming_response(stream1, "デモ1: 短い質問への回答")
        
        # デモ2: 創造的なコンテンツ生成（より長いストリーミング）
        prompt2 = "未来の宇宙旅行をテーマにした短い物語（400文字程度）を作成してください。"
        instructions2 = "あなたは創造的なSF作家です。想像力豊かで、未来の技術に基づいた物語を作成してください。"
        stream2 = create_streaming_response(client, prompt2, instructions2)
        process_streaming_response(stream2, "デモ2: 創造的なコンテンツ生成")
        
        # デモ3: 段階的な説明（構造化された長いレスポンス）
        prompt3 = "機械学習の初心者向けに、教師あり学習と教師なし学習の違いを説明し、それぞれの代表的なアルゴリズムと応用例を3つずつ挙げてください。"
        instructions3 = "あなたは教育者です。段階的で明確な説明を心がけ、専門用語は必ず平易な言葉で補足してください。見出しを使った構造化された回答を作成してください。"
        stream3 = create_streaming_response(client, prompt3, instructions3)
        process_streaming_response(stream3, "デモ3: 段階的な説明")
        
    except Exception as error:
        print(f"エラーが発生しました: {error}")


if __name__ == "__main__":
    main()