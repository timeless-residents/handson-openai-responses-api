"""
OpenAI Responses API でカスタム関数呼び出し（Function Calling）を実装したサンプル

このスクリプトは、OpenAI Responses APIを使ってカスタム関数呼び出し機能を
実装したサンプルです。天気情報照会、カレンダー予定管理、計算機能などを提供します。
"""

import os
import sys
import json
import random
from datetime import datetime
from dotenv import load_dotenv
import openai


def setup_environment():
    """環境設定を行い、APIキーを取得します。"""
    root_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(root_path)
    load_dotenv(os.path.join(root_path, ".env"))
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 環境変数が設定されていません")
    return api_key


def get_weather(city, unit="celsius"):
    """指定された都市の現在の天気情報を取得します。"""
    weather_data = {
        "東京": {"condition": "晴れ", "temperature": 28, "humidity": 65},
        "大阪": {"condition": "曇り", "temperature": 26, "humidity": 70},
        "京都": {"condition": "雨", "temperature": 24, "humidity": 80},
        "札幌": {"condition": "雪", "temperature": 5, "humidity": 90},
        "福岡": {"condition": "晴れ", "temperature": 30, "humidity": 60},
    }
    if city in weather_data:
        data = weather_data[city].copy()
        if unit == "fahrenheit":
            data["temperature"] = round(data["temperature"] * 9 / 5 + 32, 1)
            data["unit"] = "F"
        else:
            data["unit"] = "C"
        return {
            "city": city,
            "condition": data["condition"],
            "temperature": data["temperature"],
            "temperature_unit": data["unit"],
            "humidity": data["humidity"],
            "humidity_unit": "%",
            "timestamp": datetime.now().isoformat(),
        }
    else:
        return {"error": f"都市 '{city}' の天気情報は利用できません"}


def add_calendar_event(title, start_time, end_time, description="", attendees=None):
    """カレンダーに新しい予定を追加します。"""
    event_id = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
    event = {
        "id": event_id,
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "description": description,
        "attendees": attendees or [],
        "created_at": datetime.now().isoformat(),
    }
    return {
        "status": "success",
        "message": "予定が正常に作成されました",
        "event": event,
    }


def calculate(operation, values):
    """数学的な計算を行います。"""
    if not values:
        return {"error": "計算する値が提供されていません"}
    try:
        result = values[0]
        if operation == "add":
            for val in values[1:]:
                result += val
            op_str = "+"
        elif operation == "subtract":
            for val in values[1:]:
                result -= val
            op_str = "-"
        elif operation == "multiply":
            for val in values[1:]:
                result *= val
            op_str = "×"
        elif operation == "divide":
            for val in values[1:]:
                if val == 0:
                    return {"error": "0で除算することはできません"}
                result /= val
            op_str = "÷"
        elif operation == "power":
            if len(values) != 2:
                return {"error": "べき乗計算には2つの値が必要です"}
            result = values[0] ** values[1]
            op_str = "^"
        else:
            return {"error": f"サポートされていない演算: {operation}"}
        expression = str(values[0])
        for val in values[1:]:
            expression += f" {op_str} {val}"
        return {"operation": operation, "expression": expression, "result": result}
    except Exception as e:
        return {"error": f"計算中にエラーが発生しました: {str(e)}"}


def setup_functions():
    """利用可能なカスタム関数を定義します。"""
    return [
        {
            "type": "function",
            "name": "get_weather",
            "description": "指定された都市の現在の天気情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "都市名（例: 東京、大阪、京都）",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度の単位",
                    },
                },
                "required": ["city"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "add_calendar_event",
            "description": "カレンダーに新しい予定を追加します",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "予定のタイトル"},
                    "start_time": {
                        "type": "string",
                        "description": "開始時間（ISO 8601形式）",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "終了時間（ISO 8601形式）",
                    },
                    "description": {"type": "string", "description": "予定の詳細説明"},
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "参加者のメールアドレスリスト",
                    },
                },
                "required": ["title", "start_time", "end_time"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "calculate",
            "description": "数学的な計算を行います",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide", "power"],
                        "description": "実行する演算",
                    },
                    "values": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "計算に使用する数値の配列",
                    },
                },
                "required": ["operation", "values"],
                "additionalProperties": False,
            },
        },
    ]


def process_conversation(client, user_input, conversation_history, functions):
    """会話を処理し、必要に応じて関数を呼び出します。"""
    if not conversation_history:
        input_content = user_input
    else:
        previous_messages = []
        for msg in conversation_history:
            if msg["role"] == "user":
                previous_messages.append(
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": msg["content"]}],
                    }
                )
            elif msg["role"] == "assistant":
                previous_messages.append(
                    {
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": msg["content"]}],
                    }
                )
        input_content = [
            *previous_messages,
            {"role": "user", "content": [{"type": "input_text", "text": user_input}]},
        ]

    response = client.responses.create(
        model="gpt-4o",
        instructions="あなたは有用なアシスタントです。与えられたツールを使って、ユーザーの質問に答えてください。",
        input=input_content,
        tools=functions,
    )
    assistant_content = response.output_text
    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": assistant_content})

    # 関数呼び出しメッセージの抽出（属性アクセス）
    function_calls = [msg for msg in response.output if msg.type == "function_call"]
    if function_calls:
        tool_outputs = []
        for tool_call in function_calls:
            function_name = tool_call.name
            function_args = json.loads(tool_call.arguments)
            print(f"\n[関数呼び出し] {function_name}")
            print(
                f"パラメータ: {json.dumps(function_args, ensure_ascii=False, indent=2)}"
            )
            if function_name == "get_weather":
                result = get_weather(**function_args)
            elif function_name == "add_calendar_event":
                result = add_calendar_event(**function_args)
            elif function_name == "calculate":
                result = calculate(**function_args)
            else:
                result = {"error": f"未実装の関数: {function_name}"}
            print(f"結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            # call_id を使用して結果をまとめる
            tool_outputs.append(
                {"tool_call_id": tool_call.call_id, "output": json.dumps(result)}
            )
        # 各結果を "function_call_output" タイプの入力アイテムに変換
        tool_results_input = []
        for output in tool_outputs:
            tool_results_input.append(
                {
                    "type": "function_call_output",
                    "call_id": output["tool_call_id"],
                    "output": output["output"],
                }
            )
        # 前回のレスポンス ID を渡して、ツール呼び出し結果と紐付ける
        tool_response = client.responses.create(
            model="gpt-4o",
            instructions="あなたは有用なアシスタントです。与えられたツールを使って、ユーザーの質問に答えてください。",
            input=tool_results_input,
            previous_response_id=response.id,
            tools=functions,
        )
        final_content = tool_response.output_text
        print(f"\nAI: {final_content}")
        conversation_history.append({"role": "assistant", "content": final_content})
        return conversation_history, final_content
    else:
        return conversation_history, assistant_content


def demo_weather():
    """天気情報照会デモを実行します。"""
    print("\n===== 天気情報照会デモ =====")
    functions = [
        {
            "type": "function",
            "name": "get_weather",
            "description": "指定された都市の現在の天気情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "都市名（例: 東京、大阪、京都）",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度の単位",
                    },
                },
                "required": ["city"],
                "additionalProperties": False,
            },
        }
    ]
    return functions


def demo_calendar():
    """カレンダー予定管理デモを実行します。"""
    print("\n===== カレンダー予定管理デモ =====")
    functions = [
        {
            "type": "function",
            "name": "add_calendar_event",
            "description": "カレンダーに新しい予定を追加します",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "予定のタイトル"},
                    "start_time": {
                        "type": "string",
                        "description": "開始時間（ISO 8601形式）",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "終了時間（ISO 8601形式）",
                    },
                    "description": {"type": "string", "description": "予定の詳細説明"},
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "参加者のメールアドレスリスト",
                    },
                },
                "required": ["title", "start_time", "end_time"],
                "additionalProperties": False,
            },
        }
    ]
    return functions


def demo_calculator():
    """計算機能デモを実行します。"""
    print("\n===== 計算機能デモ =====")
    functions = [
        {
            "type": "function",
            "name": "calculate",
            "description": "数学的な計算を行います",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide", "power"],
                        "description": "実行する演算",
                    },
                    "values": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "計算に使用する数値の配列",
                    },
                },
                "required": ["operation", "values"],
                "additionalProperties": False,
            },
        }
    ]
    return functions


def demo_assistant():
    """複合的なアシスタントデモを実行します。"""
    print("\n===== 複合的なアシスタントデモ =====")
    print("このデモでは、以下の機能を同時に利用できます:")
    print("- 天気情報照会")
    print("- カレンダー予定管理")
    print("- 計算機能")
    return setup_functions()


def run_conversation_demo(client, functions):
    """会話デモを実行します。"""
    print("\n対話を開始します。終了するには 'exit' または 'quit' と入力してください。")
    print("利用可能な機能:")
    for func in functions:
        print(f"- {func['name']}: {func['description']}")
    conversation_history = []
    previous_response_id = None
    while True:
        user_input = input("\nあなた: ")
        if user_input.lower() in ["exit", "quit", "終了"]:
            print("対話を終了します。")
            break
        try:
            if not previous_response_id:
                response = client.responses.create(
                    model="gpt-4o",
                    instructions="あなたは有用なアシスタントです。与えられたツールを使って、ユーザーの質問に答えてください。",
                    input=user_input,
                    tools=functions,
                )
            else:
                response = client.responses.create(
                    model="gpt-4o",
                    instructions="あなたは有用なアシスタントです。与えられたツールを使って、ユーザーの質問に答えてください。",
                    input=user_input,
                    previous_response_id=previous_response_id,
                    tools=functions,
                )
            assistant_content = response.output_text
            print(f"\nAI: {assistant_content}")
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append(
                {"role": "assistant", "content": assistant_content}
            )
            function_calls = [
                msg for msg in response.output if msg.type == "function_call"
            ]
            if function_calls:
                tool_outputs = []
                for tool_call in function_calls:
                    function_name = tool_call.name
                    function_args = json.loads(tool_call.arguments)
                    print(f"\n[関数呼び出し] {function_name}")
                    print(
                        f"パラメータ: {json.dumps(function_args, ensure_ascii=False, indent=2)}"
                    )
                    if function_name == "get_weather":
                        result = get_weather(**function_args)
                    elif function_name == "add_calendar_event":
                        result = add_calendar_event(**function_args)
                    elif function_name == "calculate":
                        result = calculate(**function_args)
                    else:
                        result = {"error": f"未実装の関数: {function_name}"}
                    print(f"結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    tool_outputs.append(
                        {
                            "tool_call_id": tool_call.call_id,
                            "output": json.dumps(result),
                        }
                    )
                tool_results_input = []
                for output in tool_outputs:
                    tool_results_input.append(
                        {
                            "type": "function_call_output",
                            "call_id": output["tool_call_id"],
                            "output": output["output"],
                        }
                    )
                # 前回のレスポンスとの紐付けのため、previous_response_id を指定
                tool_response = client.responses.create(
                    model="gpt-4o",
                    instructions="あなたは有用なアシスタントです。与えられたツールを使って、ユーザーの質問に答えてください。",
                    input=tool_results_input,
                    previous_response_id=response.id,
                    tools=functions,
                )
                final_content = tool_response.output_text
                print(f"\nAI: {final_content}")
                conversation_history.append(
                    {"role": "assistant", "content": final_content}
                )
                previous_response_id = tool_response.id
            else:
                previous_response_id = response.id
        except Exception as e:
            print(f"\nエラーが発生しました: {e}")
            import traceback

            traceback.print_exc()
    return conversation_history


def main():
    try:
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)
        print("OpenAI Responses API - カスタム関数呼び出し（Function Calling）のデモ")
        print("\n実行モードを選択してください:")
        print("1: 天気情報照会")
        print("2: カレンダー予定管理")
        print("3: 計算機能")
        print("4: 複合的なアシスタント")
        while True:
            choice = input("選択 (1/2/3/4): ")
            if choice in ["1", "2", "3", "4"]:
                break
            print("1、2、3、または4を入力してください。")
        if choice == "1":
            functions = demo_weather()
        elif choice == "2":
            functions = demo_calendar()
        elif choice == "3":
            functions = demo_calculator()
        else:
            functions = demo_assistant()
        run_conversation_demo(client, functions)
    except Exception as error:
        print(f"エラーが発生しました: {error}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
