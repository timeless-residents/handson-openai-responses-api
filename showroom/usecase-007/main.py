"""
OpenAI Responses API でのメタデータ活用とレスポンス管理の実装例

このスクリプトでは、OpenAI Responses API でメタデータを活用して
リクエストを整理し、レスポンスを効率的に管理する方法を示します。
"""

import os
import sys
import json
import uuid
from datetime import datetime
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


def create_response_with_metadata(client, message, metadata=None):
    """メタデータを付加したレスポンスを生成します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        message (str): モデルへの入力テキスト
        metadata (dict, optional): リクエストに添付するメタデータ

    Returns:
        openai.types.responses.Response: APIからの応答オブジェクト
    """
    # メタデータがない場合は空の辞書を使用
    if metadata is None:
        metadata = {}
    
    return client.responses.create(
        model="gpt-4o",
        input=message,
        metadata=metadata
    )


def display_response_with_metadata(response):
    """APIからの応答とメタデータを表示します。

    Args:
        response (openai.types.responses.Response): APIからの応答オブジェクト
    """
    print(f"\n===== レスポンス: {response.id} =====")
    print(f"Model: {response.model}")
    print(f"Created at: {response.created_at}")
    print(f"\nOutput Text:\n{response.output_text}")
    
    print("\nMetadata:")
    if hasattr(response, 'metadata') and response.metadata:
        for key, value in response.metadata.items():
            print(f"  {key}: {value}")
    else:
        print("  なし")
    
    print(f"\nToken Usage:")
    print(f"  Input tokens: {response.usage.input_tokens}")
    print(f"  Output tokens: {response.usage.output_tokens}")
    print(f"  Total tokens: {response.usage.total_tokens}")
    print("=" * (len(response.id) + 16))


def run_user_tracking_example(client):
    """ユーザー追跡のためのメタデータ活用例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
    """
    print("\n# ユーザー追跡のためのメタデータ活用例")
    
    # ユーザー情報をメタデータとして設定
    user_metadata = {
        "user_id": "user_12345",
        "session_id": str(uuid.uuid4()),
        "user_type": "premium",
        "locale": "ja-JP",
        "platform": "mobile"
    }
    
    # ユーザーメタデータを含むリクエストを作成
    message = "AIについて最新のトレンドを教えてください。"
    response = create_response_with_metadata(client, message, user_metadata)
    display_response_with_metadata(response)


def run_content_categorization_example(client):
    """コンテンツ分類のためのメタデータ活用例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
    """
    print("\n# コンテンツ分類のためのメタデータ活用例")
    
    # 質問カテゴリごとに異なるメタデータを設定
    categories = [
        {
            "message": "量子コンピューティングとは何ですか？", 
            "metadata": {
                "category": "science",
                "subcategory": "physics",
                "complexity": "beginner",
                "request_type": "definition"
            }
        },
        {
            "message": "JavaScriptでの非同期処理について説明してください。", 
            "metadata": {
                "category": "programming",
                "subcategory": "javascript",
                "complexity": "intermediate",
                "request_type": "explanation"
            }
        },
        {
            "message": "効果的なリーダーシップの原則は何ですか？", 
            "metadata": {
                "category": "business",
                "subcategory": "leadership",
                "complexity": "advanced",
                "request_type": "principles"
            }
        }
    ]
    
    # 各カテゴリでリクエストを実行
    for item in categories:
        response = create_response_with_metadata(
            client, 
            item["message"], 
            item["metadata"]
        )
        display_response_with_metadata(response)


def run_business_tracking_example(client):
    """ビジネス分析のためのメタデータ活用例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
    """
    print("\n# ビジネス分析のためのメタデータ活用例")
    
    # ビジネス情報を含むメタデータ
    business_metadata = {
        "department": "marketing",
        "project_id": "campaign_2023_summer",
        "cost_center": "mkt-001",
        "purpose": "content_creation",
        "campaign_id": "summer_sale_2023",
        "timestamp": datetime.now().isoformat()
    }
    
    # マーケティングコンテンツ生成リクエスト
    message = """
    以下の商品について魅力的な商品説明を100字程度で作成してください：
    
    商品名：ウルトラライト・ハイキングバックパック
    特徴：超軽量（500g）、防水素材、多数の収納ポケット、バックサポート機能
    ターゲット：アウトドア愛好家、トレッキング初心者
    価格帯：15,000円〜20,000円
    """
    
    response = create_response_with_metadata(client, message, business_metadata)
    display_response_with_metadata(response)


def run_ab_testing_example(client):
    """A/Bテストのためのメタデータ活用例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
    """
    print("\n# A/Bテストのためのメタデータ活用例")
    
    # 同じ質問に対して異なるパラメータ設定でテスト
    variants = [
        {
            "name": "バリアントA",
            "temperature": 0.2,
            "metadata": {
                "test_id": "prompt_test_001",
                "variant": "A",
                "temperature": "0.2",
                "description": "低温度での事実ベース応答"
            }
        },
        {
            "name": "バリアントB",
            "temperature": 0.8,
            "metadata": {
                "test_id": "prompt_test_001",
                "variant": "B",
                "temperature": "0.8",
                "description": "高温度での創造的応答"
            }
        }
    ]
    
    # 共通の質問
    question = "AIの未来についてあなたの見解を教えてください。"
    
    # 各バリアントでリクエストを実行
    for variant in variants:
        print(f"\n## {variant['name']} (temperature={variant['temperature']})")
        
        response = client.responses.create(
            model="gpt-4o",
            input=question,
            temperature=variant["temperature"],
            metadata=variant["metadata"]
        )
        
        display_response_with_metadata(response)


def main():
    """メイン実行関数

    各種メタデータ活用例を実行します。
    """
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)

        # ユーザー追跡のためのメタデータ活用例
        run_user_tracking_example(client)
        
        # コンテンツ分類のためのメタデータ活用例
        run_content_categorization_example(client)
        
        # ビジネス分析のためのメタデータ活用例
        run_business_tracking_example(client)
        
        # A/Bテストのためのメタデータ活用例
        run_ab_testing_example(client)

    except Exception as error:
        print(f"エラーが発生しました: {error}")


if __name__ == "__main__":
    main()