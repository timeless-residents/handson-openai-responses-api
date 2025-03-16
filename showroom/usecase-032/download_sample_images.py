"""
サンプル不動産画像のダウンロードスクリプト

このスクリプトは、不動産物件分析のサンプル用に、
Unsplashなどのフリー画像提供サイトから不動産関連の画像を
ダウンロードし、images/ ディレクトリに保存します。
"""

import os
import requests
from PIL import Image
from io import BytesIO

# 画像を保存するディレクトリ
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

# 不動産画像のサンプルURL（Unsplashなどのフリー画像）
SAMPLE_IMAGES = [
    # 屋外/外観画像
    {
        "url": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914",
        "filename": "house_exterior_1.jpg",
        "type": "exterior",
        "description": "モダンな平屋の外観"
    },
    {
        "url": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
        "filename": "house_exterior_2.jpg",
        "type": "exterior",
        "description": "プールのある豪華な住宅"
    },
    {
        "url": "https://images.unsplash.com/photo-1576941089067-2de3c901e126",
        "filename": "apartment_exterior.jpg",
        "type": "exterior",
        "description": "モダンなアパートメント外観"
    },
    
    # リビングルーム
    {
        "url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
        "filename": "living_room_1.jpg",
        "type": "living_room",
        "description": "明るいモダンなリビングルーム"
    },
    {
        "url": "https://images.unsplash.com/photo-1600210492493-0946911123ea",
        "filename": "living_room_2.jpg",
        "type": "living_room",
        "description": "広々とした高級リビングルーム"
    },
    
    # キッチン
    {
        "url": "https://images.unsplash.com/photo-1556911220-bff31c812dba",
        "filename": "kitchen_1.jpg",
        "type": "kitchen",
        "description": "明るいモダンなキッチン"
    },
    {
        "url": "https://images.unsplash.com/photo-1556909212-d5b604d0c90d",
        "filename": "kitchen_2.jpg",
        "type": "kitchen",
        "description": "アイランドキッチン"
    },
    
    # バスルーム
    {
        "url": "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14",
        "filename": "bathroom_1.jpg",
        "type": "bathroom",
        "description": "モダンなバスルーム"
    },
    
    # ベッドルーム
    {
        "url": "https://images.unsplash.com/photo-1616594039964-ae9021a400a0",
        "filename": "bedroom_1.jpg",
        "type": "bedroom",
        "description": "広々としたベッドルーム"
    },
    {
        "url": "https://images.unsplash.com/photo-1540518614846-7eded433c457",
        "filename": "bedroom_2.jpg",
        "type": "bedroom",
        "description": "明るいベッドルーム"
    }
]


def download_image(url, filename):
    """指定されたURLから画像をダウンロードして保存します。"""
    try:
        # imagesディレクトリが存在しない場合は作成
        os.makedirs(IMAGES_DIR, exist_ok=True)
        
        # 画像をダウンロード
        response = requests.get(url, stream=True)
        response.raise_for_status()  # エラーがあれば例外を発生
        
        # 画像を開いてリサイズ
        img = Image.open(BytesIO(response.content))
        
        # 画像が大きすぎる場合はリサイズ（最大幅1280px）
        if img.width > 1280:
            ratio = 1280 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((1280, new_height), Image.LANCZOS)
        
        # 画像を保存
        img_path = os.path.join(IMAGES_DIR, filename)
        img.save(img_path, quality=85, optimize=True)
        
        print(f"ダウンロード成功: {filename}")
        return img_path
    
    except Exception as e:
        print(f"画像のダウンロードに失敗しました ({url}): {str(e)}")
        return None


def generate_metadata_file():
    """ダウンロードした画像のメタデータファイルを生成します。"""
    metadata_path = os.path.join(IMAGES_DIR, "metadata.txt")
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write("# 不動産画像サンプルメタデータ\n\n")
        
        for img in SAMPLE_IMAGES:
            f.write(f"## {img['filename']}\n")
            f.write(f"タイプ: {img['type']}\n")
            f.write(f"説明: {img['description']}\n")
            f.write(f"ソース: {img['url']}\n")
            f.write("\n")
    
    print(f"メタデータファイルを作成しました: {metadata_path}")


def main():
    """メイン関数"""
    print("不動産画像サンプルのダウンロードを開始します...")
    
    # 各画像をダウンロード
    for img_info in SAMPLE_IMAGES:
        download_image(img_info["url"], img_info["filename"])
    
    # メタデータファイルを生成
    generate_metadata_file()
    
    print("ダウンロード処理が完了しました。")


if __name__ == "__main__":
    main()