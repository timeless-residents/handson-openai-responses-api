# ユースケース 020: Web検索ツールの活用

このユースケースでは、OpenAI Responses APIのWeb検索ツール機能を使用して、最新のインターネット情報に基づいた回答を生成する方法を紹介します。

## 概要

GPT-4oなどのLLMは、トレーニングデータの期間後の情報を持っていません。最新の情報や詳細なデータが必要な場合、Web検索ツールを利用することで、モデルがリアルタイムのインターネット情報にアクセスし、より正確で最新の回答を提供できるようになります。

このサンプルでは、以下の機能を示しています：

- Web検索ツールの有効化と設定
- ユーザーの質問に基づいて必要なときに自動的にWeb検索を実行
- 検索結果の情報を利用した最新かつ正確な回答の生成
- 検索クエリや結果の詳細情報の取得と表示

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
   - 事前定義された例を実行
   - インタラクティブモードで自分の質問を入力

## 使用例

Web検索ツールは以下のような質問に特に有効です：

- 「現在の日本の首相は誰ですか？」（最新の政治情報）
- 「最新のiPhoneモデルの特徴を教えてください」（最新の製品情報）
- 「今日の東京の天気はどうですか？」（リアルタイム情報）
- 「最近のAI技術のトレンドは何ですか？」（最新の技術動向）
- 「直近の為替レートはいくらですか？」（最新の経済データ）

## Responses APIでのWeb検索ツールの実装

### 基本的な実装

Web検索ツールは、Responses APIを使って簡単に実装できます：

```python
response = client.responses.create(
    model="gpt-4o",
    input=[
        {"role": "user", "content": "最新のノーベル文学賞受賞者は誰ですか？"}
    ],
    tools=[{"type": "web_search"}]  # Web検索ツールを有効化
)
```

### 基本的な設定

注意: Responses APIでは、現時点でWeb検索ツールのパラメータカスタマイズはサポートされていません。シンプルに型を指定するだけです：

```python
response = client.responses.create(
    model="gpt-4o",
    input=[
        {"role": "user", "content": "最新のノーベル文学賞受賞者は誰ですか？"}
    ],
    tools=[{"type": "web_search"}]
)
```

### システムプロンプトの使用

より効果的な使用のためにシステムプロンプトを併用できます：

```python
response = client.responses.create(
    model="gpt-4o",
    input=[
        {"role": "system", "content": "あなたは最新の情報にアクセスできるアシスタントです。必要に応じてWeb検索を使い、情報源を明示してください。"},
        {"role": "user", "content": "最新のノーベル文学賞受賞者は誰ですか？"}
    ],
    tools=[{"type": "web_search"}]
)
```

## 制約事項

現在のResponses APIの実装では、Web検索ツールの詳細情報（検索クエリや検索結果のリストなど）は応答オブジェクトに含まれていません。Web検索は内部的に実行され、その結果がモデルの回答に反映されますが、検索結果自体にはアクセスできません。

将来的なAPI更新により、検索結果の詳細情報にアクセスできるようになる可能性があります。その場合は以下のような構造になることが予想されます：

```python
# 将来的な実装の予想（現時点では機能しません）
if response.tool_uses:
    for tool_use in response.tool_uses:
        if tool_use.type == "web_search":
            # 検索クエリ
            search_query = tool_use.web_search.search_query
            
            # 検索結果
            search_results = tool_use.web_search.search_results
            for result in search_results:
                title = result.title
                url = result.url
                snippet = result.snippet
```

これは将来のAPI仕様変更によって変わる可能性があるため、最新のOpenAI APIドキュメントを参照することをお勧めします。

## ベストプラクティス

Web検索ツールを効果的に使用するためのベストプラクティス：

1. **具体的な質問を促す**：明確で具体的な質問は、より関連性の高い検索結果を得るのに役立ちます
2. **システムプロンプトの活用**：情報源の引用や検索戦略を指示するシステムプロンプトを設定しましょう
3. **検索パラメータの調整**：質問の複雑さに応じて`max_results`を調整しましょう
4. **エラーハンドリング**：検索結果が得られない場合や不十分な場合の対応を実装しましょう
5. **情報の確認**：重要な決定の前には、提供された情報の正確性を別の情報源で確認しましょう

## 制限事項と考慮点

- 検索結果は完全ではなく、情報が古い場合や不正確な場合があります
- 検索ツールの使用には追加料金が発生する場合があります
- すべての地域やすべての言語で同等の品質の検索結果が得られるとは限りません
- プライバシーやセキュリティの観点から、機密情報を含む質問は避けるべきです
- レート制限や使用量制限が適用される場合があります

## 応用例

このサンプルは以下のような用途に応用できます：

1. **ニュースサマライザー**：最新ニュースを検索して要約する
2. **研究アシスタント**：特定のトピックに関する最新の研究を調査する
3. **ファクトチェッカー**：情報の正確性を複数のソースで確認する
4. **競合分析ツール**：特定の製品や企業に関する最新情報を収集する
5. **トレンド分析**：特定のキーワードや業界の最新トレンドを分析する

## 追加リソース

- [OpenAI Tools Documentation](https://platform.openai.com/docs/guides/tools)
- [Web Search Tool Reference](https://platform.openai.com/docs/guides/tools/web-search)
- [Responses API Reference](https://platform.openai.com/docs/api-reference/responses)