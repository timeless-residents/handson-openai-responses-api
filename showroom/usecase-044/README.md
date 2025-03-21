# バリアフリー情報アクセス支援

このアプリケーションは、OpenAI Responses APIを活用して、バリアフリー施設や情報へのアクセスを支援します。ユーザーの質問に応じて、バリアフリー施設の情報、アクセス方法、利用方法などを提供します。

## セットアップ

1. 必要なパッケージをインストールします:
```
pip install -r requirements.txt
```

2. `.env`ファイルを作成し、OpenAI APIキーを設定します:
```
OPENAI_API_KEY=your_api_key_here
```

3. アプリケーションを実行します:
```
python main.py
```

4. ブラウザで http://localhost:5000 にアクセスします。

## 機能

- バリアフリー施設に関する情報の検索と提供
- アクセシビリティ情報の構造化されたJSON形式での取得
- シンプルで使いやすいウェブインターフェース
- 音声読み上げ機能によるアクセシビリティ向上