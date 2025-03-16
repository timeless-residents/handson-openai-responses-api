"""
ツール選択の制御（tool_choice）を実装したサンプル

このサンプルでは、OpenAI Responses APIのtool_choice機能を利用して、
AIモデルがどのツールを呼び出すかを制御する方法を示します。
"""

import os
import sys
import json
from enum import Enum
from datetime import datetime
from dotenv import load_dotenv
import openai

# Python 3.7以降の場合、標準入出力のエンコーディングをUTF-8に設定
if sys.version_info >= (3, 7):
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")


class ToolChoiceMode(Enum):
    """ツール選択モードの列挙型"""

    AUTO = "auto"
    REQUIRED = "required"
    NONE = "none"
    SPECIFIC = "specific"


def setup_environment():
    """環境設定を行い、APIキーを取得します。"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(root_path, ".env")
    # .envファイルが存在する場合のみロード
    if os.path.exists(env_path):
        load_dotenv(env_path)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY が設定されていません")
    return api_key


# --- ツール関数 ---


def get_weather(city):
    """指定された都市の天気情報を取得します。"""
    data = {
        "東京": {"condition": "晴れ", "temperature": 28},
        "大阪": {"condition": "雨", "temperature": 24},
        "札幌": {"condition": "曇り", "temperature": 18},
        "福岡": {"condition": "晴れ", "temperature": 30},
    }
    if city in data:
        return {"city": city, **data[city]}
    else:
        return {"error": f"都市 '{city}' の天気情報は利用できません"}


def get_attractions(city):
    """指定された都市の観光スポット情報を取得します。"""
    data = {
        "東京": ["東京スカイツリー", "浅草寺", "東京タワー", "渋谷スクランブル交差点"],
        "大阪": ["大阪城", "ユニバーサルスタジオジャパン", "道頓堀", "梅田スカイビル"],
        "札幌": ["札幌時計台", "大通公園", "北海道大学", "もいわ山ロープウェイ"],
        "福岡": ["太宰府天満宮", "福岡タワー", "海の中道海浜公園", "博多駅"],
    }
    if city in data:
        return {"city": city, "attractions": data[city]}
    else:
        return {"error": f"都市 '{city}' の観光スポット情報は利用できません"}


def get_hotels(city):
    """指定された都市のホテル情報を取得します。"""
    data = {
        "東京": [
            "パークハイアット東京",
            "ホテルメトロポリタン",
            "ザ・リッツカールトン東京",
        ],
        "大阪": ["コンラッド大阪", "スイスホテル南海大阪", "ホテルニューオータニ大阪"],
        "札幌": ["JRタワーホテル日航札幌", "札幌グランドホテル", "札幌パークホテル"],
        "福岡": [
            "グランド・ハイアット・福岡",
            "ANAクラウンプラザホテル福岡",
            "ホテルオークラ福岡",
        ],
    }
    if city in data:
        return {"city": city, "hotels": data[city]}
    else:
        return {"error": f"都市 '{city}' のホテル情報は利用できません"}


def get_restaurants(city):
    """指定された都市の飲食店情報を取得します。"""
    data = {
        "東京": ["銀座 寿司清", "叙々苑", "bills", "一蘭 新宿中央東口店"],
        "大阪": ["蟹道楽", "たこ八", "きつねうどん なか卯", "松阪牛 よし田"],
        "札幌": [
            "回転寿司 根室花まる",
            "スープカレー 心",
            "ジンギスカン だるま",
            "みよしの",
        ],
        "福岡": [
            "博多一幸舎",
            "博多もつ鍋 やま中",
            "博多魚がし 海の路",
            "ひょうたん寿司",
        ],
    }
    if city in data:
        return {"city": city, "restaurants": data[city]}
    else:
        return {"error": f"都市 '{city}' の飲食店情報は利用できません"}


# --- ツール定義 ---


def setup_tools():
    """ツール定義を設定します。"""
    return [
        {
            "type": "function",
            "name": "get_weather",
            "description": "指定された都市の天気情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "都市名"}},
                "required": ["city"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "get_attractions",
            "description": "指定された都市の観光スポット情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "都市名"}},
                "required": ["city"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "get_hotels",
            "description": "指定された都市のホテル情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "都市名"}},
                "required": ["city"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "get_restaurants",
            "description": "指定された都市の飲食店情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "都市名"}},
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    ]


# --- ツール呼び出し処理 ---


def process_tool_call(client, user_input, tools, tool_choice_mode, specific_tool=None):
    """
    ツール呼び出しを実行し、ツールの結果を集約して最終回答を生成します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        user_input (str): ユーザー入力
        tools (list): ツール定義のリスト
        tool_choice_mode (ToolChoiceMode): ツール選択モード
        specific_tool (str, optional): 特定のツール名（tool_choice_mode=SPECIFICの場合に使用）

    Returns:
        str: 最終的な応答テキスト
    """
    # ツール選択モードに応じてtool_choiceを設定
    if tool_choice_mode == ToolChoiceMode.AUTO:
        tool_choice = "auto"
    elif tool_choice_mode == ToolChoiceMode.REQUIRED:
        tool_choice = "required"
    elif tool_choice_mode == ToolChoiceMode.NONE:
        tool_choice = "none"
    elif tool_choice_mode == ToolChoiceMode.SPECIFIC and specific_tool:
        tool_choice = {"type": "function", "function": {"name": specific_tool}}
    else:
        tool_choice = "auto"  # デフォルト

    # 最初のリクエスト
    print(f"ツール選択モード: {tool_choice_mode.value}")
    if tool_choice_mode == ToolChoiceMode.SPECIFIC and specific_tool:
        print(f"指定されたツール: {specific_tool}")

    response = client.responses.create(
        model="gpt-4o",
        instructions="ユーザーの質問に答えるため、必要に応じてツールを使用してください。",
        input=user_input,
        tools=tools,
        tool_choice=tool_choice,
        # 本サンプルではparallel_tool_calls=Falseを明示的に指定（デフォルト値）
        parallel_tool_calls=False,
    )

    print("\n初回応答:", response.output_text)

    # ツール呼び出しがなければ初回応答を返す
    function_calls = [msg for msg in response.output if msg.type == "function_call"]
    if not function_calls:
        return response.output_text

    # ツール呼び出しがある場合は処理
    print("\nツール呼び出し:")
    outputs = []
    for fc in function_calls:
        print(f"- 呼び出されたツール: {fc.name}")
        args = json.loads(fc.arguments)
        print(f"  引数: {args}")

        # ツール関数を実行
        if fc.name == "get_weather":
            result = get_weather(**args)
        elif fc.name == "get_attractions":
            result = get_attractions(**args)
        elif fc.name == "get_hotels":
            result = get_hotels(**args)
        elif fc.name == "get_restaurants":
            result = get_restaurants(**args)
        else:
            result = {"error": "未実装の関数"}

        print(f"  結果: {result}")

        # ツール呼び出し結果を追加
        outputs.append(
            {
                "type": "function_call_output",
                "call_id": fc.call_id,
                "output": json.dumps(result, ensure_ascii=False),
            }
        )

    # 最終応答の生成
    final_response = client.responses.create(
        model="gpt-4o",
        instructions="ツールから取得した情報を整理して最終回答を生成してください。",
        input=outputs,
        previous_response_id=response.id,
    )

    print("\n最終応答:", final_response.output_text)
    return final_response.output_text


def main():
    """メイン関数"""
    api_key = setup_environment()
    client = openai.Client(api_key=api_key)
    tools = setup_tools()

    # ツール選択モードの説明
    print("ツール選択モード（tool_choice）のサンプル\n")
    print("以下のモードから選択してください:")
    print("1: auto - AIがツールの使用を自動判断")
    print("2: required - ツールの使用を必須にする")
    print("3: none - ツールを使用せず")
    print("4: specific - 特定のツールのみ使用\n")

    # モード選択
    mode_choice = input("モードを選択してください (1-4): ").strip()

    # 選択されたモードに基づいてツール選択モードを設定
    if mode_choice == "1":
        tool_choice_mode = ToolChoiceMode.AUTO
        specific_tool = None
    elif mode_choice == "2":
        tool_choice_mode = ToolChoiceMode.REQUIRED
        specific_tool = None
    elif mode_choice == "3":
        tool_choice_mode = ToolChoiceMode.NONE
        specific_tool = None
    elif mode_choice == "4":
        tool_choice_mode = ToolChoiceMode.SPECIFIC
        print("\n使用可能なツール:")
        print("1: get_weather - 天気情報")
        print("2: get_attractions - 観光スポット")
        print("3: get_hotels - ホテル情報")
        print("4: get_restaurants - 飲食店情報")

        tool_number = input("使用するツールを選択してください (1-4): ").strip()
        if tool_number == "1":
            specific_tool = "get_weather"
        elif tool_number == "2":
            specific_tool = "get_attractions"
        elif tool_number == "3":
            specific_tool = "get_hotels"
        elif tool_number == "4":
            specific_tool = "get_restaurants"
        else:
            print("無効な選択です。get_weatherを使用します。")
            specific_tool = "get_weather"
    else:
        print("無効な選択です。autoモードを使用します。")
        tool_choice_mode = ToolChoiceMode.AUTO
        specific_tool = None

    # ユーザー入力
    city = input("\n都市名を入力してください (例: 東京, 大阪, 札幌, 福岡): ")
    query_type = input("質問内容を入力してください (例: 天気, 観光, ホテル, 飲食店): ")
    user_input = f"{city}の{query_type}について教えてください。"

    # ツール呼び出し処理
    process_tool_call(client, user_input, tools, tool_choice_mode, specific_tool)

    print("\n処理完了")


if __name__ == "__main__":
    main()
