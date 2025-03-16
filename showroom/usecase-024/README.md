# ユースケース 024: ツール選択の制御（tool_choice）

このユースケースでは、OpenAI Responses APIのtool_choice機能を使用して、AIモデルのツール選択を制御する方法を紹介します。

## 概要

tool_choiceパラメータを使用することで、AIモデルがツールを使用するかどうか、またどのツールを使用するかを明示的に制御できます。これにより、特定の状況に応じたツール使用の戦略を実装することが可能になります。

このサンプルでは、以下の機能を紹介しています：

- `auto` - AIモデルが自律的にツールの使用を判断する（デフォルト）
- `required` - ツールの使用を必須にする
- `none` - ツールを使用せずに応答を生成する
- `specific` - 特定のツールのみ使用するよう指定する

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

4. 実行時にツール選択モードを選び、都市名と質問内容を入力することで、各モードの挙動の違いを確認できます。

## ツール選択モードの説明

### auto モード

```python
tool_choice = "auto"
```

AIモデルが状況に応じて自律的にツールを使用するかどうか、どのツールを使用するかを判断します。これはデフォルトの動作で、多くの場合に適切な選択をしますが、確実性は保証されません。

### required モード

```python
tool_choice = "required"
```

AIモデルに対して、必ずいずれかのツールを使用するよう指示します。ツールを使用せずに直接回答することを防ぎたい場合に有用です。

### none モード

```python
tool_choice = "none"
```

AIモデルにツールを使用せずに応答を生成するよう指示します。ツールを定義していても、それらを使用せずにモデルの知識のみで回答します。

### specific モード

```python
tool_choice = {"type": "function", "function": {"name": "specific_tool_name"}}
```

特定のツールのみを使用するようAIモデルに指示します。複数のツールが定義されていても、指定されたツールのみが使用されます。

## ユースケース例

- **auto**: 一般的な質問応答で、モデルに適切なツール選択を委ねる場合
- **required**: データベースからの情報取得など、必ずツールを使用すべき場合
- **none**: モデルの一般知識のみで回答可能な質問の場合
- **specific**: 特定の情報（天気、予約状況など）のみを取得したい場合

## 応用例

1. **ヘルプデスクシステム**:
   - 一般的な質問には直接回答（none）
   - 製品仕様に関する質問は製品データベースツールを使用（specific）
   - 複雑な問い合わせには複数のツールを使用（auto/required）

2. **情報検索システム**:
   - ユーザーが特定のデータソースを指定した場合はそのツールのみ使用（specific）
   - 一般的な検索では複数のソースを検索（auto）

3. **トラブルシューティングアシスタント**:
   - 診断フェーズではシステムデータ取得ツールを必ず使用（required）
   - 解決策の提案フェーズではモデルの知識を活用（none）

## 制限事項と考慮点

- **モード選択の基準**: 各ツール選択モードの適切な使用シナリオを理解することが重要です
- **ユーザー体験**: tool_choiceの設定がユーザー体験にどのように影響するかを考慮する必要があります
- **エラー処理**: 特に`specific`モードと`required`モードでは、ツールが適切に機能しない場合の対応を考慮する必要があります

## 追加リソース

- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI Tools Documentation](https://platform.openai.com/docs/guides/tools)
- [Responses API Reference](https://platform.openai.com/docs/api-reference/responses)