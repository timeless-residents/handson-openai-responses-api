"""
OpenAI Responses API - ユースケース012: 複数画像の分析と比較

このスクリプトは、OpenAI Responses APIを使用して複数の画像を同時に分析し、
それらの間の関係、パターン、相違点を詳細に比較する方法を示します。
バッチ処理、系統的な比較、特殊なユースケースなどを実演します。
"""

import os
import sys
import json
import base64
from pathlib import Path
import requests
from dotenv import load_dotenv
import openai
from collections import defaultdict

# 表形式出力用（インストールされている場合のみインポート）
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False

# 画像処理用のライブラリ（インストールされている場合のみインポート）
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def setup_environment():
    """環境設定を行い、APIキーを取得します。"""
    # プロジェクトルートへのパスを追加
    root_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(root_path)

    # プロジェクトルートの.envファイルから環境変数を読み込む
    load_dotenv(os.path.join(root_path, ".env"))

    # OpenAI API キーを環境変数から取得
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 環境変数が設定されていません")

    return api_key


def encode_image_to_base64(image_path):
    """画像ファイルをBase64にエンコードします。

    Args:
        image_path (str): ローカル画像ファイルのパス

    Returns:
        str: Base64エンコードされた画像データ
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def prepare_images_from_directory(dir_path, max_images=5):
    """ディレクトリから画像ファイルを準備します。

    Args:
        dir_path (str): 画像ディレクトリのパス
        max_images (int, optional): 最大画像数

    Returns:
        list: 画像ファイルパスのリスト
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    image_files = []
    
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file_path)
            
    # 最大画像数を制限
    return image_files[:max_images]


def get_image_metadata(image_path):
    """画像のメタデータを取得します。

    Args:
        image_path (str): 画像ファイルのパス

    Returns:
        dict: 画像のメタデータ
    """
    metadata = {
        "filename": os.path.basename(image_path),
        "path": image_path,
        "size_bytes": os.path.getsize(image_path),
    }
    
    if PIL_AVAILABLE:
        try:
            with Image.open(image_path) as img:
                metadata["format"] = img.format
                metadata["mode"] = img.mode
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["aspect_ratio"] = round(img.width / img.height, 2)
        except Exception as e:
            print(f"画像メタデータの取得に失敗しました: {e}")
    
    return metadata


def analyze_multiple_images(client, image_paths, prompt):
    """複数の画像を分析します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_paths (list): 画像ファイルパスのリスト
        prompt (str): 分析指示

    Returns:
        dict: APIからの応答
    """
    # 入力形式を構築
    content = [{"type": "text", "text": prompt}]
    
    # 画像を追加
    for path in image_paths:
        print(f"画像を追加: {os.path.basename(path)}")
        base64_image = encode_image_to_base64(path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })
    
    # APIリクエスト
    print(f"{len(image_paths)}枚の画像を分析中...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}]
    )
    
    # レスポンスフォーマットを調整
    return {
        "id": response.id,
        "model": response.model,
        "created_at": response.created,
        "output_text": response.choices[0].message.content,
        "usage": response.usage
    }


def generate_comparative_analysis(client, image_paths, criteria_list):
    """複数の画像を指定された基準で比較分析します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_paths (list): 画像ファイルパスのリスト
        criteria_list (list): 比較基準のリスト

    Returns:
        dict: APIからの応答（JSON形式の比較表を含む）
    """
    # 基準をJSON文字列に変換
    criteria_json = json.dumps(criteria_list)
    
    # 比較プロンプトの作成
    prompt = f"""
    以下の画像を詳細に比較分析してください。
    
    比較基準:
    {criteria_json}
    
    各比較基準について、すべての画像を評価し、比較してください。
    
    結果は以下のJSON形式で出力してください:
    ```json
    {{
      "comparison_table": [
        {{
          "criteria": "基準名",
          "image1": "画像1の評価",
          "image2": "画像2の評価",
          ...
        }},
        ...
      ],
      "overall_analysis": "全体的な比較分析の要約",
      "unique_features": [
        "画像固有の特徴1",
        "画像固有の特徴2",
        ...
      ]
    }}
    ```
    
    必ずJSONフォーマットで出力してください。
    """
    
    # 分析の実行
    response = analyze_multiple_images(client, image_paths, prompt)
    
    return response


def detect_patterns_across_images(client, image_paths):
    """複数画像間の共通パターンを検出します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_paths (list): 画像ファイルパスのリスト

    Returns:
        dict: APIからの応答
    """
    prompt = """
    これらの画像を注意深く分析し、以下の点を特定してください：
    
    1. すべての画像に共通する視覚的要素やパターン
    2. 画像の一部に見られる繰り返しパターン
    3. 色彩、構図、テーマなどの共通点
    4. これらの画像がどのようなカテゴリーやコレクションに属するか
    5. 画像間の関連性や連続性
    
    回答は、見つかったパターンの種類ごとに整理し、具体的な詳細を含めてください。
    """
    
    return analyze_multiple_images(client, image_paths, prompt)


def perform_style_content_analysis(client, image_paths):
    """複数画像のスタイルとコンテンツを分析します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_paths (list): 画像ファイルパスのリスト

    Returns:
        dict: APIからの応答
    """
    prompt = """
    これらの画像について、スタイル（表現方法）とコンテンツ（被写体・題材）を分離して分析してください。
    
    各画像について：
    1. スタイル特性：色使い、構図技法、光の使い方、テクスチャ、視覚的効果
    2. コンテンツ要素：主題、被写体、物語性、象徴的意味
    
    さらに、これらの画像間でのスタイルとコンテンツの関係性を分析し、以下の点に回答してください：
    - スタイルの類似点と相違点
    - コンテンツの類似点と相違点
    - 特に際立つスタイル・コンテンツの特徴
    
    回答は体系的に整理し、各画像を参照しながら具体的な詳細を含めてください。
    """
    
    return analyze_multiple_images(client, image_paths, prompt)


def display_image_metadata(image_paths):
    """画像のメタデータを表形式で表示します。

    Args:
        image_paths (list): 画像ファイルパスのリスト
    """
    metadata_list = [get_image_metadata(path) for path in image_paths]
    
    print("\n===== 画像メタデータ =====")
    
    if TABULATE_AVAILABLE:
        # Tabulateライブラリが利用可能な場合は表形式で表示
        headers = {
            "filename": "ファイル名",
            "size_bytes": "サイズ(バイト)",
            "format": "フォーマット",
            "width": "幅(px)",
            "height": "高さ(px)",
            "aspect_ratio": "アスペクト比"
        }
        
        table_data = []
        for meta in metadata_list:
            row = []
            for key in ["filename", "size_bytes", "format", "width", "height", "aspect_ratio"]:
                row.append(meta.get(key, "N/A"))
            table_data.append(row)
        
        print(tabulate(table_data, headers=headers.values(), tablefmt="grid"))
    else:
        # 表形式ライブラリがなければシンプルに表示
        for i, meta in enumerate(metadata_list):
            print(f"\n画像 {i+1}: {meta.get('filename')}")
            for key, value in meta.items():
                if key != "path" and key != "filename":
                    print(f"  {key}: {value}")
    
    print("==========================\n")


def display_response(response, title=None):
    """APIからの応答を整形して表示します。

    Args:
        response (dict): APIからの応答オブジェクト
        title (str, optional): 表示するタイトル
    """
    if title:
        print(f"\n===== {title} =====")
    else:
        print("\n===== 分析結果 =====")
        
    print(f"Model: {response['model']}")
    print(f"Response ID: {response['id']}")
    
    print("\n--- 出力テキスト ---")
    print(response['output_text'])
    print("-------------------")

    print(f"\nToken Usage:")
    print(f"  Input tokens: {response['usage'].prompt_tokens}")
    print(f"  Output tokens: {response['usage'].completion_tokens}")
    print(f"  Total tokens: {response['usage'].total_tokens}")
    
    if title:
        print("=" * (len(title) + 12))
    else:
        print("====================")


def extract_json_from_response(text):
    """レスポンステキストからJSONを抽出します。

    Args:
        text (str): レスポンステキスト

    Returns:
        dict: 抽出されたJSONオブジェクト
    """
    try:
        # コードブロック内のJSONを探す
        if "```json" in text and "```" in text.split("```json", 1)[1]:
            json_text = text.split("```json", 1)[1].split("```", 1)[0].strip()
            return json.loads(json_text)
        
        # コードブロックがない場合は全体をJSONとして解析
        return json.loads(text)
    except Exception as e:
        print(f"JSONの抽出に失敗しました: {e}")
        return None


def display_comparison_table(comparison_data, image_paths):
    """比較データを表形式で表示します。

    Args:
        comparison_data (dict): 比較データ
        image_paths (list): 画像ファイルパスのリスト
    """
    if not comparison_data or "comparison_table" not in comparison_data:
        print("比較データがありません")
        return
    
    print("\n===== 画像比較表 =====")
    
    # 画像ファイル名のリスト
    image_names = [os.path.basename(path) for path in image_paths]
    
    if TABULATE_AVAILABLE:
        # Tabulateライブラリが利用可能な場合は表形式で表示
        headers = ["比較基準"] + [f"画像{i+1}: {name}" for i, name in enumerate(image_names)]
        
        table_data = []
        for row in comparison_data["comparison_table"]:
            table_row = [row["criteria"]]
            for i in range(len(image_names)):
                img_key = f"image{i+1}"
                table_row.append(row.get(img_key, "N/A"))
            table_data.append(table_row)
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        # 表形式ライブラリがなければシンプルに表示
        for row in comparison_data["comparison_table"]:
            print(f"\n基準: {row['criteria']}")
            for i in range(len(image_names)):
                img_key = f"image{i+1}"
                if img_key in row:
                    print(f"  画像{i+1} ({image_names[i]}): {row[img_key]}")
    
    print("\n--- 全体分析 ---")
    if "overall_analysis" in comparison_data:
        print(comparison_data["overall_analysis"])
    
    print("\n--- 固有の特徴 ---")
    if "unique_features" in comparison_data:
        for feature in comparison_data["unique_features"]:
            print(f"- {feature}")
    
    print("=====================\n")


def run_basic_comparative_analysis(client, image_dir):
    """基本的な比較分析を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_dir (str): 画像ディレクトリのパス
    """
    print("\n# 例1: 基本的な画像比較分析")
    
    # 画像ファイルパスの取得
    image_paths = prepare_images_from_directory(image_dir)
    
    if len(image_paths) < 2:
        print("比較に必要な画像が足りません")
        return
    
    # 画像メタデータの表示
    display_image_metadata(image_paths)
    
    # 比較基準の定義
    criteria = [
        "視覚的要素（色彩、構図、主な被写体）",
        "伝達される雰囲気や感情",
        "想定される用途や目的",
        "技術的品質（解像度、明瞭さ、バランス）",
        "視聴者へのインパクトと印象"
    ]
    
    # 比較分析の実行
    response = generate_comparative_analysis(client, image_paths, criteria)
    
    # 結果表示
    display_response(response, "基本的な比較分析結果")
    
    # JSONデータの抽出と表示
    json_data = extract_json_from_response(response["output_text"])
    if json_data:
        display_comparison_table(json_data, image_paths)
    
    return response


def run_pattern_detection(client, image_dir):
    """画像間のパターン検出を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_dir (str): 画像ディレクトリのパス
    """
    print("\n# 例2: 画像間のパターン検出")
    
    # 画像ファイルパスの取得
    image_paths = prepare_images_from_directory(image_dir)
    
    if len(image_paths) < 2:
        print("パターン検出に必要な画像が足りません")
        return
    
    # パターン検出の実行
    response = detect_patterns_across_images(client, image_paths)
    
    # 結果表示
    display_response(response, "パターン検出結果")
    
    return response


def run_style_content_separation(client, image_dir):
    """スタイルとコンテンツの分離分析を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_dir (str): 画像ディレクトリのパス
    """
    print("\n# 例3: スタイルとコンテンツの分離分析")
    
    # 画像ファイルパスの取得
    image_paths = prepare_images_from_directory(image_dir)
    
    if len(image_paths) < 2:
        print("スタイル分析に必要な画像が足りません")
        return
    
    # スタイル・コンテンツ分析の実行
    response = perform_style_content_analysis(client, image_paths)
    
    # 結果表示
    display_response(response, "スタイル・コンテンツ分析結果")
    
    return response


def run_specialized_use_case(client, image_dir):
    """特殊なユースケース（芸術作品分析）を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_dir (str): 画像ディレクトリのパス
    """
    print("\n# 例4: 特殊なユースケース（芸術分析）")
    
    # 画像ファイルパスの取得
    image_paths = prepare_images_from_directory(image_dir)
    
    if len(image_paths) < 2:
        print("分析に必要な画像が足りません")
        return
    
    # 芸術分析プロンプトの作成
    art_prompt = """
    美術史の専門家として、これらの画像を分析してください。
    
    各画像について以下の点を評価してください：
    1. 推定される芸術様式や時代
    2. 技法と表現方法の特徴
    3. 構図と視覚要素の配置
    4. 色彩理論の観点からの分析
    5. 芸術的意義と影響
    
    また、これらの作品間の関連性や、芸術の発展における位置づけについても考察してください。
    美術館の展示解説のような、教育的かつ専門的な分析を提供してください。
    """
    
    # 分析の実行
    response = analyze_multiple_images(client, image_paths, art_prompt)
    
    # 結果表示
    display_response(response, "芸術分析結果")
    
    return response


def main():
    """メイン実行関数

    OpenAI Responses APIを使用して、複数画像の分析と比較の例を実行します。
    """
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)
        
        # 画像ディレクトリのパス
        image_dir = os.path.join(os.path.dirname(__file__), "images")
        
        # 例1: 基本的な比較分析
        run_basic_comparative_analysis(client, image_dir)
        
        # 例2: 画像間のパターン検出
        run_pattern_detection(client, image_dir)
        
        # 例3: スタイルとコンテンツの分離分析
        run_style_content_separation(client, image_dir)
        
        # 例4: 特殊なユースケース（芸術分析）
        run_specialized_use_case(client, image_dir)
        
    except Exception as error:
        print(f"エラーが発生しました: {error}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()