# 不動産物件の画像分析と説明生成

このサンプルは、OpenAI Responses APIのマルチモーダル機能を使用して、不動産物件の画像を分析し、魅力的な物件説明を自動生成する方法を示します。

## 主な機能

- 単一画像の詳細分析（バスルーム、キッチン、リビングなど）
- 複数画像からの総合的な物件説明生成
- 物件の改善提案（ホームステージング、リノベーション、写真撮影など）
- 複数物件の比較分析（一般的、投資、デザイン、価値の観点から）

## 使い方

### 前提条件

- Python 3.9以上
- OpenAI APIキー（GPT-4o対応）

### 環境構築

```bash
# 仮想環境を有効化
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt

# サンプル画像をダウンロード
python download_sample_images.py
```

### 実行方法

#### 単一画像分析

```bash
# 基本的な物件分析
python main.py --mode analyze --image bedroom_1.jpg

# 特定視点からの分析（real_estate, interior, exteriorから選択）
python main.py --mode analyze --image kitchen_1.jpg --type interior
```

#### 物件説明生成

```bash
# 全画像から物件説明を生成（デフォルトでは一戸建て住宅、一般層向け）
python main.py --mode describe

# 特定のターゲット層向けの説明文生成（luxury, family, investment, first_timeから選択）
python main.py --mode describe --audience luxury

# 物件タイプを指定（house, apartment, condo, villa, office, commercialから選択）
python main.py --mode describe --type apartment --audience family
```

#### 改善提案

```bash
# 一般的な改善提案
python main.py --mode improve --image living_room_1.jpg

# 特定タイプの改善提案（staging, renovation, photoから選択）
python main.py --mode improve --image house_exterior_1.jpg --type staging
```

#### 物件比較

```bash
# 複数の物件を比較（少なくとも2つの画像が必要）
python main.py --mode compare

# 特定の視点からの比較（investment, design, valueから選択）
python main.py --mode compare --type investment
```

## 注意点

- APIキーは `.env` ファイルに `OPENAI_API_KEY=your_api_key_here` の形式で設定してください
- 画像ファイルは `images` ディレクトリに配置されます
- 分析結果は `results` ディレクトリに保存されます

## 技術的詳細

このサンプルでは、OpenAI Responses APIの以下の機能を活用しています：

- マルチモーダル入力（画像とテキストの組み合わせ）
- 適切なinstructionsによる専門的視点の提供
- input_imageとinput_textを組み合わせたリクエスト構造
- base64エンコード画像データの送信