# ユースケース037: 個人向け学習アシスタント

このサンプルでは、OpenAI APIを活用して個人学習を支援するアプリケーションを実装しています。学習者の理解度に合わせて適応的に学習コンテンツを提供し、質問応答や学習計画の立案を支援します。

## 機能

- 複数の学習科目をサポート（プログラミング、数学、科学、言語など）
- 学習者のレベルに応じたコンテンツ生成
- インタラクティブな質問応答
- パーソナライズされた学習計画の作成
- 学習の進捗状況の追跡
- 知識の確認のためのクイズ生成
- 学習内容の要約とノート作成支援
- フラッシュカードによる記憶強化
- コンセプトの視覚化（図表・チャート）
- 学習分析とフィードバック

## 使い方

1. 依存パッケージをインストールします：
   ```
   pip install -r requirements.txt
   ```

2. `.env`ファイルにOpenAI APIキーが設定されていることを確認します：
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. アプリケーションを起動します：
   ```
   python main.py
   ```

4. ブラウザで http://localhost:5000 にアクセスします

5. 最初にログインまたはアカウント作成を行います

6. 学習したい科目を選択し、学習レベルを設定します

7. アプリケーションの各機能を使用して学習を進めます

## 学習フロー

1. **学習計画の作成**: 目標、期間、現在の知識レベルに基づいて最適な学習計画を作成
2. **コンテンツ学習**: 選択したトピックに関する説明、例、演習問題を提供
3. **質問応答**: 学習中に生じた疑問に対する回答を取得
4. **知識の確認**: 学習した内容を確認するためのクイズやテストを実施
5. **復習と強化**: フラッシュカードや定期的な復習セッションで記憶を強化
6. **進捗評価**: 学習の進捗状況を視覚的に確認し、弱点を特定

## サポート科目

- プログラミング（Python, JavaScript, Java, C++など）
- 数学（代数学、幾何学、微積分、統計学など）
- 科学（物理学、化学、生物学、天文学など）
- 言語（英語、フランス語、スペイン語、日本語など）
- 社会科学（歴史、地理、経済学、心理学など）

## 注意事項

- このアプリケーションは教育目的で作成されたデモです
- 生成されたコンテンツは必ずしも100%正確ではないため、専門的な文献と併用することをお勧めします
- 学習者のデータはローカルに保存され、プライバシーは保護されます