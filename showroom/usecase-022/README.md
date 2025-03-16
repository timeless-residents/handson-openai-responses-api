# ユースケース 022: カスタム関数呼び出し（Function Calling）

このユースケースでは、OpenAI Responses APIを使用したカスタム関数呼び出し（Function Calling）の実装方法を紹介します。

## 概要

Function Callingは、AIモデルが特定の関数やAPIを呼び出すためのJSON形式のパラメータを生成できる機能です。これにより、AIと外部システムやサービスを連携させ、複雑なタスクを実行できるようになります。このサンプルでは、Responses APIとFunction Calling機能を使用して、様々なユースケースに応用可能なカスタム関数の定義と呼び出しを行う方法を示します。

このサンプルでは、以下の機能を紹介しています：

- カスタム関数の定義と実装
- 複数の関数を提供する方法
- 関数呼び出しのパラメータ処理
- 呼び出し結果の処理とAIへの返却
- 複数ターンの対話における関数呼び出しの使用方法

## 実行方法

1. プロジェクトのルートディレクトリに`.env`ファイルを作成し、OpenAI APIキーを設定します：

```
OPENAI_API_KEY=your_api_key_here
```

2. 必要なパッケージをインストールします：

```bash
pip install -r requirements.txt
```

3. スクリプトを実行します：

```bash
python main.py
```

4. 実行モードを選択します：
   - 天気情報照会
   - カレンダー予定管理
   - 計算機能
   - 複合的なアシスタント

## カスタム関数の定義

Responses APIのツール機能を使用して、カスタム関数を定義します：

```python
# 関数定義のリスト
functions = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "指定された都市の現在の天気情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "都市名（例: 東京、大阪、京都）"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度の単位"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_calendar_event",
            "description": "カレンダーに新しい予定を追加します",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "予定のタイトル"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "開始時間（ISO 8601形式、例: 2023-09-15T13:00:00）"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "終了時間（ISO 8601形式、例: 2023-09-15T14:00:00）"
                    },
                    "description": {
                        "type": "string",
                        "description": "予定の詳細説明"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "参加者のメールアドレスリスト"
                    }
                },
                "required": ["title", "start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "数学的な計算を行います",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide", "power"],
                        "description": "実行する演算（加算、減算、乗算、除算、べき乗）"
                    },
                    "values": {
                        "type": "array",
                        "items": {
                            "type": "number"
                        },
                        "description": "計算に使用する数値の配列"
                    }
                },
                "required": ["operation", "values"]
            }
        }
    }
]
```

## 関数の実装

定義した関数は以下のように実装されます：

```python
def get_weather(city, unit="celsius"):
    """指定された都市の現在の天気情報を取得します。
    
    Args:
        city (str): 都市名
        unit (str, optional): 温度の単位. デフォルトは "celsius"
        
    Returns:
        dict: 天気情報
    """
    # 実際のアプリケーションでは、ここで天気APIを呼び出します
    # このサンプルではモックデータを返します
    weather_data = {
        "東京": {"condition": "晴れ", "temperature": 28, "humidity": 65},
        "大阪": {"condition": "曇り", "temperature": 26, "humidity": 70},
        "京都": {"condition": "雨", "temperature": 24, "humidity": 80},
        "札幌": {"condition": "雪", "temperature": 5, "humidity": 90},
        "福岡": {"condition": "晴れ", "temperature": 30, "humidity": 60}
    }
    
    if city in weather_data:
        data = weather_data[city].copy()
        
        # 温度単位の変換
        if unit == "fahrenheit":
            data["temperature"] = round(data["temperature"] * 9/5 + 32, 1)
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
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {"error": f"都市 '{city}' の天気情報は利用できません"}

def add_calendar_event(title, start_time, end_time, description="", attendees=None):
    """カレンダーに新しい予定を追加します。
    
    Args:
        title (str): 予定のタイトル
        start_time (str): 開始時間（ISO 8601形式）
        end_time (str): 終了時間（ISO 8601形式）
        description (str, optional): 予定の詳細説明
        attendees (list, optional): 参加者のメールアドレスリスト
        
    Returns:
        dict: 作成された予定の情報
    """
    # 実際のアプリケーションでは、ここでカレンダーAPIを呼び出します
    # このサンプルでは予定が作成されたというレスポンスを返します
    
    # ランダムなイベントIDを生成
    event_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
    
    event = {
        "id": event_id,
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "description": description,
        "attendees": attendees or [],
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "message": "予定が正常に作成されました",
        "event": event
    }

def calculate(operation, values):
    """数学的な計算を行います。
    
    Args:
        operation (str): 実行する演算（加算、減算、乗算、除算、べき乗）
        values (list): 計算に使用する数値の配列
        
    Returns:
        dict: 計算結果
    """
    if not values:
        return {"error": "計算する値が提供されていません"}
    
    try:
        result = values[0]
        
        if operation == "add":
            for val in values[1:]:
                result += val
            operation_str = "+"
        elif operation == "subtract":
            for val in values[1:]:
                result -= val
            operation_str = "-"
        elif operation == "multiply":
            for val in values[1:]:
                result *= val
            operation_str = "×"
        elif operation == "divide":
            for val in values[1:]:
                if val == 0:
                    return {"error": "0で除算することはできません"}
                result /= val
            operation_str = "÷"
        elif operation == "power":
            if len(values) != 2:
                return {"error": "べき乗計算には2つの値が必要です"}
            result = values[0] ** values[1]
            operation_str = "^"
        else:
            return {"error": f"サポートされていない演算: {operation}"}
        
        # 式の構築
        expression = str(values[0])
        for val in values[1:]:
            expression += f" {operation_str} {val}"
        
        return {
            "operation": operation,
            "expression": expression,
            "result": result
        }
    except Exception as e:
        return {"error": f"計算中にエラーが発生しました: {str(e)}"}
```

## 関数呼び出しのフロー

このサンプルでは、AIと関数呼び出しを組み合わせた対話フローを実装しています：

1. ユーザーからの入力を受け取る
2. AIがどの関数を呼び出すべきかを判断
3. 関数実行に必要なパラメータをAIが生成
4. 関数を実行して結果を取得
5. 結果をAIに返して応答を生成

```python
def process_conversation(client, user_input, conversation_history, functions):
    """会話を処理し、必要に応じて関数を呼び出します。
    
    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        user_input (str): ユーザーの入力
        conversation_history (list): 会話履歴
        functions (list): 利用可能な関数のリスト
        
    Returns:
        tuple: 更新された会話履歴と、AIの応答
    """
    # ユーザー入力を会話履歴に追加
    conversation_history.append({"role": "user", "content": user_input})
    
    # AIに問い合わせ
    response = client.responses.create(
        model="gpt-4o",
        instructions="あなたは有用なアシスタントです。与えられたツールを使って、ユーザーの質問に答えてください。",
        input=conversation_history,
        tools=functions
    )
    
    # AIの応答を会話履歴に追加
    conversation_history.append({"role": "assistant", "content": response.output_text})
    
    # 関数呼び出しがある場合
    if response.tool_calls:
        tool_outputs = []
        
        for tool_call in response.tool_calls:
            function_name = tool_call.name
            function_args = tool_call.arguments
            
            # 関数を実行
            if function_name == "get_weather":
                result = get_weather(**function_args)
            elif function_name == "add_calendar_event":
                result = add_calendar_event(**function_args)
            elif function_name == "calculate":
                result = calculate(**function_args)
            else:
                result = {"error": f"未実装の関数: {function_name}"}
            
            # 結果を追加
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })
        
        # ツール呼び出し結果を会話履歴に追加
        conversation_history.append({"role": "tool_calls", "content": tool_outputs})
        
        # AIに再度問い合わせ
        response = client.responses.create(
            model="gpt-4o",
            instructions="あなたは有用なアシスタントです。与えられたツールを使って、ユーザーの質問に答えてください。",
            input=conversation_history,
            tools=functions
        )
        
        # AIの応答を会話履歴に追加
        conversation_history.append({"role": "assistant", "content": response.output_text})
    
    return conversation_history, response.output_text
```

## 応用例

この機能は以下のような用途に応用できます：

1. **個人アシスタント**: 予定管理、天気確認、計算など、複数の機能を統合したアシスタント
2. **顧客サポート**: 注文状況確認、返品処理、FAQ応答などの自動化
3. **データ分析**: データベースクエリ、データ可視化、レポート生成の統合
4. **IoT制御**: スマートホームデバイスの状態確認や操作
5. **旅行予約**: フライト検索、ホテル予約、レンタカー手配などの連携処理

## 制限事項と考慮点

- 関数定義は正確でわかりやすい説明と適切なパラメータ構造が重要です
- 機密情報の扱いには注意が必要です（APIキーや個人情報など）
- エラー処理を適切に行い、AIがエラーを理解できる形で返すことが重要です
- 複雑な関数パラメータの場合、AIが正確に生成できるよう十分な情報を提供する必要があります
- APIの使用には料金が発生します（特に大量のやり取りを行う場合）

## 追加リソース

- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI Tools Documentation](https://platform.openai.com/docs/guides/tools)
- [JSON Schema](https://json-schema.org/understanding-json-schema/)
- [Responses API Reference](https://platform.openai.com/docs/api-reference/responses)