import os
import json
import markdown
import plotly.express as px
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import uuid
import time
import datetime

# 環境変数の読み込み
load_dotenv()

# OpenAI Clientの初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Flaskアプリの初期化
app = Flask(__name__)
app.secret_key = os.urandom(24)

# カスタムフィルターの追加
@app.template_filter('strftime')
def _jinja2_filter_strftime(date_str, format_str='%Y-%m-%d'):
    """日付文字列をフォーマットするフィルター"""
    today = datetime.datetime.now()
    return today.strftime(format_str)

# ユーザーセッション情報を管理するディクショナリ
user_sessions = {}

# サンプル科目と関連トピック
SUBJECTS = {
    "math": {"name": "数学", "topics": ["代数", "幾何", "確率統計", "微分積分"]},
    "science": {"name": "理科", "topics": ["物理", "化学", "生物", "地学"]},
    "language": {"name": "国語", "topics": ["現代文", "古文", "漢文", "文法"]},
    "social": {"name": "社会", "topics": ["歴史", "地理", "公民", "経済"]},
}

# 学習レベル
LEVELS = ["小学生", "中学生", "高校生", "大学生"]


def get_or_create_user_session(session_id):
    """ユーザーセッションを取得または新規作成"""
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            "profile": None,
            "learning_history": [],
            "current_subject": None,
            "current_topic": None,
            "understanding_level": 0.5,  # 0.0〜1.0の範囲で理解度を表現
            "preferred_style": "visual",  # visual, verbal, practical
        }
    return user_sessions[session_id]


def generate_educational_content(subject, topic, level, style, previous_content=None):
    """教育コンテンツを生成する関数"""
    system_instruction = """
    あなたは教育コンテンツ専門のAIアシスタントです。正確で教育的に適切な内容を提供してください。
    学習者のレベルと好みの学習スタイルに合わせた説明を生成してください。
    科学的・学術的に正確な情報を提供し、複雑な概念は適切な例や比喩を用いて説明してください。
    """

    # 学習スタイルに基づく追加指示
    style_instructions = {
        "visual": "視覚的な例えや図表の説明を多く含めてください。「〜のように見える」「〜を想像してください」などの表現を使ってください。",
        "verbal": "論理的な説明と言葉による定義を重視してください。概念間の関係性を明確にしてください。",
        "practical": "実践的な応用例や日常生活との関連を強調してください。「〜の場面で使える」「〜に役立つ」などの表現を使ってください。",
    }

    system_instruction += style_instructions.get(style, "")

    # コンテンツ生成リクエスト
    messages = [
        {"role": "system", "content": system_instruction},
        {
            "role": "user",
            "content": f"「{SUBJECTS[subject]['name']}」の「{topic}」について、{level}向けの教材を作成してください。マークダウン形式で、以下を含めてください：\n1. 概念の基本説明\n2. 重要なポイント（3-5つ）\n3. わかりやすい例題と解説\n4. 発展的な内容や関連トピックへの言及",
        },
    ]

    if previous_content:
        messages.append({"role": "assistant", "content": previous_content})
        messages.append(
            {
                "role": "user",
                "content": "この内容をもう少し詳しく説明してください。特に難しい部分を噛み砕いて説明し、具体例を増やしてください。",
            }
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o", messages=messages, temperature=0.7, max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"APIエラー: {e}")
        return "コンテンツの生成中にエラーが発生しました。後でもう一度お試しください。"


def generate_practice_problems(subject, topic, level, understanding_level):
    """学習者の理解度に合わせた問題を生成する関数"""
    difficulty = (
        "基本的"
        if understanding_level < 0.3
        else "標準的" if understanding_level < 0.7 else "発展的"
    )

    system_instruction = """
    あなたは教育問題作成の専門家です。学習者の理解度に合わせた適切な難易度の問題を生成してください。
    問題は明確で、教育的に価値があり、指定された科目とトピックに関連したものにしてください。
    各問題には、解答と詳細な解説を必ず含めてください。
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_instruction},
                {
                    "role": "user",
                    "content": f"「{SUBJECTS[subject]['name']}」の「{topic}」に関する{difficulty}な練習問題を3題、{level}向けに作成してください。\n\n各問題には:\n1. 問題文\n2. 解答\n3. 詳細な解説\nを含めてください。マークダウン形式で出力してください。",
                },
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"APIエラー: {e}")
        return "問題の生成中にエラーが発生しました。後でもう一度お試しください。"


def evaluate_answer(subject, topic, level, question, user_answer, correct_answer):
    """ユーザーの回答を評価し、フィードバックを生成する関数"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは教育評価の専門家です。学習者の回答を公平かつ建設的に評価し、具体的なフィードバックを提供してください。",
                },
                {
                    "role": "user",
                    "content": f"以下の問題と回答を評価してください：\n\n問題: {question}\n\n学習者の回答: {user_answer}\n\n模範解答: {correct_answer}\n\n評価と具体的なフィードバックを提供してください。正しい点、改善できる点、そして次のステップの提案を含めてください。",
                },
            ],
            temperature=0.7,
            max_tokens=800,
        )

        # 理解度スコア推定のためのJSON応答も取得
        score_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは学習評価システムです。学習者の回答を評価し、理解度スコアを0.0〜1.0の範囲で提供してください。",
                },
                {
                    "role": "user",
                    "content": f"問題: {question}\n学習者の回答: {user_answer}\n模範解答: {correct_answer}\n\n学習者の回答を評価し、理解度スコアを0.0〜1.0の範囲で提供してください。完全な理解は1.0、まったく理解していない場合は0.0とします。JSONフォーマットで{{'understanding_score': 数値}}の形式で出力してください。",
                },
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        score_data = json.loads(score_response.choices[0].message.content)
        understanding_score = score_data.get("understanding_score", 0.5)

        return {
            "feedback": response.choices[0].message.content,
            "understanding_score": understanding_score,
        }
    except Exception as e:
        print(f"APIエラー: {e}")
        return {
            "feedback": "回答の評価中にエラーが発生しました。",
            "understanding_score": 0.5,
        }


def generate_concept_explanation(subject, topic, concept, level):
    """特定の概念について詳細な説明を生成する関数"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは教育者です。学習者が理解しやすいように、概念を明確かつ詳細に説明してください。",
                },
                {
                    "role": "user",
                    "content": f"「{SUBJECTS[subject]['name']}」の「{topic}」における「{concept}」という概念について、{level}向けに詳しく説明してください。基本的な定義、重要なポイント、具体例、よくある誤解などを含めてください。",
                },
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"APIエラー: {e}")
        return "説明の生成中にエラーが発生しました。後でもう一度お試しください。"


def create_learning_plan(subject, topic, level, goals, duration):
    """学習計画を生成する関数"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは学習計画の専門家です。効果的で段階的な学習計画を作成してください。",
                },
                {
                    "role": "user",
                    "content": f"「{SUBJECTS[subject]['name']}」の「{topic}」を{level}が{duration}で学ぶための計画を作成してください。\n\n学習目標: {goals}\n\n以下を含む詳細な学習計画を作成してください：\n1. 週ごとのトピックと目標\n2. 推奨される学習リソースと活動\n3. 理解度を確認するためのチェックポイント\n4. 予想される難所とその対策",
                },
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"APIエラー: {e}")
        return "学習計画の生成中にエラーが発生しました。後でもう一度お試しください。"


def answer_question(subject, topic, level, question, user_session):
    """学習者の質問に回答する関数"""
    # 学習履歴と理解度に基づいた回答の調整
    understanding_context = (
        "基本的な説明から始めてください"
        if user_session["understanding_level"] < 0.3
        else (
            "標準的な説明を提供してください"
            if user_session["understanding_level"] < 0.7
            else "発展的な内容も含めて詳細に説明してください"
        )
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"あなたは{SUBJECTS[subject]['name']}の教師です。学習者からの質問に対して、{level}向けに適切な回答を提供してください。{understanding_context}",
                },
                {"role": "user", "content": f"「{topic}」に関する質問：{question}"},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"APIエラー: {e}")
        return "回答の生成中にエラーが発生しました。後でもう一度お試しください。"


@app.route("/")
def index():
    """トップページ"""
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())

    user_session = get_or_create_user_session(session["user_id"])
    return render_template(
        "index.html", subjects=SUBJECTS, levels=LEVELS, user_session=user_session
    )


@app.route("/set_profile", methods=["POST"])
def set_profile():
    """ユーザープロフィールの設定"""
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())

    user_session = get_or_create_user_session(session["user_id"])
    user_session["profile"] = {
        "name": request.form.get("name", "学習者"),
        "level": request.form.get("level", "中学生"),
        "preferred_style": request.form.get("learning_style", "visual"),
    }

    return redirect(url_for("select_subject"))


@app.route("/select_subject")
def select_subject():
    """科目選択ページ"""
    if "user_id" not in session:
        return redirect(url_for("index"))

    user_session = get_or_create_user_session(session["user_id"])
    if not user_session["profile"]:
        return redirect(url_for("index"))

    return render_template(
        "select_subject.html", subjects=SUBJECTS, user_session=user_session
    )


@app.route("/select_topic/<subject>")
def select_topic(subject):
    """トピック選択ページ"""
    if "user_id" not in session or subject not in SUBJECTS:
        return redirect(url_for("index"))

    user_session = get_or_create_user_session(session["user_id"])
    user_session["current_subject"] = subject

    return render_template(
        "select_topic.html",
        subject=SUBJECTS[subject],
        subject_key=subject,
        topics=SUBJECTS[subject]["topics"],
        user_session=user_session,
    )


@app.route("/learning/<subject>/<topic>")
def learning(subject, topic):
    """学習ページ"""
    if "user_id" not in session:
        return redirect(url_for("index"))

    user_session = get_or_create_user_session(session["user_id"])
    user_session["current_subject"] = subject
    user_session["current_topic"] = topic

    # 教育コンテンツの生成
    content = generate_educational_content(
        subject,
        topic,
        user_session["profile"]["level"],
        user_session["profile"]["preferred_style"],
    )

    # マークダウンをHTMLに変換
    content_html = markdown.markdown(content)

    return render_template(
        "learning.html",
        subject=SUBJECTS[subject],
        subject_key=subject,
        topic=topic,
        content=content_html,
        raw_content=content,
        user_session=user_session,
    )


@app.route("/practice/<subject>/<topic>")
def practice(subject, topic):
    """練習問題ページ"""
    if "user_id" not in session:
        return redirect(url_for("index"))

    user_session = get_or_create_user_session(session["user_id"])

    # 新しい問題を生成するかどうかをクエリパラメータから取得（デフォルトはFalse）
    regenerate = request.args.get('regenerate', 'false').lower() == 'true'
    
    # キャッシュキー - 同じ問題を再表示するために使用
    cache_key = f"practice_{subject}_{topic}"
    
    # 練習問題の生成 (regenerateがtrueの場合または初めての場合)
    if regenerate or cache_key not in user_session:
        problems = generate_practice_problems(
            subject,
            topic,
            user_session["profile"]["level"],
            user_session["understanding_level"],
        )
        # セッションにキャッシュ
        user_session[cache_key] = problems
    else:
        # キャッシュから問題を取得
        problems = user_session[cache_key]

    # マークダウンをHTMLに変換
    problems_html = markdown.markdown(problems)

    return render_template(
        "practice.html",
        subject=SUBJECTS[subject],
        subject_key=subject,
        topic=topic,
        problems=problems_html,
        raw_problems=problems,
        user_session=user_session,
    )


@app.route("/evaluate_answer", methods=["POST"])
def evaluate_user_answer():
    """ユーザーの回答を評価"""
    if "user_id" not in session:
        return jsonify({"error": "セッションが無効です"})

    data = request.json
    user_session = get_or_create_user_session(session["user_id"])

    result = evaluate_answer(
        data["subject"],
        data["topic"],
        user_session["profile"]["level"],
        data["question"],
        data["user_answer"],
        data["correct_answer"],
    )

    # 理解度の更新（過去の理解度と新しい評価を加重平均）
    user_session["understanding_level"] = (
        0.7 * user_session["understanding_level"] + 0.3 * result["understanding_score"]
    )

    # 学習履歴に記録
    user_session["learning_history"].append(
        {
            "timestamp": time.time(),
            "subject": data["subject"],
            "topic": data["topic"],
            "activity": "問題回答",
            "understanding_score": result["understanding_score"],
        }
    )

    return jsonify(
        {
            "feedback": markdown.markdown(result["feedback"]),
            "understanding_score": result["understanding_score"],
        }
    )


@app.route("/ask_question", methods=["POST"])
def ask_question():
    """質問に回答"""
    if "user_id" not in session:
        return jsonify({"error": "セッションが無効です"})

    data = request.json
    user_session = get_or_create_user_session(session["user_id"])

    answer = answer_question(
        data["subject"],
        data["topic"],
        user_session["profile"]["level"],
        data["question"],
        user_session,
    )

    # 学習履歴に記録
    user_session["learning_history"].append(
        {
            "timestamp": time.time(),
            "subject": data["subject"],
            "topic": data["topic"],
            "activity": "質問",
            "question": data["question"],
        }
    )

    return jsonify({"answer": markdown.markdown(answer)})


@app.route("/create_plan", methods=["GET", "POST"])
def create_plan():
    """学習計画の作成"""
    if "user_id" not in session:
        return redirect(url_for("index"))

    user_session = get_or_create_user_session(session["user_id"])

    if request.method == "POST":
        subject = request.form.get("subject")
        topic = request.form.get("topic")
        goals = request.form.get("goals")
        duration = request.form.get("duration")

        plan = create_learning_plan(
            subject, topic, user_session["profile"]["level"], goals, duration
        )

        # マークダウンをHTMLに変換
        plan_html = markdown.markdown(plan)

        return render_template(
            "plan_result.html",
            subject=SUBJECTS[subject],
            subject_key=subject,
            topic=topic,
            goals=goals,
            duration=duration,
            plan=plan_html,
            user_session=user_session,
        )

    return render_template(
        "create_plan.html", subjects=SUBJECTS, user_session=user_session
    )


@app.route("/progress")
def progress():
    """学習進捗の表示"""
    if "user_id" not in session:
        return redirect(url_for("index"))

    user_session = get_or_create_user_session(session["user_id"])

    if not user_session["learning_history"]:
        return render_template(
            "progress.html", user_session=user_session, has_data=False
        )

    # 学習履歴からデータを抽出
    history = user_session["learning_history"]

    # 時系列での理解度変化
    understanding_data = [
        {
            "timestamp": entry.get("timestamp", 0),
            "score": entry.get("understanding_score", None),
        }
        for entry in history
        if "understanding_score" in entry
    ]

    if understanding_data:
        df = pd.DataFrame(understanding_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

        # 理解度の時系列グラフ
        fig = px.line(
            df,
            x="timestamp",
            y="score",
            title="学習理解度の推移",
            labels={"timestamp": "日時", "score": "理解度スコア"},
        )
        understanding_graph = fig.to_html(full_html=False)
    else:
        understanding_graph = None

    # 科目・トピック別の活動数
    activity_counts = {}
    for entry in history:
        key = f"{SUBJECTS.get(entry.get('subject', ''), {}).get('name', '')} - {entry.get('topic', '')}"
        activity_counts[key] = activity_counts.get(key, 0) + 1

    if activity_counts:
        activity_df = pd.DataFrame(
            list(activity_counts.items()), columns=["area", "count"]
        )
        activity_fig = px.bar(
            activity_df,
            x="area",
            y="count",
            title="科目・トピック別学習活動",
            labels={"area": "学習分野", "count": "活動回数"},
        )
        activity_graph = activity_fig.to_html(full_html=False)
    else:
        activity_graph = None

    return render_template(
        "progress.html",
        user_session=user_session,
        has_data=True,
        understanding_graph=understanding_graph,
        activity_graph=activity_graph,
    )


# コンソールモードのメイン関数
def console_mode():
    """コンソールインターフェースでの実行"""
    print("===== 教育コンテンツ生成システム =====")

    # プロフィール設定
    print("\n[プロフィール設定]")
    name = input("お名前: ")
    print("\n学習レベルを選択してください:")
    for i, level in enumerate(LEVELS):
        print(f"{i+1}. {level}")
    level_idx = int(input("番号を入力: ")) - 1
    level = LEVELS[level_idx] if 0 <= level_idx < len(LEVELS) else "中学生"

    print("\n好みの学習スタイルを選択してください:")
    print("1. 視覚的 (図や画像、視覚的な例えを好む)")
    print("2. 言語的 (言葉による説明や論理的な解説を好む)")
    print("3. 実践的 (実例や応用例を通じた学習を好む)")
    style_idx = int(input("番号を入力: "))
    styles = ["visual", "verbal", "practical"]
    style = styles[style_idx - 1] if 1 <= style_idx <= 3 else "visual"

    user_profile = {"name": name, "level": level, "preferred_style": style}

    while True:
        # 科目選択
        print("\n[科目選択]")
        subjects_list = list(SUBJECTS.items())
        for i, (key, subject) in enumerate(subjects_list):
            print(f"{i+1}. {subject['name']}")

        subject_idx = int(input("科目を選択してください (0: 終了): "))
        if subject_idx == 0:
            break

        if not (1 <= subject_idx <= len(subjects_list)):
            print("無効な選択です。もう一度お試しください。")
            continue

        subject_key, subject = subjects_list[subject_idx - 1]

        # トピック選択
        print(f"\n[{subject['name']}のトピック選択]")
        for i, topic in enumerate(subject["topics"]):
            print(f"{i+1}. {topic}")

        topic_idx = int(input("トピックを選択してください: "))
        if not (1 <= topic_idx <= len(subject["topics"])):
            print("無効な選択です。もう一度お試しください。")
            continue

        topic = subject["topics"][topic_idx - 1]

        # 教育コンテンツの生成
        print(f"\n「{subject['name']}」の「{topic}」の{level}向け教材を生成中...\n")
        content = generate_educational_content(subject_key, topic, level, style)
        print(content)

        # オプション選択
        while True:
            print("\n[オプション]")
            print("1. 練習問題を生成")
            print("2. この内容について質問する")
            print("3. 詳細説明を取得")
            print("4. 別のトピックを選択")
            print("0. メインメニューに戻る")

            option = int(input("選択してください: "))

            if option == 0:
                break
            elif option == 1:
                print("\n練習問題を生成中...\n")
                problems = generate_practice_problems(subject_key, topic, level, 0.5)
                print(problems)
            elif option == 2:
                question = input("\n質問を入力してください: ")
                print("\n回答を生成中...\n")
                answer = answer_question(
                    subject_key, topic, level, question, {"understanding_level": 0.5}
                )
                print(answer)
            elif option == 3:
                concept = input("\n詳細説明が欲しい概念や用語を入力してください: ")
                print(f"\n「{concept}」の詳細説明を生成中...\n")
                explanation = generate_concept_explanation(
                    subject_key, topic, concept, level
                )
                print(explanation)
            elif option == 4:
                break

    print("\nご利用ありがとうございました！")


if __name__ == "__main__":
    # コマンドライン引数で実行モードを指定可能
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        console_mode()
    else:
        # テンプレートディレクトリの確認
        if not os.path.exists("templates"):
            print(
                "警告: templatesディレクトリが見つかりません。Webインターフェースは動作しない可能性があります。"
            )
            print("コンソールモードで実行するには: python main.py --console\n")

        print("Webサーバーを起動中...")
        print("URLにアクセスしてください: http://127.0.0.1:5007")
        app.run(
            debug=True,
            port=5007,
        )
