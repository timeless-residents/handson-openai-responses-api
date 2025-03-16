"""
マーケティングコンテンツの自動生成

このサンプルは、OpenAI Responses APIを使用して、
様々なマーケティングコンテンツを生成する方法を示します。
ソーシャルメディア投稿、ブログ記事、メールニュースレター、
プレスリリース、広告コピーなど、多様なマーケティング素材を
対象とした活用例を提供します。
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional, Union
import base64
import io
from pathlib import Path
import time
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from PIL import Image
from dotenv import load_dotenv
import openai
from tqdm import tqdm


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


def load_product_data(file_path: Optional[str] = None) -> Dict[str, Any]:
    """商品データを読み込みます。指定がない場合はサンプルデータを使用。"""
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # サンプル商品データを返す
        return {
            "name": "EcoBoost Pro 5000",
            "category": "家電",
            "sub_category": "空気清浄機",
            "description": "次世代型スマート空気清浄機。PM2.5、花粉、ペットの毛などを99.97%除去する高性能HEPAフィルターを搭載。スマートフォンアプリと連携し、外出先からも操作可能。自動モードでは、内蔵センサーが空気の汚れを検知して自動で運転レベルを調整します。静音設計で寝室でも快適に使用できます。",
            "features": [
                "高性能HEPAフィルター搭載",
                "スマートフォンアプリ連携",
                "AIによる自動運転モード",
                "静音設計（最小18db）",
                "省エネ設計（年間電気代約2,000円）",
                "スタイリッシュなデザイン",
                "8畳~16畳対応",
                "フィルター交換お知らせ機能"
            ],
            "benefits": [
                "アレルギー症状の軽減",
                "睡眠の質の向上",
                "ペットの匂いを軽減",
                "花粉シーズンも快適に過ごせる",
                "子どもやお年寄りがいる家庭も安心"
            ],
            "specifications": {
                "サイズ": "幅30cm × 奥行30cm × 高さ60cm",
                "重量": "5.2kg",
                "消費電力": "5W-45W",
                "運転音": "18db-45db",
                "適用畳数": "8畳~16畳",
                "フィルター寿命": "約1年",
                "カラー": "ホワイト、シルバー、ブラック"
            },
            "price": {
                "regular": 49800,
                "sale": 39800,
                "currency": "円"
            },
            "availability": "在庫あり",
            "release_date": "2023年9月15日",
            "target_audience": [
                "アレルギー持ちの方",
                "小さなお子様がいるご家庭",
                "ペットを飼っている方",
                "空気の質にこだわる方",
                "スマートホーム製品愛好家"
            ],
            "unique_selling_points": [
                "業界トップクラスの静音性",
                "アプリによる詳細な空気質レポート機能",
                "デザイン賞受賞のスタイリッシュな外観",
                "他社製スマートホーム製品との連携"
            ],
            "testimonials": [
                {
                    "name": "佐藤健太",
                    "age": 42,
                    "comment": "花粉症に悩まされていましたが、このEcoBoost Proを使い始めてから症状が劇的に改善しました。朝起きたときの目のかゆみや鼻づまりがほとんどなくなりました。"
                },
                {
                    "name": "鈴木美咲",
                    "age": 35,
                    "comment": "2歳の子どもがいるので、空気の質には特に気を使っています。アプリで常に空気の状態が確認できるので安心感が違います。静かなのも子どもの寝室に置くのに最適です。"
                },
                {
                    "name": "田中誠",
                    "age": 28,
                    "comment": "猫を2匹飼っているのですが、以前は来客時に猫の匂いを指摘されることがありました。使い始めてからは、そのようなことがなくなり、自分でも空気の綺麗さの違いを実感しています。"
                }
            ],
            "comparison": [
                {
                    "competitor": "CleanAir X3",
                    "price": 52000,
                    "pros": ["フィルター寿命が長い", "デザイン性が高い"],
                    "cons": ["運転音が大きい", "アプリの使い勝手が悪い", "消費電力が大きい"]
                },
                {
                    "competitor": "PureZone 2000",
                    "price": 34800,
                    "pros": ["価格が安い", "軽量"],
                    "cons": ["適用畳数が小さい", "フィルター交換が頻繁", "スマート機能なし"]
                }
            ],
            "images": {
                "main": "product_main.jpg",
                "lifestyle": ["lifestyle1.jpg", "lifestyle2.jpg"],
                "details": ["detail1.jpg", "detail2.jpg"]
            },
            "marketing_points": {
                "headline": "空気をきれいに、生活を健やかに",
                "tagline": "次世代スマート空気清浄機",
                "campaign_theme": "Breathe Better, Live Better",
                "seasonal_focus": {
                    "spring": "花粉対策",
                    "summer": "熱中症対策と空気循環",
                    "autumn": "乾燥対策",
                    "winter": "ウイルス対策"
                },
                "keywords": [
                    "空気清浄機", "スマートホーム", "花粉対策", "ペット", "アレルギー", 
                    "HEPAフィルター", "静音", "省エネ", "IoT家電", "空気質", "健康"
                ]
            }
        }


def load_brand_info(file_path: Optional[str] = None) -> Dict[str, Any]:
    """ブランド情報を読み込みます。指定がない場合はサンプルデータを使用。"""
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # サンプルブランド情報を返す
        return {
            "name": "TechEco",
            "founded": 2010,
            "mission": "環境に配慮した革新的なテクノロジーで、より健康で快適な生活を実現する",
            "vision": "持続可能な未来のために、省エネで高性能なスマート家電を世界中に広める",
            "values": [
                "環境への配慮",
                "革新的な技術開発",
                "品質と信頼性",
                "顧客中心主義",
                "持続可能性"
            ],
            "brand_voice": {
                "tone": "専門的かつ親しみやすい",
                "personality": "信頼性があり、革新的で、環境に配慮した",
                "language_style": "明確でわかりやすく、専門用語は必要最小限に"
            },
            "target_markets": [
                "環境意識の高い消費者",
                "テクノロジー愛好家",
                "健康志向の家族",
                "都市部の若いプロフェッショナル",
                "スマートホーム導入者"
            ],
            "competitors": ["EcoTech", "GreenLiving", "SmartLife", "PureHome"],
            "social_media": {
                "platforms": ["Instagram", "Twitter", "Facebook", "LinkedIn", "YouTube"],
                "follower_count": {
                    "Instagram": 50000,
                    "Twitter": 35000,
                    "Facebook": 45000,
                    "LinkedIn": 20000,
                    "YouTube": 30000
                },
                "posting_frequency": {
                    "Instagram": "週3回",
                    "Twitter": "毎日",
                    "Facebook": "週2回",
                    "LinkedIn": "週1回",
                    "YouTube": "月2回"
                }
            },
            "website": "https://www.techeco.com",
            "slogan": "テクノロジーで地球と暮らしを豊かに",
            "brand_colors": {
                "primary": "#00796B",  # 深い緑
                "secondary": "#4CAF50",  # 明るい緑
                "accent": "#FFC107",  # 黄色
                "neutral": "#FAFAFA"  # 薄い灰色
            },
            "logo": "techeco_logo.png"
        }


def load_campaign_info(file_path: Optional[str] = None) -> Dict[str, Any]:
    """キャンペーン情報を読み込みます。指定がない場合はサンプルデータを使用。"""
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # サンプルキャンペーン情報を返す
        return {
            "name": "クリーンエア・サマーキャンペーン",
            "concept": "夏の暑さと汚れた空気から解放され、快適な夏を過ごそう",
            "duration": "2023年6月1日〜8月31日",
            "target_audience": [
                {
                    "segment": "アレルギー持ちの方",
                    "pain_points": ["夏の花粉", "ハウスダスト", "睡眠障害"],
                    "motivations": ["症状の緩和", "快適な睡眠", "家族の健康"]
                },
                {
                    "segment": "ペットオーナー",
                    "pain_points": ["ペットの毛", "におい", "来客時の恥ずかしさ"],
                    "motivations": ["清潔な家", "来客時の安心", "ペットの健康"]
                },
                {
                    "segment": "在宅ワーカー",
                    "pain_points": ["長時間の室内滞在", "集中力低下", "疲労感"],
                    "motivations": ["作業効率向上", "快適な作業環境", "健康維持"]
                }
            ],
            "key_messages": [
                "夏こそ空気清浄が重要な理由",
                "テクノロジーで変わる夏の室内環境",
                "睡眠の質を高め、夏を元気に過ごす",
                "家族の健康を守る見えない働き"
            ],
            "promotion": {
                "discount": "期間限定20%オフ",
                "gifts": "フィルター1年分プレゼント",
                "special_offer": "2台購入で配送料無料"
            },
            "channels": {
                "owned": ["公式サイト", "メールマガジン", "LINEアカウント"],
                "paid": ["Google広告", "SNS広告", "インフルエンサーマーケティング"],
                "earned": ["ユーザーレビュー", "メディア掲載", "SNSシェア"]
            },
            "content_plan": {
                "blogs": [
                    "夏の空気汚染:知っておくべき5つのこと",
                    "在宅ワーク環境を改善する簡単な方法",
                    "専門家が教える、アレルギー症状を軽減する室内環境作り"
                ],
                "social_media": [
                    "使用者のビフォーアフター体験",
                    "製品の特徴紹介シリーズ",
                    "質問回答セッション",
                    "季節のヘルスケアTips"
                ],
                "emails": [
                    "キャンペーン開始告知",
                    "ユーザー体験談シリーズ",
                    "限定タイムセール",
                    "関連コンテンツニュースレター"
                ],
                "videos": [
                    "製品機能詳細解説",
                    "実際の使用シーン",
                    "専門家インタビュー"
                ]
            },
            "success_metrics": {
                "sales_targets": "前年同期比30%増",
                "engagement": "SNSエンゲージメント率5%以上",
                "leads": "新規リード獲得3000件",
                "conversion": "ウェブサイト訪問からの購入率3%向上"
            },
            "hashtags": [
                "#クリーンエア2023",
                "#TechEcoサマー",
                "#健康な夏",
                "#スマート空気清浄"
            ]
        }


def encode_image_base64(image_path: str) -> str:
    """画像をbase64エンコードします。"""
    if not os.path.exists(image_path):
        return ""
    
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_social_media_posts(
    client, product_data: Dict[str, Any], brand_info: Dict[str, Any], campaign_info: Dict[str, Any], 
    platform: str = "Instagram", count: int = 3, style: str = "general"
) -> List[Dict[str, Any]]:
    """特定のソーシャルメディアプラットフォーム向けの投稿を生成します。"""
    
    # スタイルに応じたガイダンスを設定
    style_guidance = {
        "general": "一般的なトーンで明確でわかりやすい投稿を作成します",
        "casual": "親しみやすく、会話的なトーンでカジュアルな投稿を作成します",
        "professional": "専門的で信頼性のある、ビジネスライクな投稿を作成します",
        "playful": "楽しくて遊び心のある、エンターテイニングな投稿を作成します",
        "educational": "情報価値が高く、読者に知識を提供する教育的な投稿を作成します",
        "promotional": "商品の魅力を直接的に伝え、購入を促す宣伝的な投稿を作成します",
        "emotional": "感情に訴えかけ、共感を生むストーリーテリング重視の投稿を作成します",
        "minimalist": "簡潔かつ洗練された、余計な装飾のない最小限の投稿を作成します",
    }
    
    # プラットフォーム別の特徴を設定
    platform_specs = {
        "Instagram": {
            "max_length": 2200,  # キャプションの最大文字数
            "hashtag_count": "5-10",  # 推奨ハッシュタグ数
            "emphasis": "視覚的要素を強調し、感情や体験を伝える",
            "format": "画像重視のキャプション、絵文字の適度な使用、ハッシュタグ"
        },
        "Twitter": {
            "max_length": 280,  # ツイートの最大文字数
            "hashtag_count": "1-3",  # 推奨ハッシュタグ数
            "emphasis": "簡潔で共有しやすい情報、時事的な内容",
            "format": "短文、リンク、絵文字やハッシュタグの戦略的使用"
        },
        "Facebook": {
            "max_length": 63206,  # 長文OK（実際の制限は非常に大きい）
            "hashtag_count": "1-2",  # 推奨ハッシュタグ数（少なめ）
            "emphasis": "コミュニティとの対話、詳細情報の共有",
            "format": "より詳細な説明、質問の投げかけ、コメント誘導"
        },
        "LinkedIn": {
            "max_length": 3000,  # テキスト投稿の最大文字数
            "hashtag_count": "3-5",  # 推奨ハッシュタグ数
            "emphasis": "プロフェッショナルな洞察、業界関連情報、専門知識",
            "format": "専門的な文体、パラグラフ分け、業界ハッシュタグの活用"
        }
    }
    
    # 入力プロンプトの作成
    prompt = f"""
    {platform}向けのソーシャルメディア投稿{count}件を作成してください。
    
    【製品情報】
    製品名: {product_data['name']}
    カテゴリ: {product_data['category']} > {product_data['sub_category']}
    説明: {product_data['description']}
    主な特徴: {', '.join(product_data['features'][:3])}
    主なメリット: {', '.join(product_data['benefits'][:3])}
    セールスポイント: {', '.join(product_data['unique_selling_points'][:2])}
    
    【ブランド情報】
    ブランド名: {brand_info['name']}
    スローガン: {brand_info['slogan']}
    ブランドボイス: {brand_info['brand_voice']['tone']}
    
    【キャンペーン情報】
    キャンペーン名: {campaign_info['name']}
    コンセプト: {campaign_info['concept']}
    プロモーション: {campaign_info['promotion']['discount']}
    ハッシュタグ: {', '.join(campaign_info['hashtags'][:3])}
    
    【投稿スタイル】
    スタイル: {style} - {style_guidance[style]}
    
    【プラットフォーム仕様】
    プラットフォーム: {platform}
    最大文字数: {platform_specs[platform]['max_length']}文字
    推奨ハッシュタグ数: {platform_specs[platform]['hashtag_count']}個
    重視すべき点: {platform_specs[platform]['emphasis']}
    フォーマット: {platform_specs[platform]['format']}
    
    各投稿には以下の要素を含めてください：
    1. キャッチーな書き出し
    2. 製品の主な特徴やベネフィットの簡潔な説明
    3. ターゲットオーディエンスの課題解決方法
    4. 明確なCTA（行動喚起）
    5. 適切なハッシュタグ
    6. 必要に応じて絵文字を活用
    
    各投稿は、メインテキスト、ハッシュタグ、そして画像のキャプション提案を含めてください。
    """
    
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions=f"{brand_info['name']}のマーケティング担当者として、効果的なソーシャルメディア投稿を作成してください。{brand_info['brand_voice']['tone']}なトーンを維持し、ブランドの価値観と一致する内容を心がけてください。",
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            max_output_tokens=4000,
        )
        
        # 結果のパース
        result_text = response.output_text
        
        # 投稿をリスト形式に整形
        posts = []
        current_post = {"platform": platform, "style": style}
        
        # 簡易的なパース処理（実際の出力形式によって調整が必要）
        for line in result_text.split('\n'):
            if line.strip().startswith("投稿") or line.strip().startswith("===") or line.strip().startswith("---"):
                if "text" in current_post:  # 投稿データが存在する場合は追加
                    posts.append(current_post)
                    current_post = {"platform": platform, "style": style}
            elif ":" in line and not line.strip().startswith("#"):
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key == "メインテキスト" or key == "本文" or key == "テキスト" or key == "キャプション":
                    current_post["text"] = value
                elif key == "ハッシュタグ" or key == "タグ":
                    current_post["hashtags"] = value
                elif key == "cta" or key == "行動喚起":
                    current_post["cta"] = value
                elif key == "画像キャプション" or key == "画像説明":
                    current_post["image_caption"] = value
            else:
                # 特定のキーが見つからない場合は、現在処理中のフィールドに追加
                for field in ["text", "hashtags", "cta", "image_caption"]:
                    if field in current_post:
                        current_post[field] += "\n" + line
        
        # 最後の投稿を追加
        if "text" in current_post:
            posts.append(current_post)
        
        # 不完全な投稿を除外
        posts = [post for post in posts if "text" in post and post["text"]]
        
        # 指定数だけ返す
        return posts[:count]
        
    except Exception as e:
        print(f"ソーシャルメディア投稿の生成中にエラーが発生しました: {str(e)}")
        return []


def generate_blog_post(
    client, product_data: Dict[str, Any], brand_info: Dict[str, Any], topic: str,
    word_count: int = 800, target_audience: Optional[str] = None, seo_keywords: Optional[List[str]] = None
) -> Dict[str, Any]:
    """指定されたトピックとターゲットオーディエンス向けのブログ記事を生成します。"""
    
    # ターゲットオーディエンスが指定されていない場合は製品データから取得
    if not target_audience and "target_audience" in product_data:
        target_audience = ", ".join(product_data["target_audience"][:3])
    elif not target_audience:
        target_audience = "一般消費者"
    
    # SEOキーワードが指定されていない場合は製品データから取得
    if not seo_keywords and "marketing_points" in product_data and "keywords" in product_data["marketing_points"]:
        seo_keywords = product_data["marketing_points"]["keywords"][:5]
    elif not seo_keywords:
        seo_keywords = [product_data["category"], product_data["sub_category"], product_data["name"]]
    
    # 入力プロンプトの作成
    prompt = f"""
    以下の情報をもとに、ブログ記事を作成してください。
    
    【ブログ情報】
    タイトル/トピック: {topic}
    推奨単語数: 約{word_count}語
    対象読者: {target_audience}
    SEOキーワード: {', '.join(seo_keywords)}
    
    【製品情報】
    製品名: {product_data['name']}
    カテゴリ: {product_data['category']} > {product_data['sub_category']}
    説明: {product_data['description']}
    主な特徴: {', '.join(product_data['features'])}
    主なメリット: {', '.join(product_data['benefits'])}
    価格: {product_data['price']['regular']}円
    
    【ブランド情報】
    ブランド名: {brand_info['name']}
    ミッション: {brand_info['mission']}
    ブランドボイス: {brand_info['brand_voice']['tone']}
    
    ブログ記事には以下の要素を含めてください：
    1. 読者の注意を引く魅力的な導入部
    2. トピックの重要性や背景情報の説明
    3. 問題提起とその解決策の提示
    4. {product_data['name']}がどのように解決策となるかの説明
    5. 具体的なユースケースや活用方法
    6. 統計データや研究結果などの事実に基づく情報（架空でも可）
    7. 読者への質問や考えるきっかけを与える内容
    8. 明確な結論とCTA（Call to Action）
    
    記事はSEO最適化をしつつも、読者にとって価値のある情報を提供する内容にしてください。
    見出し（H2, H3等）を適切に使用し、読みやすい構成にしてください。
    """
    
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions=f"{brand_info['name']}のコンテンツマーケターとして、情報価値が高く魅力的なブログ記事を作成してください。{brand_info['brand_voice']['tone']}なトーンを維持しながら、読者にとって役立つ知識と洞察を提供することを心がけてください。",
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            max_output_tokens=4000,
        )
        
        # 結果の整形とメタデータの追加
        blog_post = {
            "title": topic,
            "content": response.output_text,
            "word_count": len(response.output_text.split()),
            "target_audience": target_audience,
            "seo_keywords": seo_keywords,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "product": product_data["name"],
            "brand": brand_info["name"]
        }
        
        return blog_post
        
    except Exception as e:
        print(f"ブログ記事の生成中にエラーが発生しました: {str(e)}")
        return {
            "title": topic,
            "content": f"エラーが発生しました: {str(e)}",
            "error": True
        }


def generate_email_newsletter(
    client, product_data: Dict[str, Any], brand_info: Dict[str, Any], campaign_info: Dict[str, Any],
    email_type: str = "promotional", target_segment: Optional[str] = None
) -> Dict[str, Any]:
    """特定のタイプとターゲットセグメント向けのメールニュースレターを生成します。"""
    
    # メールのタイプに応じた情報を設定
    email_types = {
        "promotional": {
            "purpose": "新商品や特別オファーの宣伝",
            "tone": "熱意があり直接的",
            "structure": "魅力的な見出し、主要セールスポイント、明確なCTA",
            "content_focus": "製品の特徴とメリット、特別オファーの詳細",
            "cta": "今すぐ購入、詳細を見る"
        },
        "welcome": {
            "purpose": "新規購読者への歓迎と紹介",
            "tone": "友好的で励ますような",
            "structure": "歓迎メッセージ、ブランド紹介、次のステップ",
            "content_focus": "ブランドストーリー、提供価値、期待される内容",
            "cta": "ウェブサイトを探索、SNSでフォロー"
        },
        "educational": {
            "purpose": "価値ある情報やインサイトの提供",
            "tone": "情報提供的で洞察に富む",
            "structure": "興味深い導入、主要なポイント、関連リソース",
            "content_focus": "業界のトレンド、使用方法のヒント、専門知識",
            "cta": "詳細を学ぶ、リソースをダウンロード"
        },
        "newsletter": {
            "purpose": "定期的な更新と様々なコンテンツの提供",
            "tone": "会話的でエンゲージメントを促す",
            "structure": "簡潔な導入、複数のセクション、様々なCTA",
            "content_focus": "最新ニュース、役立つコンテンツ、コミュニティハイライト",
            "cta": "記事を読む、イベントに参加、フィードバックを共有"
        },
        "announcement": {
            "purpose": "重要な発表や変更の通知",
            "tone": "明確で直接的",
            "structure": "重要な発表、影響の説明、次のステップ",
            "content_focus": "新機能、イベント詳細、重要な変更",
            "cta": "詳細を確認、アクションを取る"
        }
    }
    
    # ターゲットセグメントが指定されていない場合
    if not target_segment and "target_audience" in campaign_info:
        # キャンペーン情報からランダムにセグメントを選択
        import random
        segment_info = random.choice(campaign_info["target_audience"])
        target_segment = segment_info["segment"]
        pain_points = segment_info["pain_points"]
        motivations = segment_info["motivations"]
    else:
        # デフォルト値の設定
        target_segment = target_segment or "一般顧客"
        pain_points = ["不便", "高コスト", "時間の無駄"]
        motivations = ["効率化", "コスト削減", "生活の質向上"]
    
    email_info = email_types.get(email_type, email_types["promotional"])
    
    # 入力プロンプトの作成
    prompt = f"""
    以下の情報をもとに、{email_type}タイプのメールニュースレターを作成してください。
    
    【メール情報】
    タイプ: {email_type}
    目的: {email_info['purpose']}
    トーン: {email_info['tone']}
    構造: {email_info['structure']}
    コンテンツ重点: {email_info['content_focus']}
    推奨CTA: {email_info['cta']}
    
    【ターゲット情報】
    セグメント: {target_segment}
    課題/ペインポイント: {', '.join(pain_points)}
    動機: {', '.join(motivations)}
    
    【製品情報】
    製品名: {product_data['name']}
    説明: {product_data['description']}
    主な特徴: {', '.join(product_data['features'][:3])}
    主なメリット: {', '.join(product_data['benefits'][:3])}
    価格: 通常価格{product_data['price']['regular']}円、セール価格{product_data['price']['sale']}円
    
    【ブランド情報】
    ブランド名: {brand_info['name']}
    スローガン: {brand_info['slogan']}
    ウェブサイト: {brand_info['website']}
    
    【キャンペーン情報】
    キャンペーン名: {campaign_info['name']}
    コンセプト: {campaign_info['concept']}
    期間: {campaign_info['duration']}
    プロモーション: {campaign_info['promotion']['discount']} / {campaign_info['promotion']['gifts']}
    
    メールには以下の要素を含めてください：
    1. 注目を集める件名
    2. パーソナライズされたあいさつ
    3. 魅力的な導入文
    4. メインメッセージ（製品/オファーの詳細など）
    5. 視覚的に強調すべきポイント
    6. 明確なCTA
    7. フッター情報（連絡先、ソーシャルメディアリンクなど）
    
    HTML形式ではなく、件名、本文テキスト、CTAボタンテキストのみを提供してください。
    """
    
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions=f"{brand_info['name']}のメールマーケティング担当者として、効果的なメールニュースレターを作成してください。{brand_info['brand_voice']['tone']}なトーンを維持し、読み手の注目を引きながらも価値を提供するメールを心がけてください。",
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            max_output_tokens=4000,
        )
        
        # 結果から重要な部分を抽出
        content = response.output_text
        lines = content.split('\n')
        
        subject = ""
        body = ""
        cta_text = ""
        
        # 件名、本文、CTAテキストの抽出（単純な方法）
        for i, line in enumerate(lines):
            if '件名:' in line or 'Subject:' in line:
                subject = line.split(':', 1)[1].strip()
            elif 'CTA:' in line or 'ボタンテキスト:' in line:
                cta_text = line.split(':', 1)[1].strip()
        
        # 本文は単純に件名とCTAを除いた全テキスト
        # より洗練された方法では、正規表現やより高度な解析が必要かもしれません
        body = content
        
        email = {
            "type": email_type,
            "subject": subject or "【" + brand_info["name"] + "】" + campaign_info["name"],
            "body": body,
            "cta_text": cta_text or "詳細を見る",
            "target_segment": target_segment,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "campaign": campaign_info["name"],
            "product": product_data["name"],
            "brand": brand_info["name"]
        }
        
        return email
        
    except Exception as e:
        print(f"メールニュースレターの生成中にエラーが発生しました: {str(e)}")
        return {
            "type": email_type,
            "subject": f"{brand_info['name']} - エラーが発生しました",
            "body": f"メールニュースレターの生成中にエラーが発生しました: {str(e)}",
            "error": True
        }


def generate_ad_copy(
    client, product_data: Dict[str, Any], brand_info: Dict[str, Any], campaign_info: Dict[str, Any],
    ad_type: str = "search", platform: str = "Google", character_limit: int = 90
) -> List[Dict[str, Any]]:
    """指定された種類と文字制限の広告コピーを生成します。"""
    
    # 広告タイプに応じた情報を設定
    ad_types = {
        "search": {
            "purpose": "検索意図にマッチした広告を表示し、クリックを促す",
            "structure": "見出し（複数）+ 説明文",
            "character_limits": {
                "headlines": "30文字×3",
                "descriptions": "90文字×2"
            },
            "best_practices": "キーワードの適切な使用、明確な価値提案、行動喚起"
        },
        "display": {
            "purpose": "ビジュアルとテキストで認知度を高め、興味を引く",
            "structure": "見出し + 簡潔な説明文 + 画像",
            "character_limits": {
                "headline": "25文字",
                "description": "90文字"
            },
            "best_practices": "注目を引くビジュアル、簡潔なメッセージ、明確なCTA"
        },
        "social": {
            "purpose": "ソーシャルフィードで注目を集め、エンゲージメントを促す",
            "structure": "キャッチーな見出し + 説明文 + 画像/動画",
            "character_limits": {
                "headline": "40文字",
                "text": "125文字"
            },
            "best_practices": "ターゲットに響く文脈的なメッセージ、感情への訴えかけ"
        },
        "video": {
            "purpose": "動画広告の始めと終わりに表示し、メッセージを強化する",
            "structure": "インパクトのある見出し + 簡潔な説明 + CTA",
            "character_limits": {
                "headline": "15文字",
                "description": "60文字"
            },
            "best_practices": "最初の5秒で注目を引く、感情に訴える、明確なCTA"
        }
    }
    
    # プラットフォーム別の特徴
    platforms = {
        "Google": {
            "search_focus": "ユーザーの検索意図に対応",
            "tone": "情報提供的で実用的",
            "unique_features": "キーワードの適切な使用、拡張機能の活用"
        },
        "Facebook": {
            "search_focus": "ユーザーの興味やデモグラフィックに合わせる",
            "tone": "会話的で親しみやすい",
            "unique_features": "画像との調和、コミュニティ感の醸成"
        },
        "Instagram": {
            "search_focus": "ビジュアルに訴える",
            "tone": "インスピレーショナルで洗練された",
            "unique_features": "トレンディな表現、視覚的な魅力との連携"
        },
        "LinkedIn": {
            "search_focus": "プロフェッショナルなコンテキスト",
            "tone": "ビジネスライクで価値提案重視",
            "unique_features": "業界用語の適切な使用、プロフェッショナルな課題解決"
        }
    }
    
    ad_info = ad_types.get(ad_type, ad_types["search"])
    platform_info = platforms.get(platform, platforms["Google"])
    
    # 入力プロンプトの作成
    prompt = f"""
    以下の情報をもとに、{platform}プラットフォーム向けの{ad_type}広告コピーを5種類作成してください。
    
    【広告情報】
    タイプ: {ad_type}
    目的: {ad_info['purpose']}
    構造: {ad_info['structure']}
    文字制限: {ad_info['character_limits']}
    ベストプラクティス: {ad_info['best_practices']}
    
    【プラットフォーム特性】
    フォーカス: {platform_info['search_focus']}
    トーン: {platform_info['tone']}
    特有の機能: {platform_info['unique_features']}
    
    【製品情報】
    製品名: {product_data['name']}
    カテゴリ: {product_data['category']} > {product_data['sub_category']}
    主な特徴: {', '.join(product_data['features'][:3])}
    主なメリット: {', '.join(product_data['benefits'][:3])}
    セールスポイント: {', '.join(product_data['unique_selling_points'][:2])}
    価格: {product_data['price']['sale']}円（通常{product_data['price']['regular']}円）
    
    【ブランド情報】
    ブランド名: {brand_info['name']}
    スローガン: {brand_info['slogan']}
    
    【キャンペーン情報】
    キャンペーン名: {campaign_info['name']}
    プロモーション: {campaign_info['promotion']['discount']}
    訴求ポイント: {', '.join(campaign_info['key_messages'][:2])}
    
    以下の項目を含む広告コピーを作成してください：
    - 注目を引く見出し（複数のバリエーション）
    - 製品の主要な利点を強調する説明文
    - 明確なCTA（行動喚起）
    - 各部分の文字数カウント
    
    それぞれの広告コピーは、異なる角度や訴求ポイントを強調し、明確に区別できるものにしてください。
    文字数制限を厳守してください。
    """
    
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions=f"{brand_info['name']}の広告担当者として、効果的で説得力のある広告コピーを作成してください。{platform}の特性を理解し、{ad_type}広告に最適化されたコピーを心がけてください。文字数制限を厳守し、クリックや行動につながる明確なメッセージを作成してください。",
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            max_output_tokens=4000,
        )
        
        # 結果のパース
        result_text = response.output_text
        
        # 広告コピーをリスト形式に整形
        ad_copies = []
        current_ad = {"type": ad_type, "platform": platform}
        
        # 簡易的なパース処理（実際の出力形式によって調整が必要）
        parsing_headlines = False
        parsing_descriptions = False
        
        for line in result_text.split('\n'):
            line = line.strip()
            
            if not line:
                continue
                
            if line.startswith("広告") or line.startswith("===") or line.startswith("---") or line.startswith("##"):
                if "headlines" in current_ad or "headline" in current_ad:  # 広告データが存在する場合は追加
                    ad_copies.append(current_ad)
                    current_ad = {"type": ad_type, "platform": platform}
                parsing_headlines = False
                parsing_descriptions = False
                
            elif line.lower().startswith("headline") or line.startswith("見出し"):
                parsing_headlines = True
                parsing_descriptions = False
                current_ad["headlines"] = []
                
            elif line.lower().startswith("description") or line.startswith("説明"):
                parsing_headlines = False
                parsing_descriptions = True
                current_ad["descriptions"] = []
                
            elif line.lower().startswith("cta") or line.startswith("行動喚起"):
                parsing_headlines = False
                parsing_descriptions = False
                if ":" in line:
                    current_ad["cta"] = line.split(":", 1)[1].strip()
                
            elif parsing_headlines:
                # 文字数表示と番号を削除してヘッドラインをクリーンアップ
                cleaned_line = line
                if '(' in cleaned_line and ')' in cleaned_line:
                    cleaned_line = cleaned_line.split('(')[0].strip()
                if cleaned_line.startswith(tuple("0123456789")) and ". " in cleaned_line:
                    cleaned_line = cleaned_line.split(". ", 1)[1].strip()
                if cleaned_line:
                    current_ad["headlines"].append(cleaned_line)
                    
            elif parsing_descriptions:
                # 文字数表示と番号を削除して説明文をクリーンアップ
                cleaned_line = line
                if '(' in cleaned_line and ')' in cleaned_line:
                    cleaned_line = cleaned_line.split('(')[0].strip()
                if cleaned_line.startswith(tuple("0123456789")) and ". " in cleaned_line:
                    cleaned_line = cleaned_line.split(". ", 1)[1].strip()
                if cleaned_line:
                    current_ad["descriptions"].append(cleaned_line)
        
        # 最後の広告を追加
        if "headlines" in current_ad or "headline" in current_ad:
            ad_copies.append(current_ad)
        
        # 形式を整える
        standardized_copies = []
        for ad in ad_copies:
            standardized_ad = {
                "type": ad_type,
                "platform": platform,
                "headlines": ad.get("headlines", [])[:3],  # 最大3つのヘッドラインに制限
                "descriptions": ad.get("descriptions", [])[:2],  # 最大2つの説明文に制限
                "cta": ad.get("cta", "今すぐ見る")
            }
            standardized_copies.append(standardized_ad)
        
        return standardized_copies[:5]  # 最大5つの広告コピーを返す
        
    except Exception as e:
        print(f"広告コピーの生成中にエラーが発生しました: {str(e)}")
        return [{
            "type": ad_type,
            "platform": platform,
            "headlines": [f"エラーが発生しました"],
            "descriptions": [f"広告コピーの生成中にエラーが発生しました: {str(e)}"],
            "error": True
        }]


def generate_press_release(
    client, product_data: Dict[str, Any], brand_info: Dict[str, Any], campaign_info: Optional[Dict[str, Any]] = None,
    release_type: str = "product_launch", release_date: Optional[str] = None
) -> Dict[str, Any]:
    """指定された種類のプレスリリースを生成します。"""
    
    # リリースタイプに応じた情報を設定
    release_types = {
        "product_launch": {
            "purpose": "新製品の発表と特徴の説明",
            "focus": "製品の革新性、特徴、市場での位置づけ",
            "key_sections": "製品概要、主要機能、価格・発売日、企業コメント",
            "tone": "情報提供的かつ前向きで期待感を高める"
        },
        "company_news": {
            "purpose": "企業の重要な発表や変更の通知",
            "focus": "企業の成長、方向性の変化、経営陣の交代など",
            "key_sections": "発表概要、背景情報、影響、将来計画",
            "tone": "公式かつプロフェッショナル"
        },
        "event_announcement": {
            "purpose": "イベントやキャンペーンの告知",
            "focus": "イベントの詳細、参加メリット、背景情報",
            "key_sections": "イベント概要、日時・場所、プログラム内容、参加方法",
            "tone": "招待的かつ情報提供的"
        },
        "partnership": {
            "purpose": "他社との提携や協業の発表",
            "focus": "提携内容、シナジー効果、両社の強み",
            "key_sections": "提携概要、両社の情報、期待される効果、今後の展開",
            "tone": "コラボレーティブで前向き"
        },
        "award_recognition": {
            "purpose": "受賞や認定の発表",
            "focus": "受賞内容、評価されたポイント、業界での位置づけ",
            "key_sections": "受賞概要、選定理由、企業コメント、背景情報",
            "tone": "誇りを持ち謙虚な姿勢を示す"
        }
    }
    
    # リリース日が指定されていない場合は現在の日付を使用
    if not release_date:
        release_date = datetime.now().strftime("%Y年%m月%d日")
    
    # キャンペーン情報が提供されていない場合のデフォルト
    if not campaign_info:
        campaign_info = {
            "name": f"{product_data['name']} 新発売キャンペーン",
            "concept": "革新的な機能で日常生活をもっと快適に",
            "key_messages": [
                f"{product_data['name']}で実現する新しい生活様式",
                "最先端技術で日常の悩みを解決",
                "スマートな選択で未来を変える"
            ]
        }
    
    release_info = release_types.get(release_type, release_types["product_launch"])
    
    # 入力プロンプトの作成
    prompt = f"""
    以下の情報をもとに、{release_type}タイプのプレスリリースを作成してください。
    
    【リリース情報】
    タイプ: {release_type}
    目的: {release_info['purpose']}
    重点: {release_info['focus']}
    主要セクション: {release_info['key_sections']}
    トーン: {release_info['tone']}
    リリース日: {release_date}
    
    【企業情報】
    企業名: {brand_info['name']}
    設立: {brand_info['founded']}年
    ミッション: {brand_info['mission']}
    ウェブサイト: {brand_info['website']}
    
    【製品情報】
    製品名: {product_data['name']}
    カテゴリ: {product_data['category']} > {product_data['sub_category']}
    説明: {product_data['description']}
    主な特徴: {', '.join(product_data['features'][:5])}
    セールスポイント: {', '.join(product_data['unique_selling_points'])}
    価格: {product_data['price']['regular']}円
    発売日: {product_data['release_date']}
    
    【キャンペーン情報】
    キャンペーン名: {campaign_info['name']}
    コンセプト: {campaign_info['concept']}
    キーメッセージ: {', '.join(campaign_info['key_messages'][:2])}
    
    プレスリリースには以下の要素を含めてください：
    1. 見出し（注目を引く簡潔なタイトル）
    2. リード文（最も重要な情報を含む要約）
    3. 本文（詳細情報を段落ごとに説明）
    4. 企業責任者の引用コメント
    5. 価格・発売時期・入手方法
    6. 企業概要
    7. 報道関係者向け問い合わせ先
    
    見出しはインパクトがあり、サーチエンジンで検索されやすいものにしてください。
    リード文は5W1H（誰が、何を、いつ、どこで、なぜ、どのように）を含み、記事の要点を把握できるようにしてください。
    本文は重要度の高い情報から順に記載する「逆ピラミッド構造」を意識してください。
    """
    
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions=f"{brand_info['name']}の広報担当者として、プロフェッショナルで効果的なプレスリリースを作成してください。メディアや読者に訴求力のある内容を心がけ、企業のメッセージを明確に伝えるよう作成してください。",
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            max_output_tokens=4000,
        )
        
        # 結果のパース
        content = response.output_text
        lines = content.split('\n')
        
        # タイトルは最初の非空行
        title = next((line for line in lines if line.strip()), "プレスリリース")
        
        # 簡易的なメタデータ抽出
        press_release = {
            "type": release_type,
            "title": title,
            "content": content,
            "release_date": release_date,
            "company": brand_info["name"],
            "product": product_data["name"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return press_release
        
    except Exception as e:
        print(f"プレスリリースの生成中にエラーが発生しました: {str(e)}")
        return {
            "type": release_type,
            "title": f"{brand_info['name']}プレスリリース - エラー",
            "content": f"プレスリリースの生成中にエラーが発生しました: {str(e)}",
            "release_date": release_date,
            "error": True
        }


def save_content(content, content_type, output_dir="output"):
    """生成したコンテンツをファイルに保存します。"""
    # 出力ディレクトリの作成
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(script_dir))
    output_path = os.path.join(root_dir, output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    # 現在の日時を取得してファイル名に使用
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if content_type == "social_media":
        # ソーシャルメディア投稿の保存
        file_path = os.path.join(output_path, f"social_media_{timestamp}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
            
        # テキスト版も保存
        text_path = os.path.join(output_path, f"social_media_{timestamp}.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            for i, post in enumerate(content, 1):
                f.write(f"===== 投稿 {i} ({post['platform']} - {post['style']}) =====\n\n")
                f.write(f"本文:\n{post.get('text', '')}\n\n")
                f.write(f"ハッシュタグ:\n{post.get('hashtags', '')}\n\n")
                if "image_caption" in post:
                    f.write(f"画像キャプション:\n{post['image_caption']}\n\n")
                f.write("\n\n")
        
        print(f"ソーシャルメディア投稿を保存しました: {file_path}")
        return file_path
        
    elif content_type == "blog":
        # ブログ記事の保存
        file_path = os.path.join(output_path, f"blog_{timestamp}.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {content['title']}\n\n")
            f.write(content['content'])
            f.write(f"\n\n---\n")
            f.write(f"対象読者: {content['target_audience']}\n")
            f.write(f"キーワード: {', '.join(content['seo_keywords'])}\n")
            f.write(f"作成日: {content['created_at']}\n")
        
        # JSON版も保存
        json_path = os.path.join(output_path, f"blog_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
            
        print(f"ブログ記事を保存しました: {file_path}")
        return file_path
        
    elif content_type == "email":
        # メールニュースレターの保存
        file_path = os.path.join(output_path, f"email_{timestamp}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"タイプ: {content['type']}\n")
            f.write(f"件名: {content['subject']}\n\n")
            f.write(f"=== 本文 ===\n\n")
            f.write(content['body'])
            f.write(f"\n\n=== メタデータ ===\n")
            f.write(f"CTA: {content['cta_text']}\n")
            f.write(f"ターゲット: {content['target_segment']}\n")
            f.write(f"作成日: {content['created_at']}\n")
        
        # JSON版も保存
        json_path = os.path.join(output_path, f"email_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
            
        print(f"メールニュースレターを保存しました: {file_path}")
        return file_path
        
    elif content_type == "ad":
        # 広告コピーの保存
        file_path = os.path.join(output_path, f"ads_{timestamp}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"広告タイプ: {content[0]['type']}\n")
            f.write(f"プラットフォーム: {content[0]['platform']}\n\n")
            
            for i, ad in enumerate(content, 1):
                f.write(f"===== 広告 {i} =====\n\n")
                
                f.write("見出し:\n")
                for j, headline in enumerate(ad['headlines'], 1):
                    f.write(f"{j}. {headline} ({len(headline)}文字)\n")
                
                f.write("\n説明文:\n")
                for j, desc in enumerate(ad['descriptions'], 1):
                    f.write(f"{j}. {desc} ({len(desc)}文字)\n")
                
                f.write(f"\nCTA: {ad.get('cta', '今すぐ見る')}\n\n")
        
        # JSON版も保存
        json_path = os.path.join(output_path, f"ads_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
            
        print(f"広告コピーを保存しました: {file_path}")
        return file_path
        
    elif content_type == "press_release":
        # プレスリリースの保存
        file_path = os.path.join(output_path, f"press_release_{timestamp}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content['content'])
            
        # JSON版も保存
        json_path = os.path.join(output_path, f"press_release_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
            
        print(f"プレスリリースを保存しました: {file_path}")
        return file_path
    
    else:
        # その他のコンテンツはJSONで保存
        file_path = os.path.join(output_path, f"{content_type}_{timestamp}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        
        print(f"{content_type}を保存しました: {file_path}")
        return file_path


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="マーケティングコンテンツの自動生成")
    parser.add_argument(
        "--content-type", "-t", type=str, default="social_media",
        choices=["social_media", "blog", "email", "ad", "press_release"],
        help="生成するコンテンツの種類"
    )
    parser.add_argument(
        "--platform", "-p", type=str, default="Instagram",
        choices=["Instagram", "Twitter", "Facebook", "LinkedIn", "Google"],
        help="ソーシャルメディアや広告のプラットフォーム"
    )
    parser.add_argument(
        "--style", "-s", type=str, default="general",
        choices=["general", "casual", "professional", "playful", "educational", "promotional", "emotional", "minimalist"],
        help="コンテンツのスタイル"
    )
    parser.add_argument(
        "--count", "-c", type=int, default=3,
        help="生成するコンテンツの数（ソーシャルメディア投稿や広告の場合）"
    )
    parser.add_argument(
        "--topic", type=str,
        help="ブログ記事のトピック"
    )
    parser.add_argument(
        "--word-count", type=int, default=800,
        help="ブログ記事の単語数"
    )
    parser.add_argument(
        "--email-type", type=str, default="promotional",
        choices=["promotional", "welcome", "educational", "newsletter", "announcement"],
        help="メールニュースレターのタイプ"
    )
    parser.add_argument(
        "--target-segment", type=str,
        help="ターゲットセグメント"
    )
    parser.add_argument(
        "--ad-type", type=str, default="search",
        choices=["search", "display", "social", "video"],
        help="広告のタイプ"
    )
    parser.add_argument(
        "--release-type", type=str, default="product_launch",
        choices=["product_launch", "company_news", "event_announcement", "partnership", "award_recognition"],
        help="プレスリリースのタイプ"
    )
    parser.add_argument(
        "--output-dir", "-o", type=str, default="output",
        help="出力ディレクトリ"
    )
    parser.add_argument(
        "--product-data", type=str,
        help="商品データのJSONファイルパス（指定がない場合はサンプルデータを使用）"
    )
    parser.add_argument(
        "--brand-info", type=str,
        help="ブランド情報のJSONファイルパス（指定がない場合はサンプルデータを使用）"
    )
    parser.add_argument(
        "--campaign-info", type=str,
        help="キャンペーン情報のJSONファイルパス（指定がない場合はサンプルデータを使用）"
    )
    args = parser.parse_args()
    
    try:
        # OpenAI APIの設定
        api_key = setup_environment()
        client = openai.Client(api_key=api_key)
        
        # データの読み込み
        product_data = load_product_data(args.product_data)
        brand_info = load_brand_info(args.brand_info)
        campaign_info = load_campaign_info(args.campaign_info)
        
        # コンテンツタイプに応じた処理
        if args.content_type == "social_media":
            print(f"{args.platform}向けの{args.style}スタイルのソーシャルメディア投稿を{args.count}件生成します...")
            content = generate_social_media_posts(
                client, product_data, brand_info, campaign_info, 
                platform=args.platform, count=args.count, style=args.style
            )
            
            if content:
                file_path = save_content(content, "social_media", args.output_dir)
                print(f"\n生成されたソーシャルメディア投稿（{len(content)}件）:")
                for i, post in enumerate(content, 1):
                    print(f"\n----- 投稿 {i} -----")
                    print(f"{post.get('text', '')[:150]}...")
            else:
                print("投稿の生成に失敗しました。")
                
        elif args.content_type == "blog":
            topic = args.topic or f"{product_data['name']}の効果的な使い方：{product_data['benefits'][0]}"
            print(f"トピック「{topic}」のブログ記事（約{args.word_count}語）を生成します...")
            content = generate_blog_post(
                client, product_data, brand_info, 
                topic=topic, word_count=args.word_count, target_audience=args.target_segment
            )
            
            if content and not content.get("error"):
                file_path = save_content(content, "blog", args.output_dir)
                print(f"\n生成されたブログ記事:")
                print(f"タイトル: {content['title']}")
                print(f"単語数: 約{content['word_count']}語")
                print(f"内容プレビュー: {content['content'][:200]}...")
            else:
                print("ブログ記事の生成に失敗しました。")
                
        elif args.content_type == "email":
            print(f"{args.email_type}タイプのメールニュースレターを生成します...")
            content = generate_email_newsletter(
                client, product_data, brand_info, campaign_info,
                email_type=args.email_type, target_segment=args.target_segment
            )
            
            if content and not content.get("error"):
                file_path = save_content(content, "email", args.output_dir)
                print(f"\n生成されたメールニュースレター:")
                print(f"件名: {content['subject']}")
                print(f"本文プレビュー: {content['body'][:200]}...")
            else:
                print("メールニュースレターの生成に失敗しました。")
                
        elif args.content_type == "ad":
            print(f"{args.platform}向けの{args.ad_type}広告コピーを{args.count}件生成します...")
            content = generate_ad_copy(
                client, product_data, brand_info, campaign_info,
                ad_type=args.ad_type, platform=args.platform, character_limit=90
            )
            
            if content and not content[0].get("error", False):
                file_path = save_content(content, "ad", args.output_dir)
                print(f"\n生成された広告コピー（{len(content)}件）:")
                for i, ad in enumerate(content, 1):
                    print(f"\n----- 広告 {i} -----")
                    for headline in ad.get('headlines', [])[:1]:
                        print(f"見出し: {headline}")
                    for desc in ad.get('descriptions', [])[:1]:
                        print(f"説明: {desc}")
            else:
                print("広告コピーの生成に失敗しました。")
                
        elif args.content_type == "press_release":
            print(f"{args.release_type}タイプのプレスリリースを生成します...")
            content = generate_press_release(
                client, product_data, brand_info, campaign_info,
                release_type=args.release_type
            )
            
            if content and not content.get("error"):
                file_path = save_content(content, "press_release", args.output_dir)
                print(f"\n生成されたプレスリリース:")
                print(f"タイトル: {content['title']}")
                print(f"内容プレビュー: {content['content'][:200]}...")
            else:
                print("プレスリリースの生成に失敗しました。")
                
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()