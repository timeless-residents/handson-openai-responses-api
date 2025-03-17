"""
災害情報の整備と配信支援サンプル

このサンプルアプリケーションは、OpenAIを使用して、
災害情報を整理し、異なる対象者向けに適切なメッセージを生成します。
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import openai
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

# 災害種別
DISASTER_TYPES = {
    "earthquake": "地震",
    "flood": "洪水",
    "tsunami": "津波",
    "fire": "火災",
    "typhoon": "台風",
    "landslide": "土砂災害",
}

# 警戒レベル
ALERT_LEVELS = {
    "info": "情報",
    "advisory": "注意報",
    "warning": "警報",
    "emergency": "緊急警報",
}

# 対象グループ
TARGET_GROUPS = {
    "general": "一般市民",
    "elderly": "高齢者",
    "children": "子ども・保護者",
    "disabled": "障がい者",
    "foreigners": "外国人",
    "tourists": "観光客",
}

# 言語
LANGUAGES = {
    "ja": "日本語",
    "en": "英語",
    "easy_ja": "やさしい日本語",
}

# サンプル災害情報
SAMPLE_DISASTERS = [
    {
        "id": "eq20250317001",
        "disaster_type": "earthquake",
        "alert_level": "warning",
        "title": "東京湾北部地震",
        "description": "3月17日午前10時30分頃、東京湾北部を震源とするマグニチュード5.5の地震が発生しました。東京都内で最大震度5弱を観測しています。",
        "affected_areas": ["東京都千代田区", "東京都中央区", "東京都港区", "東京都新宿区"],
        "evacuation_centers": [
            {"name": "千代田区立九段小学校", "address": "千代田区九段南2-1-11"},
            {"name": "港区立芝公園小学校", "address": "港区芝公園3-5-37"}
        ],
        "start_time": "2025-03-17T10:30:00",
        "estimated_end_time": None,
        "instructions": "落ち着いて行動し、テレビやラジオ、防災無線の情報に注意してください。余震に備えてください。",
        "emergency_contacts": {
            "police": "110",
            "fire": "119",
            "disaster_info": "03-1234-5678"
        },
        "update_time": "2025-03-17T10:45:00"
    },
    {
        "id": "ty20250315001",
        "disaster_type": "typhoon",
        "alert_level": "warning",
        "title": "台風8号接近",
        "description": "大型で非常に強い台風8号が本州に接近しています。最大風速45m/s、瞬間最大風速60m/sの見込みです。",
        "affected_areas": ["東京都全域", "神奈川県全域", "千葉県全域", "埼玉県南部"],
        "evacuation_centers": [
            {"name": "各市区町村の指定避難所", "address": "お住まいの自治体にお問い合わせください"}
        ],
        "start_time": "2025-03-18T00:00:00",
        "estimated_end_time": "2025-03-19T12:00:00",
        "instructions": "不要不急の外出を控え、早めに安全な場所に避難してください。停電に備えて懐中電灯や携帯ラジオ、モバイルバッテリーを準備してください。",
        "emergency_contacts": {
            "weather_info": "177",
            "disaster_prevention": "03-9876-5432"
        },
        "update_time": "2025-03-17T16:00:00"
    }
]

def setup_environment() -> str:
    """
    環境設定を行い、.env ファイルから API キーを取得します。
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(script_dir))
    load_dotenv(os.path.join(root_dir, ".env"))

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY が設定されていません")
    return api_key


def generate_disaster_message(
    disaster_info: Dict[str, Any],
    target_group: str,
    language: str,
    custom_instructions: Optional[str] = None,
) -> str:
    """
    災害情報から特定の対象グループと言語に適した災害メッセージを生成する
    """
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
- 種別: {disaster_info.get('disaster_type', '')}
- 警戒レベル: {disaster_info.get('alert_level', '')}
- タイトル: {disaster_info.get('title', '')}
- 説明: {disaster_info.get('description', '')}
- 影響地域: {', '.join(disaster_info.get('affected_areas', []))}
- 避難所: {', '.join([f"{center['name']}（{center['address']}）" for center in disaster_info.get('evacuation_centers', [])])}
- 指示事項: {disaster_info.get('instructions', '')}
- 緊急連絡先: {', '.join([f"{k}: {v}" for k, v in disaster_info.get('emergency_contacts', {}).items()])}

言語に応じたメッセージを作成し、必要な情報をすべて含めてください。
"""
    }
    messages.append(user_message)
    
    # 対象グループ別の指示
    group_specific_instructions = {
        "elderly": "高齢者向けのメッセージでは、簡潔でわかりやすい表現を使い、大きなフォントで読みやすく、具体的な行動指示を含めてください。",
        "children": "子どもと保護者向けのメッセージでは、子どもが理解できる平易な言葉を使いつつ、保護者が取るべき行動を明確に示してください。",
        "disabled": "障がい者向けのメッセージでは、明確で具体的な指示と、サポートが必要な場合の連絡先を含めてください。",
        "foreigners": "外国人向けのメッセージでは、文化的な違いを考慮し、日本特有の災害対応について補足説明を加えてください。",
        "tourists": "観光客向けのメッセージでは、地理に不案内な人でも理解できるよう、ランドマークを用いた説明を含めてください。"
    }
    if target_group in group_specific_instructions:
        messages.append({
            "role": "user",
            "content": f"追加指示：{group_specific_instructions[target_group]}"
        })
    
    # 言語別の指示
    language_specific_instructions = {
        "en": "英語でメッセージを作成してください。日本特有の表現や場所については補足説明を加えてください。",
        "easy_ja": "「やさしい日本語」でメッセージを作成してください。難しい漢字にはふりがなをつけ、一文を短くし、外来語や専門用語を避けてください。"
    }
    if language in language_specific_instructions:
        messages.append({
            "role": "user",
            "content": f"言語指示：{language_specific_instructions[language]}"
        })

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"メッセージ生成中にエラーが発生しました: {str(e)}"

def analyze_multiple_sources(sources: List[str]) -> Dict[str, Any]:
    """
    複数の情報源から災害情報を分析し、整理する
    """
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
    
    # 情報源の導入
    messages.append({
        "role": "user",
        "content": "以下の複数の情報源から災害情報を分析し、整理してください："
    })
    
    # 各情報源
    for i, source in enumerate(sources, 1):
        messages.append({
            "role": "user", 
            "content": f"情報源{i}:\n{source}"
        })
    
    # フォーマット指示
    messages.append({
        "role": "user",
        "content": """
以下の構造でJSON形式で返してください：
{
  "災害の種類": "ここに災害の種類を記述",
  "災害の規模と強度": "ここに規模と強度を記述",
  "影響を受ける地域": "ここに地域を記述", 
  "推定される被害": "ここに推定被害を記述",
  "現在の状況": "ここに現状を記述",
  "予測される進展": "ここに予測を記述",
  "推奨される行動": "ここに推奨行動を記述",
  "信頼できる情報源": "ここに情報源を記述",
  "不確実または矛盾する情報": "ここに不確実情報を記述"
}
"""
    })

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"情報分析中にエラーが発生しました: {str(e)}"}

def generate_social_media_updates(
    disaster_info: Dict[str, Any], platform: str, character_limit: int = 280
) -> List[str]:
    """
    災害情報からソーシャルメディア用の投稿を生成する
    """
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
    
    # 災害情報
    info_message = {
        "role": "user",
        "content": f"""
# 災害情報
- 種別: {disaster_info.get('disaster_type', '')}
- 警戒レベル: {disaster_info.get('alert_level', '')}
- タイトル: {disaster_info.get('title', '')}
- 説明: {disaster_info.get('description', '')}
- 影響地域: {', '.join(disaster_info.get('affected_areas', []))}
- 指示事項: {disaster_info.get('instructions', '')}
"""
    }
    messages.append(info_message)
    
    # 投稿指示
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
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        content = response.choices[0].message.content.strip()
        
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

# Flaskアプリケーションの設定
app = Flask(__name__)
app.secret_key = os.urandom(24)

# インメモリデータストア
disasters = SAMPLE_DISASTERS.copy()

# 日時フォーマットフィルター
@app.template_filter('format_datetime')
def format_datetime(value, format="%Y年%m月%d日 %H:%M"):
    """テンプレートで日時フォーマットを行うフィルター"""
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return value.strftime(format)

# ホームページ
@app.route('/')
def index():
    return render_template('index.html', disasters=disasters)

# 災害情報詳細ページ
@app.route('/disaster/<disaster_id>')
def view_disaster(disaster_id):
    disaster = next((d for d in disasters if d['id'] == disaster_id), None)
    if not disaster:
        flash('指定された災害情報が見つかりません', 'danger')
        return redirect(url_for('index'))
    
    return render_template('view_disaster.html', disaster=disaster)

# メッセージ生成ページ
@app.route('/disaster/<disaster_id>/message', methods=['GET', 'POST'])
def generate_message(disaster_id):
    disaster = next((d for d in disasters if d['id'] == disaster_id), None)
    if not disaster:
        flash('指定された災害情報が見つかりません', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        target_group = request.form.get('target_group', 'general')
        language = request.form.get('language', 'ja')
        custom_instructions = request.form.get('custom_instructions', '')
        
        # メッセージ生成
        message = generate_disaster_message(
            disaster_info=disaster,
            target_group=target_group,
            language=language,
            custom_instructions=custom_instructions
        )
        
        return render_template(
            'message_result.html',
            disaster=disaster,
            message=message,
            target_group=TARGET_GROUPS.get(target_group, '一般市民'),
            language=LANGUAGES.get(language, '日本語')
        )
    
    return render_template(
        'generate_message.html', 
        disaster=disaster, 
        target_groups=TARGET_GROUPS,
        languages=LANGUAGES
    )

# 情報分析ページ
@app.route('/analyze', methods=['GET', 'POST'])
def analyze_sources():
    if request.method == 'POST':
        sources = []
        for i in range(1, 5):  # 最大4つの情報源
            source = request.form.get(f'source{i}', '').strip()
            if source:
                sources.append(source)
        
        if len(sources) < 2:
            flash('少なくとも2つの情報源が必要です', 'warning')
            return render_template('analyze_sources.html')
        
        # 情報分析
        result = analyze_multiple_sources(sources)
        
        return render_template('analysis_result.html', result=result, sources=sources)
    
    return render_template('analyze_sources.html')

# SNS投稿生成ページ
@app.route('/disaster/<disaster_id>/social', methods=['GET', 'POST'])
def social_media(disaster_id):
    disaster = next((d for d in disasters if d['id'] == disaster_id), None)
    if not disaster:
        flash('指定された災害情報が見つかりません', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        platform = request.form.get('platform', 'Twitter/X')
        character_limit = int(request.form.get('character_limit', 280))
        
        # SNS投稿生成
        posts = generate_social_media_updates(
            disaster_info=disaster,
            platform=platform,
            character_limit=character_limit
        )
        
        return render_template(
            'social_media_result.html',
            disaster=disaster,
            posts=posts,
            platform=platform
        )
    
    platforms = ["Twitter/X", "Facebook", "Instagram", "LINE"]
    return render_template('social_media.html', disaster=disaster, platforms=platforms)

# 新規災害情報の登録
@app.route('/disaster/new', methods=['GET', 'POST'])
def new_disaster():
    if request.method == 'POST':
        # 災害情報の作成
        new_id = f"{request.form.get('disaster_type')}{datetime.now().strftime('%Y%m%d%H%M')}"
        
        # 影響地域の処理
        affected_areas = []
        areas_text = request.form.get('affected_areas', '')
        if areas_text:
            affected_areas = [area.strip() for area in areas_text.split('\n') if area.strip()]
        
        # 避難所の処理
        evacuation_centers = []
        centers_text = request.form.get('evacuation_centers', '')
        if centers_text:
            for line in centers_text.split('\n'):
                if ':' in line:
                    name, address = line.split(':', 1)
                    evacuation_centers.append({
                        "name": name.strip(),
                        "address": address.strip()
                    })
        
        # 緊急連絡先の処理
        emergency_contacts = {}
        contacts_text = request.form.get('emergency_contacts', '')
        if contacts_text:
            for line in contacts_text.split('\n'):
                if ':' in line:
                    name, contact = line.split(':', 1)
                    emergency_contacts[name.strip()] = contact.strip()
        
        # 開始時刻・終了時刻の処理
        start_time = request.form.get('start_time', '')
        estimated_end_time = request.form.get('estimated_end_time', '')
        
        # 災害情報の作成
        disaster = {
            "id": new_id,
            "disaster_type": request.form.get('disaster_type', ''),
            "alert_level": request.form.get('alert_level', ''),
            "title": request.form.get('title', ''),
            "description": request.form.get('description', ''),
            "affected_areas": affected_areas,
            "evacuation_centers": evacuation_centers,
            "start_time": start_time,
            "estimated_end_time": estimated_end_time if estimated_end_time else None,
            "instructions": request.form.get('instructions', ''),
            "emergency_contacts": emergency_contacts,
            "update_time": datetime.now().isoformat()
        }
        
        disasters.append(disaster)
        flash('災害情報が登録されました', 'success')
        return redirect(url_for('index'))
    
    return render_template(
        'new_disaster.html',
        disaster_types=DISASTER_TYPES,
        alert_levels=ALERT_LEVELS
    )

# APIエンドポイント - 災害情報一覧
@app.route('/api/disasters', methods=['GET'])
def api_disasters():
    return jsonify(disasters)

# APIエンドポイント - 災害情報詳細
@app.route('/api/disasters/<disaster_id>', methods=['GET'])
def api_disaster(disaster_id):
    disaster = next((d for d in disasters if d['id'] == disaster_id), None)
    if not disaster:
        return jsonify({"error": "災害情報が見つかりません"}), 404
    return jsonify(disaster)

if __name__ == '__main__':
    # 環境変数の設定
    api_key = setup_environment()
    os.environ["OPENAI_API_KEY"] = api_key
    
    # アプリケーションの実行
    app.run(debug=True, port=5006, host="0.0.0.0")