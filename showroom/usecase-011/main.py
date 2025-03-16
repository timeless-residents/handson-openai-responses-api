"""
OpenAI Responses API - ユースケース011: テキストと画像の複合入力

このスクリプトは、OpenAI Responses APIを使用してテキストと画像を組み合わせた
複合入力を処理し、複雑な対話や分析を行う方法を示します。
単一の会話で複数の画像や文脈を維持する方法などを実演します。
"""

import os
import sys
import json
import base64
from pathlib import Path
import requests
from dotenv import load_dotenv
import openai

# 画像処理用のライブラリ（インストールされている場合のみインポート）
try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


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


def encode_image_to_base64(image_path):
    """画像ファイルをBase64にエンコードします。

    Args:
        image_path (str): ローカル画像ファイルのパス

    Returns:
        str: Base64エンコードされた画像データ
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def create_conversation(messages):
    """会話履歴をフォーマットします。

    Args:
        messages (list): メッセージのリスト

    Returns:
        list: フォーマットされた会話履歴
    """
    formatted_messages = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", [])

        if isinstance(content, str):
            # テキストのみのメッセージ
            formatted_messages.append({"role": role, "content": content})
        else:
            # 複合メッセージ（テキスト+画像）
            formatted_content = []

            for item in content:
                if item["type"] == "text":
                    formatted_content.append({"type": "text", "text": item["text"]})
                elif item["type"] == "image":
                    # ローカルファイルパスの場合はBase64エンコード
                    if "path" in item:
                        image_data = encode_image_to_base64(item["path"])
                        formatted_content.append(
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                },
                            }
                        )
                    # URLの場合はそのまま使用
                    elif "url" in item:
                        formatted_content.append(
                            {"type": "image_url", "image_url": {"url": item["url"]}}
                        )

            formatted_messages.append({"role": role, "content": formatted_content})

    return formatted_messages


def chat_with_images(client, messages):
    """画像を含む会話を行います。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        messages (list): 会話メッセージのリスト

    Returns:
        dict: APIからの応答
    """
    formatted_messages = create_conversation(messages)

    # APIリクエスト
    response = client.chat.completions.create(
        model="gpt-4o", messages=formatted_messages
    )

    # レスポンスフォーマットを調整
    return {
        "id": response.id,
        "model": response.model,
        "created_at": response.created,
        "output_text": response.choices[0].message.content,
        "usage": response.usage,
    }


def display_conversation(messages, response=None):
    """会話履歴と応答を表示します。

    Args:
        messages (list): 会話メッセージのリスト
        response (dict, optional): APIからの応答
    """
    print("\n===== 会話履歴 =====")

    for i, msg in enumerate(messages):
        role = msg.get("role", "user")
        content = msg.get("content", [])

        print(f"\n--- {role.upper()} #{i+1} ---")

        if isinstance(content, str):
            print(content)
        else:
            for item in content:
                if item["type"] == "text":
                    print(item["text"])
                elif item["type"] == "image":
                    if "path" in item:
                        print(f"[画像: {os.path.basename(item['path'])}]")
                    elif "url" in item:
                        print(f"[画像URL: {item['url']}]")

    if response:
        print("\n--- ASSISTANT 応答 ---")
        print(response["output_text"])
        print(f"\nモデル: {response['model']}")
        print(
            f"トークン使用量: {response['usage'].prompt_tokens}(入力) + {response['usage'].completion_tokens}(出力) = {response['usage'].total_tokens}(合計)"
        )

    print("\n=====================")


def run_visual_qa_example(client, image_dir):
    """視覚的なQ&A例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_dir (str): 画像ディレクトリのパス

    Returns:
        dict: APIからの応答
    """
    print("\n# 例1: 視覚的なQ&A")

    # 画像ファイルパス
    chart_path = os.path.join(image_dir, "chart.jpg")

    # 会話メッセージの作成
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "この図表を解析して、主要なデータポイントと傾向を教えてください。",
                },
                {"type": "image", "path": chart_path},
            ],
        }
    ]

    # 応答の取得
    response = chat_with_images(client, messages)

    # 結果表示
    display_conversation(messages, response)

    # フォローアップ質問
    messages.append({"role": "assistant", "content": response["output_text"]})

    messages.append(
        {
            "role": "user",
            "content": "この図表から読み取れるビジネスへの影響や推奨事項は何ですか？",
        }
    )

    # フォローアップ応答の取得
    follow_up_response = chat_with_images(client, messages)

    # 結果表示
    display_conversation(messages, follow_up_response)

    return follow_up_response


def run_multiimage_comparison(client, image_dir):
    """複数画像の比較例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_dir (str): 画像ディレクトリのパス

    Returns:
        dict: APIからの応答
    """
    print("\n# 例2: 複数画像の比較分析")

    # 画像ファイルパス
    landscape_path = os.path.join(image_dir, "landscape.jpg")
    chart_path = os.path.join(image_dir, "chart.jpg")

    # 会話メッセージの作成
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "これら2つの画像を比較して、それぞれの主な特徴と用途の違いを説明してください。",
                },
                {"type": "image", "path": landscape_path},
                {"type": "image", "path": chart_path},
            ],
        }
    ]

    # 応答の取得
    response = chat_with_images(client, messages)

    # 結果表示
    display_conversation(messages, response)

    return response


def run_creative_writing_example(client, image_dir):
    """創造的なライティング例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_dir (str): 画像ディレクトリのパス

    Returns:
        dict: APIからの応答
    """
    print("\n# 例3: 画像をベースにした創造的なライティング")

    # 画像ファイルパス
    landscape_path = os.path.join(image_dir, "landscape.jpg")

    # 会話メッセージの作成
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "この風景画像をインスピレーションにして、200字程度の短い物語を書いてください。物語には、この場所を訪れる旅人と自然の神秘的な出会いを含めてください。",
                },
                {"type": "image", "path": landscape_path},
            ],
        }
    ]

    # 応答の取得
    response = chat_with_images(client, messages)

    # 結果表示
    display_conversation(messages, response)

    # フォローアップ依頼
    messages.append({"role": "assistant", "content": response["output_text"]})

    messages.append(
        {
            "role": "user",
            "content": "素晴らしいです。今度はこの物語を俳句の形式で表現してください。",
        }
    )

    # フォローアップ応答の取得
    follow_up_response = chat_with_images(client, messages)

    # 結果表示
    display_conversation(messages, follow_up_response)

    return follow_up_response


def run_visual_analysis_with_context(client, image_dir):
    """文脈のある視覚分析例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_dir (str): 画像ディレクトリのパス

    Returns:
        dict: APIからの応答
    """
    print("\n# 例4: 文脈のある視覚分析")

    # 画像ファイルパス
    landscape_path = os.path.join(image_dir, "landscape.jpg")

    # 会話メッセージの作成 - 背景情報と目的を含む詳細なプロンプト
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "私は自然保護団体のマーケティング担当者です。この風景画像を環境保全キャンペーンで使用したいと考えています。この画像の以下の側面について分析してください：\n\n1. 保全価値がある自然要素\n2. 画像が訴える感情的メッセージ\n3. 環境保護のための潜在的なスローガンのアイデア\n4. 想定されるターゲットオーディエンス\n5. 補完するテキストメッセージの提案",
                },
                {"type": "image", "path": landscape_path},
            ],
        }
    ]

    # 応答の取得
    response = chat_with_images(client, messages)

    # 結果表示
    display_conversation(messages, response)

    return response


def main():
    """メイン実行関数

    OpenAI Responses APIを使用して、テキストと画像の複合入力の例を実行します。
    """
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)

        # 画像ディレクトリのパス
        image_dir = os.path.join(os.path.dirname(__file__), "images")

        # 例1: 視覚的なQ&A（フォローアップ質問を含む）
        run_visual_qa_example(client, image_dir)

        # 例2: 複数画像の比較分析
        run_multiimage_comparison(client, image_dir)

        # 例3: 画像をベースにした創造的なライティング
        run_creative_writing_example(client, image_dir)

        # 例4: 文脈のある視覚分析
        run_visual_analysis_with_context(client, image_dir)

    except Exception as error:
        print(f"エラーが発生しました: {error}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
