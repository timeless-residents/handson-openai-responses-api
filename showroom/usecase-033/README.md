# マーケティングコンテンツの自動生成

このサンプルは、OpenAI Responses APIを使用して、様々なマーケティングコンテンツを自動生成する方法を示します。ソーシャルメディア投稿、ブログ記事、メールニュースレター、広告コピー、プレスリリースなど、多様なマーケティング素材を対象とした活用例を提供します。

## 主な機能

- 特定のプラットフォームとスタイルに合わせたソーシャルメディア投稿の生成
- ターゲットオーディエンス向けSEO最適化ブログ記事の作成
- 様々なタイプのメールニュースレターの作成
- プラットフォームと広告タイプに最適化された広告コピーの生成
- 各種プレスリリースの作成

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
```

### 実行方法

#### ソーシャルメディア投稿の生成

```bash
# 基本的なソーシャルメディア投稿生成（デフォルトはInstagram）
python main.py --content-type social_media

# 特定のプラットフォームと投稿スタイルを指定
python main.py --content-type social_media --platform Twitter --style casual

# より多くの投稿を生成
python main.py --content-type social_media --count 5
```

#### ブログ記事の生成

```bash
# デフォルトのトピックでブログ記事を生成
python main.py --content-type blog

# 特定のトピックと単語数を指定
python main.py --content-type blog --topic "空気清浄機を選ぶ際のポイント" --word-count 1200

# 特定のターゲットセグメントを指定
python main.py --content-type blog --target-segment "アレルギー持ちの方"
```

#### メールニュースレターの生成

```bash
# 基本的なプロモーションメール生成
python main.py --content-type email

# 特定のメールタイプを指定
python main.py --content-type email --email-type welcome

# ターゲットセグメントを指定
python main.py --content-type email --email-type educational --target-segment "新規ユーザー"
```

#### 広告コピーの生成

```bash
# 基本的な検索広告の生成（デフォルトはGoogle）
python main.py --content-type ad

# プラットフォームと広告タイプを指定
python main.py --content-type ad --platform Facebook --ad-type social

# より多くの広告案を生成
python main.py --content-type ad --count 5
```

#### プレスリリースの生成

```bash
# 基本的な製品発表プレスリリースの生成
python main.py --content-type press_release

# 特定のプレスリリースタイプを指定
python main.py --content-type press_release --release-type partnership
```

### カスタムデータの使用

組み込みのサンプルデータではなく、独自の商品やブランドデータを使用することもできます：

```bash
# 独自のJSONファイルを使用
python main.py --content-type blog --product-data path/to/product.json --brand-info path/to/brand.json
```

または、プログラム内からproduct_data.pyを使って直接利用することも可能です：

```python
from product_data import SMARTWATCH, TECHECO_BRAND, FITNESS_CAMPAIGN
```

## 出力

生成されたコンテンツはすべて次の2つの形式で保存されます：

1. 読みやすいテキスト形式（.txt/.md）
2. 構造化されたJSON形式（.json）

すべての出力は、デフォルトではプロジェクトルートの`output`ディレクトリに保存されます。

## テクニカルノート

- Responses APIのオブジェクト構造とブランドボイスの一貫性を維持する方法を示しています
- 複数の入力データソースを構造化してプロンプトに組み込む手法を提供
- 生成された出力を解析して適切な形式に変換する方法を実装

## 応用例

- マーケティングチームでの類似コンテンツの大量生成
- A/Bテスト用の様々なバリエーション作成
- 季節やターゲット層に合わせたコンテンツの迅速な作成
- マーケティングプラットフォームとの連携による配信自動化