import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from disaster_data import DisasterInfo, TARGET_GROUPS, LANGUAGES
import openai

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIキーを設定
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEYが設定されていません。.envファイルを確認してください。")

# OpenAIクライアントの初期化
client = openai.Client(api_key=api_key)

def generate_disaster_message(
    disaster_info: DisasterInfo,
    target_group: str,
    language: str,
    custom_instructions: Optional[str] = None
) -> str:
    """
    災害情報から特定の対象グループと言語に適した災害メッセージを生成する
    
    Args:
        disaster_info: 災害情報
        target_group: 対象グループ（一般市民、高齢者など）
        language: 言語（日本語、英語、やさしい日本語）
        custom_instructions: 追加のカスタム指示（オプション）
    
    Returns:
        生成された災害メッセージ
    """
    # システムメッセージと複数のユーザーメッセージを作成
    messages = []
    
    # システムメッセージ
    system_message = {
        "role": "system", 
        "content": f"""
あなたは災害情報を伝える専門家です。与えられた災害情報を基に、適切な災害メッセージを作成してください。
対象グループ: {TARGET_GROUPS.get(target_group, "一般市民")}
言語: {LANGUAGES.get(language, "日本語")}

以下の点に注意してください：
1. 正確な情報を簡潔に伝える
2. パニックを引き起こさないよう冷静な表現を使う
3. 最も重要な情報を最初に伝える
4. 具体的な指示と行動方針を含める
5. 信頼できる情報源と緊急連絡先を明記する

{custom_instructions or ""}
"""
    }
    
    messages.append(system_message)
    
    # ユーザーメッセージ
    user_message = {
        "role": "user",
        "content": f"""
# 災害情報
- 種別: {disaster_info.disaster_type}
- 警戒レベル: {disaster_info.alert_level}
- タイトル: {disaster_info.title}
- 説明: {disaster_info.description}
- 影響地域: {disaster_info.get_formatted_affected_areas()}
- 避難所: {disaster_info.get_formatted_evacuation_centers()}
- 指示事項: {disaster_info.instructions}
- 緊急連絡先: {", ".join([f"{k}: {v}" for k, v in disaster_info.emergency_contacts.items()])}

言語に応じたメッセージを作成し、必要な情報をすべて含めてください。
"""
    }
    
    messages.append(user_message)
    
    # 特定の対象グループに合わせた追加指示
    group_specific_instructions = {
        "elderly": "高齢者向けのメッセージでは、簡潔でわかりやすい表現を使い、大きなフォントで読みやすく、具体的な行動指示を含めてください。",
        "children": "子どもと保護者向けのメッセージでは、子どもが理解できる平易な言葉を使いつつ、保護者が取るべき行動を明確に示してください。",
        "disabled": "障がい者向けのメッセージでは、明確で具体的な指示と、サポートが必要な場合の連絡先を含めてください。",
        "foreigners": "外国人向けのメッセージでは、文化的な違いを考慮し、日本特有の災害対応について補足説明を加えてください。",
        "tourists": "観光客向けのメッセージでは、地理に不案内な人でも理解できるよう、ランドマークを用いた説明を含めてください。"
    }

    if target_group in group_specific_instructions:
        additional_message = {
            "role": "user",
            "content": f"追加指示：{group_specific_instructions[target_group]}"
        }
        messages.append(additional_message)

    # 言語に応じた追加指示
    language_specific_instructions = {
        "en": "英語でメッセージを作成してください。日本特有の表現や場所については補足説明を加えてください。",
        "easy_ja": "「やさしい日本語」でメッセージを作成してください。難しい漢字にはふりがなをつけ、一文を短くし、外来語や専門用語を避けてください。"
    }

    if language in language_specific_instructions:
        language_message = {
            "role": "user",
            "content": f"言語指示：{language_specific_instructions[language]}"
        }
        messages.append(language_message)

    # OpenAI Responses APIを使用してメッセージを生成
    try:
        response = client.responses.create(
            model="gpt-4o",
            input=messages
        )
        return response.output_text
    except Exception as e:
        return f"メッセージ生成中にエラーが発生しました: {str(e)}"

def analyze_multiple_sources(sources: List[str]) -> Dict[str, Any]:
    """
    複数の情報源から災害情報を分析し、整理する
    
    Args:
        sources: 災害に関する複数の情報源テキスト
    
    Returns:
        整理された災害情報の辞書
    """
    # メッセージリストを作成
    messages = []
    
    # システムメッセージ
    system_message = {
        "role": "system",
        "content": """
あなたは災害情報を分析する専門家です。複数の情報源から得られた災害関連情報を整理し、一貫性のある正確な情報にまとめてください。
矛盾する情報がある場合は、より信頼性の高い情報源や新しい情報を優先してください。
情報の欠落がある場合は、その旨を明記してください。
"""
    }
    
    messages.append(system_message)
    
    # 情報源のメッセージ
    source_intro = {
        "role": "user",
        "content": "以下の複数の情報源から災害情報を分析し、整理してください："
    }
    
    messages.append(source_intro)
    
    # 各情報源をメッセージとして追加
    for i, source in enumerate(sources, 1):
        source_message = {
            "role": "user",
            "content": f"情報源{i}:\n{source}"
        }
        messages.append(source_message)
    
    # フォーマット指示
    format_message = {
        "role": "user",
        "content": """
以下の構造で情報を整理してJSON形式で返してください：
1. 災害の種類
2. 災害の規模と強度
3. 影響を受ける地域
4. 推定される被害
5. 現在の状況
6. 予測される進展
7. 推奨される行動
8. 信頼できる情報源
9. 不確実または矛盾する情報
"""
    }
    
    messages.append(format_message)

    try:
        response = client.responses.create(
            model="gpt-4o",  # より高度な分析のためのモデル
            input=messages,
            text={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "災害の種類": {"type": "string"},
                            "災害の規模と強度": {"type": "string"},
                            "影響を受ける地域": {"type": "string"},
                            "推定される被害": {"type": "string"},
                            "現在の状況": {"type": "string"},
                            "予測される進展": {"type": "string"},
                            "推奨される行動": {"type": "string"},
                            "信頼できる情報源": {"type": "string"},
                            "不確実または矛盾する情報": {"type": "string"}
                        },
                        "required": ["災害の種類", "災害の規模と強度", "影響を受ける地域", "現在の状況", "推奨される行動"]
                    },
                    "strict": True
                }
            }
        )
        return json.loads(response.output_text)
    except Exception as e:
        return {"error": f"情報分析中にエラーが発生しました: {str(e)}"}

def generate_social_media_updates(
    disaster_info: DisasterInfo,
    platform: str,
    character_limit: int = 280
) -> List[str]:
    """
    災害情報からソーシャルメディア用の投稿を生成する
    
    Args:
        disaster_info: 災害情報
        platform: ソーシャルメディアプラットフォーム（twitter, facebook, instagram等）
        character_limit: 文字数制限
    
    Returns:
        生成されたソーシャルメディア投稿のリスト
    """
    # メッセージリストを作成
    messages = []
    
    # システムメッセージ
    system_message = {
        "role": "system",
        "content": f"""
あなたは災害情報を{platform}で発信する広報担当者です。与えられた災害情報を基に、効果的な{platform}投稿を作成してください。

以下の点に注意してください：
1. {platform}の特性に合わせた表現を使う
2. 文字数制限は{character_limit}文字以内
3. 重要な情報を優先して伝える
4. ハッシュタグを適切に使用する
5. 信頼できる情報源へのリンクを含める（可能であれば）
"""
    }
    
    messages.append(system_message)
    
    # 災害情報のメッセージ
    info_message = {
        "role": "user",
        "content": f"""
# 災害情報
- 種別: {disaster_info.disaster_type}
- 警戒レベル: {disaster_info.alert_level}
- タイトル: {disaster_info.title}
- 説明: {disaster_info.description}
- 影響地域: {disaster_info.get_formatted_affected_areas()}
- 指示事項: {disaster_info.instructions}
"""
    }
    
    messages.append(info_message)
    
    # 投稿指示のメッセージ
    post_instruction = {
        "role": "user",
        "content": f"""
以下の3つの投稿を作成してください：
1. 初期告知用の投稿
2. 更新情報用の投稿
3. 行動指示に焦点を当てた投稿

それぞれ{character_limit}文字以内にしてください。
"""
    }
    
    messages.append(post_instruction)

    try:
        response = client.responses.create(
            model="gpt-4o",
            input=messages
        )
        content = response.output_text.strip()
        # 投稿を分割
        posts = []
        current_post = None
        for line in content.split("\n"):
            if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
                if current_post is not None:
                    posts.append(current_post)
                current_post = line
            elif current_post is not None and line:
                current_post += "\n" + line
        
        if current_post is not None:
            posts.append(current_post)
            
        return posts if posts else [content]
    except Exception as e:
        return [f"投稿生成中にエラーが発生しました: {str(e)}"]