import os
import json
import openai
from dotenv import load_dotenv


def setup_environment():
    """
    環境変数から API キーを読み込み、openai.api_key を設定します。
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY が設定されていません")
    openai.api_key = api_key


# --- ツール関数（モック実装） ---
def get_weather(location: str):
    """
    指定された場所の天気情報を返します（モック実装）。
    """
    if "paris" in location.lower():
        return {"temperature": 20, "unit": "celsius"}
    return {"error": "No weather data available for this location."}


def get_attractions(location: str):
    """
    指定された場所の観光スポット情報を返します（モック実装）。
    """
    if "paris" in location.lower():
        return {"attractions": ["Eiffel Tower", "Louvre Museum"]}
    return {"error": "No attractions available for this location."}


def get_hotels(location: str):
    """
    指定された場所のホテル情報を返します（モック実装）。
    """
    if "paris" in location.lower():
        return {"hotels": ["Hotel Le Meurice", "Hotel Lutetia"]}
    return {"error": "No hotel data available for this location."}


# --- ツールのスキーマ定義 ---
def setup_tools():
    return [
        {
            "type": "function",
            "name": "get_weather",
            "description": "Get current temperature for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country e.g. Paris, France",
                    }
                },
                "required": ["location"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "get_attractions",
            "description": "Get top attractions for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country e.g. Paris, France",
                    }
                },
                "required": ["location"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "get_hotels",
            "description": "Get hotel recommendations for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country e.g. Paris, France",
                    }
                },
                "required": ["location"],
                "additionalProperties": False,
            },
        },
    ]


# --- 関数呼び出しのルーティング ---
def call_function(function_name, arguments):
    """
    モデルからの関数呼び出しに基づき、対応するローカル関数を実行します。
    """
    if function_name == "get_weather":
        return get_weather(arguments["location"])
    elif function_name == "get_attractions":
        return get_attractions(arguments["location"])
    elif function_name == "get_hotels":
        return get_hotels(arguments["location"])
    else:
        return {"error": "未実装の関数です"}


def main():
    # 環境設定とツール定義
    setup_environment()
    tools = setup_tools()

    # ユーザーからの問い合わせ（旅行計画）
    messages = [
        {
            "role": "user",
            "content": "I am planning a trip to Paris. Can you give me the current weather, top attractions, and hotel recommendations?",
        }
    ]

    print("=" * 60)
    print("【初回リクエスト】")
    print("ユーザーメッセージ:")
    print("  " + messages[0]["content"])
    print("=" * 60)

    client = openai.Client()

    # parallel_tool_calls を有効にして初回リクエストを送信
    response = client.responses.create(
        model="gpt-4o", input=messages, tools=tools, parallel_tool_calls=True
    )

    print("\n【並列ツール呼び出し結果】")
    function_outputs = []
    for output in response.output:
        if output.type == "function_call":
            print(f"\nFunction: {output.name}")
            print(f"  Arguments: {output.arguments}")
            args = json.loads(output.arguments)
            result = call_function(output.name, args)
            print(f"  Result: {json.dumps(result, ensure_ascii=False)}")
            function_outputs.append(
                {
                    "role": "assistant",
                    "content": json.dumps({output.name: result}, ensure_ascii=False),
                }
            )
    print("=" * 60)

    # 取得した各ツールの結果を会話履歴に追加
    messages.extend(function_outputs)

    # ユーザーから最終回答を求めるメッセージを追加
    final_user_msg = {
        "role": "user",
        "content": "Please provide a final summary integrating all the above information.",
    }
    messages.append(final_user_msg)

    print("\n【更新された会話履歴】")
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        print(f"{role.capitalize()}: {content}")
    print("=" * 60)

    # 最終リクエスト：更新した会話履歴に基づき、最終応答を生成
    final_response = client.responses.create(
        model="gpt-4o", input=messages, tools=tools
    )

    # --- 最終応答の整形表示 ---
    # final_response.output は ResponseOutputMessage のリストになっているので、
    # その中からテキスト部分のみを抽出して整形して表示します。
    final_text = ""
    for message in final_response.output:
        # もし message.content がリストになっている場合、その中の各テキストを連結
        if isinstance(message.content, list):
            for item in message.content:
                if hasattr(item, "text"):
                    final_text += item.text + "\n"
        elif isinstance(message.content, str):
            final_text += message.content + "\n"

    print("\n【最終応答】")
    print(final_text.strip())
    print("=" * 60)


if __name__ == "__main__":
    main()
