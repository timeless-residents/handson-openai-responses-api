# ユースケース 021: ファイル検索ツールの活用

このユースケースでは、OpenAI Responses APIを使用したファイル検索ツールの実装方法を紹介します。

## 概要

AIが大量のファイルやドキュメントを検索して情報を抽出する能力は、知識管理や意思決定支援に大きな価値をもたらします。このサンプルでは、Responses APIとツール呼び出し機能を使用して、ローカルファイルシステム内のファイル検索と情報抽出を行う方法を示します。

このサンプルでは、以下の機能を紹介しています：

- ファイル検索ツールの定義と実装
- ファイルパターンに基づく検索機能
- ファイル内容のキーワード検索機能
- 検索結果の要約と分析
- 複数ファイルのコンテキスト理解と情報統合

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
   - ファイル名パターンによる検索
   - キーワードによる検索
   - 複合検索と分析

## ファイル検索ツールの定義

Responses APIのツール機能を使用して、カスタムファイル検索ツールを定義します：

```python
# ファイル検索ツールの定義
file_search_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_files_by_pattern",
            "description": "指定されたディレクトリ内でファイル名パターンに一致するファイルを検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "検索を開始するディレクトリパス"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "検索するファイル名パターン（*.py, *.txt など）"
                    }
                },
                "required": ["directory", "pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_content_by_keyword",
            "description": "指定されたディレクトリ内のファイルからキーワードを検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "検索を開始するディレクトリパス"
                    },
                    "keyword": {
                        "type": "string",
                        "description": "検索するキーワードまたは正規表現パターン"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "検索対象のファイル種類（*.py, *.txt など）"
                    }
                },
                "required": ["directory", "keyword"]
            }
        }
    }
]
```

## ファイル検索の実装

ツールの機能は以下のように実装されます：

```python
def search_files_by_pattern(directory, pattern):
    """指定されたディレクトリ内でファイル名パターンに一致するファイルを検索します。
    
    Args:
        directory (str): 検索を開始するディレクトリパス
        pattern (str): 検索するファイル名パターン（*.py, *.txt など）
        
    Returns:
        list: 見つかったファイルのリスト
    """
    import glob
    import os
    
    # ディレクトリが存在するか確認
    if not os.path.exists(directory):
        return {"error": f"ディレクトリが見つかりません: {directory}"}
    
    # ファイル検索
    search_path = os.path.join(directory, pattern)
    files = glob.glob(search_path, recursive=True)
    
    return {
        "count": len(files),
        "files": files
    }

def search_content_by_keyword(directory, keyword, file_pattern="*"):
    """指定されたディレクトリ内のファイルからキーワードを検索します。
    
    Args:
        directory (str): 検索を開始するディレクトリパス
        keyword (str): 検索するキーワードまたは正規表現パターン
        file_pattern (str, optional): 検索対象のファイル種類. デフォルトは "*"
        
    Returns:
        dict: 検索結果を含む辞書
    """
    import glob
    import os
    import re
    
    # ディレクトリが存在するか確認
    if not os.path.exists(directory):
        return {"error": f"ディレクトリが見つかりません: {directory}"}
    
    # ファイルリストを取得
    search_path = os.path.join(directory, file_pattern)
    files = glob.glob(search_path, recursive=True)
    
    results = []
    
    # 各ファイルでキーワード検索
    for file_path in files:
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = re.finditer(keyword, content)
                    
                    file_matches = []
                    for match in matches:
                        # マッチの前後のコンテキストを取得
                        start = max(0, match.start() - 50)
                        end = min(len(content), match.end() + 50)
                        context = content[start:end]
                        
                        file_matches.append({
                            "match": match.group(),
                            "position": match.start(),
                            "context": context
                        })
                    
                    if file_matches:
                        results.append({
                            "file": file_path,
                            "matches": file_matches
                        })
            except Exception as e:
                # ファイル読み込みエラーをスキップ
                continue
    
    return {
        "count": len(results),
        "results": results
    }
```

## AIによる検索結果の分析

Responses APIを使用して、検索結果をAIに分析させることができます：

```python
def analyze_search_results(client, search_results):
    """検索結果をAIに分析させます。
    
    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        search_results (dict): 検索結果
        
    Returns:
        dict: 分析結果
    """
    # 検索結果をJSON文字列に変換
    results_str = json.dumps(search_results, indent=2)
    
    # 分析リクエスト
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "system",
                "content": "あなたはファイル検索結果を分析するエキスパートです。提供された検索結果を詳細に分析し、重要な情報、パターン、関連性を特定してください。"
            },
            {
                "role": "user",
                "content": f"以下の検索結果を分析し、主要な発見事項と洞察をまとめてください:\n\n{results_str}"
            }
        ]
    )
    
    return {
        "analysis": response.output_text
    }
```

## 複合検索シナリオ

このサンプルでは、複数の検索機能を組み合わせた複合検索シナリオも実装しています：

1. まずパターンでファイルを検索
2. 見つかったファイル内でキーワード検索
3. 検索結果をAIで分析・要約

```python
# 複合検索フロー
file_matches = search_files_by_pattern(directory, "*.py")
content_matches = []

for file in file_matches["files"]:
    result = search_content_by_keyword(file, keyword)
    if result["count"] > 0:
        content_matches.append(result)

# 分析
analysis = analyze_search_results(client, content_matches)
```

## 応用例

この機能は以下のような用途に応用できます：

1. **コードベースの分析**: 大規模プロジェクトのコード解析と理解
2. **ドキュメント検索**: 社内文書やマニュアルから必要な情報を素早く抽出
3. **パターン特定**: 複数ファイル間の関連性やパターンの識別
4. **データ監査**: コードやファイルのセキュリティ監査や品質チェック
5. **トラブルシューティング**: システム全体に渡る問題の原因特定

## 制限事項と考慮点

- 大量のファイルや大きなファイルの検索は処理時間とリソースを消費します
- バイナリファイルやエンコードの異なるファイルの処理には注意が必要です
- 機密情報を含むファイルを扱う場合はセキュリティ対策を検討してください
- 複雑な検索パターンやコンテキスト理解には、検索結果のポストプロセッシングが必要な場合があります
- APIの使用には料金が発生します（特に大量のテキスト処理を行う場合）

## 追加リソース

- [OpenAI Tools Documentation](https://platform.openai.com/docs/guides/function-calling)
- [Python glob モジュール](https://docs.python.org/3/library/glob.html)
- [Python re モジュール（正規表現）](https://docs.python.org/3/library/re.html)
- [Responses API Reference](https://platform.openai.com/docs/api-reference/responses)