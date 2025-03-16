"""
製品レビュー分析と洞察抽出

このサンプルは、OpenAI Responses APIを使用して、
製品レビューの分析と洞察の抽出を行う方法を示しています。
テキストベースのレビューから感情分析、キーワード抽出、トレンド特定などの
分析を行い、ビジネス判断に役立つ洞察を提供します。
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any, Optional, Union
import math
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from datetime import datetime
from collections import Counter, defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from dotenv import load_dotenv
import openai


# --- 日本語フォント設定 ---
def setup_japanese_fonts():
    """システムで利用可能な日本語フォントを設定し、フォントキャッシュをクリアします"""
    import matplotlib.font_manager as fm
    import matplotlib as mpl
    import glob
    
    # フォントキャッシュのクリア（フォント読み込みの問題を解決するため）
    try:
        cache_dir = mpl.get_cachedir()
        font_cache = os.path.join(cache_dir, 'fontlist-*.json')
        for cache_file in glob.glob(font_cache):
            print(f"フォントキャッシュをクリア: {cache_file}")
            os.remove(cache_file)
    except Exception as e:
        print(f"フォントキャッシュのクリアに失敗: {e}")
    
    # フォントマネージャーを再構築
    try:
        # 新しいバージョンのmatplotlib
        if hasattr(fm, '_rebuild'):
            fm._rebuild()
        # 古いバージョンのmatplotlib
        elif hasattr(fm, 'fontManager'):
            fm.fontManager.findfont.cache.clear()
            fm.fontManager._load_fontmanager(try_read_cache=False)
        # もっと古いバージョン
        else:
            fm._get_fontconfig_fonts.cache_clear()
            fm.findfont.cache_clear()
    except Exception as e:
        print(f"フォントキャッシュのリセットに失敗しましたが、処理を続行します: {e}")
    
    # 日本語フォント候補（優先順位順）
    japanese_font_names = [
        # macOS
        "Hiragino Sans GB", "Hiragino Maru Gothic Pro", "Hiragino Kaku Gothic Pro", 
        "AppleGothic", "YuGothic", "Osaka",
        # Windows
        "MS Gothic", "Meiryo", "Yu Gothic", "MS Mincho", "Yu Mincho",
        # Linux
        "Noto Sans CJK JP", "IPAGothic", "IPAPGothic", "VL Gothic", "Sazanami Gothic",
        # 代替
        "Arial Unicode MS", "Dejavu Sans"
    ]
    
    # システムからすべてのフォントを取得
    font_list = fm.findSystemFonts()
    japanese_fonts = []
    
    # matplotlibのフォントファミリー一覧から日本語フォントを探す
    available_families = set(f.name for f in fm.fontManager.ttflist)
    for font_name in japanese_font_names:
        if font_name in available_families:
            japanese_fonts.append(font_name)
            print(f"フォント名で日本語フォントを見つけました: {font_name}")
    
    # フォントパスから直接検索（名前で見つからない場合）
    if not japanese_fonts:
        for font_path in font_list:
            font_path_lower = font_path.lower()
            if any(keyword in font_path_lower for keyword in [
                "hiragino", "gothic", "meiryo", "mincho", "msgothic", 
                "yumin", "yugoth", "ipa", "noto", "cjk", "osaka"
            ]):
                try:
                    # フォントを登録して名前を取得
                    fm.fontManager.addfont(font_path)
                    prop = fm.FontProperties(fname=font_path)
                    japanese_fonts.append(font_path)
                    print(f"フォントパスで日本語フォントを見つけました: {font_path}")
                    break
                except Exception as e:
                    print(f"フォント登録失敗 {font_path}: {e}")
    
    # 日本語フォントが見つからなかった場合
    if not japanese_fonts:
        print("警告: 日本語フォントが見つかりませんでした")
        return None, None
    
    # 最初のフォントを選択して設定
    chosen_font = japanese_fonts[0]
    font_prop = None
    
    try:
        # フォントパスの場合
        if os.path.exists(chosen_font):
            # フォントを登録して使用
            fm.fontManager.addfont(chosen_font)
            font_prop = fm.FontProperties(fname=chosen_font)
            font_family = font_prop.get_name()
        else:
            # フォント名の場合
            font_family = chosen_font
            font_prop = fm.FontProperties(family=font_family)
        
        # すべてのテキスト要素に同じフォントを適用
        mpl.rcParams['font.family'] = 'sans-serif'  # まずサンセリフファミリーに設定
        mpl.rcParams['font.sans-serif'] = [font_family] + mpl.rcParams.get('font.sans-serif', [])  # 選択したフォントを先頭に追加
        mpl.rcParams['axes.unicode_minus'] = False  # マイナス記号の問題を修正
        
        # 明示的にテキスト描画関数にフォントプロパティを指定
        plt.rc('font', family='sans-serif')
        plt.rc('axes', unicode_minus=False)
        
        print(f"日本語フォント設定完了: {font_family}")
        return font_prop, font_family
    
    except Exception as e:
        print(f"警告: 日本語フォントの設定に失敗しました: {str(e)}")
        return None, None

# 日本語フォントのセットアップを実行
japanese_font_prop, japanese_font_family = setup_japanese_fonts()

# 商品レビューデータを読み込み
from review_data import (
    get_all_reviews,
    get_product_reviews,
    get_reviews_by_rating,
    get_reviews_by_date_range,
    search_reviews,
    SMARTPHONE_REVIEWS,
    LAPTOP_REVIEWS,
    EARPHONE_REVIEWS,
)

# Python 3.7以降の場合、標準入出力のエンコーディングをUTF-8に設定
if sys.version_info >= (3, 7):
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

# NLTKのリソースをダウンロード（初回実行時のみ）
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")


# --- データ準備と前処理 ---
def prepare_reviews_dataframe(reviews):
    """レビューデータをpandasデータフレームに変換します。"""
    df = pd.DataFrame(reviews)
    # 日付型に変換
    df["date"] = pd.to_datetime(df["date"])
    # 月単位のカラムを追加
    df["month"] = df["date"].dt.strftime("%Y-%m")
    return df


def clean_review_text(text):
    """レビューテキストのクリーニングを行います。"""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_reviews(reviews_df, column="text"):
    """レビューテキストをトークン化します。"""
    tokenized_reviews = []
    for review in reviews_df[column]:
        clean_text = clean_review_text(review)
        tokens = clean_text.split()
        tokens = [token for token in tokens if len(token) > 1]
        tokenized_reviews.append(tokens)
    return tokenized_reviews


# --- 基本的な統計分析 ---
def calculate_rating_distribution(reviews_df):
    """評価点の分布を計算します。"""
    rating_counts = reviews_df["rating"].value_counts().sort_index()
    return rating_counts


def calculate_review_trends(reviews_df):
    """時間経過に伴うレビュー数と評価点の推移を計算します。"""
    monthly_counts = reviews_df.groupby("month").size()
    monthly_ratings = reviews_df.groupby("month")["rating"].mean()
    return monthly_counts, monthly_ratings


def plot_rating_distribution(rating_counts, title="評価点の分布"):
    """評価点の分布を棒グラフで可視化します。"""
    plt.figure(figsize=(10, 6))
    sns.set(font_scale=1.2)
    
    # seaborn 0.14.0以降のための対応 (hueを追加し、legendをFalseに)
    x_values = rating_counts.index
    ax = sns.barplot(
        x=x_values, 
        y=rating_counts.values, 
        hue=x_values,  # FutureWarning対応
        palette="viridis", 
        legend=False   # 凡例を非表示
    )
    
    # テキスト装飾（日本語フォントプロパティを明示的に指定）
    if japanese_font_prop:
        plt.title(title, fontsize=18, pad=20, fontproperties=japanese_font_prop)
        plt.xlabel("評価点", fontsize=14, labelpad=10, fontproperties=japanese_font_prop)
        plt.ylabel("レビュー数", fontsize=14, labelpad=10, fontproperties=japanese_font_prop)
    else:
        plt.title(title, fontsize=18, pad=20)
        plt.xlabel("評価点", fontsize=14, labelpad=10)
        plt.ylabel("レビュー数", fontsize=14, labelpad=10)
    
    # 目盛り設定
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    # 各バーの上に値を表示
    for i, v in enumerate(rating_counts.values):
        ax.text(i, v + 0.1, str(v), ha="center", fontsize=11)
    
    # グリッド線
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    return plt


def plot_review_trends(monthly_counts, monthly_ratings, title="レビュートレンド"):
    """レビュー数と評価点の時間的推移を可視化します。"""
    fig, ax1 = plt.subplots(figsize=(12, 6))
    color = "tab:blue"
    
    # フォントプロパティを使用（利用可能な場合）
    if japanese_font_prop:
        ax1.set_xlabel("月", fontsize=14, labelpad=10, fontproperties=japanese_font_prop)
        ax1.set_ylabel("レビュー数", color=color, fontsize=14, labelpad=10, fontproperties=japanese_font_prop)
    else:
        ax1.set_xlabel("月", fontsize=14, labelpad=10)
        ax1.set_ylabel("レビュー数", color=color, fontsize=14, labelpad=10)
    
    ax1.plot(
        monthly_counts.index,
        monthly_counts.values,
        color=color,
        marker="o",
        linewidth=2,
    )
    ax1.tick_params(axis="y", labelcolor=color, labelsize=12)
    ax1.tick_params(axis="x", labelsize=12, rotation=45)
    for i, v in enumerate(monthly_counts.values):
        ax1.text(i, v + 0.1, str(v), ha="center", color=color, fontsize=11)
    
    ax2 = ax1.twinx()
    color = "tab:red"
    
    if japanese_font_prop:
        ax2.set_ylabel("平均評価点", color=color, fontsize=14, labelpad=10, fontproperties=japanese_font_prop)
    else:
        ax2.set_ylabel("平均評価点", color=color, fontsize=14, labelpad=10)
    
    ax2.plot(
        monthly_ratings.index,
        monthly_ratings.values,
        color=color,
        marker="s",
        linewidth=2,
    )
    ax2.tick_params(axis="y", labelcolor=color, labelsize=12)
    for i, v in enumerate(monthly_ratings.values):
        ax2.text(i, v + 0.05, f"{v:.1f}", ha="center", color=color, fontsize=11)
    ax1.grid(axis="y", linestyle="--", alpha=0.3)
    
    if japanese_font_prop:
        plt.title(title, fontsize=18, pad=20, fontproperties=japanese_font_prop)
    else:
        plt.title(title, fontsize=18, pad=20)
    
    ax1.plot([], [], color="tab:blue", marker="o", linewidth=2, label="レビュー数")
    ax2.plot([], [], color="tab:red", marker="s", linewidth=2, label="平均評価点")
    plt.legend(fontsize=12, loc="best")
    fig.tight_layout()
    return plt


def create_word_cloud(tokenized_reviews, title="頻出ワードクラウド"):
    """トークン化されたレビューからワードクラウドを生成します。"""
    all_tokens = [
        token for review_tokens in tokenized_reviews for token in review_tokens
    ]
    word_freq = Counter(all_tokens)
    font_path = None
    potential_font_paths = []
    
    # macOS用フォントパス
    if sys.platform.startswith("darwin"):
        potential_font_paths.extend([
            "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
            "/System/Library/Fonts/AppleGothic.ttf",
            "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
            "/Library/Fonts/Osaka.ttf",
            "/Library/Fonts/ヒラギノ明朝 ProN.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            # macOS Big Sur以降
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/Hiragino Maru Gothic Pro.ttc",
            "/System/Library/Fonts/Hiragino Kaku Gothic Pro.ttc",
        ])
    # Windows用フォントパス
    elif sys.platform.startswith("win"):
        potential_font_paths.extend([
            "C:\\Windows\\Fonts\\msgothic.ttc",
            "C:\\Windows\\Fonts\\meiryo.ttc",
            "C:\\Windows\\Fonts\\YuGothic.ttf",
            "C:\\Windows\\Fonts\\MSMincho.ttc",
            "C:\\Windows\\Fonts\\Arial Unicode.ttf",
        ])
    # Linux用フォントパス
    else:
        potential_font_paths.extend([
            "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
            "/usr/share/fonts/truetype/ipafont-gothic/ipag.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/vlgothic/VL-Gothic-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ])
    
    # 設定済みのフォントプロパティがあれば、そのパスを追加
    if japanese_font_prop:
        # matplotlibのfontpropertyからフォントファイルを取得
        try:
            import matplotlib.font_manager as fm
            path = fm.findfont(japanese_font_prop)
            if path and os.path.exists(path):
                potential_font_paths.append(path)
                print(f"既存のフォントプロパティからパスを取得: {path}")
        except Exception as e:
            print(f"フォントパス取得エラー: {e}")
            
    # 日本語フォント名が判明している場合
    if japanese_font_family:
        try:
            path = matplotlib.font_manager.findfont(
                matplotlib.font_manager.FontProperties(family=japanese_font_family)
            )
            if path and os.path.exists(path):
                potential_font_paths.append(path)
                print(f"フォント名からパスを取得: {path}")
        except Exception as e:
            print(f"フォント名からのパス取得エラー: {e}")
    # 利用可能なフォントパスを探す
    for path in potential_font_paths:
        if os.path.exists(path):
            font_path = path
            print(f"WordCloud用フォントが見つかりました: {path}")
            break
    
    # ワードクラウドのパラメータ設定
    wordcloud_params = {
        "width": 800,
        "height": 400,
        "background_color": "white",
        "max_words": 100,
        "contour_width": 3,
        "contour_color": "steelblue",
        "colormap": "viridis",
        "prefer_horizontal": 0.9,
    }
    
    # フォントパスが見つかった場合は設定
    if font_path:
        print(f"ワードクラウド用日本語フォント: {font_path}")
        wordcloud_params["font_path"] = font_path
    else:
        print("警告: 日本語フォントが見つかりませんでした。ワードクラウドが正常に表示されない可能性があります。")
    
    # ワードクラウド生成の試行
    try:
        wordcloud = WordCloud(**wordcloud_params).generate_from_frequencies(word_freq)
    except Exception as e:
        print(f"ワードクラウド生成エラー: {str(e)}")
        
        # フォント指定を解除して再試行
        if "font_path" in wordcloud_params:
            del wordcloud_params["font_path"]
            print("フォント指定を解除して再試行します。")
            try:
                wordcloud = WordCloud(**wordcloud_params).generate_from_frequencies(word_freq)
            except Exception as e:
                print(f"再試行も失敗: {str(e)}")
                # 最小限の設定で再試行
                wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(word_freq)
        else:
            # 最小限の設定で再試行
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(word_freq)
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    
    # 日本語タイトルの表示
    if japanese_font_prop:
        plt.title(title, fontsize=16, fontproperties=japanese_font_prop)
    else:
        plt.title(title, fontsize=16)
        
    plt.tight_layout()
    return plt, word_freq


# --- OpenAI APIを使用した高度な分析 ---
def extract_sentiments_with_openai(client, reviews, batch_size=5):
    """OpenAI APIを使用してレビューの感情分析を行います。"""
    sentiments = []
    for i in range(0, len(reviews), batch_size):
        batch = reviews[i : i + batch_size]
        prompt = f"""
        以下の製品レビューを分析し、各レビューの感情（ポジティブ、ネガティブ、ニュートラル）を判定し、
        主要なポジティブポイントとネガティブポイントを抽出してください。
        
        レビュー:
        {json.dumps(batch, ensure_ascii=False, indent=2)}
        
        各レビューについて以下の形式で回答してください:
        - レビューID: (レビューのID)
        - 感情: (ポジティブ/ネガティブ/ニュートラル)
        - 感情スコア: (1-5の範囲で、5が最もポジティブ)
        - ポジティブポイント: (箇条書きで最大3つ)
        - ネガティブポイント: (箇条書きで最大3つ)
        - キーワード: (重要なキーワードを最大5つ)
        """
        try:
            response = client.responses.create(
                model="gpt-4o",
                instructions="あなたは製品レビュー分析の専門家です。与えられたレビューの感情分析、キーポイント抽出、キーワード特定を行ってください。",
                input=prompt,
                max_output_tokens=4000,
            )
            analysis_text = response.output_text
            reviews_analysis = parse_sentiment_analysis(analysis_text, batch)
            sentiments.extend(reviews_analysis)
            print(
                f"バッチ {i//batch_size + 1}/{math.ceil(len(reviews)/batch_size)} の感情分析が完了しました"
            )
        except Exception as e:
            print(f"エラー: {str(e)}")
            print(f"バッチ {i//batch_size + 1} の処理に失敗しました。スキップします。")
    return sentiments


def parse_sentiment_analysis(analysis_text, original_reviews):
    """OpenAI APIからのレスポンスをパースして構造化された感情分析データを抽出します。"""
    results = []
    for review in original_reviews:
        review_id = review["review_id"]
        pattern = rf"レビューID:\s*{review_id}.*?(?=レビューID:|$)"
        match = re.search(pattern, analysis_text, re.DOTALL)
        if match:
            analysis_section = match.group(0)
            sentiment_match = re.search(
                r"感情:\s*(ポジティブ|ネガティブ|ニュートラル)", analysis_section
            )
            sentiment = sentiment_match.group(1) if sentiment_match else "不明"
            score_match = re.search(r"感情スコア:\s*(\d+)", analysis_section)
            sentiment_score = int(score_match.group(1)) if score_match else 3
            positive_points = []
            pos_section_match = re.search(
                r"ポジティブポイント:(.*?)ネガティブポイント:",
                analysis_section,
                re.DOTALL,
            )
            if pos_section_match:
                pos_text = pos_section_match.group(1)
                positive_points = [
                    point.strip()
                    for point in re.findall(r"-\s*(.*?)(?=$|\n)", pos_text)
                    if point.strip()
                ]
            negative_points = []
            neg_section_match = re.search(
                r"ネガティブポイント:(.*?)キーワード:", analysis_section, re.DOTALL
            )
            if neg_section_match:
                neg_text = neg_section_match.group(1)
                negative_points = [
                    point.strip()
                    for point in re.findall(r"-\s*(.*?)(?=$|\n)", neg_text)
                    if point.strip()
                ]
            keywords = []
            keyword_match = re.search(
                r"キーワード:(.*?)(?=$)", analysis_section, re.DOTALL
            )
            if keyword_match:
                keyword_text = keyword_match.group(1)
                keywords = [
                    word.strip()
                    for word in re.findall(r"[\w\s]+", keyword_text)
                    if word.strip()
                ]
            results.append(
                {
                    "review_id": review_id,
                    "product_id": review["product_id"],
                    "product_name": review["product_name"],
                    "rating": review["rating"],
                    "sentiment": sentiment,
                    "sentiment_score": sentiment_score,
                    "positive_points": positive_points,
                    "negative_points": negative_points,
                    "keywords": keywords,
                    "original_review": review,
                }
            )
        else:
            results.append(
                {
                    "review_id": review_id,
                    "product_id": review["product_id"],
                    "product_name": review["product_name"],
                    "rating": review["rating"],
                    "sentiment": "不明",
                    "sentiment_score": 3,
                    "positive_points": [],
                    "negative_points": [],
                    "keywords": [],
                    "original_review": review,
                }
            )
    return results


def extract_insights_with_openai(client, sentiment_analysis, product_name):
    """OpenAI APIを使用してレビュー分析から洞察を抽出します。"""
    prompt = f"""
    以下は「{product_name}」の製品レビュー分析結果です。
    この分析結果から、製品の強み、弱み、改善点、市場での位置づけなどに関する洞察を抽出してください。
    
    分析データ:
    {json.dumps(sentiment_analysis, ensure_ascii=False, indent=2)}
    
    以下の形式で洞察を提供してください:
    
    # 主要な洞察
    
    ## 製品の強み
    - (強みポイント1)
    - (強みポイント2)
    - ...
    
    ## 製品の弱み
    - (弱みポイント1)
    - (弱みポイント2)
    - ...
    
    ## 改善すべき点
    - (改善点1)
    - (改善点2)
    - ...
    
    ## 顧客セグメント分析
    - (顧客セグメント1)
    - (顧客セグメント2)
    - ...
    
    ## 競合製品との差別化ポイント
    - (差別化ポイント1)
    - (差別化ポイント2)
    - ...
    
    ## マーケティングへの提案
    - (マーケティング提案1)
    - (マーケティング提案2)
    - ...
    
    ## 次期バージョンへの提案
    - (次期バージョン提案1)
    - (次期バージョン提案2)
    - ...
    """
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions="あなたは製品マーケティングと顧客インサイト分析の専門家です。製品レビューの分析結果から、ビジネス判断に役立つ洞察を抽出してください。",
            input=prompt,
            max_output_tokens=4000,
        )
        return response.output_text
    except Exception as e:
        print(f"エラー: {str(e)}")
        return f"洞察の抽出に失敗しました: {str(e)}"


def generate_report_with_openai(
    client, insights, sentiment_analysis, stats, product_name
):
    """OpenAI APIを使用して分析レポートを生成します。"""
    prompt = f"""
    以下の情報を基に、「{product_name}」に関する包括的な製品レビュー分析レポートを作成してください。
    
    ## 基本統計
    {json.dumps(stats, ensure_ascii=False, indent=2)}
    
    ## 感情分析とキーポイント
    {json.dumps(sentiment_analysis[:3], ensure_ascii=False, indent=2)}
    ※ 分析結果の一部のみ表示
    
    ## 抽出された洞察
    {insights}
    
    以下のフォーマットでレポートを作成してください：
    
    # 「{product_name}」製品レビュー分析レポート
    
    ## エグゼクティブサマリー
    (主要な発見と推奨事項の簡潔なまとめ)
    
    ## 分析概要
    - 分析対象レビュー数: (総レビュー数)
    - 平均評価点: (平均評価)
    - レビュー期間: (最初のレビュー日) 〜 (最後のレビュー日)
    
    ## 主要な発見
    (重要な発見ポイントを箇条書きで)
    
    ## 肯定的なフィードバック
    (肯定的なフィードバックの主要な傾向と例)
    
    ## 否定的なフィードバック
    (否定的なフィードバックの主要な傾向と例)
    
    ## ユーザーセグメント分析
    (異なるユーザーグループからのフィードバックの傾向)
    
    ## 推奨される改善点
    (製品改善のための具体的な提案)
    
    ## マーケティング提案
    (マーケティング戦略に活かせる提案)
    
    ## 結論
    (全体の分析結果に基づく結論)
    """
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions="あなたは製品分析レポートの専門家です。与えられた分析データを基に、経営判断に役立つ包括的な分析レポートを作成してください。",
            input=prompt,
            max_output_tokens=4000,
        )
        return response.output_text
    except Exception as e:
        print(f"エラー: {str(e)}")
        return f"レポートの生成に失敗しました: {str(e)}"


# --- メイン処理関数 ---
def analyze_product_reviews(client, product_id=None, output_dir="output"):
    """製品レビューの分析を実行し、結果を可視化・出力します。"""
    os.makedirs(output_dir, exist_ok=True)
    if product_id:
        reviews = get_product_reviews(product_id)
        if not reviews:
            print(f"製品ID '{product_id}' のレビューが見つかりません。")
            return
        product_name = reviews[0]["product_name"]
    else:
        reviews = SMARTPHONE_REVIEWS
        product_id = "SP-100"
        product_name = "TechX Phone Pro"
    print(f"「{product_name}」のレビュー分析を開始します（合計 {len(reviews)} 件）")
    reviews_df = prepare_reviews_dataframe(reviews)
    rating_counts = calculate_rating_distribution(reviews_df)
    monthly_counts, monthly_ratings = calculate_review_trends(reviews_df)
    tokenized_reviews = tokenize_reviews(reviews_df)
    plt_rating = plot_rating_distribution(
        rating_counts, f"「{product_name}」の評価点分布"
    )
    plt_rating.savefig(f"{output_dir}/{product_id}_rating_distribution.png")
    plt_trend = plot_review_trends(
        monthly_counts, monthly_ratings, f"「{product_name}」のレビュートレンド"
    )
    plt_trend.savefig(f"{output_dir}/{product_id}_review_trends.png")
    plt_wordcloud, word_freq = create_word_cloud(
        tokenized_reviews, f"「{product_name}」のレビューワードクラウド"
    )
    plt_wordcloud.savefig(f"{output_dir}/{product_id}_wordcloud.png")
    stats = {
        "product_id": product_id,
        "product_name": product_name,
        "total_reviews": len(reviews),
        "average_rating": reviews_df["rating"].mean(),
        "rating_distribution": rating_counts.to_dict(),
        "review_period": {
            "start": reviews_df["date"].min().strftime("%Y-%m-%d"),
            "end": reviews_df["date"].max().strftime("%Y-%m-%d"),
        },
        "top_keywords": dict(word_freq.most_common(20)),
    }
    with open(f"{output_dir}/{product_id}_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print("基本統計分析が完了しました。")
    print("OpenAI APIを使用した感情分析を開始します...")
    sentiment_analysis = extract_sentiments_with_openai(client, reviews)
    with open(
        f"{output_dir}/{product_id}_sentiment_analysis.json", "w", encoding="utf-8"
    ) as f:
        json.dump(sentiment_analysis, f, ensure_ascii=False, indent=2)
    print("感情分析が完了しました。")
    print("レビューからの洞察抽出を開始します...")
    insights = extract_insights_with_openai(client, sentiment_analysis, product_name)
    with open(f"{output_dir}/{product_id}_insights.md", "w", encoding="utf-8") as f:
        f.write(insights)
    print("洞察抽出が完了しました。")
    print("分析レポートの生成を開始します...")
    report = generate_report_with_openai(
        client, insights, sentiment_analysis, stats, product_name
    )
    with open(f"{output_dir}/{product_id}_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"分析レポートが生成されました: {output_dir}/{product_id}_report.md")
    return {
        "stats": stats,
        "sentiment_analysis": sentiment_analysis,
        "insights": insights,
        "report": report,
    }


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="製品レビュー分析ツール")
    parser.add_argument(
        "--product", "-p", type=str, help="分析する製品ID（例: SP-100, LT-200, EP-300）"
    )
    parser.add_argument(
        "--output", "-o", type=str, default="output", help="出力ディレクトリのパス"
    )
    args = parser.parse_args()
    api_key = setup_environment()
    client = openai.Client(api_key=api_key)
    if not args.product:
        print("\n選択可能な製品:")
        print("1: スマートフォン (TechX Phone Pro, 製品ID: SP-100)")
        print("2: ノートパソコン (UltraBook Pro, 製品ID: LT-200)")
        print("3: ワイヤレスイヤホン (SoundPods Pro, 製品ID: EP-300)")
        choice = input("\n分析する製品を選択してください (1-3): ").strip()
        if choice == "1":
            product_id = "SP-100"
        elif choice == "2":
            product_id = "LT-200"
        elif choice == "3":
            product_id = "EP-300"
        else:
            print("無効な選択です。デフォルトのスマートフォン製品を分析します。")
            product_id = "SP-100"
    else:
        product_id = args.product
    analyze_product_reviews(client, product_id, args.output)
    print("\n分析が完了しました！")
    print(f"結果は '{args.output}' ディレクトリに保存されています。")


def setup_environment():
    """環境設定を行い、APIキーを取得します。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(script_dir))
    load_dotenv(os.path.join(root_dir, ".env"))
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY が設定されていません")
    return api_key


if __name__ == "__main__":
    main()
