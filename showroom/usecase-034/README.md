# 多言語対応ドキュメント翻訳と要約

このサンプルは、OpenAI Responses APIを使用して、様々な言語のドキュメントを翻訳し、要約する方法を示します。複数のファイル形式に対応し、言語検出機能も備えており、多言語環境でのドキュメント管理や国際的なコミュニケーションを効率化するためのツールとして利用できます。

## 主な機能

- 多言語テキストの自動言語検出
- 高品質な翻訳（多数の言語ペアに対応）
- テキストの効率的な要約（長さと焦点を調整可能）
- 複数のファイル形式対応（TXT、PDF、DOCX、その他）
- ドキュメント分析と統計情報の提供
- 技術用語と固有名詞の保持オプション
- 書式保持翻訳オプション

## 使い方

### 前提条件

- Python 3.9以上
- OpenAI APIキー（GPT-4o対応）
- 必要なライブラリ（requirements.txtに記載）

### 環境構築

```bash
# 仮想環境を有効化
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 実行方法

#### 翻訳機能

```bash
# 英語から日本語への翻訳（書式保持あり）
python main.py --file path/to/document.txt --mode translate --target-lang ja --preserve-formatting

# 日本語から英語への翻訳（技術用語の保持）
python main.py --file path/to/document.txt --mode translate --target-lang en --tech-terms "OpenAI" "GPT-4" "Transformer"
```

#### 要約機能

```bash
# 文書の簡潔な要約を生成
python main.py --file path/to/document.txt --mode summarize --summary-length short

# 技術的内容に焦点を当てた詳細な要約（箇条書き形式）
python main.py --file path/to/document.txt --mode summarize --summary-length detailed --summary-focus technical --bullet-points
```

#### 文書分析

```bash
# 文書の分析情報のみ生成
python main.py --file path/to/document.txt --mode analyze

# 文書の翻訳、要約、分析を全て実行
python main.py --file path/to/document.txt --mode all
```

### オプション一覧

- `--file`, `-f`: 処理するファイルのパス（必須）
- `--mode`, `-m`: 実行モード（translate, summarize, analyze, all）
- `--target-lang`, `-t`: 翻訳対象言語（ISO 639-1コード: en, ja, zh-cn, fr, de, es, など）
- `--summary-length`: 要約の長さ（short, medium, detailed）
- `--summary-focus`: 要約の焦点（general, technical, business, academic）
- `--bullet-points`: 要約を箇条書き形式で出力
- `--preserve-formatting`: 翻訳時に元の書式を保持
- `--tech-terms`: 保持すべき技術用語や固有名詞のリスト
- `--output-dir`, `-o`: 出力ディレクトリ

## サンプルファイル

このディレクトリには以下のサンプルファイルが含まれています：

- `sample_en.txt`: 英語のサンプルテキスト（AIに関する概要）
- `sample_fr.txt`: フランス語のサンプルテキスト（AIに関する概要）
- `sample_ja.txt`: 日本語のサンプルテキスト（AIに関する概要）

これらのファイルを使用して、ツールの機能をテストできます。

## 出力例

翻訳、要約、および分析の結果は、`output`ディレクトリに保存されます。出力には以下が含まれます：

1. 翻訳されたテキスト（{ファイル名}_{対象言語}_{タイムスタンプ}.txt）
2. 要約テキスト（{ファイル名}_summary_{言語}_{タイムスタンプ}.txt）
3. 分析レポート（{ファイル名}_report_{タイムスタンプ}.md）
4. 統計グラフ（{ファイル名}_sentence_dist_{タイムスタンプ}.png）

## 応用例

- 国際的なビジネス文書の迅速な翻訳
- 多言語ドキュメントの効率的な要約作成
- 外国語文書の内容把握と分析
- 研究論文の多言語化と要約
- 技術マニュアルの翻訳と簡略化