"""
学習コンテンツ関連ルート: コンテンツの生成、表示、会話機能
"""

import json
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import Subject, Topic, Conversation, Message, StudySession
from ..ai_helpers import generate_learning_content, summarize_text, ask_ai_tutor
from ..utils import markdown_to_html

# ロギングの設定
logger = logging.getLogger(__name__)

# Blueprintの作成
learning_bp = Blueprint("learning", __name__, url_prefix="/learn")


@learning_bp.route("/")
@login_required
def index():
    # 全科目と関連トピックを取得
    subjects = Subject.query.all()

    return render_template("learning/index.html", subjects=subjects)


@learning_bp.route("/select_subject")
@login_required
def select_subject():
    # 全科目を取得
    subjects = Subject.query.all()

    return render_template("learning/select_subject.html", subjects=subjects)


@learning_bp.route("/topic/<int:topic_id>")
@login_required
def topic(topic_id):
    # トピックを取得
    topic = Topic.query.get_or_404(topic_id)

    # 現在時刻を記録して学習セッション開始
    from datetime import datetime, timedelta
    current_time = datetime.utcnow()
    
    # 既存のアクティブセッションをチェック
    active_session = StudySession.query.filter_by(
        user_id=current_user.id,
        subject_id=topic.subject_id,
        topic=topic.name,
        end_time=None
    ).first()
    
    # アクティブセッションがなければ新規作成
    if not active_session:
        session = StudySession(
            user_id=current_user.id,
            subject_id=topic.subject_id,
            topic=topic.name,
            start_time=current_time
        )
        db.session.add(session)
        db.session.commit()
    
    # キャッシュの有効期限 (1週間)
    cache_expiry = timedelta(days=7)
    
    # 学習コンテンツを取得または生成
    cache_valid = topic.cache_updated_at is not None and (current_time - topic.cache_updated_at) < cache_expiry
    if topic.content_cache and cache_valid:
        # キャッシュが有効な場合はキャッシュを使用
        content = topic.content_cache
        logger.info(f"キャッシュされたコンテンツを使用: トピックID {topic_id}")
    else:
        # キャッシュがない、または古い場合は新しく生成
        content = generate_learning_content(topic.subject.name, topic.name, topic.level)
        
        # キャッシュを更新
        topic.content_cache = content
        topic.cache_updated_at = current_time
        db.session.commit()
        logger.info(f"コンテンツをキャッシュしました: トピックID {topic_id}")

    # Markdownを変換
    content_html = markdown_to_html(content)

    # 追加の学習リソースを提案
    additional_resources = [
        {"title": "例題と練習問題", "content_type": "examples"},
        {"title": "重要ポイントの要約", "content_type": "summary"},
        {"title": "理解度チェック", "content_type": "assessment"},
    ]

    # セッションIDをJavaScriptに渡すために取得
    active_session = StudySession.query.filter_by(
        user_id=current_user.id,
        subject_id=topic.subject_id,
        topic=topic.name,
        end_time=None
    ).first()
    
    return render_template(
        "learning/topic.html",
        topic=topic,
        content_html=content_html,
        additional_resources=additional_resources,
        session_id=active_session.id if active_session else None,
    )


@learning_bp.route("/subject/<subject_code>")
@login_required
def subject(subject_code):
    # 科目を取得
    subject = Subject.query.filter_by(code=subject_code).first_or_404()

    # 科目に関連するトピックを取得
    beginner_topics = Topic.query.filter_by(
        subject_id=subject.id, level="beginner"
    ).all()
    intermediate_topics = Topic.query.filter_by(
        subject_id=subject.id, level="intermediate"
    ).all()
    advanced_topics = Topic.query.filter_by(
        subject_id=subject.id, level="advanced"
    ).all()

    # 新しいトピックがなければ、AIを使って生成
    if not beginner_topics:
        # 初級トピックを生成
        try:
            beginner_topics_data = generate_topic_suggestions(
                subject.name, "beginner", 5
            )
            for topic_name in beginner_topics_data:
                topic = Topic(name=topic_name, level="beginner", subject_id=subject.id)
                db.session.add(topic)
                beginner_topics.append(topic)
        except:
            # エラー時は空のリストを使用
            pass

    if not intermediate_topics:
        # 中級トピックを生成
        try:
            intermediate_topics_data = generate_topic_suggestions(
                subject.name, "intermediate", 5
            )
            for topic_name in intermediate_topics_data:
                topic = Topic(
                    name=topic_name, level="intermediate", subject_id=subject.id
                )
                db.session.add(topic)
                intermediate_topics.append(topic)
        except:
            # エラー時は空のリストを使用
            pass

    if not advanced_topics:
        # 上級トピックを生成
        try:
            advanced_topics_data = generate_topic_suggestions(
                subject.name, "advanced", 5
            )
            for topic_name in advanced_topics_data:
                topic = Topic(name=topic_name, level="advanced", subject_id=subject.id)
                db.session.add(topic)
                advanced_topics.append(topic)
        except:
            # エラー時は空のリストを使用
            pass

    # 変更をコミット
    db.session.commit()

    return render_template(
        "learning/subject.html",
        subject=subject,
        beginner_topics=beginner_topics,
        intermediate_topics=intermediate_topics,
        advanced_topics=advanced_topics,
    )


@learning_bp.route("/conversation", methods=["GET", "POST"])
@login_required
def conversation():
    if request.method == "POST":
        title = request.form.get("title")
        subject_code = request.form.get("subject")
        topic = request.form.get("topic")

        # 科目を取得
        subject = Subject.query.filter_by(code=subject_code).first()

        if not subject:
            flash("無効な科目です。", "danger")
            return redirect(url_for("learning.conversation"))

        # 新しい会話を作成
        conversation = Conversation(
            title=title, subject_id=subject.id, topic=topic, user_id=current_user.id
        )

        db.session.add(conversation)
        db.session.commit()

        flash("新しい会話が作成されました。", "success")
        return redirect(url_for("learning.chat", conversation_id=conversation.id))

    # 全科目を取得
    subjects = Subject.query.all()

    # 既存の会話を取得
    conversations = (
        Conversation.query.filter_by(user_id=current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    return render_template(
        "learning/conversation.html", subjects=subjects, conversations=conversations
    )


@learning_bp.route("/chat/<int:conversation_id>", methods=["GET", "POST"])
@login_required
def chat(conversation_id):
    # 会話を取得
    conversation = Conversation.query.get_or_404(conversation_id)

    # 権限チェック
    if conversation.user_id != current_user.id:
        flash("この会話にアクセスする権限がありません。", "danger")
        return redirect(url_for("learning.conversation"))

    if request.method == "POST":
        # ユーザーメッセージを取得
        user_content = request.form.get("content")

        if user_content:
            # ユーザーメッセージを保存
            user_message = Message(
                conversation_id=conversation.id, role="user", content=user_content
            )
            db.session.add(user_message)

            # 会話の更新日時を更新
            conversation.updated_at = user_message.created_at

            # 会話履歴を取得
            messages = (
                Message.query.filter_by(conversation_id=conversation.id)
                .order_by(Message.created_at)
                .all()
            )

            # AIへの入力用メッセージリスト
            api_messages = [{"role": m.role, "content": m.content} for m in messages]

            # AIからの回答を生成
            assistant_content = ask_ai_tutor(
                api_messages,
                conversation.subject.name if conversation.subject else None,
                conversation.topic,
            )

            # AIの回答を保存
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=assistant_content,
            )
            db.session.add(assistant_message)

            db.session.commit()

            return redirect(url_for("learning.chat", conversation_id=conversation.id))

    # メッセージを取得
    messages = (
        Message.query.filter_by(conversation_id=conversation.id)
        .order_by(Message.created_at)
        .all()
    )

    # メッセージのHTMLを作成
    for message in messages:
        if message.role == "assistant":
            message.content_html = markdown_to_html(message.content)

    return render_template(
        "learning/chat.html", conversation=conversation, messages=messages
    )


@learning_bp.route("/api/content/<int:topic_id>", methods=["GET"])
@login_required
def api_get_content(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    
    # 現在時刻を取得
    from datetime import datetime, timedelta
    current_time = datetime.utcnow()
    
    # キャッシュの有効期限 (1週間)
    cache_expiry = timedelta(days=7)

    # コンテンツタイプ
    content_type = request.args.get("type", "explanation")
    
    # キャッシュ確認とコンテンツ取得
    cache_valid = topic.cache_updated_at is not None and (current_time - topic.cache_updated_at) < cache_expiry
    
    if content_type == "examples" and topic.examples_cache and cache_valid:
        # 例題キャッシュを使用
        content = topic.examples_cache
        logger.info(f"キャッシュされた例題を使用: トピックID {topic_id}")
    elif content_type == "summary" and topic.summary_cache and cache_valid:
        # 要約キャッシュを使用
        content = topic.summary_cache
        logger.info(f"キャッシュされた要約を使用: トピックID {topic_id}")
    elif content_type == "assessment" and topic.assessment_cache and cache_valid:
        # 評価問題キャッシュを使用
        content = topic.assessment_cache
        logger.info(f"キャッシュされた評価問題を使用: トピックID {topic_id}")
    else:
        # キャッシュがない場合は新しく生成
        content = generate_learning_content(
            topic.subject.name, topic.name, topic.level, content_type=content_type
        )
        
        # コンテンツタイプに応じてキャッシュを更新
        if content_type == "examples":
            topic.examples_cache = content
            topic.cache_updated_at = current_time
        elif content_type == "summary":
            topic.summary_cache = content
            topic.cache_updated_at = current_time
        elif content_type == "assessment":
            topic.assessment_cache = content
            topic.cache_updated_at = current_time
            
        db.session.commit()
        logger.info(f"{content_type}コンテンツをキャッシュしました: トピックID {topic_id}")

    return jsonify(
        {"topic": topic.name, "content_type": content_type, "content": content}
    )
    
@learning_bp.route("/api/end_session", methods=["POST"])
@login_required
def api_end_session():
    """学習セッションを終了し、学習時間を記録する"""
    session_id = request.json.get("session_id")
    
    if not session_id:
        return jsonify({"error": "セッションIDが提供されていません"}), 400
        
    # セッションの検索
    session = StudySession.query.filter_by(
        id=session_id,
        user_id=current_user.id,
        end_time=None
    ).first()
    
    if not session:
        return jsonify({"error": "アクティブなセッションが見つかりません"}), 404
        
    # 現在時刻を設定
    from datetime import datetime
    end_time = datetime.utcnow()
    
    # 経過時間を分で計算
    duration_minutes = int((end_time - session.start_time).total_seconds() / 60)
    
    # セッションを更新
    session.end_time = end_time
    session.duration_minutes = duration_minutes
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "学習セッションを終了しました",
        "duration_minutes": duration_minutes
    })


@learning_bp.route("/api/summarize", methods=["POST"])
@login_required
def api_summarize():
    text = request.json.get("text", "")
    if not text:
        return jsonify({"error": "テキストが提供されていません"}), 400

    # テキストを要約
    summary = summarize_text(text)

    return jsonify({"summary": summary})


def generate_topic_suggestions(subject, level, count=5):
    """指定された科目とレベルに適したトピック名のリストを生成する"""

    # プロンプトの作成
    prompt = f"{subject}の{level}レベルに適したトピックを{count}個提案してください。"
    prompt += f"各トピックは100文字以内の簡潔な名前にしてください。"
    prompt += f"トピック名のみのJSON配列形式で返してください。余分なテキストは含めないでください。"

    try:
        # テスト環境では直接デフォルトトピックを返す
        from ..ai_helpers import MOCK_MODE

        if MOCK_MODE:
            default_topics = {
                "python": [
                    "基本構文と変数",
                    "関数とモジュール",
                    "クラスとオブジェクト",
                    "データ構造",
                    "ファイル操作",
                ],
                "javascript": [
                    "基本構文",
                    "DOM操作",
                    "イベント処理",
                    "非同期処理",
                    "モダンJavaScript",
                ],
                "math": ["数と計算", "代数学", "幾何学", "確率と統計", "微積分"],
                "science": [
                    "物理学の基礎",
                    "化学の基礎",
                    "生物学入門",
                    "地球科学",
                    "科学的思考法",
                ],
                "history": [
                    "古代文明",
                    "中世の社会",
                    "近代の変革",
                    "現代史",
                    "文化と芸術の歴史",
                ],
                "language": [
                    "文法の基礎",
                    "語彙と表現",
                    "読解スキル",
                    "作文技術",
                    "コミュニケーション",
                ],
            }

            # 科目名から適切なデフォルトトピックを選択
            for key in default_topics:
                if key.lower() in subject.lower():
                    return default_topics[key]

            # 一致する科目がない場合は最初のデフォルトを使用
            return list(default_topics.values())[0]

        # OpenAI Responses APIを呼び出し
        from ..ai_core import client, DEFAULT_MODEL

        response = client.responses.create(
            model=DEFAULT_MODEL,
            input=prompt,
            temperature=0.7,
        )

        # 生成された内容をパース
        content = response.output_text
        topics = json.loads(content)

        return topics
    except Exception as e:
        # エラーが発生した場合はデフォルトのトピックを返す
        default_topics = {
            "python": [
                "基本構文と変数",
                "関数とモジュール",
                "クラスとオブジェクト",
                "データ構造",
                "ファイル操作",
            ],
            "javascript": [
                "基本構文",
                "DOM操作",
                "イベント処理",
                "非同期処理",
                "モダンJavaScript",
            ],
            "math": ["数と計算", "代数学", "幾何学", "確率と統計", "微積分"],
            "science": [
                "物理学の基礎",
                "化学の基礎",
                "生物学入門",
                "地球科学",
                "科学的思考法",
            ],
            "history": [
                "古代文明",
                "中世の社会",
                "近代の変革",
                "現代史",
                "文化と芸術の歴史",
            ],
            "language": [
                "文法の基礎",
                "語彙と表現",
                "読解スキル",
                "作文技術",
                "コミュニケーション",
            ],
        }

        # 科目名から適切なデフォルトトピックを選択
        for key in default_topics:
            if key.lower() in subject.lower():
                return default_topics[key]

        # 一致する科目がない場合は最初のデフォルトを使用
        return list(default_topics.values())[0]
