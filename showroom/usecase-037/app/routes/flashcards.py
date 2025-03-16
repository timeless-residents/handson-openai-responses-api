"""
フラッシュカード関連ルート: カードの作成、表示、学習機能
"""

import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import Subject, Flashcard
from ..forms import FlashcardForm
from ..ai_helpers import generate_flashcards

# Blueprintの作成
flashcards_bp = Blueprint("flashcards", __name__, url_prefix="/flashcards")


@flashcards_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = FlashcardForm()

    # 科目のリストを設定
    subjects = Subject.query.all()
    form.subject.choices = [(s.code, s.name) for s in subjects]

    if form.validate_on_submit():
        subject_code = form.subject.data
        topic = form.topic.data
        level = form.level.data
        num_cards = form.num_cards.data

        # 科目情報を取得
        subject = Subject.query.filter_by(code=subject_code).first()
        if not subject:
            flash("無効な科目です。", "danger")
            return redirect(url_for("flashcards.index"))

        # AIを使ってフラッシュカードを生成
        try:
            cards = generate_flashcards(subject.name, topic, level, num_cards)

            # フラッシュカードをデータベースに保存
            for card_data in cards:
                flashcard = Flashcard(
                    subject_id=subject.id,
                    topic=topic,
                    front=card_data.get("front", ""),
                    back=card_data.get("back", ""),
                    level=level,
                    user_id=current_user.id,
                )
                db.session.add(flashcard)

            db.session.commit()

            flash("フラッシュカードが作成されました。", "success")
            return redirect(
                url_for("flashcards.study", subject_code=subject_code, topic=topic)
            )

        except Exception as e:
            db.session.rollback()
            flash(f"フラッシュカードの生成中にエラーが発生しました: {str(e)}", "danger")
            return redirect(url_for("flashcards.index"))

    return render_template("flashcards/index.html", form=form)


@flashcards_bp.route("/library")
@login_required
def library():
    # すべての科目を取得
    subjects = Subject.query.all()

    # 各科目ごとのトピックを集計
    topics_by_subject = {}

    for subject in subjects:
        # この科目に関連するフラッシュカードからトピックを取得
        flashcards = Flashcard.query.filter_by(
            user_id=current_user.id, subject_id=subject.id
        ).all()

        # トピックを集計
        topics = set()
        card_count = 0

        for card in flashcards:
            if card.topic:
                topics.add(card.topic)
            card_count += 1

        # 科目ごとの情報を保存
        if card_count > 0:
            topics_by_subject[subject] = {
                "topics": sorted(list(topics)),
                "card_count": card_count,
            }

    return render_template(
        "flashcards/library.html", topics_by_subject=topics_by_subject
    )


@flashcards_bp.route("/study")
@login_required
def study_selection():
    # すべての科目を取得
    subjects = Subject.query.all()

    # 各科目ごとのトピックを集計（フラッシュカードが存在するもののみ）
    topics_by_subject = {}

    for subject in subjects:
        # この科目に関連するフラッシュカードからトピックを取得
        flashcards = Flashcard.query.filter_by(
            user_id=current_user.id, subject_id=subject.id
        ).all()

        # トピックを集計
        topics = set()
        card_count = 0

        for card in flashcards:
            if card.topic:
                topics.add(card.topic)
            card_count += 1

        # 科目ごとの情報を保存
        if card_count > 0:
            topics_by_subject[subject] = {
                "topics": sorted(list(topics)),
                "card_count": card_count,
            }

    return render_template(
        "flashcards/study_selection.html", topics_by_subject=topics_by_subject
    )


@flashcards_bp.route("/study/<subject_code>/<topic>")
@login_required
def study(subject_code, topic):
    # 科目を取得
    subject = Subject.query.filter_by(code=subject_code).first_or_404()

    # フラッシュカードを取得
    flashcards = Flashcard.query.filter_by(
        user_id=current_user.id, subject_id=subject.id, topic=topic
    ).all()

    if not flashcards:
        flash("指定されたトピックのフラッシュカードが見つかりません。", "warning")
        return redirect(url_for("flashcards.study_selection"))

    return render_template(
        "flashcards/study.html", subject=subject, topic=topic, flashcards=flashcards
    )


@flashcards_bp.route("/update_familiarity", methods=["POST"])
@login_required
def update_familiarity():
    card_id = request.form.get("card_id")
    familiarity = request.form.get("familiarity")

    if not card_id or not familiarity:
        return (
            jsonify(
                {"status": "error", "message": "必要なパラメータが不足しています。"}
            ),
            400,
        )

    try:
        familiarity = int(familiarity)
        if familiarity < 0 or familiarity > 5:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "理解度は0〜5の範囲で指定してください。",
                    }
                ),
                400,
            )
    except:
        return (
            jsonify({"status": "error", "message": "理解度は数値で指定してください。"}),
            400,
        )

    # カードを取得
    card = Flashcard.query.get_or_404(card_id)

    # 権限チェック
    if card.user_id != current_user.id:
        return (
            jsonify(
                {"status": "error", "message": "このカードを更新する権限がありません。"}
            ),
            403,
        )

    # 理解度と最終レビュー日時を更新
    card.familiarity = familiarity
    card.last_reviewed = datetime.utcnow()

    db.session.commit()

    return jsonify(
        {"status": "success", "card_id": card_id, "familiarity": familiarity}
    )


@flashcards_bp.route("/create_manual", methods=["GET", "POST"])
@login_required
def create_manual():
    if request.method == "POST":
        subject_code = request.form.get("subject")
        topic = request.form.get("topic")
        front = request.form.get("front")
        back = request.form.get("back")
        level = request.form.get("level")

        # バリデーション
        if not subject_code or not topic or not front or not back or not level:
            flash("すべての項目を入力してください。", "danger")
            return redirect(url_for("flashcards.create_manual"))

        # 科目情報を取得
        subject = Subject.query.filter_by(code=subject_code).first()
        if not subject:
            flash("無効な科目です。", "danger")
            return redirect(url_for("flashcards.create_manual"))

        # フラッシュカードを作成
        flashcard = Flashcard(
            subject_id=subject.id,
            topic=topic,
            front=front,
            back=back,
            level=level,
            user_id=current_user.id,
        )

        db.session.add(flashcard)
        db.session.commit()

        flash("フラッシュカードが作成されました。", "success")
        return redirect(
            url_for("flashcards.study", subject_code=subject_code, topic=topic)
        )

    # 科目のリストを取得
    subjects = Subject.query.all()

    return render_template(
        "flashcards/create_manual.html", subjects=[(s.code, s.name) for s in subjects]
    )
