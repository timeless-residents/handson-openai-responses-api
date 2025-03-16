"""
ユーティリティ関数: 様々なヘルパー関数を提供
"""

import io
import base64
import json
import re
import logging
import nltk
from nltk.tokenize import sent_tokenize
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import markdown
import MeCab  # 日本語形態素解析器

# ロギングの設定
logger = logging.getLogger(__name__)


def format_datetime(dt):
    """日時を日本語形式でフォーマット"""
    if dt is None:
        return ""
    return dt.strftime("%Y年%m月%d日 %H:%M")


def calculate_duration(start_time, end_time):
    """2つの時間から経過時間（分）を計算"""
    if start_time is None or end_time is None:
        return 0
    delta = end_time - start_time
    return int(delta.total_seconds() / 60)


def count_words(text):
    """テキスト内の単語数をカウント"""
    if not text:
        return 0
    words = re.findall(r"\w+", text.lower())
    return len(words)


def extract_key_terms(texts, top_n=10):
    """テキストから重要な用語を抽出"""
    if not texts or len(texts) == 0:
        return []

    # TF-IDFベクトル化
    vectorizer = TfidfVectorizer(max_df=0.85, min_df=2, stop_words="english")

    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()

        # スコアの平均を計算
        mean_tfidf = tfidf_matrix.mean(axis=0).A1

        # スコアと用語をソート
        scored_terms = [(term, score) for term, score in zip(feature_names, mean_tfidf)]
        scored_terms.sort(key=lambda x: x[1], reverse=True)

        # 上位N個を返す
        return [term for term, score in scored_terms[:top_n]]
    except Exception as e:
        logger.error(f"key terms 抽出エラー: {str(e)}")
        return []


def tokenize_japanese(text):
    """日本語テキストを単語に分割する"""
    try:
        # 分かち書きモードでMeCabを初期化
        tagger = MeCab.Tagger('-Owakati')
        
        # テキストを解析して単語に分割
        parsed = tagger.parse(text)
        
        # 単語リストを作成（短すぎる単語を除外）
        words = []
        for word in parsed.split():
            # 2文字以上の単語のみ使用
            if len(word) > 1:
                # 記号やストップワードの除外（必要に応じて調整）
                if not re.match(r'^[ぁ-んァ-ン一-龥]+$', word) or word in ['これ', 'それ', 'あれ', 'この', 'その', 'あの']:
                    continue
                words.append(word)
        
        # 単語の頻度カウント
        word_count = {}
        for word in words:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1
        
        # 結果が空の場合は単純なn-gramを試みる
        if not word_count:
            # テキストを2文字ずつの部分文字列に分割
            for i in range(len(text) - 1):
                if i + 2 <= len(text):
                    ngram = text[i:i+2]
                    if len(ngram.strip()) < 2:
                        continue
                    if ngram not in word_count:
                        word_count[ngram] = 1
                    else:
                        word_count[ngram] += 1
        
        # それでも空の場合はデフォルト値を返す
        if not word_count:
            return {"分析できるキーワードがありません": 1}
        
        return word_count
    
    except Exception as e:
        logger.error(f"日本語形態素解析エラー: {str(e)}")
        # エラーメッセージを表示するための代替データ
        return {"キーワード抽出エラー": 1}


def generate_wordcloud(text):
    """テキストからワードクラウド画像を生成"""
    if not text:
        return None

    try:
        # 日本語フォントパス
        jp_font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"  # macOS用日本語フォント
        
        # 日本語テキストの単語分割
        word_frequencies = tokenize_japanese(text)
        
        # ワードクラウドの設定（日本語対応）
        wordcloud = WordCloud(
            font_path=jp_font_path,  # 日本語フォントを指定
            width=800,
            height=400,
            background_color="white",
            max_words=100,
            contour_width=3,
            contour_color="steelblue",
            collocations=False  # 複合語の処理を無効化
        ).generate_from_frequencies(word_frequencies)

        # プロットの作成
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")

        # 画像をバイト列に変換
        img_data = io.BytesIO()
        plt.savefig(img_data, format="png")
        img_data.seek(0)
        plt.close()

        # Base64エンコード
        encoded = base64.b64encode(img_data.read()).decode("utf-8")

        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        logger.error(f"ワードクラウド生成エラー: {str(e)}")
        try:
            # シンプルな方法でもう一度試行
            logger.info("シンプルな方法でワードクラウドを再生成します")
            
            # 分かち書きのみを使用して単純化
            default_words = {"キーワード抽出に失敗しました": 1, "別の方法で再試行してください": 1}
            
            # シンプルな設定でWordCloud生成
            wordcloud = WordCloud(
                font_path="/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                width=800,
                height=400,
                background_color="white",
                max_words=10,
                contour_width=3,
                contour_color="steelblue",
            ).generate_from_frequencies(default_words)
            
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            
            img_data = io.BytesIO()
            plt.savefig(img_data, format="png")
            img_data.seek(0)
            plt.close()
            
            encoded = base64.b64encode(img_data.read()).decode("utf-8")
            
            return f"data:image/png;base64,{encoded}"
        except Exception as fallback_error:
            logger.error(f"フォールバックでもエラー: {str(fallback_error)}")
            return None


def markdown_to_html(text):
    """MarkdownテキストをHTML形式に変換"""
    if not text:
        return ""
    return markdown.markdown(text, extensions=["fenced_code", "tables"])


def calculate_reading_time(text):
    """テキストの読了時間（分）を推定"""
    if not text:
        return 1

    # 単語数をカウント
    word_count = count_words(text)

    # 平均的な読書速度（1分あたり200単語）で計算
    minutes = word_count / 200

    # 最低1分を返す
    return max(1, int(minutes))


def extract_sentences(text, max_sentences=5):
    """テキストから重要な文を抽出"""
    if not text:
        return []

    # テキストを文に分割
    try:
        sentences = sent_tokenize(text)
    except:
        # NLTKのダウンロードが必要な場合
        nltk.download("punkt", quiet=True)
        sentences = sent_tokenize(text)

    # 文が少ない場合はそのまま返す
    if len(sentences) <= max_sentences:
        return sentences

    # 単純な方法: 文の長さでソートして中程度の長さの文を選択
    sorted_by_length = sorted(sentences, key=len)
    start_idx = len(sorted_by_length) // 3
    selected = sorted_by_length[start_idx : start_idx + max_sentences]

    # 元の順序で並び替え
    original_order = [s for s in sentences if s in selected]

    return original_order


def parse_json_string(json_string):
    """JSON文字列をパースしてPythonオブジェクトを返す"""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logger.error(f"JSON パースエラー: {str(e)}")
        logger.error(f"JSON文字列: {json_string}")
        return None