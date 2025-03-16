#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenAI Responses API - ユースケース002: 複数の入力テキストによる応答生成

このスクリプトは、OpenAI Responses APIを使用して、複数の入力テキスト（メッセージ）を
配列として送信し、それらすべてを考慮した応答を生成する方法を示します。
これは会話履歴を模倣したり、文脈を提供するために役立ちます。
"""

import os
import sys
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


def create_response_with_multiple_inputs(client, messages):
    """複数の入力テキスト（メッセージ）を使用してレスポンスを生成します。

    Args:
        client: OpenAIクライアントインスタンス
        messages: 入力メッセージの配列

    Returns:
        生成されたレスポンス
    """
    response = client.responses.create(
        model="gpt-4o",
        input=messages
    )
    return response


def create_single_message(role, content):
    """単一のメッセージオブジェクトを作成します。

    Args:
        role: メッセージの役割 ("user" または "assistant")
        content: メッセージの内容

    Returns:
        メッセージオブジェクト
    """
    return {
        "type": "message",
        "role": role,
        "content": [
            {
                "type": "input_text" if role == "user" else "output_text",
                "text": content
            }
        ]
    }


def display_conversation_and_response(messages, response):
    """会話履歴と生成された応答を表示します。"""
    print("\n===== 会話履歴 =====")
    for i, message in enumerate(messages):
        role = message.get("role", "")
        content_list = message.get("content", [])
        
        if content_list and len(content_list) > 0:
            text = content_list[0].get("text", "")
            print(f"{i+1}. {role.upper()}: {text}")
    
    print("\n===== 生成された応答 =====")
    print(response.output_text)
    
    print("\n===== トークン使用量 =====")
    print(f"Input tokens: {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")
    print("=" * 80)


def main():
    """メイン関数: 複数の入力テキストを使用した応答生成のデモンストレーション"""
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)
        
        # ケース1: 単純な会話
        messages1 = [
            create_single_message("user", "こんにちは、私の名前は田中です。"),
            create_single_message("assistant", "こんにちは田中さん。どのようにお手伝いできますか？"),
            create_single_message("user", "今日の東京の天気を教えてください。")
        ]
        
        # ケース2: テキスト要約タスク
        messages2 = [
            create_single_message("user", "以下のテキストを要約してください:"),
            create_single_message("user", """
            人工知能（AI）は、人間の知能を模倣し、学習し、問題解決を行うことができるコンピュータシステムです。
            AIには、特定のタスクに特化した「狭いAI」と、人間のような幅広い知能を持つことを目指す「汎用AI」があります。
            機械学習は、AIの一分野であり、データから学習してパターンを見つけ出し、予測や分類を行うアルゴリズムを使用します。
            ディープラーニングは機械学習の一種で、人間の脳の神経回路を模倣したニューラルネットワークを使用し、大量のデータから複雑なパターンを学習します。
            AIは、医療診断、金融取引、自然言語処理、画像認識、自動運転車など、多くの分野で活用されています。
            AIの発展に伴い、プライバシー、雇用への影響、セキュリティ、倫理的配慮など、社会的な課題も生じています。
            """),
            create_single_message("user", "100文字以内でお願いします。")
        ]
        
        # ケース3: 複数の文書比較分析
        messages3 = [
            create_single_message("user", "以下の2つの製品説明を比較して、主な違いをまとめてください:"),
            create_single_message("user", """
            【製品A】最新のスマートフォン「X-Phone 12」
            • 6.2インチ有機ELディスプレイ（解像度: 2400×1080）
            • 8コアプロセッサ、8GB RAM、ストレージ容量: 128GB/256GB
            • 背面カメラ: 50MP（メイン）+ 12MP（超広角）+ 8MP（望遠）
            • 前面カメラ: 16MP
            • バッテリー容量: 4200mAh、急速充電対応（30W）
            • 防水・防塵規格: IP68
            • OSバージョン: Android 12
            • 価格: 89,800円（税込）
            """),
            create_single_message("user", """
            【製品B】最新のスマートフォン「Galaxy Z22」
            • 6.4インチダイナミックAMOLEDディスプレイ（解像度: 3200×1440）
            • 10コアプロセッサ、12GB RAM、ストレージ容量: 256GB/512GB
            • 背面カメラ: 108MP（メイン）+ 12MP（超広角）+ 10MP（望遠）+ 10MP（マクロ）
            • 前面カメラ: 32MP
            • バッテリー容量: 5000mAh、急速充電対応（45W）、ワイヤレス充電対応
            • 防水・防塵規格: IP68
            • OSバージョン: Android 12
            • 価格: 124,800円（税込）
            """),
            create_single_message("user", "表形式で比較してください。")
        ]
        
        # 各ケースで応答を生成
        print("\n【ケース1: 単純な会話】")
        response1 = create_response_with_multiple_inputs(client, messages1)
        display_conversation_and_response(messages1, response1)
        
        print("\n【ケース2: テキスト要約タスク】")
        response2 = create_response_with_multiple_inputs(client, messages2)
        display_conversation_and_response(messages2, response2)
        
        print("\n【ケース3: 複数の文書比較分析】")
        response3 = create_response_with_multiple_inputs(client, messages3)
        display_conversation_and_response(messages3, response3)
        
    except Exception as error:
        print(f"エラーが発生しました: {error}")


if __name__ == "__main__":
    main()