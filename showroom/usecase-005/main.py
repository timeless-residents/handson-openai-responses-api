"""
OpenAI Responses API を使用した構造化JSON出力の生成デモ

このスクリプトは、OpenAI Responses API を使用して、テキスト情報を
構造化されたJSON形式で出力する方法をデモンストレーションします。
"""

import os
import json
import requests
import jsonschema
from dotenv import load_dotenv


def setup_environment():
    """環境設定を行い、APIキーを取得する"""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY が設定されていません。")
        return None
    return api_key


def create_json_response(api_key, prompt, format_type="json_object"):
    """OpenAI Responses APIを使用してJSON形式の応答を取得する

    Args:
        api_key (str): OpenAI APIキー
        prompt (str): 入力プロンプト
        format_type (str): JSONフォーマットタイプ ("json_object" または "json_schema")

    Returns:
        dict: APIレスポンス（成功時）、None（失敗時）
    """
    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4o",
        "input": prompt,
        "text": {"format": {"type": format_type}},
        "max_output_tokens": 150,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # エラーレスポンスの場合に例外を発生
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"APIリクエストエラー: {e}")
        print(f"レスポンス: {response.text}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

    return None


def create_json_schema_response(api_key, prompt, schema):
    """JSONスキーマを使用した構造化レスポンスを取得する

    Args:
        api_key (str): OpenAI APIキー
        prompt (str): 入力プロンプト
        schema (dict): JSONスキーマ定義

    Returns:
        dict: APIレスポンス（成功時）、None（失敗時）
    """
    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # strict を True にして、スキーマで指定された全フィールドが出力されることを要求する
    payload = {
        "model": "gpt-4o",
        "input": prompt,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "response_format",
                "schema": schema,
                "strict": True,
            }
        },
        "max_output_tokens": 500,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"APIリクエストエラー: {e}")
        print(f"レスポンス: {response.text}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

    return None


def extract_generated_json(data):
    """
    APIのレスポンス全体から、実際に生成されたJSON文字列部分を抽出し、
    パースして dict として返す。
    """
    try:
        output = data.get("output", [])
        if output:
            msg = output[0]
            content = msg.get("content", [])
            if content:
                text = content[0].get("text", "")
                return json.loads(text)
    except Exception as e:
        print("JSON抽出・解析エラー:", e)
    return None


def validate_json_response(parsed, schema):
    """抽出したJSONを指定のスキーマでバリデーションする"""
    if not parsed:
        return False
    try:
        jsonschema.validate(instance=parsed, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        print("JSONバリデーションエラー:", e)
        return False


def display_json_response(data, schema=None):
    """レスポンス全体ではなく、生成されたJSON部分を抽出・検証して表示する"""
    if not data:
        return

    if schema:
        parsed = extract_generated_json(data)
        if parsed is not None:
            is_valid = validate_json_response(parsed, schema)
            validation_status = (
                "✓ バリデーション成功" if is_valid else "✗ バリデーション失敗"
            )
            print(f"\n===== JSON出力結果 (抽出内容) ({validation_status}) =====")
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
        else:
            print("抽出されたJSONがありません。")
    else:
        print("\n===== JSON出力結果 =====")
        print(json.dumps(data, ensure_ascii=False, indent=2))

    print("========================\n")


def main():
    """メイン実行関数"""
    # 環境設定
    api_key = setup_environment()
    if not api_key:
        return

    # 例1: 基本的なJSONオブジェクト出力の例
    basic_prompt = (
        "次の情報をJSON形式で出力してください：\n"
        "名前: 山田太郎\n"
        "年齢: 35\n"
        "職業: ソフトウェアエンジニア"
    )

    print("例1: 基本的なJSON出力の例を実行中...")
    data1 = create_json_response(api_key, basic_prompt)
    display_json_response(data1)

    # 例2: スキーマを使用した製品情報の構造化
    product_prompt = (
        "次の製品説明からJSON形式で製品情報を抽出してください：\n\n"
        "新型スマートフォン「TechX Pro」は2024年5月15日に発売予定。価格は98,000円（税抜き）。\n"
        "主な特徴は高性能カメラ（5000万画素）、大容量バッテリー（5000mAh）、\n"
        "高速プロセッサ（Snapdragon 8 Gen 3）、防水防塵対応（IP68）です。"
    )

    product_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "product_name": {"type": "string", "description": "製品の名称"},
            "price": {"type": "number", "description": "製品の価格（税抜き）"},
            "release_date": {
                "type": "string",
                "description": "発売予定日（YYYY-MM-DD形式）",
            },
            "features": {
                "type": "array",
                "items": {"type": "string", "description": "製品の特徴"},
                "description": "製品の主な特徴リスト",
            },
        },
        "required": ["product_name", "price", "release_date", "features"],
    }

    print("\n例2: JSONスキーマを使用した製品情報の構造化を実行中...")
    data2 = create_json_schema_response(api_key, product_prompt, product_schema)
    display_json_response(data2, product_schema)

    # 例3: イベントスケジュールの構造化
    # ※各イベントで必ず required_items と optional_items を出力するように指示しています。
    event_prompt = (
        "以下のイベント情報をJSON形式で構造化してください。"
        "各イベントは必ず以下のフィールドを出力すること。該当する情報がない場合は、空の配列 [] を出力してください。\n\n"
        "1. 技術セミナー「AIの最新動向」\n"
        "   日時: 2024年6月10日 14:00-16:00\n"
        "   場所: テックハブ東京（渋谷区）\n"
        "   参加費: 3,000円\n"
        "   持ち物: ノートPC（オプション）\n\n"
        "2. ワークショップ「実践的機械学習」\n"
        "   日時: 2024年6月15日 10:00-17:00\n"
        "   場所: デジタルスクエア大阪\n"
        "   参加費: 12,000円\n"
        "   持ち物: ノートPC（必須）、USBメモリ\n\n"
        "3. オンラインウェビナー「APIの活用法」\n"
        "   日時: 2024年6月20日 19:00-20:30\n"
        "   場所: Zoom（リンクは申込後に送付）\n"
        "   参加費: 無料\n"
        "   持ち物: []\n"
    )

    event_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "イベントのタイトル",
                        },
                        "date": {
                            "type": "string",
                            "description": "開催日（YYYY-MM-DD形式）",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "開始時間（HH:MM形式）",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "終了時間（HH:MM形式）",
                        },
                        "location": {"type": "string", "description": "開催場所"},
                        "fee": {
                            "type": "number",
                            "description": "参加費（円）、無料の場合は0",
                        },
                        "required_items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "必須の持ち物リスト",
                        },
                        "optional_items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "オプションの持ち物リスト",
                        },
                    },
                    "required": [
                        "title",
                        "date",
                        "start_time",
                        "end_time",
                        "location",
                        "fee",
                        "required_items",
                        "optional_items",
                    ],
                },
            }
        },
        "required": ["events"],
    }

    print("\n例3: イベントスケジュールの構造化を実行中...")
    data3 = create_json_schema_response(api_key, event_prompt, event_schema)
    display_json_response(data3, event_schema)

    # 例4: 感情分析の構造化出力
    # ※必ず全フィールドを出力するように指示しています。情報がない場合は空配列 [] を出力してください。
    sentiment_prompt = (
        "次のレビューテキストを感情分析し、JSON形式で結果を出力してください。"
        "必ず全てのフィールドを出力すること。情報がない場合は、空の配列 [] を出力してください。\n\n"
        "「このアプリは非常に使いやすいインターフェースで気に入っています。特に検索機能と通知の設定が素晴らしいです。"
        "ただ、最近のアップデート後に時々クラッシュする問題があり、少し不便です。"
        "それでも全体的には満足していて、友人にも勧めたいと思います。」"
    )

    sentiment_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "sentiment": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "overall_rating": {
                        "type": "number",
                        "description": "全体的な評価（1-5の範囲）",
                    },
                    "overall_sentiment": {
                        "type": "string",
                        "enum": [
                            "very_negative",
                            "negative",
                            "neutral",
                            "positive",
                            "very_positive",
                        ],
                        "description": "全体的な感情の分類",
                    },
                },
                "required": ["overall_rating", "overall_sentiment"],
            },
            "aspects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "aspect": {
                            "type": "string",
                            "description": "言及された製品/サービスの側面（機能、使いやすさなど）",
                        },
                        "sentiment": {
                            "type": "string",
                            "enum": [
                                "very_negative",
                                "negative",
                                "neutral",
                                "positive",
                                "very_positive",
                            ],
                            "description": "その側面に対する感情",
                        },
                        "text_snippet": {
                            "type": "string",
                            "description": "その側面に関連するテキスト部分",
                        },
                    },
                    "required": ["aspect", "sentiment", "text_snippet"],
                },
                "description": "レビュー内で言及された製品/サービスの異なる側面とその感情",
            },
            "key_points": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "positive": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "レビュー内のポジティブなポイント",
                    },
                    "negative": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "レビュー内のネガティブなポイント",
                    },
                },
                "required": ["positive", "negative"],
            },
        },
        "required": ["sentiment", "aspects", "key_points"],
    }

    print("\n例4: 感情分析の構造化出力を実行中...")
    data4 = create_json_schema_response(api_key, sentiment_prompt, sentiment_schema)
    display_json_response(data4, sentiment_schema)


if __name__ == "__main__":
    main()
