"""
OpenAI Responses API での会話状態管理の実装例

このスクリプトでは、OpenAI Responses API の previous_response_id パラメータを使用して
会話の状態を管理する方法を示します。同じ質問をステートありとステートなしで比較できます。
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


def create_stateless_response(client, message):
    """ステートを保持しない単発的な応答を生成します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        message (str): モデルへの入力テキスト

    Returns:
        openai.types.responses.Response: APIからの応答オブジェクト
    """
    return client.responses.create(
        model="gpt-4o",
        input=message,
    )


def create_stateful_response(client, message, previous_response_id=None):
    """ステートを保持する会話応答を生成します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        message (str): モデルへの入力テキスト
        previous_response_id (str, optional): 直前の応答のID。Noneの場合は新規会話を開始。

    Returns:
        openai.types.responses.Response: APIからの応答オブジェクト
    """
    # previous_response_idが指定されている場合は会話を継続
    if previous_response_id:
        return client.responses.create(
            model="gpt-4o",
            input=message,
            previous_response_id=previous_response_id,
        )
    # previous_response_idが指定されていない場合は新規会話を開始
    else:
        return client.responses.create(
            model="gpt-4o",
            input=message,
        )


def display_response(response, label):
    """APIからの応答を整形して表示します。

    Args:
        response (openai.types.responses.Response): APIからの応答オブジェクト
        label (str): 応答に付けるラベル（ステートフルかステートレスかなど）
    """
    print(f"\n===== {label} =====")
    print(f"Response ID: {response.id}")
    print(f"Output Text: {response.output_text}")
    print(f"Token Usage: {response.usage.total_tokens} tokens")
    print("=" * (len(label) + 12))


def run_stateless_conversation(client):
    """ステートを保持しない会話の流れを実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
    """
    print("\n# ステートなし会話のデモ（毎回新しいコンテキスト）")

    # 最初の質問
    message1 = "私の名前は田中です。"
    response1 = create_stateless_response(client, message1)
    display_response(response1, "ステートなし応答 1")

    # 2回目の質問 - 前の会話を覚えていないはず
    message2 = "私の名前は何ですか？"
    response2 = create_stateless_response(client, message2)
    display_response(response2, "ステートなし応答 2")

    # 3回目の質問 - 前の会話を覚えていないはず
    message3 = "私は何歳だと思いますか？"
    response3 = create_stateless_response(client, message3)
    display_response(response3, "ステートなし応答 3")


def run_stateful_conversation(client):
    """ステートを保持する会話の流れを実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
    """
    print("\n# ステートあり会話のデモ（前回の会話を記憶）")

    # 最初の質問
    message1 = "私の名前は田中です。"
    response1 = create_stateful_response(client, message1)
    display_response(response1, "ステートあり応答 1")

    # 2回目の質問 - previous_response_idを指定して会話を継続
    message2 = "私の名前は何ですか？"
    response2 = create_stateful_response(client, message2, response1.id)
    display_response(response2, "ステートあり応答 2")

    # 3回目の質問 - previous_response_idを指定して会話を継続
    message3 = "私は何歳だと思いますか？"
    response3 = create_stateful_response(client, message3, response2.id)
    display_response(response3, "ステートあり応答 3")

    return response3.id  # 最後の応答IDを返す（会話継続のために使用できる）


def run_mixed_conversation(client, last_response_id):
    """会話の途中から状態を引き継ぐデモを実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        last_response_id (str): 前の会話の最後のレスポンスID
    """
    print("\n# 会話の途中から状態を引き継ぐデモ")

    # 前の会話から状態を引き継いで新しい質問
    message = "私の趣味はプログラミングです。"
    response = create_stateful_response(client, message, last_response_id)
    display_response(response, "会話継続応答")

    # さらに続けて質問
    message2 = "私についてこれまでに分かっていることを要約してください。"
    response2 = create_stateful_response(client, message2, response.id)
    display_response(response2, "会話継続応答（要約）")


def run_conversation_comparison(client):
    """ステートありとステートなしの会話を比較します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
    """
    print("\n# 会話の比較デモ")

    # 共通の初期メッセージ
    setup_message = "私の名前は佐藤です。2人の子供がいます。"
    
    # ステートありの会話
    stateful_response1 = create_stateful_response(client, setup_message)
    display_response(stateful_response1, "ステートあり初期設定")
    
    follow_up = "子供の名前は太郎と花子です。"
    stateful_response2 = create_stateful_response(client, follow_up, stateful_response1.id)
    display_response(stateful_response2, "ステートあり追加情報")
    
    question = "私の家族構成を教えてください。"
    stateful_response3 = create_stateful_response(client, question, stateful_response2.id)
    display_response(stateful_response3, "ステートあり質問応答")
    
    # ステートなしの会話
    stateless_response = create_stateless_response(client, question)
    display_response(stateless_response, "ステートなし同じ質問")


def main():
    """メイン実行関数

    各種デモを実行します。
    """
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)

        # ステートなし会話のデモを実行
        run_stateless_conversation(client)

        # ステートあり会話のデモを実行
        last_response_id = run_stateful_conversation(client)

        # 会話の途中から状態を引き継ぐデモを実行
        run_mixed_conversation(client, last_response_id)

        # ステートありとステートなしの比較を実行
        run_conversation_comparison(client)

    except Exception as error:
        print(f"エラーが発生しました: {error}")


if __name__ == "__main__":
    main()