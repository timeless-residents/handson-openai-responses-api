"""
不動産物件の画像分析と説明生成

このサンプルは、OpenAI Responses APIのマルチモーダル機能を使用して、
不動産物件の画像を分析し、魅力的な物件説明を自動生成する方法を示します。
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any, Optional
import glob
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import base64
import io
from dotenv import load_dotenv
import openai


# Python 3.7以降の場合、標準入出力のエンコーディングをUTF-8に設定
if sys.version_info >= (3, 7):
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")


def setup_environment():
    """環境設定を行い、APIキーを取得します。"""
    # プロジェクトのルートディレクトリの.envファイルを読み込む
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(script_dir))
    load_dotenv(os.path.join(root_dir, ".env"))

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY が設定されていません")
    return api_key


def get_image_paths(directory="images"):
    """指定ディレクトリ内の画像ファイルパスを取得します。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(script_dir, directory)

    # 画像ファイルの拡張子
    extensions = ["jpg", "jpeg", "png", "gif"]

    # 画像ファイルを検索
    image_paths = []
    for ext in extensions:
        image_paths.extend(glob.glob(os.path.join(image_dir, f"*.{ext}")))

    # メタデータファイルを除外
    image_paths = [p for p in image_paths if os.path.basename(p) != "metadata.txt"]

    return image_paths


def encode_image_to_base64(image_path):
    """画像をbase64エンコードし、データURIを返します。"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_metadata(image_path):
    """画像のメタデータを取得します（ファイル名、サイズなど）。"""
    filename = os.path.basename(image_path)

    # PILを使用して画像のメタデータを取得
    with Image.open(image_path) as img:
        width, height = img.size
        format = img.format
        mode = img.mode

    # ファイルサイズを取得
    file_size = os.path.getsize(image_path)

    return {
        "filename": filename,
        "width": width,
        "height": height,
        "format": format,
        "mode": mode,
        "file_size": file_size,
        "path": image_path,
    }


def display_image(image_path, title=None):
    """画像を表示します（Jupyter Notebook環境用）。"""
    img = Image.open(image_path)
    plt.figure(figsize=(10, 8))
    plt.imshow(np.array(img))
    if title:
        plt.title(title)
    plt.axis("off")
    plt.show()


def analyze_image(client, image_path, analysis_type="general"):
    """画像を分析し、その内容を説明します。"""
    image_b64 = encode_image_to_base64(image_path)
    image_metadata = get_image_metadata(image_path)
    filename = image_metadata["filename"]

    # 分析タイプに応じたプロンプトを設定
    prompts = {
        "general": f"この不動産物件の画像({filename})について詳細に説明してください。何が見えますか？どのような特徴がありますか？",
        "real_estate": f"不動産エージェントとして、この物件画像({filename})の特徴と魅力を詳細に分析してください。売りポイントは何ですか？",
        "interior": f"インテリアデザイナーの視点で、この室内画像({filename})を分析してください。デザイン、色使い、家具の配置などの特徴を説明してください。",
        "exterior": f"建築家の視点で、この建物の外観画像({filename})を分析してください。建築様式、構造的特徴、周辺環境などについて説明してください。",
    }

    prompt = prompts.get(analysis_type, prompts["general"])

    # APIリクエスト
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions="あなたは不動産や建築、インテリアの専門家です。画像を詳細に分析し、専門的な視点から説明してください。",
            input=[
                {
                    "role": "user", 
                    "content": [
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_b64}"},
                        {"type": "input_text", "text": prompt}
                    ]
                }
            ],
            max_output_tokens=1000,
        )

        return {"image_metadata": image_metadata, "analysis": response.output_text}

    except Exception as e:
        print(f"画像分析エラー: {str(e)}")
        return {"image_metadata": image_metadata, "analysis": f"エラー: {str(e)}"}


def generate_property_description(
    client, image_paths, property_type="house", target_audience="general"
):
    """複数の物件画像を分析し、魅力的な物件説明を生成します。"""
    # 各画像をbase64エンコード
    encoded_images = []
    for path in image_paths:
        encoded_images.append(
            {
                "path": path,
                "filename": os.path.basename(path),
                "base64": encode_image_to_base64(path),
            }
        )

    # 物件タイプとターゲット層に応じたプロンプトを設定
    audience_descriptions = {
        "general": "一般的な購入者や賃借人",
        "luxury": "高級物件を求める富裕層",
        "family": "子育て世帯や家族向け",
        "investment": "投資目的の購入者",
        "first_time": "初めての住宅購入者",
    }

    property_descriptions = {
        "house": "一戸建て住宅",
        "apartment": "アパートメント/マンション",
        "condo": "コンドミニアム",
        "villa": "別荘/ヴィラ",
        "office": "オフィススペース",
        "commercial": "商業施設",
    }

    audience = audience_descriptions.get(
        target_audience, audience_descriptions["general"]
    )
    prop_type = property_descriptions.get(property_type, property_descriptions["house"])

    # 指示と画像入力を準備
    instructions = f"""
    あなたは経験豊富な不動産エージェントで、魅力的な物件説明を作成するエキスパートです。
    {audience}向けの{prop_type}の魅力的な説明文を作成してください。

    次のガイドラインに従ってください：
    1. 複数の画像から物件の特徴を総合的に分析する
    2. 物件の最も魅力的な特徴や売りポイントを強調する
    3. 空間、設備、デザイン、環境などの観点から説明する
    4. ポジティブで魅力的な表現を使用する
    5. 具体的な詳細と感情的な要素を組み合わせる
    6. {audience}に特に響く要素を強調する
    """

    # 入力の準備
    user_content = []

    # 画像を追加
    for img in encoded_images:
        user_content.append(
            {"type": "input_image", "image_url": f"data:image/jpeg;base64,{img['base64']}"}
        )

    # テキストプロンプトを追加
    user_content.append(
        {
            "type": "input_text",
            "text": f"これらの画像は同じ物件（{prop_type}）の異なる部分を撮影したものです。{audience}に向けた魅力的な物件説明文を作成してください。タイトルと本文形式で、最大1000文字程度で作成してください。",
        }
    )

    # APIリクエスト
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions=instructions,
            input=[{"role": "user", "content": user_content}],
            max_output_tokens=2000,
        )

        return {
            "property_type": property_type,
            "target_audience": target_audience,
            "image_count": len(image_paths),
            "image_paths": [os.path.basename(p) for p in image_paths],
            "description": response.output_text,
        }

    except Exception as e:
        print(f"物件説明生成エラー: {str(e)}")
        return {
            "property_type": property_type,
            "target_audience": target_audience,
            "image_count": len(image_paths),
            "image_paths": [os.path.basename(p) for p in image_paths],
            "description": f"エラー: {str(e)}",
        }


def suggest_improvements(client, image_path, improvement_type="general"):
    """物件画像を分析し、改善点を提案します。"""
    image_b64 = encode_image_to_base64(image_path)
    filename = os.path.basename(image_path)

    # 改善タイプに応じたプロンプトを設定
    prompts = {
        "general": f"この不動産物件の画像({filename})を分析し、売却や賃貸の可能性を高めるための改善点を提案してください。",
        "staging": f"ホームステージングの専門家として、この物件画像({filename})を分析し、より魅力的に見せるための具体的な提案をしてください。",
        "renovation": f"リノベーションの専門家として、この物件画像({filename})を分析し、価値を高めるためのリノベーションの提案をしてください。コストと効果のバランスも考慮してください。",
        "photo": f"不動産写真の専門家として、この物件画像({filename})の撮影方法や角度、構図などについて改善点を提案してください。より魅力的に見せるためのアドバイスをお願いします。",
    }

    prompt = prompts.get(improvement_type, prompts["general"])

    # APIリクエスト
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions="あなたは不動産改善やホームステージングの専門家です。物件の魅力を最大化するための具体的かつ実用的な提案をしてください。",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_b64}"},
                        {"type": "input_text", "text": prompt}
                    ]
                }
            ],
            max_output_tokens=1500,
        )

        return {
            "image_path": image_path,
            "improvement_type": improvement_type,
            "suggestions": response.output_text,
        }

    except Exception as e:
        print(f"改善提案エラー: {str(e)}")
        return {
            "image_path": image_path,
            "improvement_type": improvement_type,
            "suggestions": f"エラー: {str(e)}",
        }


def compare_properties(client, image_paths, comparison_type="general"):
    """複数の物件画像を比較分析します。"""
    if len(image_paths) < 2:
        return {"error": "比較には少なくとも2つの画像が必要です"}

    # 各画像をbase64エンコード
    encoded_images = []
    for path in image_paths:
        encoded_images.append(
            {
                "path": path,
                "filename": os.path.basename(path),
                "base64": encode_image_to_base64(path),
            }
        )

    # 比較タイプに応じたプロンプトを設定
    prompts = {
        "general": "これらの不動産物件画像を比較分析してください。各物件の特徴、強み、弱みを比較し、どのような購入者/賃借人に適しているかを説明してください。",
        "investment": "投資の観点から、これらの物件を比較分析してください。投資価値、潜在的な収益性、リスク要因などを比較してください。",
        "design": "デザインやインテリアの観点から、これらの物件を比較分析してください。スタイル、機能性、現代的なトレンドとの一致度などを比較してください。",
        "value": "コストパフォーマンスの観点から、これらの物件を比較分析してください。提供される価値、潜在的な追加コスト、長期的な価値などを比較してください。",
    }

    prompt = prompts.get(comparison_type, prompts["general"])

    # 入力の準備
    user_content = []

    # 画像を追加
    for img in encoded_images:
        user_content.append(
            {"type": "input_image", "image_url": f"data:image/jpeg;base64,{img['base64']}"}
        )

    # テキストプロンプトを追加
    user_content.append({"type": "input_text", "text": prompt})

    # APIリクエスト
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions="あなたは不動産の比較分析の専門家です。物件の特徴を客観的に比較し、それぞれの強みと弱みを明確に説明してください。",
            input=[{"role": "user", "content": user_content}],
            max_output_tokens=2000,
        )

        return {
            "comparison_type": comparison_type,
            "image_count": len(image_paths),
            "image_paths": [os.path.basename(p) for p in image_paths],
            "comparison": response.output_text,
        }

    except Exception as e:
        print(f"物件比較エラー: {str(e)}")
        return {
            "comparison_type": comparison_type,
            "image_count": len(image_paths),
            "image_paths": [os.path.basename(p) for p in image_paths],
            "comparison": f"エラー: {str(e)}",
        }


def save_results(results, output_dir="results"):
    """分析結果をファイルに保存します。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, output_dir)

    # 結果ディレクトリが存在しない場合は作成
    os.makedirs(results_dir, exist_ok=True)

    # 結果の種類に応じたファイル名を設定
    if "analysis" in results:
        # 単一画像の分析結果
        filename = os.path.basename(results["image_metadata"]["path"])
        output_file = os.path.join(
            results_dir, f"{os.path.splitext(filename)[0]}_analysis.txt"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# 画像分析結果: {filename}\n\n")
            f.write(f"## メタデータ\n")
            f.write(
                f"- サイズ: {results['image_metadata']['width']} x {results['image_metadata']['height']}\n"
            )
            f.write(f"- フォーマット: {results['image_metadata']['format']}\n")
            f.write(
                f"- ファイルサイズ: {results['image_metadata']['file_size'] / 1024:.1f} KB\n\n"
            )
            f.write(f"## 分析\n")
            f.write(results["analysis"])

    elif "description" in results:
        # 物件説明の生成結果
        output_file = os.path.join(
            results_dir,
            f"property_description_{results['property_type']}_{results['target_audience']}.txt",
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(
                f"# 物件説明: {results['property_type']} ({results['target_audience']}向け)\n\n"
            )
            f.write(f"## 使用画像\n")
            for img in results["image_paths"]:
                f.write(f"- {img}\n")
            f.write(f"\n## 説明文\n")
            f.write(results["description"])

    elif "suggestions" in results:
        # 改善提案の結果
        filename = os.path.basename(results["image_path"])
        output_file = os.path.join(
            results_dir,
            f"{os.path.splitext(filename)[0]}_improvements_{results['improvement_type']}.txt",
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# 改善提案: {filename} ({results['improvement_type']})\n\n")
            f.write(results["suggestions"])

    elif "comparison" in results:
        # 物件比較の結果
        output_file = os.path.join(
            results_dir, f"property_comparison_{results['comparison_type']}.txt"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# 物件比較分析 ({results['comparison_type']})\n\n")
            f.write(f"## 比較対象\n")
            for img in results["image_paths"]:
                f.write(f"- {img}\n")
            f.write(f"\n## 比較結果\n")
            f.write(results["comparison"])

    else:
        # その他の結果
        output_file = os.path.join(results_dir, "results.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"結果を保存しました: {output_file}")
    return output_file


def main():
    """メイン関数"""
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="不動産物件の画像分析と説明生成")
    parser.add_argument(
        "--mode",
        "-m",
        type=str,
        default="analyze",
        choices=["analyze", "describe", "improve", "compare"],
        help="実行モード（analyze:単一画像分析, describe:物件説明生成, improve:改善提案, compare:物件比較）",
    )
    parser.add_argument(
        "--image", "-i", type=str, help="分析する画像ファイル名（imagesディレクトリ内）"
    )
    parser.add_argument(
        "--type",
        "-t",
        type=str,
        help="分析タイプ（general, real_estate, interior, exterior）または物件タイプ（house, apartment, etc.）",
    )
    parser.add_argument(
        "--audience",
        "-a",
        type=str,
        default="general",
        help="ターゲット層（general, luxury, family, investment, first_time）",
    )
    parser.add_argument(
        "--output", "-o", type=str, default="results", help="結果の出力ディレクトリ"
    )
    args = parser.parse_args()

    # OpenAI APIの設定
    api_key = setup_environment()
    client = openai.Client(api_key=api_key)

    # 画像パスの取得
    all_image_paths = get_image_paths()
    if not all_image_paths:
        print(
            "画像が見つかりませんでした。まず `python download_sample_images.py` を実行してサンプル画像をダウンロードしてください。"
        )
        return

    # 選択された画像または全画像
    if args.image:
        selected_image = [
            path for path in all_image_paths if os.path.basename(path) == args.image
        ]
        if not selected_image:
            print(f"指定された画像 '{args.image}' が見つかりませんでした。")
            return
        image_paths = selected_image
    else:
        image_paths = all_image_paths

    # 出力ファイルの初期化
    output_file = None

    # 実行モードに応じた処理
    if args.mode == "analyze":
        # 単一画像の分析
        if len(image_paths) > 1:
            print(
                "分析モードでは単一の画像を指定してください。--image オプションで特定の画像を指定できます。"
            )
            image_path = image_paths[0]  # デフォルトで最初の画像を使用
            print(f"最初の画像を使用します: {os.path.basename(image_path)}")
        else:
            image_path = image_paths[0]

        analysis_type = args.type or "general"
        print(
            f"画像 '{os.path.basename(image_path)}' を '{analysis_type}' モードで分析します..."
        )

        results = analyze_image(client, image_path, analysis_type)
        output_file = save_results(results, args.output)

        print(f"\n= 分析結果 =\n{results['analysis']}")

    elif args.mode == "describe":
        # 物件説明の生成
        property_type = args.type or "house"
        target_audience = args.audience
        print(
            f"{len(image_paths)}枚の画像から '{property_type}' タイプの物件説明を '{target_audience}' 向けに生成します..."
        )

        results = generate_property_description(
            client, image_paths, property_type, target_audience
        )
        output_file = save_results(results, args.output)

        print(f"\n= 生成された物件説明 =\n{results['description']}")

    elif args.mode == "improve":
        # 改善提案
        if len(image_paths) > 1:
            print(
                "改善提案モードでは単一の画像を指定してください。--image オプションで特定の画像を指定できます。"
            )
            image_path = image_paths[0]  # デフォルトで最初の画像を使用
            print(f"最初の画像を使用します: {os.path.basename(image_path)}")
        else:
            image_path = image_paths[0]

        improvement_type = args.type or "general"
        print(
            f"画像 '{os.path.basename(image_path)}' に対する '{improvement_type}' タイプの改善提案を生成します..."
        )

        results = suggest_improvements(client, image_path, improvement_type)
        output_file = save_results(results, args.output)

        print(f"\n= 改善提案 =\n{results['suggestions']}")

    elif args.mode == "compare":
        # 物件比較
        if len(image_paths) < 2:
            print("比較モードでは少なくとも2つの画像が必要です。")
            return

        comparison_type = args.type or "general"
        print(
            f"{len(image_paths)}枚の画像を '{comparison_type}' の観点で比較分析します..."
        )

        results = compare_properties(client, image_paths, comparison_type)
        output_file = save_results(results, args.output)

        print(f"\n= 比較分析結果 =\n{results['comparison']}")

    print(f"\n分析結果は '{output_file}' に保存されました。")


if __name__ == "__main__":
    main()
