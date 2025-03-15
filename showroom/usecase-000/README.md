# ユースケース 000: 基本的なテキスト応答生成

このユースケースは、OpenAI Responses APIを使用して基本的なテキスト応答を生成する最小限の実装例です。

## 概要

このサンプルでは、以下の機能を示しています：

- OpenAI APIクライアントの初期化
- Responses APIを使用した単純なテキスト入力と出力
- レスポンスの結果表示とトークン使用量の確認

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

## コード説明

`main.py`は以下の主要な機能で構成されています：

1. **環境設定**: .envファイルからAPIキーを読み込み、環境を設定します
2. **API呼び出し**: Responses APIを使用してテキスト応答を生成します
3. **結果表示**: 応答結果とトークン使用量を表示します

## カスタマイズ

以下の部分をカスタマイズして、異なる応答を生成できます：

- 入力テキスト: `prompt` 変数の内容を変更します
- モデル: `model` パラメータを変更します（例: "gpt-4o", "gpt-4o-mini"など）
- 応答オプション: 追加のパラメータを指定して応答の生成方法をカスタマイズできます

例:

```python
response = client.responses.create(
    model="gpt-4o-mini",
    input="Hello, can you explain quantum computing in simple terms?",
    temperature=0.7,  # 応答のランダム性を調整
    max_output_tokens=100  # 出力トークン数の上限を設定
)
```

## 応用例

このサンプルを拡張して、以下のような機能を追加できます：

- 対話的なチャットボットの作成
- ファイルからの入力テキスト読み込み
- 複数の質問に対する一括応答生成