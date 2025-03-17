import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import json
import requests

# 環境変数の読み込み
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
API_URL = "https://api.openai.com/v1/chat/completions"  # ChatCompletion APIのエンドポイント


@app.route("/", methods=["GET", "POST"])
def index():
    response_data = None
    query_type = "facility"  # デフォルトのクエリ種別

    if request.method == "POST":
        user_query = request.form.get("query", "")
        query_type = request.form.get("query_type", "facility")

        try:
            # システムプロンプトの設定
            system_prompt = """
            あなたはバリアフリー情報アクセス支援の専門家です。ユーザーの質問に対して、バリアフリー施設や情報へのアクセスを支援する情報を提供してください。
            必ず以下のJSON形式で回答してください:
            
            {
                "title": "タイトル", 
                "summary": "情報の要約",
                "details": [
                    {
                        "category": "カテゴリ",
                        "information": "詳細情報"
                    }
                ],
                "accessibility_tips": ["ヒント1", "ヒント2"],
                "additional_resources": ["リソース1", "リソース2"]
            }
            """
            if query_type == "facility":
                system_prompt += """
                施設に関する質問の場合は、以下の情報も含めてください:
                - 車いすアクセス
                - 視覚障害者向け設備
                - 聴覚障害者向け設備
                - 多目的トイレの有無
                - 最寄りの公共交通機関からのアクセス
                """
            elif query_type == "service":
                system_prompt += """
                サービスに関する質問の場合は、以下の情報も含めてください:
                - 利用可能な支援サービス
                - 事前予約の必要性
                - 利用料金
                - 対応している言語
                - オンラインでの申請方法
                """

            # ChatCompletion API用のペイロード作成
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                "response_format": {"type": "json_object"}
            }

            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            }

            # APIへリクエスト送信
            api_response = requests.post(API_URL, headers=headers, json=payload)
            api_response.raise_for_status()
            response_json = api_response.json()

            # レスポンステキストの取得
            response_text = response_json["choices"][0]["message"]["content"]
            parsed_json = json.loads(response_text)

            response_data = {
                "raw_response": response_text,
                "parsed_json": parsed_json,
                "model": response_json.get("model", ""),
                "id": response_json.get("id", ""),
                "usage": {
                    "input_tokens": response_json["usage"]["prompt_tokens"],
                    "output_tokens": response_json["usage"]["completion_tokens"],
                    "total_tokens": response_json["usage"]["total_tokens"]
                }
            }

        except Exception as e:
            # 例外発生時はエラーメッセージとAPIレスポンスの詳細も返す
            error_details = ""
            if "api_response" in locals():
                try:
                    error_details = api_response.text
                except:
                    error_details = "APIレスポンスの詳細を取得できませんでした"
            response_data = {"error": str(e), "details": error_details}

    return render_template("index.html", response=response_data, query_type=query_type)


if __name__ == "__main__":
    app.run(debug=True, port=5012)