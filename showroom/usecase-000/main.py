"""
OpenAI Responses API の基本的な使用例を示すスクリプト
w
このスクリプトは、OpenAI Responses APIを使用してシンプルなテキスト入力と出力を実行する
最小限の実装例です。APIキーは環境変数またはプロジェクトルートの.envファイルから読み込みます。
"""

import os
import sys
import json
from dotenv import load_dotenv
import openai


def setup_environment():
    """環境設定を行い、APIキーを取得します。

    プロジェクトルートの.envファイルから環境変数を読み込み、
    OpenAI APIキーを取得します。

    Returns:
        str: OpenAI APIキー

    Raises:
        ValueError: APIキーが設定されていない場合
    """
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


def create_response(client, prompt_text):
    """OpenAI Responses APIを使用してテキスト応答を生成します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        prompt_text (str): モデルへの入力テキスト

    Returns:
        openai.types.responses.Response: APIからの応答オブジェクト

    Raises:
        Exception: API呼び出し中にエラーが発生した場合
    """
    response = client.responses.create(
        model="gpt-4o",
        input=prompt_text,
    )
    return response


def display_response(response):
    """APIからの応答を整形して表示します。

    Args:
        response (openai.types.responses.Response): APIからの応答オブジェクト
    """
    print("Response ID:", response.id)
    print("Model:", response.model)
    print("Created at:", response.created_at)
    print("\nOutput Text:")
    print(response.output_text)

    print("\nToken Usage:")
    print(f"Input tokens: {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")


def main():
    """メイン関数

    OpenAI Responses APIを呼び出し、結果を表示します。
    """
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)

        # APIリクエスト
        prompt = "こんにちは、挨拶を日本語・英語・中国語で回答してください。"
        response = create_response(client, prompt)

        # 結果表示
        display_response(response)

    except Exception as error:
        print(f"エラーが発生しました: {error}")


if __name__ == "__main__":
    main()
