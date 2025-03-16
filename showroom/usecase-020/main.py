"""
OpenAI Responses API の Web検索ツール機能を示すスクリプト

このスクリプトは、OpenAI Responses APIのWeb検索ツールを使って
インターネット検索を行い、最新情報に基づいた回答を生成する実装例です。
"""

import os
import sys
import json
from dotenv import load_dotenv
import openai
from datetime import datetime


def setup_environment():
    """環境設定を行い、APIキーを取得します。"""
    # プロジェクトルートのパスを設定し、.envからAPIキーを読み込む
    root_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(root_path)
    load_dotenv(os.path.join(root_path, ".env"))

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 環境変数が設定されていません")

    return api_key


def create_response_with_web_search(client, user_query, search_params=None):
    """Web検索ツールを使用してレスポンスを生成します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        user_query (str): ユーザーからの質問
        search_params (dict, optional): Web検索の設定パラメータ

    Returns:
        dict: APIからの応答
    """
    # システムプロンプト
    system_prompt = "あなたは最新の情報にアクセスできるアシスタントです。インターネット検索を使って、正確で最新の情報を提供します。検索結果の情報源も明示してください。"

    # APIリクエスト
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
        tools=[{"type": "web_search"}],
    )

    # レスポンス処理
    result = {
        "id": response.id,
        "model": response.model,
        "created_at": response.created_at,
        "output_text": response.output_text,
        "usage": response.usage,
        "tools_usage": [],
    }

    # Responses APIではツール使用情報が返されない（現在の実装では）
    # 今後APIが更新されたらここを修正

    return result


def display_response_with_tool_usage(response):
    """APIからの応答とツール使用状況を表示します。

    Args:
        response (dict): APIからの応答
    """
    print(f"\n===== 回答生成結果 =====")
    print(f"モデル: {response['model']}")
    print(
        f"生成日時: {datetime.fromtimestamp(response['created_at']).strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print("\n--- 回答 ---")
    print(response["output_text"])
    print("------------")

    # 現在のResponses API実装ではツール使用情報が返されないため、
    # 回答のみを表示する
    print("\n注: 現在のResponses API実装ではWeb検索の詳細情報は表示できません")

    print(f"\nトークン使用量:")
    print(f"  入力: {response['usage'].input_tokens}")
    print(f"  出力: {response['usage'].output_tokens}")
    print(f"  合計: {response['usage'].total_tokens}")
    print("==========================")


def run_predefined_examples(client):
    """事前定義された例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
    """
    examples = [
        {
            "title": "最新情報の取得",
            "query": "現在の日本の首相は誰ですか？その主な政策は何ですか？",
        },
        {
            "title": "時事問題の分析",
            "query": "最近の人工知能技術の最新動向について教えてください。特に生成AIの進展について知りたいです。",
        },
        {
            "title": "事実確認",
            "query": "東京オリンピックはいつ開催されましたか？コロナ禍の影響はありましたか？",
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n例{i}: {example['title']}")
        print(f"質問: {example['query']}")
        print("処理中...")

        response = create_response_with_web_search(client, example["query"])
        display_response_with_tool_usage(response)


def interactive_mode(client):
    """インタラクティブモードで実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
    """
    print("\n===== インタラクティブモード =====")
    print(
        "質問を入力してください。終了するには 'exit' または 'quit' と入力してください。"
    )

    while True:
        user_query = input("\n質問: ")

        if user_query.lower() in ["exit", "quit", "終了"]:
            print("プログラムを終了します。")
            break

        if not user_query.strip():
            print("質問を入力してください。")
            continue

        print("処理中...")
        response = create_response_with_web_search(client, user_query)
        display_response_with_tool_usage(response)


def main():
    """メイン関数"""
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)

        print("OpenAI Responses API - Web検索ツールのデモ")

        # 実行モード選択
        print("\n実行モードを選択してください:")
        print("1: 事前定義された例を実行")
        print("2: インタラクティブモード（自分で質問を入力）")

        while True:
            choice = input("選択 (1/2): ")
            if choice in ["1", "2"]:
                break
            print("1か2を入力してください。")

        if choice == "1":
            run_predefined_examples(client)
        else:
            interactive_mode(client)

    except Exception as error:
        print(f"エラーが発生しました: {error}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
