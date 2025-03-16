"""
OpenAI Responses API でファイル検索ツールを実装したサンプル

このスクリプトは、OpenAI Responses APIを使ってファイル検索ツールを
実装したサンプルです。ファイルパターン検索とキーワード検索機能を提供します。
"""

import os
import sys
import glob
import json
import re
from dotenv import load_dotenv
import openai
from datetime import datetime


def setup_environment():
    """環境設定を行い、APIキーを取得します。"""
    # プロジェクトルートのパスを設定し、.envからAPIキーを読み込む
    root_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(root_path)
    load_dotenv(os.path.join(root_path, ".env"))
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 環境変数が設定されていません")
    
    return api_key


def search_files_by_pattern(directory, pattern):
    """指定されたディレクトリ内でファイル名パターンに一致するファイルを検索します。
    
    Args:
        directory (str): 検索を開始するディレクトリパス
        pattern (str): 検索するファイル名パターン（*.py, *.txt など）
        
    Returns:
        dict: 見つかったファイルのリスト
    """
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


def display_file_search_results(results):
    """ファイル検索結果を表示します。
    
    Args:
        results (dict): 検索結果
    """
    print(f"\n===== ファイル検索結果 =====")
    
    if "error" in results:
        print(f"エラー: {results['error']}")
        return
    
    print(f"見つかったファイル数: {results['count']}")
    
    if results['count'] > 0:
        print("\n見つかったファイル:")
        for i, file in enumerate(results['files'], 1):
            print(f"{i}. {file}")
    else:
        print("条件に一致するファイルは見つかりませんでした。")
    
    print("=======================")


def display_content_search_results(results):
    """コンテンツ検索結果を表示します。
    
    Args:
        results (dict): 検索結果
    """
    print(f"\n===== コンテンツ検索結果 =====")
    
    if "error" in results:
        print(f"エラー: {results['error']}")
        return
    
    print(f"キーワードが見つかったファイル数: {results['count']}")
    
    if results['count'] > 0:
        for i, result in enumerate(results['results'], 1):
            print(f"\nファイル {i}: {result['file']}")
            print(f"  ヒット数: {len(result['matches'])}")
            
            for j, match in enumerate(result['matches'], 1):
                print(f"  マッチ {j}:")
                print(f"    位置: {match['position']}")
                print(f"    マッチ: {match['match']}")
                print(f"    コンテキスト: ...{match['context']}...")
                if j < len(result['matches']):
                    print("    ------")
    else:
        print("キーワードに一致する内容は見つかりませんでした。")
    
    print("===========================")


def display_analysis_results(analysis):
    """分析結果を表示します。
    
    Args:
        analysis (dict): 分析結果
    """
    print(f"\n===== 分析結果 =====")
    print(analysis["analysis"])
    print("===================")


def demo_pattern_search():
    """ファイルパターン検索のデモを実行します。"""
    print("\n===== ファイルパターン検索デモ =====")
    print("検索を開始するディレクトリのパスを入力してください:")
    directory = input("> ")
    
    print("検索するファイル名パターンを入力してください (例: *.py, *.txt):")
    pattern = input("> ")
    
    print("検索を実行中...")
    results = search_files_by_pattern(directory, pattern)
    display_file_search_results(results)
    
    return results


def demo_keyword_search():
    """キーワード検索のデモを実行します。"""
    print("\n===== キーワード検索デモ =====")
    print("検索を開始するディレクトリのパスを入力してください:")
    directory = input("> ")
    
    print("検索するキーワードを入力してください:")
    keyword = input("> ")
    
    print("検索対象のファイル種類を入力してください (例: *.py, *.txt, デフォルト: *):")
    file_pattern = input("> ").strip() or "*"
    
    print("検索を実行中...")
    results = search_content_by_keyword(directory, keyword, file_pattern)
    display_content_search_results(results)
    
    return results


def demo_combined_search(client):
    """複合検索と分析のデモを実行します。"""
    print("\n===== 複合検索と分析デモ =====")
    print("このデモでは、以下の手順を実行します:")
    print("1. ファイルパターンで対象ファイルを検索")
    print("2. 見つかったファイル内でキーワード検索")
    print("3. 検索結果をAIで分析・要約")
    
    print("\nステップ1: 検索を開始するディレクトリのパスを入力してください:")
    directory = input("> ")
    
    print("検索するファイル名パターンを入力してください (例: *.py, *.txt):")
    pattern = input("> ")
    
    print("ファイル検索を実行中...")
    file_results = search_files_by_pattern(directory, pattern)
    display_file_search_results(file_results)
    
    if "error" in file_results or file_results["count"] == 0:
        print("ファイルが見つからないため、検索を終了します。")
        return
    
    print("\nステップ2: 検索するキーワードを入力してください:")
    keyword = input("> ")
    
    print("コンテンツ検索を実行中...")
    content_results = []
    
    for file in file_results["files"]:
        result = search_content_by_keyword(os.path.dirname(file), keyword, os.path.basename(file))
        if result["count"] > 0:
            content_results.extend(result["results"])
    
    combined_results = {
        "count": len(content_results),
        "results": content_results
    }
    
    display_content_search_results(combined_results)
    
    if combined_results["count"] == 0:
        print("キーワードが見つからないため、分析を終了します。")
        return
    
    print("\nステップ3: 検索結果を分析中...")
    analysis = analyze_search_results(client, combined_results)
    display_analysis_results(analysis)


def setup_file_search_tools():
    """ファイル検索ツールを定義します。
    
    Returns:
        list: ツール定義のリスト
    """
    return [
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


def demo_tool_usage_with_ai(client):
    """AIによるツール使用のデモを実行します。"""
    print("\n===== AIによるツール使用デモ =====")
    print("AIに指示を与えて、ファイル検索ツールを使用させることができます。")
    print("例: 「このプロジェクト内のPythonファイルで、'openai'を含むものを探して分析してください」")
    
    # ツール定義
    tools = setup_file_search_tools()
    
    # ツール実装の辞書
    tool_implementations = {
        "search_files_by_pattern": search_files_by_pattern,
        "search_content_by_keyword": search_content_by_keyword
    }
    
    print("\nAIへの指示を入力してください:")
    user_instruction = input("> ")
    
    print("\nAIと対話を開始します...")
    
    # AIに問い合わせ
    response = client.responses.create(
        model="gpt-4o",
        instructions="あなたはファイル検索と分析を支援するAIアシスタントです。ユーザーの指示に従って、提供されたツールを使用してファイル検索と分析を行ってください。",
        input=user_instruction,
        tools=tools
    )
    
    # 応答を取得して表示
    assistant_content = response.output_text
    print(f"\nAI: {assistant_content}")
    
    # ツール呼び出しのループ
    max_turns = 5  # 最大対話ターン数
    previous_response_id = response.id
    
    for turn in range(max_turns):
        if not response.tool_calls:
            break
        
        tool_outputs = []
        
        for tool_call in response.tool_calls:
            tool_name = tool_call.name
            tool_args = tool_call.arguments
            
            print(f"\n[ツール呼び出し] {tool_name}: {tool_args}")
            
            if tool_name in tool_implementations:
                # ツールの実行
                try:
                    result = tool_implementations[tool_name](**tool_args)
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(result)
                    })
                    
                    if tool_name == "search_files_by_pattern":
                        display_file_search_results(result)
                    elif tool_name == "search_content_by_keyword":
                        display_content_search_results(result)
                        
                except Exception as e:
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"error": str(e)})
                    })
            else:
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps({"error": f"未実装のツール: {tool_name}"})
                })
        
        # ツール呼び出し結果を使って再度リクエスト
        response = client.responses.create(
            model="gpt-4o",
            instructions="あなたはファイル検索と分析を支援するAIアシスタントです。ユーザーの指示に従って、提供されたツールを使用してファイル検索と分析を行ってください。",
            input={
                "type": "tool_results",
                "tool_results": tool_outputs,
                "previous_response_id": previous_response_id
            },
            tools=tools
        )
        
        # 新しい応答を取得して表示
        new_content = response.output_text
        print(f"\nAI: {new_content}")
        
        # 次のループのために更新
        previous_response_id = response.id
        
        if not response.tool_calls:
            break
    
    print("\n対話を終了します。")


def main():
    """メイン関数"""
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)
        
        print("OpenAI Responses API - ファイル検索ツールのデモ")
        
        # 実行モード選択
        print("\n実行モードを選択してください:")
        print("1: ファイル名パターンによる検索")
        print("2: キーワードによる検索")
        print("3: 複合検索と分析")
        print("4: AIによるツール使用")
        
        while True:
            choice = input("選択 (1/2/3/4): ")
            if choice in ['1', '2', '3', '4']:
                break
            print("1、2、3、または4を入力してください。")
        
        if choice == '1':
            demo_pattern_search()
        elif choice == '2':
            demo_keyword_search()
        elif choice == '3':
            demo_combined_search(client)
        else:
            demo_tool_usage_with_ai(client)
        
    except Exception as error:
        print(f"エラーが発生しました: {error}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()