# ユースケース 023: 並列ツール呼び出し（parallel_tool_calls）

このユースケースでは、OpenAI Responses APIを使用した並列ツール呼び出し（parallel_tool_calls）の実装方法を紹介します。

## 概要

parallel_tool_callsは、AIモデルが複数のツール（関数）を一度に呼び出すことができる機能です。これにより、複数の独立したタスクを効率的に実行し、ユーザーとの対話をよりスムーズに行うことができます。このサンプルでは、Responses APIとparallel_tool_calls機能を使用して、複数のデータソースから情報を同時に取得する方法を示します。

このサンプルでは、以下の機能を紹介しています：

- 複数のツールを同時に呼び出す方法
- 並列ツール呼び出しの設定と制御
- 複数のデータソースからの情報の統合
- 効率的な対話処理の実装

## 実行方法

1. `.env`ファイルを作成し、OpenAI APIキーを設定します：

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

4. プロンプトで都市名（例：東京）を入力すると、その都市に関する天気、観光スポット、ホテル情報が並列で取得され、まとめられた情報が表示されます。

## 並列ツール呼び出しの設定

Responses APIでparallel_tool_callsを有効にするには、以下のように設定します：

```python
response = client.responses.create(
    model="gpt-4o",
    instructions="あなたは有用なアシスタントです。複数のデータソースから情報を効率的に取得して答えてください。",
    input=user_input,
    tools=tools,
    tool_choice="auto",
    parallel_tool_calls=True
)
```

## 並列ツール呼び出しの実装例

このサンプルでは、複数のデータソースから同時に情報を取得する例を示します：

```python
def get_travel_info(client, destination):
    """旅行先の情報を並列で取得します。
    
    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        destination (str): 旅行先の都市名
        
    Returns:
        dict: 旅行情報（天気、観光スポット、ホテル）
    """
    user_input = f"{destination}への旅行について調べています。天気、観光スポット、ホテルについて教えてください。"
    
    response = client.responses.create(
        model="gpt-4o",
        instructions="あなたは旅行アシスタントです。指定された都市の情報を複数のデータソースから取得して提供してください。",
        input=user_input,
        tools=travel_tools,
        tool_choice="auto",
        parallel_tool_calls=True
    )
    
    # 関数呼び出しの処理
    if response.tool_calls:
        tool_outputs = []
        results = {}
        
        for tool_call in response.tool_calls:
            function_name = tool_call.name
            function_args = tool_call.arguments
            
            # 関数を並列で実行（実際のアプリケーションでは非同期処理を使用）
            if function_name == "get_weather":
                result = get_weather(**function_args)
                results["weather"] = result
            elif function_name == "get_attractions":
                result = get_attractions(**function_args)
                results["attractions"] = result
            elif function_name == "get_hotels":
                result = get_hotels(**function_args)
                results["hotels"] = result
            
            # 結果を追加
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })
        
        # ツール呼び出し結果をモデルに渡して最終応答を生成
        final_response = client.responses.create(
            model="gpt-4o",
            instructions="あなたは旅行アシスタントです。取得した情報を統合して分かりやすく伝えてください。",
            input=tool_outputs,
            previous_response_id=response.id
        )
        
        return {
            "destination": destination,
            "results": results,
            "summary": final_response.output_text
        }
    else:
        return {
            "destination": destination,
            "error": "情報を取得できませんでした"
        }
```

## 応用例

この機能は以下のような用途に応用できます：

1. **旅行計画アシスタント**: 天気、観光スポット、ホテル、交通情報などを同時に取得
2. **ニュースアグリゲーター**: 複数のニュースソースから同時に情報を収集して要約
3. **製品比較ツール**: 複数の製品情報やレビューを並列で取得して比較分析
4. **金融情報ダッシュボード**: 株価、経済指標、ニュースなど複数の金融データを同時取得
5. **健康管理アプリ**: 運動データ、食事記録、睡眠情報などを並列で分析

## 制限事項と考慮点

- 並列ツール呼び出しは、独立したタスクに最適です（相互依存性のあるタスクには適していません）
- 一度に処理できるツール呼び出しの数には上限があります
- 各ツールの実行時間が異なる場合、最も遅いツールの完了を待つ必要があります
- 実際のアプリケーションでは、非同期処理（asyncio など）を使用して真の並列処理を実現することをお勧めします
- モデルが必要なツールを適切に選択するよう、明確な指示と十分なコンテキストを提供することが重要です

## 追加リソース

- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI Parallel Function Calling](https://platform.openai.com/docs/guides/parallel-function-calling)
- [OpenAI Tools Documentation](https://platform.openai.com/docs/guides/tools)
- [Responses API Reference](https://platform.openai.com/docs/api-reference/responses)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)