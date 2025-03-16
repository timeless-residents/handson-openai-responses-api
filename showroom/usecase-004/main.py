#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenAI Responses API - ユースケース004: パラメータ調整（temperature, top_p, max_output_tokens）

このスクリプトは、OpenAI Responses APIの出力調整パラメータの効果を実演します。
temperature、top_p、max_output_tokensなどのパラメータを変更することで、
モデルの応答の創造性、多様性、長さをコントロールする方法を示します。
"""

import os
import sys
import json
from dotenv import load_dotenv
import openai
from tabulate import tabulate


def setup_environment():
    """環境設定を行い、APIキーを取得します。"""
    # プロジェクトルートへのパスを追加
    root_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(root_path)

    # プロジェクトルートの.envファイルから環境変数を読み込む
    load_dotenv(os.path.join(root_path, ".env"))

    # OpenAI API キーを環境変数から取得
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 環境変数が設定されていません")

    return api_key


def create_response_with_params(client, prompt_text, params=None):
    """指定されたパラメータでレスポンスを生成します。

    Args:
        client: OpenAIクライアントインスタンス
        prompt_text: 入力テキスト
        params: APIリクエストに追加するパラメータの辞書

    Returns:
        生成されたレスポンス
    """
    # 基本パラメータ
    request_params = {
        "model": "gpt-4o",
        "input": prompt_text,
    }

    # 追加パラメータがあれば追加
    if params:
        request_params.update(params)

    # APIを呼び出し
    return client.responses.create(**request_params)


def compare_temperature_responses(client, prompt):
    """異なるtemperature値での応答を比較します。

    Args:
        client: OpenAIクライアントインスタンス
        prompt: 入力テキスト

    Returns:
        各temperatureでの応答のリスト
    """
    print("\n===== temperature パラメータの比較 =====")
    print(f'プロンプト: "{prompt}"')
    print(
        "temperatureは出力の多様性と創造性に影響します。高い値はより創造的な応答を、低い値はより決定論的な応答を生成します。"
    )

    temperatures = [0.0, 0.5, 1.0, 1.5]
    results = []

    for temp in temperatures:
        response = create_response_with_params(client, prompt, {"temperature": temp})

        results.append(
            {
                "temperature": temp,
                "output": response.output_text,
                "tokens": response.usage.output_tokens,
            }
        )

        print(f"\ntemperature = {temp}:")
        print(f"出力: {response.output_text}")
        print(f"出力トークン数: {response.usage.output_tokens}")

    return results


def compare_top_p_responses(client, prompt):
    """異なるtop_p値での応答を比較します。

    Args:
        client: OpenAIクライアントインスタンス
        prompt: 入力テキスト

    Returns:
        各top_pでの応答のリスト
    """
    print("\n===== top_p パラメータの比較 =====")
    print(f'プロンプト: "{prompt}"')
    print(
        "top_pはnucleusサンプリングを制御します。0.1は上位10%の確率質量のトークンのみを考慮し、top_pが低いほど予測可能な出力になります。"
    )

    top_p_values = [0.1, 0.5, 0.9, 1.0]
    results = []

    for top_p in top_p_values:
        response = create_response_with_params(
            client, prompt, {"top_p": top_p, "temperature": 1.0}  # 温度を固定して比較
        )

        results.append(
            {
                "top_p": top_p,
                "output": response.output_text,
                "tokens": response.usage.output_tokens,
            }
        )

        print(f"\ntop_p = {top_p}:")
        print(f"出力: {response.output_text}")
        print(f"出力トークン数: {response.usage.output_tokens}")

    return results


def compare_max_tokens_responses(client, prompt):
    """異なるmax_output_tokens値での応答を比較します。

    Args:
        client: OpenAIクライアントインスタンス
        prompt: 入力テキスト

    Returns:
        各max_output_tokensでの応答のリスト
    """
    print("\n===== max_output_tokens パラメータの比較 =====")
    print(f'プロンプト: "{prompt}"')
    print(
        "max_output_tokensは生成される出力の最大トークン数を制限します。短い応答や特定の長さの応答を得るのに有用です。"
    )

    # OpenAIのAPIドキュメントによると、max_output_tokensの最小値は16
    max_tokens_values = [16, 30, 100, 300]
    results = []

    for max_tokens in max_tokens_values:
        response = create_response_with_params(
            client, prompt, {"max_output_tokens": max_tokens}
        )

        results.append(
            {
                "max_tokens": max_tokens,
                "output": response.output_text,
                "tokens": response.usage.output_tokens,
            }
        )

        print(f"\nmax_output_tokens = {max_tokens}:")
        print(f"出力: {response.output_text}")
        print(f"出力トークン数: {response.usage.output_tokens}")

    return results


def combined_parameter_examples(client):
    """パラメータの組み合わせの例を示します。

    Args:
        client: OpenAIクライアントインスタンス
    """
    print("\n===== パラメータの組み合わせの例 =====")

    # クリエイティブな短い詩の生成（高温度、中程度のトークン数）
    creative_prompt = "「月」をテーマにした短い詩を書いてください。"
    creative_params = {
        "temperature": 1.5,
        "max_output_tokens": 150,
        "instructions": "あなたは革新的で実験的な詩人です。比喩や象徴を多用してください。",
    }

    creative_response = create_response_with_params(
        client, creative_prompt, creative_params
    )
    print("\n【創造的な詩の生成】")
    print(
        f"パラメータ: temperature={creative_params['temperature']}, max_output_tokens={creative_params['max_output_tokens']}"
    )
    print(f"出力:\n{creative_response.output_text}")
    print(f"出力トークン数: {creative_response.usage.output_tokens}")

    # 事実に基づく簡潔な説明（低温度、制限されたトークン数）
    factual_prompt = "光合成のプロセスを説明してください。"
    factual_params = {
        "temperature": 0.2,
        "max_output_tokens": 200,
        "instructions": "あなたは科学教師です。正確で簡潔な事実のみを伝えてください。",
    }

    factual_response = create_response_with_params(
        client, factual_prompt, factual_params
    )
    print("\n【事実に基づく説明】")
    print(
        f"パラメータ: temperature={factual_params['temperature']}, max_output_tokens={factual_params['max_output_tokens']}"
    )
    print(f"出力:\n{factual_response.output_text}")
    print(f"出力トークン数: {factual_response.usage.output_tokens}")

    # 特定のフォーマットに従った出力（中程度の温度、top_p制限）
    format_prompt = "次の3つの都市（東京、ニューヨーク、ロンドン）の人口、面積、有名な観光地を箇条書きで紹介してください。"
    format_params = {
        "temperature": 0.7,
        "top_p": 0.8,
        "instructions": "回答は箇条書きリストで、各都市ごとに人口、面積、観光地の情報を含めてください。",
    }

    format_response = create_response_with_params(client, format_prompt, format_params)
    print("\n【特定フォーマットの出力】")
    print(
        f"パラメータ: temperature={format_params['temperature']}, top_p={format_params['top_p']}"
    )
    print(f"出力:\n{format_response.output_text}")
    print(f"出力トークン数: {format_response.usage.output_tokens}")


def main():
    """メイン関数: 様々なパラメータ設定での応答生成のデモンストレーション"""
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)

        # 1. temperatureパラメータの比較
        creative_prompt = "未来の技術について新しいアイデアを提案してください。"
        compare_temperature_responses(client, creative_prompt)

        # 2. top_pパラメータの比較
        variation_prompt = "「AI」という単語から連想されるものを挙げてください。"
        compare_top_p_responses(client, variation_prompt)

        # 3. max_output_tokensパラメータの比較
        length_prompt = "クラウドコンピューティングの利点と課題を説明してください。"
        compare_max_tokens_responses(client, length_prompt)

        # 4. パラメータを組み合わせた実用例
        combined_parameter_examples(client)

    except Exception as error:
        print(f"エラーが発生しました: {error}")


if __name__ == "__main__":
    main()
