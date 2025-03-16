# ユースケース 005: JSONフォーマットによる構造化出力の生成

このユースケースでは、OpenAI Responses APIを使用して構造化されたJSON形式の出力を生成する方法を紹介します。

## 概要

Responses APIでは、`text.format`パラメータを使用してモデルの出力形式を指定できます。JSONスキーマを定義することで、特定の構造に従ったJSON形式の応答を得ることができます。これにより：

- アプリケーションで直接利用できる構造化データを取得
- 出力の一貫性と予測可能性を向上
- 複雑な情報の整理と分類を実現
- 後処理の手間を大幅に削減

このサンプルでは、以下の4つの異なる例を通じてJSON出力の可能性を示します：

1. **基本的なJSON出力**: シンプルな情報をJSON形式に変換
2. **製品情報の構造化**: テキスト説明から製品情報を抽出し構造化
3. **イベントスケジュールの構造化**: 複数のイベント情報をJSONオブジェクトの配列として整理
4. **感情分析の構造化**: レビューテキストの感情分析結果を構造化

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

このスクリプトを実行すると、4つの例が順番に実行され、それぞれ異なる形式のJSON出力が生成されます。

### 例1: 基本的なJSON出力

```json
{
  "名前": "山田太郎",
  "年齢": 35,
  "職業": "ソフトウェアエンジニア"
}
```

### 例2: 製品情報（スキーマ適用）

```json
{
  "product_name": "TechX Pro",
  "price": 98000,
  "release_date": "2024-05-15",
  "features": [
    "高性能カメラ（5000万画素）",
    "大容量バッテリー（5000mAh）",
    "高速プロセッサ（Snapdragon 8 Gen 3）",
    "防水防塵対応（IP68）"
  ]
}
```

### 例3: イベントスケジュール（配列形式）

```json
{
  "events": [
    {
      "title": "AIの最新動向",
      "date": "2024-06-10",
      "start_time": "14:00",
      "end_time": "16:00",
      "location": "テックハブ東京（渋谷区）",
      "fee": 3000,
      "required_items": [],
      "optional_items": ["ノートPC"]
    },
    {
      "title": "実践的機械学習",
      "date": "2024-06-15",
      "start_time": "10:00",
      "end_time": "17:00",
      "location": "デジタルスクエア大阪",
      "fee": 12000,
      "required_items": ["ノートPC", "USBメモリ"],
      "optional_items": []
    },
    {
      "title": "APIの活用法",
      "date": "2024-06-20",
      "start_time": "19:00",
      "end_time": "20:30",
      "location": "Zoom（リンクは申込後に送付）",
      "fee": 0,
      "required_items": [],
      "optional_items": []
    }
  ]
}
```

### 例4: 感情分析（ネスト構造）

```json
{
  "sentiment": {
    "overall_rating": 4,
    "overall_sentiment": "positive"
  },
  "aspects": [
    {
      "aspect": "インターフェース",
      "sentiment": "very_positive",
      "text_snippet": "非常に使いやすいインターフェースで気に入っています"
    },
    {
      "aspect": "検索機能",
      "sentiment": "positive",
      "text_snippet": "特に検索機能が素晴らしいです"
    },
    {
      "aspect": "安定性",
      "sentiment": "negative",
      "text_snippet": "最近のアップデート後に時々クラッシュする問題があり"
    }
  ],
  "key_points": {
    "positive": [
      "使いやすいインターフェース",
      "優れた検索機能と通知設定",
      "友人に勧めたいと思えるレベル"
    ],
    "negative": [
      "時々クラッシュする問題"
    ]
  }
}
```

## JSONスキーマの構造

Responses APIでJSONフォーマットの出力を指定するには、以下のようなパラメータを設定します：

```python
client.responses.create(
    model="gpt-4o",
    input=prompt,
    text={
        "format": {
            "type": "json_schema",
            "name": "response_format",  # nameパラメータは必須
            "schema": {
                "type": "object",
                "additionalProperties": False,  # 追加のプロパティを禁止
                "properties": {
                    # プロパティ定義
                }
            }
        }
    }
)
```

JSONスキーマは以下の要素で構成されます：

- `type`: データ型（"object", "array", "string", "number", "integer", "boolean"）
- `additionalProperties`: falseを指定して追加のプロパティを禁止（必須）
- `properties`: オブジェクトのプロパティ定義
- `items`: 配列の項目定義
- `description`: プロパティの説明
- `required`: 必須プロパティのリスト
- `enum`: 列挙型の定義
- その他の制約（minimum, maximum, patternなど）

## サンプル例の詳細

### 例1: 基本的なJSON出力

シンプルな情報を構造化されたJSON形式で出力します。この例では特別なスキーマは使用せず、`json_object`タイプを指定するだけで、モデルが適切なJSON形式で応答します。

**実装方法**:
```python
payload = {
    "model": "gpt-4o",
    "input": prompt,
    "text": {"format": {"type": "json_object"}},
    "max_output_tokens": 150,
}
```

### 例2: 製品情報の構造化

製品の説明テキストから、名前、価格、発売日、機能リストなどの情報を抽出し、一貫した構造で返します。

**主なスキーマ要素**:
- 基本的なオブジェクト構造
- 文字列、数値、配列の組み合わせ
- 必須フィールドの指定

**スキーマ例**:
```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "product_name": { "type": "string" },
    "price": { "type": "number" },
    "release_date": { "type": "string", "format": "date" },
    "features": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["product_name", "price", "release_date", "features"]
}
```

### 例3: イベントスケジュールの構造化

複数の会議・イベント情報を含むテキストから、日時、場所、参加費などの情報を抽出し、イベントの配列として構造化します。

**主なスキーマ要素**:
- オブジェクトの配列
- 日付と時間の標準フォーマット
- 条件付きフィールド（持ち物など）

**配列スキーマの一部**:
```json
"events": {
  "type": "array",
  "items": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "title": { "type": "string" },
      "date": { "type": "string", "format": "date" },
      "start_time": { "type": "string" }
      // 他のプロパティ...
    }
  }
}
```

### 例4: 感情分析の構造化

レビューテキストの感情分析結果を、全体評価、各側面の評価、ポジティブ/ネガティブなポイントなど、構造化された形式で返します。

**主なスキーマ要素**:
- ネストされたオブジェクトと配列
- 列挙型（enum）を使った制限付き値
- 数値範囲の指定（感情スコア）

**感情スキーマの一部**:
```json
"sentiment": {
  "type": "object",
  "properties": {
    "overall_rating": {
      "type": "number",
      "minimum": 1,
      "maximum": 5
    },
    "overall_sentiment": {
      "type": "string",
      "enum": ["very_negative", "negative", "neutral", "positive", "very_positive"]
    }
  }
}
```

## 応用例

構造化JSON出力は以下のような用途に適しています：

1. **データ抽出・変換**: 非構造化テキストからの情報抽出
2. **API連携**: 他のシステムやAPIと連携するためのデータ形式
3. **データベース登録**: 抽出した情報を直接データベースに保存
4. **レポート生成**: 分析結果の構造化された表現
5. **カスタムUI向けデータ**: フロントエンドでの表示に適した形式

## 実装上の注意点

- スキーマが複雑になりすぎると、モデルの出力精度が低下する場合があります
- 出力は常にスキーマに完全に準拠するとは限らないため、バリデーションが重要です
  - このサンプルでは `jsonschema` ライブラリを使用してバリデーションを実装しています
- 重要な情報については、`required`属性を使用して必須フィールドに指定しましょう
- 複雑なスキーマでは、わかりやすい`description`を添えることで精度が向上します
- Responses APIの最新仕様では、以下の2点が必須となっています：
  - `text.format.name`パラメータ（スキーマを使用する場合）
  - すべてのオブジェクトタイプに`additionalProperties: false`を設定（定義されていないプロパティを禁止するため）
- ネストされたオブジェクトにも`additionalProperties: false`を設定する必要があります
- スキーマの構造を適切に設計することで、より整形された一貫性のある結果が得られます

## 追加リソース

- [OpenAI Responses API ドキュメント](https://platform.openai.com/docs/api-reference/responses)
- [OpenAI JSON形式の指定](https://platform.openai.com/docs/api-reference/responses/object#format)
- [JSON Schema 公式ドキュメント](https://json-schema.org/learn/getting-started-step-by-step)
- [JSONスキーマバリデーション ライブラリ](https://github.com/python-jsonschema/jsonschema)

## 主な実装ポイント

1. **JSON出力タイプの指定方法**:
   - 単純なJSON出力: `"text": {"format": {"type": "json_object"}}`
   - スキーマを使用したJSON出力: `"text": {"format": {"type": "json_schema", "name": "response_format", "schema": schema}}`

2. **スキーマ定義のポイント**:
   - すべてのオブジェクトに `"additionalProperties": false` を設定する
   - `"name"` パラメータを必ず指定する
   - 明確な `"description"` を添えることでモデルの理解を助ける
   - ネスト構造でも各レベルで `"additionalProperties": false` を設定する

3. **スキーマデザインのベストプラクティス**:
   - **シンプルに保つ**: スキーマは必要な構造だけにとどめる
   - **明確な制約**: 数値範囲、文字列の形式、列挙型などで出力を制限
   - **階層構造**: 複雑な情報は入れ子構造で整理
   - **必須項目**: `required` で重要なフィールドを指定

4. **エラーハンドリング**:
   - APIレスポンスのステータスコードをチェック
   - JSONバリデーションを実装して出力を検証
   - 出力が期待通りでない場合のフォールバック処理を考慮