# OpenAI Responses API ハンズオン

このリポジトリは、OpenAI Responses APIを利用するための実践的なサンプルコードを提供します。Responses APIは、OpenAIの最も高度なインターフェースであり、テキストや画像の入力、テキスト出力をサポートしています。

## 目次

- [環境構築](#環境構築)
- [使い方](#使い方)
- [ユースケース](#ユースケース)
- [ライセンス](#ライセンス)

## 環境構築

### 前提条件

- Python 3.9以上
- OpenAI APIキー

### インストール

リポジトリをクローンし、必要なパッケージをインストールします。

```bash
# リポジトリをクローン
git clone https://github.com/timeless-residents/handson-openai-responses-api.git
cd handson-openai-responses-api

# 仮想環境を作成して有効化
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r showroom/usecase-000/requirements.txt
```

### 環境変数の設定

プロジェクトのルートディレクトリに `.env` ファイルを作成し、OpenAI APIキーを設定します。

```
OPENAI_API_KEY=your_api_key_here
```

## 使い方

各ユースケースは `showroom` ディレクトリ内にあります。それぞれのユースケースフォルダ内の説明に従って実行してください。

### 基本的な例（usecase-000）

最も基本的なAPIの使用例は以下のコマンドで実行できます：

```bash
python showroom/usecase-000/main.py
```

## ユースケース

このリポジトリには以下のユースケースが含まれています：

- **usecase-000**: 基本的なテキスト応答の生成
- *(今後追加予定)*

## ライセンス

このプロジェクトは [MIT License](LICENSE) のもとで公開されています。