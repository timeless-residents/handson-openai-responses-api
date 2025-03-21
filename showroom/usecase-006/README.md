# ユースケース 006: 会話状態の管理（previous_response_id）

このユースケースでは、OpenAI Responses APIを使用して会話の状態を管理する方法を紹介します。

## 概要

通常、APIリクエストは独立しており、各リクエストは前のリクエストのコンテキストや会話の履歴を保持していません。しかし、Responses APIの`previous_response_id`パラメータを使用することで、モデルは以前の会話の文脈を記憶し、一貫した対話を維持できます。

このサンプルでは、以下のような会話状態管理の例を示します：

1. **ステートなし対話**: 各リクエストが独立した会話として扱われる従来の方法
2. **ステートあり対話**: `previous_response_id`を使用して会話の文脈を維持する方法
3. **会話の継続**: 途中から以前の会話を再開する方法
4. **比較デモ**: 同じ質問に対するステートありとステートなしの違いを比較

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

## 出力例

このスクリプトを実行すると、ステートありとステートなしの会話の違いが明確に表示されます。

### ステートなし会話の例

ステートなしの会話では、各リクエストは独立しており、前の会話を覚えていません：

```
===== ステートなし応答 1 =====
Response ID: resp_abc123...
Output Text: こんにちは、田中さん。何かお手伝いできることはありますか？
Token Usage: 28 tokens
============================

===== ステートなし応答 2 =====
Response ID: resp_def456...
Output Text: あなたの名前については情報を持っていません。先ほど教えていただけましたか？
Token Usage: 35 tokens
============================
```

### ステートあり会話の例

ステートありの会話では、`previous_response_id`を使用して前の会話の文脈を維持します：

```
===== ステートあり応答 1 =====
Response ID: resp_ghi789...
Output Text: こんにちは、田中さん。何かお手伝いできることはありますか？
Token Usage: 28 tokens
============================

===== ステートあり応答 2 =====
Response ID: resp_jkl012...
Output Text: あなたの名前は田中さんです。
Token Usage: 32 tokens
============================
```

## 会話管理のメカニズム

Responses APIで会話状態を管理するには、以下の手順を実行します：

1. **初期会話**: 最初のリクエストでは`previous_response_id`を指定せず、新しい会話を開始します
2. **応答IDの保存**: レスポンスから返される`id`を保存します
3. **会話の継続**: 次のリクエストでは`previous_response_id`パラメータに前回の応答IDを指定します
4. **チェーン**: 各リクエストで新しい応答IDを取得し、次のリクエストで使用します

```python
# 最初の会話
response1 = client.responses.create(
    model="gpt-4o",
    input="こんにちは",
)

# 会話を継続
response2 = client.responses.create(
    model="gpt-4o",
    input="私の名前は田中です",
    previous_response_id=response1.id,  # ここで前回の応答IDを指定
)
```

## 応用例

会話状態管理は以下のようなユースケースに有用です：

1. **チャットボット**: 顧客との連続的な会話を維持する
2. **ユーザー補助**: ユーザーの以前の質問や好みを記憶する
3. **複雑なタスク**: 複数のステップに分かれたタスクの情報を保持する
4. **パーソナライズ**: ユーザーの背景情報を会話全体で維持する
5. **文脈依存タスク**: 「前の回答を修正して」などの文脈依存指示に対応する

## 実装上の注意点

- 会話履歴は90日間保持されますが、長い会話では情報が失われる可能性があります
- 会話の文脈はトークン制限の影響を受けるため、非常に長い会話では要約などの工夫が必要です
- セキュリティのため、会話IDは適切に管理し、他のユーザーとの混同を避けるべきです
- 会話履歴は自動的にOpenAIのシステムに保存されるため、プライバシーとデータセキュリティを考慮してください

## 追加リソース

- [OpenAI Responses APIドキュメント](https://platform.openai.com/docs/api-reference/responses)
- [会話履歴の管理に関するガイドライン](https://platform.openai.com/docs/guides/prompt-engineering/conversation-history)