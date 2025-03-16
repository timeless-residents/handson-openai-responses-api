"""
OpenAI Responses API - ユースケース010: 画像入力と説明生成

このスクリプトは、OpenAI Responses APIを使用して画像を分析し、
説明を生成する方法を示します。URLからの画像、ローカルファイル、
Base64エンコード画像など、さまざまな画像入力方法をデモンストレーションします。
"""

import os
import sys
import json
import base64
from pathlib import Path
from io import BytesIO
import requests
from dotenv import load_dotenv
import openai

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


def download_image(url, save_path):
    """URLから画像をダウンロードして保存します。

    Args:
        url (str): 画像のURL
        save_path (str): 保存先のパス

    Returns:
        bool: ダウンロードが成功したかどうか
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"画像のダウンロードに失敗しました: {e}")
        return False


def resize_image_if_needed(image_path, max_size=(1024, 1024)):
    """必要に応じて画像をリサイズします。

    Args:
        image_path (str): ローカル画像ファイルのパス
        max_size (tuple): 最大幅と高さ

    Returns:
        str: 処理された画像のパス
    """
    if not PIL_AVAILABLE:
        print("警告: PIL/Pillowがインストールされていないため、リサイズは行われません")
        return image_path
        
    try:
        img = Image.open(image_path)
        
        # リサイズが必要かチェック
        if img.width > max_size[0] or img.height > max_size[1]:
            print(f"画像をリサイズします: {img.width}x{img.height} -> 最大{max_size[0]}x{max_size[1]}")
            img.thumbnail(max_size, Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.BICUBIC)
            
            # 新しいファイル名で保存
            filename, ext = os.path.splitext(image_path)
            new_path = f"{filename}_resized{ext}"
            img.save(new_path)
            return new_path
        
        return image_path
    except Exception as e:
        print(f"画像のリサイズに失敗しました: {e}")
        return image_path


def create_image_response(client, prompt_text, image_data, image_type="base64"):
    """画像を含むレスポンスを生成します。
    
    最新のOpenAI Chat Completions APIフォーマットに準拠しています。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        prompt_text (str): 画像に関する指示や質問
        image_data (str): 画像データ（Base64文字列またはURL）
        image_type (str): 'base64'または'url'

    Returns:
        openai.types.responses.Response: APIからの応答オブジェクト
    """
    # 入力形式を構築
    content = []
    
    # テキスト部分を追加
    content.append({"type": "text", "text": prompt_text})
    
    # 画像部分を追加
    if image_type == "base64":
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_data}"
            }
        })
    else:  # url
        content.append({
            "type": "image_url",
            "image_url": {
                "url": image_data
            }
        })

    # APIリクエスト
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}]
    )
    
    # レスポンスフォーマットを調整
    return {
        "id": response.id,
        "model": response.model,
        "created_at": response.created,  # ChatCompletionでは created_at ではなく created を使用
        "output_text": response.choices[0].message.content,
        "usage": response.usage
    }


def display_response(response, title=None):
    """APIからの応答を整形して表示します。

    Args:
        response (dict): APIからの応答オブジェクト
        title (str, optional): 表示するタイトル
    """
    if title:
        print(f"\n===== {title} =====")
    else:
        print("\n===== レスポンス =====")
        
    print(f"Model: {response['model']}")
    print(f"Response ID: {response['id']}")
    print(f"Created at: {response['created_at']}")
    
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
        print("=====================")


def prepare_sample_images(images_dir):
    """サンプル画像を準備します。

    Args:
        images_dir (str): 画像ディレクトリのパス

    Returns:
        dict: 画像のパスを含む辞書
    """
    os.makedirs(images_dir, exist_ok=True)
    
    # サンプル画像のURL
    sample_images = {
        "landscape": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1000&q=80",
        "chart": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1000&q=80"
    }
    
    # 画像をダウンロード
    image_paths = {}
    for name, url in sample_images.items():
        save_path = os.path.join(images_dir, f"{name}.jpg")
        
        # 画像が存在しない場合はダウンロードを試みる
        if not os.path.exists(save_path):
            print(f"{name}.jpg をダウンロード中...")
            if download_image(url, save_path):
                print(f"{save_path} にダウンロードしました")
            else:
                print(f"{name}.jpg のダウンロードに失敗しました")
                continue
        
        # 画像をリサイズ（必要な場合）
        processed_path = resize_image_if_needed(save_path)
        image_paths[name] = processed_path
    
    return image_paths


def run_local_image_example(client, image_path):
    """ローカル画像を使った例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_path (str): 分析する画像のパス
    """
    if not os.path.exists(image_path):
        print(f"エラー: 画像ファイルが見つかりません: {image_path}")
        return
    
    # 画像をBase64エンコード
    print(f"画像をエンコード中: {image_path}")
    base64_image = encode_image_to_base64(image_path)
    
    # プロンプト
    prompt = "この画像を詳細に説明してください。写っているものや、画像の雰囲気、特徴的な要素についても触れてください。"
    
    # レスポンス生成
    print("APIリクエスト送信中...")
    response = create_image_response(client, prompt, base64_image, "base64")
    
    # 結果表示
    display_response(response, "ローカル画像分析の結果")


def run_url_image_example(client, image_url=None):
    """URLから取得した画像を使った例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_url (str, optional): 画像のURL
    """
    # デフォルトのサンプル画像URL
    if image_url is None:
        image_url = "https://images.unsplash.com/photo-1682687982501-1e58ab814714?w=800&q=80"
    
    # プロンプト
    prompt = "この画像に何が写っていますか？主な被写体と背景について説明してください。"
    
    # レスポンス生成
    print(f"URL画像を分析中: {image_url}")
    response = create_image_response(client, prompt, image_url, "url")
    
    # 結果表示
    display_response(response, "URL画像分析の結果")


def run_specialized_analysis_example(client, image_path):
    """特殊な画像分析の例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_path (str): 分析する画像のパス
    """
    if not os.path.exists(image_path):
        print(f"エラー: 画像ファイルが見つかりません: {image_path}")
        return
    
    # 画像をBase64エンコード
    print(f"画像をエンコード中: {image_path}")
    base64_image = encode_image_to_base64(image_path)
    
    # 専門的なプロンプト
    prompt = """
    この画像を詳細に分析し、以下の情報を提供してください：
    1. 画像の種類（写真、図表、イラストなど）
    2. 主要な視覚要素とその配置
    3. 色調と全体的な雰囲気
    4. 画像から読み取れるストーリーや文脈
    5. この画像が適している用途や活用方法
    
    専門的な視点から分析し、詳細な説明を提供してください。
    """
    
    # レスポンス生成
    print("APIリクエスト送信中...")
    response = create_image_response(client, prompt, base64_image, "base64")
    
    # 結果表示
    display_response(response, "専門的画像分析の結果")


def run_multilingual_analysis(client, image_path):
    """多言語での画像分析例を実行します。

    Args:
        client (openai.Client): OpenAIクライアントインスタンス
        image_path (str): 分析する画像のパス
    """
    if not os.path.exists(image_path):
        print(f"エラー: 画像ファイルが見つかりません: {image_path}")
        return
    
    # 画像をBase64エンコード
    print(f"画像をエンコード中: {image_path}")
    base64_image = encode_image_to_base64(image_path)
    
    # 多言語プロンプト
    prompt = """
    Analyze this image and provide your description in three languages:
    1. First in English
    2. Then in Japanese (日本語)
    3. Finally in Spanish (Español)
    
    Include details about the main elements, colors, mood, and any interesting aspects.
    """
    
    # レスポンス生成
    print("APIリクエスト送信中...")
    response = create_image_response(client, prompt, base64_image, "base64")
    
    # 結果表示
    display_response(response, "多言語画像分析の結果")


def main():
    """メイン関数

    OpenAI Responses APIを使用して画像分析と説明生成のデモを実行します。
    """
    try:
        # 環境設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)

        # サンプル画像の準備
        images_dir = os.path.join(os.path.dirname(__file__), "images")
        image_paths = prepare_sample_images(images_dir)
        
        if not image_paths:
            print("サンプル画像の準備に失敗しました。インターネット接続を確認してください。")
            return
        
        # ローカル画像を使った例
        if "landscape" in image_paths:
            print("\n1. ローカル画像を使った基本的な分析")
            run_local_image_example(client, image_paths["landscape"])
        
        # URLから取得した画像を使った例
        print("\n2. URLから取得した画像の分析")
        run_url_image_example(client)
        
        # 特殊な画像分析の例
        if "chart" in image_paths:
            print("\n3. 特殊な画像分析（詳細分析）")
            run_specialized_analysis_example(client, image_paths["chart"])
        
        # 多言語での画像分析
        if "landscape" in image_paths:
            print("\n4. 多言語での画像分析")
            run_multilingual_analysis(client, image_paths["landscape"])

    except Exception as error:
        print(f"エラーが発生しました: {error}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()