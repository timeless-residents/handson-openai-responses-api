# OpenAI Responses API ハンズオン

このリポジトリは、OpenAI Responses APIを利用するための実践的なサンプルコードを提供します。Responses APIは、OpenAIの最も高度なインターフェースであり、テキストや画像の入力、テキスト出力をサポートしています。

## 目次

- [環境構築](#環境構築)
- [使い方](#使い方)
- [ユースケース一覧](#ユースケース一覧)
- [ライセンス](#ライセンス)

## 環境構築

### 前提条件

- Python 3.9以上
- OpenAI APIキー

### インストール

リポジトリをクローンし、必要なパッケージをインストールします。

```bash
# リポジトリをクローン
git clone https://github.com/timeless-residents/handson-openai-responses-api.git
cd handson-openai-responses-api

# 仮想環境を作成して有効化
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r showroom/usecase-000/requirements.txt
```

### 環境変数の設定

プロジェクトのルートディレクトリに `.env` ファイルを作成し、OpenAI APIキーを設定します。

```
OPENAI_API_KEY=your_api_key_here
```

## 使い方

各ユースケースは `showroom` ディレクトリ内にあります。それぞれのユースケースフォルダ内の説明に従って実行してください。

### 基本的な例（usecase-000）

最も基本的なAPIの使用例は以下のコマンドで実行できます：

```bash
python showroom/usecase-000/main.py
```

## ユースケース一覧

### 基本機能

- **usecase-000**: [基本的なテキスト応答の生成](showroom/usecase-000/README.md) - Responses APIの基本的な使い方と単純なテキスト生成
- **usecase-001**: [システムプロンプト（instructions）を使用した応答調整](showroom/usecase-001/README.md) - AIの役割や制約を指定する方法
- **usecase-002**: [複数の入力テキストによる応答生成](showroom/usecase-002/README.md) - 複数のメッセージを送信して文脈を理解させる方法
- **usecase-003**: [ストリーミングによるリアルタイム応答表示](showroom/usecase-003/README.md) - リアルタイムでトークンを受け取り表示する方法
- **usecase-004**: [パラメータ調整（temperature, top_p, max_output_tokens）](showroom/usecase-004/README.md) - 応答の多様性や長さをコントロールする方法
- **usecase-005**: [JSONフォーマットによる構造化出力の生成](showroom/usecase-005/README.md) - JSONオブジェクトやJSONスキーマを使って構造化データを取得
- **usecase-006**: [会話状態の管理（previous_response_id）](showroom/usecase-006/README.md) - 会話の文脈を維持して連続的な対話を実現する方法
- **usecase-007**: [メタデータの活用とレスポンス管理](showroom/usecase-007/README.md) - リクエストの分類と追跡を効率化するメタデータの活用法

### マルチモーダル入力

- **usecase-010**: [画像入力と説明生成](showroom/usecase-010/README.md) - 画像を分析して詳細な説明を生成する方法
- **usecase-011**: [テキストと画像の複合入力](showroom/usecase-011/README.md) - テキストと画像を組み合わせた高度な対話を実現する方法
- **usecase-012**: [複数画像の分析と比較](showroom/usecase-012/README.md) - 複数画像間のパターン検出と系統的な比較分析を行う方法

### ツール連携

- **usecase-020**: [Web検索ツールの活用](showroom/usecase-020/README.md) - モデルにインターネット検索能力を提供し最新情報にアクセスする方法
- **usecase-021**: [ファイル検索ツールの活用](showroom/usecase-021/README.md) - ローカルファイルシステム内のファイル検索と分析を行う方法
- **usecase-022**: [カスタム関数呼び出し（Function Calling）](showroom/usecase-022/README.md) - AIモデルに外部機能を提供し複雑なタスクを実行する方法
- **usecase-023**: [並列ツール呼び出し（parallel_tool_calls）](showroom/usecase-023/README.md) - 複数のツールを同時に呼び出して効率的にデータを取得する方法
- **usecase-024**: [ツール選択の制御（tool_choice）](showroom/usecase-024/README.md) - AIモデルのツール使用を明示的に制御する方法

### 応用シナリオ（民間利用）

- **usecase-030**: [カスタマーサポートチャットボット](showroom/usecase-030/README.md) - 商品情報や注文状況を提供するインタラクティブなサポートボット
- **usecase-031**: [製品レビュー分析と洞察抽出](showroom/usecase-031/README.md) - テキストレビューから重要な洞察を抽出し製品改善に活かす分析ツール
- **usecase-032**: [不動産物件の画像分析と説明生成](showroom/usecase-032/README.md) - 物件画像を分析して詳細な説明や改善提案を生成するツール
- **usecase-033**: [マーケティングコンテンツの自動生成](showroom/usecase-033/README.md) - 多様なマーケティング素材を自動生成する統合ソリューション
- **usecase-034**: [多言語対応ドキュメント翻訳と要約](showroom/usecase-034/README.md) - 文書の翻訳・要約・分析を行う多言語対応ツール
- **usecase-035**: [データ分析レポート自動生成](showroom/usecase-035/README.md) - 販売データからAIを活用した詳細な分析レポートを自動生成するツール
- **usecase-036**: [法的文書のレビューと要約](showroom/usecase-036/README.md) - PDF形式の法的文書を分析し、要約・リスク評価・専門用語の説明を行うWebアプリケーション
- **usecase-037**: [個人向け学習アシスタント](showroom/usecase-037/README.md) - AIを活用してパーソナライズされたコンテンツと学習プランを提供する学習支援アプリケーション
- **usecase-038**: [メディア内容のモデレーションと分類](showroom/usecase-038/README.md) - テキストコンテンツの安全性評価とポリシー違反検出を行うモデレーションツール
- **usecase-039**: [データ分析と可視化レポート生成](showroom/usecase-039/README.md) - CSV/JSONデータの自動分析とインサイト抽出を行う対話型分析ツール

### 応用シナリオ（公共利用）

- **usecase-040**: 市民向け行政サービス案内
- **usecase-041**: 医療情報の理解支援と説明
- **usecase-042**: 災害情報の整理と配信支援
- **usecase-043**: 教育コンテンツの生成と適応
- **usecase-044**: バリアフリー情報アクセス支援
- **usecase-045**: 公共データの可視化と説明

### 統合ソリューション

- **usecase-050**: Web APIとの統合（Webサービス構築）
- **usecase-051**: データベースとの連携
- **usecase-052**: バッチ処理システムの構築
- **usecase-053**: ダッシュボード分析との連携
- **usecase-054**: ワークフロー自動化との統合

### パフォーマンスと最適化

- **usecase-060**: キャッシュ戦略とコスト最適化
- **usecase-061**: 大規模処理のバッチ最適化
- **usecase-062**: レスポンス品質の評価と改善
- **usecase-063**: プロンプトエンジニアリングの高度な手法
- **usecase-064**: マルチモデル連携と比較

### セキュリティとコンプライアンス

- **usecase-070**: 個人情報保護とデータ処理
- **usecase-071**: 倫理的配慮とバイアス軽減
- **usecase-072**: 監査とログ記録

## 実装予定

上記のユースケースは段階的に実装していく予定です。完成したユースケースは随時更新されます。各ユースケースの詳細な説明と実装状況は、対応するディレクトリ内のREADME.mdを参照してください。

## ライセンス

このプロジェクトは [MIT License](LICENSE) のもとで公開されています。