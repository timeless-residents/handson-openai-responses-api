"""
多言語対応ドキュメント翻訳と要約

このサンプルは、OpenAI Responses APIを使用して、
様々な言語のドキュメントを翻訳し、要約する方法を示します。
複数のファイル形式に対応し、言語検出機能も備えており、
多言語環境でのドキュメント管理や国際的なコミュニケーションを
効率化するためのツールとして利用できます。
"""

import os
import sys
import json
import re
import argparse
import datetime
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import base64
import io
import traceback

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from langdetect import detect, DetectorFactory
from nltk.tokenize import sent_tokenize
import nltk
import PyPDF2
import docx
from dotenv import load_dotenv
import openai

# 結果の再現性のために言語検出のシード値を固定
DetectorFactory.seed = 0

# 必要なNLTKデータをダウンロード
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("NLTKのpunktデータをダウンロードしています...")
    nltk.download('punkt', quiet=True)

# NLTK言語検出のためのデータをダウンロード
# punktデータは言語によって必要な場合があります
for lang in ['english', 'french', 'german', 'italian', 'spanish', 'portuguese', 'dutch', 'japanese']:
    try:
        nltk.data.find(f'tokenizers/punkt/{lang}.pickle')
    except LookupError:
        print(f"NLTK {lang} データをダウンロードしています...")
        nltk.download(f'punkt', quiet=True)

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


def read_file(file_path: str) -> Tuple[str, str]:
    """ファイルを読み込み、テキスト内容とファイル拡張子を返します。"""
    file_path = os.path.expanduser(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        # テキストファイル
        if file_ext in ['.txt', '.md', '.json', '.csv', '.py', '.js', '.html', '.css']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # PDFファイル
        elif file_ext == '.pdf':
            content = ''
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text() + '\n\n'
        
        # Word文書
        elif file_ext in ['.docx', '.doc']:
            doc = docx.Document(file_path)
            content = '\n'.join([para.text for para in doc.paragraphs])
        
        # 対応していない形式
        else:
            raise ValueError(f"対応していないファイル形式です: {file_ext}")
            
        return content, file_ext
    
    except Exception as e:
        print(f"ファイル読み込みエラー: {str(e)}")
        traceback.print_exc()
        return "", file_ext


def detect_language(text: str) -> str:
    """テキストの言語を検出します。"""
    try:
        language = detect(text[:5000])  # 長いテキストの場合は最初の5000文字のみ使用
        return language
    except:
        return "unknown"


def get_language_name(language_code: str) -> str:
    """言語コードから言語名を取得します。"""
    language_dict = {
        'en': '英語',
        'ja': '日本語',
        'zh-cn': '中国語（簡体字）',
        'zh-tw': '中国語（繁体字）',
        'ko': '韓国語',
        'fr': 'フランス語',
        'de': 'ドイツ語',
        'es': 'スペイン語',
        'it': 'イタリア語',
        'ru': 'ロシア語',
        'pt': 'ポルトガル語',
        'ar': 'アラビア語',
        'hi': 'ヒンディー語',
        'bn': 'ベンガル語',
        'pa': 'パンジャブ語',
        'jw': 'ジャワ語',
        'vi': 'ベトナム語',
        'th': 'タイ語',
        'tr': 'トルコ語',
        'nl': 'オランダ語',
        'pl': 'ポーランド語',
        'unknown': '不明'
    }
    
    return language_dict.get(language_code, f'その他 ({language_code})')


def chunk_text(text: str, max_chunk_size: int = 4000) -> List[str]:
    """テキストを文単位で分割し、指定サイズ以下のチャンクに分けます。"""
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # この文を追加しても最大サイズを超えない場合
        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
            current_chunk += sentence + " "
        # 最大サイズを超える場合
        else:
            # 現在のチャンクが空でなければリストに追加
            if current_chunk:
                chunks.append(current_chunk.strip())
            # 新しいチャンクを開始
            current_chunk = sentence + " "
    
    # 最後のチャンクをリストに追加
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def calculate_chunk_statistics(chunks: List[str]) -> Dict[str, Any]:
    """チャンク分割の統計情報を計算します。"""
    chunk_lengths = [len(chunk) for chunk in chunks]
    return {
        "chunk_count": len(chunks),
        "avg_chunk_length": np.mean(chunk_lengths) if chunk_lengths else 0,
        "min_chunk_length": min(chunk_lengths) if chunk_lengths else 0,
        "max_chunk_length": max(chunk_lengths) if chunk_lengths else 0,
        "median_chunk_length": np.median(chunk_lengths) if chunk_lengths else 0
    }


def translate_text(
    client, text: str, source_lang: str, target_lang: str, 
    preserve_formatting: bool = True, tech_terms: List[str] = None
) -> str:
    """テキストを翻訳します。"""
    # 技術用語リストを整形
    tech_terms_str = ""
    if tech_terms and len(tech_terms) > 0:
        tech_terms_str = "以下の専門用語や固有名詞は適切に処理してください：\n" + "\n".join(tech_terms)
    
    # 翻訳指示を生成
    source_lang_name = get_language_name(source_lang)
    target_lang_name = get_language_name(target_lang)
    
    if preserve_formatting:
        formatting_instruction = "元のテキストの書式（段落、箇条書き、強調など）を可能な限り維持してください。"
    else:
        formatting_instruction = ""
    
    # テキストを適切なサイズにチャンク分割
    chunks = chunk_text(text)
    translated_chunks = []
    
    for i, chunk in enumerate(chunks):
        print(f"チャンク {i+1}/{len(chunks)} を翻訳中...")
        
        instruction = f"""
        これから{source_lang_name}から{target_lang_name}への翻訳をお願いします。

        【翻訳指示】
        - 正確で自然な翻訳を心がけてください
        - 原文の意味や文脈が正確に反映されるようにしてください
        - {target_lang_name}のネイティブスピーカーが読んで自然な表現を使ってください
        - {formatting_instruction}
        {tech_terms_str}

        あなたは専門的な翻訳者として、上記の指示に従って以下のテキストを翻訳してください。
        """
        
        try:
            response = client.responses.create(
                model="gpt-4o",
                instructions=instruction,
                input=[{"role": "user", "content": [{"type": "input_text", "text": chunk}]}],
                max_output_tokens=4096,
            )
            
            translated_chunks.append(response.output_text)
            
            # APIレート制限を避けるために少し待機
            time.sleep(0.5)
            
        except Exception as e:
            print(f"翻訳エラー（チャンク {i+1}）: {str(e)}")
            translated_chunks.append(f"[翻訳エラー: {str(e)}]")
            traceback.print_exc()
    
    # 翻訳されたチャンクを結合
    result = "\n".join(translated_chunks)
    return result


def summarize_text(
    client, text: str, language: str, summary_length: str = "medium", 
    focus_area: str = "general", format_as_bullets: bool = False
) -> str:
    """テキストを要約します。"""
    # 要約長の設定
    length_settings = {
        "short": "全体の内容を簡潔に要約し、単一の段落（約100-200単語）にまとめてください。",
        "medium": "重要なポイントを網羅する中程度の要約（約300-500単語）を作成してください。",
        "detailed": "主要な情報をしっかりと含む詳細な要約（約700-1000単語）を作成してください。"
    }
    
    # 要約の焦点領域
    focus_settings = {
        "general": "文書全体の重要なポイントをバランスよく含めてください。",
        "technical": "技術的な詳細や仕様に焦点を当てて要約してください。",
        "business": "ビジネス関連の情報や市場動向、戦略的側面に焦点を当ててください。",
        "academic": "学術的な知見、方法論、研究結果に焦点を当ててください。",
    }
    
    # 出力形式
    format_instruction = "箇条書きのリスト形式で要約を提示してください。" if format_as_bullets else "段落形式で要約を提示してください。"
    
    # テキストを適切なサイズにチャンク分割
    chunks = chunk_text(text)
    
    # チャンクが1つの場合は直接要約
    if len(chunks) == 1:
        instruction = f"""
        次のテキストを要約してください。

        【要約指示】
        - {length_settings.get(summary_length, length_settings["medium"])}
        - {focus_settings.get(focus_area, focus_settings["general"])}
        - {format_instruction}
        - {get_language_name(language)}で要約を作成してください。
        """
        
        try:
            response = client.responses.create(
                model="gpt-4o",
                instructions=instruction,
                input=[{"role": "user", "content": [{"type": "input_text", "text": text}]}],
                max_output_tokens=4096,
            )
            
            return response.output_text
            
        except Exception as e:
            print(f"要約エラー: {str(e)}")
            traceback.print_exc()
            return f"[要約エラー: {str(e)}]"
    
    # 複数チャンクの場合は階層的要約
    else:
        print(f"テキストが長いため、{len(chunks)}チャンクを段階的に要約します...")
        
        # 各チャンクの要約を生成
        chunk_summaries = []
        
        for i, chunk in enumerate(chunks):
            print(f"チャンク {i+1}/{len(chunks)} を要約中...")
            
            chunk_instruction = f"""
            次のテキストのセクションを要約してください。
            これは長い文書の一部であり、最終的にこのセクションの要約を他のセクションと組み合わせます。

            【要約指示】
            - このセクションの重要なポイントを簡潔に要約してください。
            - {get_language_name(language)}で作成してください。
            """
            
            try:
                response = client.responses.create(
                    model="gpt-4o",
                    instructions=chunk_instruction,
                    input=[{"role": "user", "content": [{"type": "input_text", "text": chunk}]}],
                    max_output_tokens=2048,
                )
                
                chunk_summaries.append(response.output_text)
                
                # APIレート制限を避けるために少し待機
                time.sleep(0.5)
                
            except Exception as e:
                print(f"セクション要約エラー（チャンク {i+1}）: {str(e)}")
                chunk_summaries.append(f"[要約エラー: {str(e)}]")
                traceback.print_exc()
        
        # 最終的な要約を生成
        combined_summaries = "\n\n".join(chunk_summaries)
        
        final_instruction = f"""
        以下は長い文書の各セクションから生成された要約です。
        これらの要約を統合して、文書全体の一貫性のある要約を作成してください。

        【要約指示】
        - {length_settings.get(summary_length, length_settings["medium"])}
        - {focus_settings.get(focus_area, focus_settings["general"])}
        - {format_instruction}
        - {get_language_name(language)}で要約を作成してください。
        - 重複を排除し、情報を整理して、一貫性のある流れで要約を提示してください。
        """
        
        try:
            response = client.responses.create(
                model="gpt-4o",
                instructions=final_instruction,
                input=[{"role": "user", "content": [{"type": "input_text", "text": combined_summaries}]}],
                max_output_tokens=4096,
            )
            
            return response.output_text
            
        except Exception as e:
            print(f"最終要約エラー: {str(e)}")
            traceback.print_exc()
            return f"[最終要約エラー: {str(e)}]"


def analyze_document(text: str, language: str) -> Dict[str, Any]:
    """ドキュメントの分析を行います。"""
    # 簡易的な文書分析を実行
    total_chars = len(text)
    total_words = len(text.split())
    
    # 言語に応じた文の分割処理
    try:
        sentences = sent_tokenize(text)
    except Exception as e:
        print(f"文の分割処理でエラーが発生しました: {str(e)}")
        # エラーが発生した場合は改行で分割するフォールバック
        sentences = [s.strip() for s in text.split('\n') if s.strip()]
        print(f"改行による分割を使用します。{len(sentences)}の段落が検出されました。")
    
    total_sentences = len(sentences)
    
    # 平均文長を計算
    avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
    
    # 文の長さの分布を計算
    sentence_lengths = [len(s.split()) for s in sentences]
    
    return {
        "language": language,
        "language_name": get_language_name(language),
        "total_chars": total_chars,
        "total_words": total_words,
        "total_sentences": total_sentences,
        "avg_sentence_length": avg_sentence_length,
        "sentence_length_stats": {
            "min": min(sentence_lengths) if sentence_lengths else 0,
            "max": max(sentence_lengths) if sentence_lengths else 0,
            "median": np.median(sentence_lengths) if sentence_lengths else 0
        }
    }


def create_document_report(
    content: str, analysis: Dict[str, Any], summary: str = None, 
    translated_text: str = None, target_lang: str = None
) -> str:
    """ドキュメントの分析レポートを作成します。"""
    report = f"""# ドキュメント分析レポート
生成日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 基本情報
- 言語: {analysis['language_name']} ({analysis['language']})
- 文字数: {analysis['total_chars']}
- 単語数: {analysis['total_words']}
- 文の数: {analysis['total_sentences']}
- 平均文長: {analysis['avg_sentence_length']:.2f} 単語

## 文の長さの統計
- 最短: {analysis['sentence_length_stats']['min']} 単語
- 最長: {analysis['sentence_length_stats']['max']} 単語
- 中央値: {analysis['sentence_length_stats']['median']} 単語
"""

    if summary:
        report += f"\n## 要約\n{summary}\n"
    
    if translated_text and target_lang:
        report += f"\n## {get_language_name(target_lang)}への翻訳\n{translated_text}\n"
    
    return report


def save_output(content: str, file_path: str, mode: str = "w") -> None:
    """出力内容をファイルに保存します。"""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, mode, encoding="utf-8") as f:
            f.write(content)
        print(f"出力を保存しました: {file_path}")
    except Exception as e:
        print(f"ファイル保存エラー: {str(e)}")
        traceback.print_exc()


def plot_sentence_distribution(analysis: Dict[str, Any], text: str, file_path: str) -> None:
    """文の長さの分布をプロットして保存します。"""
    try:
        # 言語に応じた文の分割処理
        try:
            sentences = sent_tokenize(text)
        except Exception:
            # エラーが発生した場合は改行で分割するフォールバック
            sentences = [s.strip() for s in text.split('\n') if s.strip()]
        
        # 文の長さ（単語数）を計算
        sentence_lengths = [len(s.split()) for s in sentences]
        
        plt.figure(figsize=(10, 6))
        sns.histplot(sentence_lengths, bins=20, kde=True)
        plt.title(f"文の長さの分布 - {analysis['language_name']}")
        plt.xlabel("単語数")
        plt.ylabel("頻度")
        plt.grid(True, alpha=0.3)
        plt.savefig(file_path, dpi=100, bbox_inches="tight")
        plt.close()
        print(f"分布図を保存しました: {file_path}")
    except Exception as e:
        print(f"グラフ作成エラー: {str(e)}")
        traceback.print_exc()


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="多言語対応ドキュメント翻訳と要約")
    parser.add_argument("--file", "-f", type=str, required=True, help="処理するファイルのパス")
    parser.add_argument(
        "--mode", "-m", type=str, default="all", 
        choices=["translate", "summarize", "analyze", "all"],
        help="実行モード（translate: 翻訳のみ, summarize: 要約のみ, analyze: 分析のみ, all: すべて実行）"
    )
    parser.add_argument(
        "--target-lang", "-t", type=str, default="ja",
        help="翻訳の対象言語（ISO 639-1コード: en, ja, zh-cn, fr, de, es, etc.）"
    )
    parser.add_argument(
        "--summary-length", type=str, default="medium",
        choices=["short", "medium", "detailed"],
        help="要約の長さ（short: 短い, medium: 中程度, detailed: 詳細）"
    )
    parser.add_argument(
        "--summary-focus", type=str, default="general",
        choices=["general", "technical", "business", "academic"],
        help="要約の焦点（general: 一般的, technical: 技術的, business: ビジネス, academic: 学術的）"
    )
    parser.add_argument(
        "--bullet-points", action="store_true",
        help="要約を箇条書き形式で出力"
    )
    parser.add_argument(
        "--preserve-formatting", action="store_true",
        help="翻訳時に元の書式を保持"
    )
    parser.add_argument(
        "--tech-terms", type=str, nargs="*", default=[],
        help="保持すべき技術用語や固有名詞のリスト"
    )
    parser.add_argument(
        "--output-dir", "-o", type=str, default="output",
        help="出力ディレクトリ"
    )
    
    args = parser.parse_args()
    
    # ファイルが存在するか確認
    if not os.path.exists(args.file):
        print(f"指定されたファイルが見つかりません: {args.file}")
        return
    
    try:
        # 環境設定とクライアント初期化
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)
        
        # ファイル読み込み
        print(f"ファイルを読み込んでいます: {args.file}")
        content, file_ext = read_file(args.file)
        
        if not content:
            print("ファイルの内容が空または読み込みに失敗しました。")
            return
        
        # 言語検出
        print("言語を検出しています...")
        source_lang = detect_language(content)
        print(f"検出された言語: {get_language_name(source_lang)} ({source_lang})")
        
        # 出力ディレクトリの作成
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(script_dir))
        output_dir = os.path.join(root_dir, args.output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # ベースとなる出力ファイル名
        file_base = os.path.splitext(os.path.basename(args.file))[0]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # ドキュメント分析
        print("ドキュメントを分析しています...")
        analysis = analyze_document(content, source_lang)
        
        # モードに応じた処理
        translated_text = None
        summary = None
        
        if args.mode in ["translate", "all"]:
            print(f"{get_language_name(source_lang)}から{get_language_name(args.target_lang)}へ翻訳しています...")
            translated_text = translate_text(
                client, content, source_lang, args.target_lang,
                preserve_formatting=args.preserve_formatting,
                tech_terms=args.tech_terms
            )
            
            # 翻訳結果を保存
            translated_file = os.path.join(output_dir, f"{file_base}_{args.target_lang}_{timestamp}.txt")
            save_output(translated_text, translated_file)
        
        if args.mode in ["summarize", "all"]:
            # 要約を生成する言語を決定（翻訳モードの場合は対象言語、それ以外は元の言語）
            summary_lang = args.target_lang if args.mode == "all" else source_lang
            summary_text = content if summary_lang == source_lang else (translated_text or "")
            
            if summary_text:
                print(f"{get_language_name(summary_lang)}で要約を生成しています...")
                summary = summarize_text(
                    client, summary_text, summary_lang,
                    summary_length=args.summary_length,
                    focus_area=args.summary_focus,
                    format_as_bullets=args.bullet_points
                )
                
                # 要約結果を保存
                summary_file = os.path.join(output_dir, f"{file_base}_summary_{summary_lang}_{timestamp}.txt")
                save_output(summary, summary_file)
        
        # 分析レポートを作成
        if args.mode in ["analyze", "all"]:
            report = create_document_report(
                content, analysis, summary, translated_text, args.target_lang
            )
            
            # 分析レポートを保存
            report_file = os.path.join(output_dir, f"{file_base}_report_{timestamp}.md")
            save_output(report, report_file)
            
            # 統計グラフを生成
            graph_file = os.path.join(output_dir, f"{file_base}_sentence_dist_{timestamp}.png")
            plot_sentence_distribution(analysis, content, graph_file)
        
        print("処理が完了しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()