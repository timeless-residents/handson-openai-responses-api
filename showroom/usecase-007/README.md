# ユースケース 007: メタデータの活用とレスポンス管理

このユースケースでは、OpenAI Responses APIのメタデータ機能とレスポンス管理手法について紹介します。

## 概要

APIリクエストとレスポンスにメタデータを添付することで、応答の追跡、分類、フィルタリングが容易になります。このサンプルでは、以下のメタデータ活用方法を示します：

1. **リクエストへのメタデータ追加**: `metadata`パラメータを使用してリクエストを分類・整理する方法
2. **レスポンスメタデータの取得**: 応答に含まれるメタデータを取得し処理する方法
3. **メタデータを活用した応答管理**: メタデータによる応答の検索・フィルタリング・分析
4. **ユースケース別メタデータ設計**: 異なるシナリオでのメタデータ設計のベストプラクティス

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

## メタデータの活用例

### リクエストへのメタデータ追加

```python
# ユーザーID、セッションID、カテゴリなどをメタデータとして設定
response = client.responses.create(
    model="gpt-4o",
    input="質問文をここに入力",
    metadata={
        "user_id": "user_12345",
        "session_id": "session_67890",
        "category": "customer_support",
        "locale": "ja-JP",
        "platform": "mobile",
    }
)
```

### レスポンスの取得と管理

```python
# レスポンスのメタデータを取得
print(f"Response ID: {response.id}")
print(f"Metadata: {response.metadata}")
print(f"Created at: {response.created_at}")
```

## 実装例

このサンプルには、メタデータを効果的に活用する4つの異なる実装例が含まれています：

### 1. ユーザー追跡

ユーザーIDやセッション情報をメタデータとして記録し、ユーザーごとの利用状況を追跡します。

```python
user_metadata = {
    "user_id": "user_12345",
    "session_id": str(uuid.uuid4()),
    "user_type": "premium",
    "locale": "ja-JP",
    "platform": "mobile"
}
```

### 2. コンテンツ分類

質問のカテゴリや複雑さをメタデータとして記録し、応答を分類します。

```python
content_metadata = {
    "category": "science",
    "subcategory": "physics",
    "complexity": "beginner",
    "request_type": "definition"
}
```

### 3. ビジネス分析

部門、プロジェクト、コストセンターなどのビジネス情報をメタデータとして記録し、コスト配分や使用状況分析を可能にします。

```python
business_metadata = {
    "department": "marketing",
    "project_id": "campaign_2023_summer",
    "cost_center": "mkt-001",
    "purpose": "content_creation"
}
```

### 4. A/Bテスト

異なるパラメータ設定（温度など）での応答を比較するためのメタデータを記録します。

```python
ab_metadata = {
    "test_id": "prompt_test_001",
    "variant": "A",
    "temperature": "0.2",  # 文字列として格納 (数値は使用不可)
    "description": "低温度での事実ベース応答"
}
```

## メタデータ設計のベストプラクティス

メタデータは以下のような情報を含めると有用です：

1. **識別情報**:
   - ユーザーID
   - セッションID
   - リクエスト固有ID

2. **カテゴリ情報**:
   - 会話カテゴリ（サポート、販売など）
   - 応答のタイプ（質問、回答、エラーなど）
   - コンテンツの言語や地域

3. **トラッキング情報**:
   - ソースアプリケーション
   - デバイスタイプ
   - タイムスタンプ

4. **ビジネス情報**:
   - 部門コード
   - プロジェクトID
   - コスト中心

## 応用例

メタデータを活用した実用的なシナリオ：

1. **分析ダッシュボード**: 会話カテゴリごとのAPI使用状況を追跡
2. **費用配分**: 部門やプロジェクト別にAPIコストを割り当て
3. **A/Bテスト**: 異なるバージョンのプロンプトやパラメータの効果を比較
4. **品質管理**: 特定のユーザーセグメントの応答品質をモニタリング
5. **応答検索**: 膨大な応答データから特定の条件に合うものを検索

## 実装上の注意点

- メタデータは文字列または整数のキーと値のペアである必要があります（浮動小数点数は文字列に変換する必要があります）
- メタデータのキーと値は英数字とアンダースコアのみを使用することが推奨されます
- メタデータのサイズには制限があるため、簡潔に保つことが重要です
- センシティブな個人情報をメタデータに含めないよう注意してください
- メタデータの一貫した命名規則を使用すると、後の分析が容易になります
- レスポンスの検索・フィルタリングが効率的になるようメタデータを設計してください

## 追加リソース

- [OpenAI Responses APIドキュメント](https://platform.openai.com/docs/api-reference/responses)
- [OpenAI メタデータガイド](https://platform.openai.com/docs/api-reference/responses/create#metadata)