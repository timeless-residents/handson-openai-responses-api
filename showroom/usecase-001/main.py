#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenAI Responses API - ユースケース001: システムプロンプト（instructions）を使用した応答調整

このスクリプトは、OpenAI Responses APIを使用して、システムプロンプト（instructions）
パラメータを使った応答調整の例を示します。同じ入力テキストに対して異なるシステムプロンプトを
適用することで、応答の調整が可能であることを示します。
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


def create_response_with_instructions(client, prompt_text, instructions):
    """指定されたシステムプロンプト（instructions）を使用してレスポンスを生成します。

    Args:
        client: OpenAIクライアントインスタンス
        prompt_text: ユーザー入力テキスト
        instructions: システムプロンプト（instructions）

    Returns:
        生成されたレスポンス
    """
    response = client.responses.create(
        model="gpt-4o",
        input=prompt_text,
        instructions=instructions
    )
    return response


def display_response(response, instructions_description):
    """APIからの応答を整形して表示します。"""
    print(f"\n===== {instructions_description} =====")
    print(f"Instructions: {response.instructions}")
    print("\nOutput Text:")
    print(response.output_text)
    print("\nToken Usage:")
    print(f"Input tokens: {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")
    print("=" * 80)


def main():
    """メイン関数: 異なるシステムプロンプトを使用した応答生成を行います。"""
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)
        
        # 共通の入力テキスト
        input_text = "AIの未来について教えてください。"
        
        # 異なるシステムプロンプト（instructions）を定義
        instructions_list = [
            {
                "description": "ポジティブな視点",
                "instructions": "あなたは楽観的な未来学者です。技術の発展によるポジティブな側面に焦点を当ててください。"
            },
            {
                "description": "バランスの取れた視点",
                "instructions": "あなたは中立的な技術アナリストです。AIの可能性とリスクの両方をバランス良く議論してください。"
            },
            {
                "description": "批判的な視点",
                "instructions": "あなたは慎重な技術批評家です。新技術の潜在的なリスクや課題を強調してください。"
            },
            {
                "description": "教育的な視点",
                "instructions": "あなたは大学教授です。論理的で教育的な解説をしてください。400字以内で簡潔に説明してください。"
            },
            {
                "description": "クリエイティブな視点",
                "instructions": "あなたはSF作家です。想像力豊かな未来シナリオを短い物語形式で描写してください。"
            }
        ]
        
        # 各システムプロンプトで応答を生成
        for inst in instructions_list:
            response = create_response_with_instructions(
                client, input_text, inst["instructions"]
            )
            display_response(response, inst["description"])
        
    except Exception as error:
        print(f"エラーが発生しました: {error}")


if __name__ == "__main__":
    main()