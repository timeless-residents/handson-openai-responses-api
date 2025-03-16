"""
クイズ関連ルート: クイズの作成、表示、回答、結果確認機能
"""

import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import Subject, Quiz, QuizQuestion
from ..forms import CreateQuizForm
from ..ai_helpers import generate_quiz_questions

# Blueprintの作成
quizzes_bp = Blueprint("quizzes", __name__, url_prefix="/quizzes")


@quizzes_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = CreateQuizForm()

    # 科目のリストを設定
    subjects = Subject.query.all()
    form.subject.choices = [(s.code, s.name) for s in subjects]

    if form.validate_on_submit():
        subject_code = form.subject.data
        topic = form.topic.data
        level = form.level.data
        title = form.title.data
        num_questions = form.num_questions.data

        # 科目情報を取得
        subject = Subject.query.filter_by(code=subject_code).first()
        if not subject:
            flash("無効な科目です。", "danger")
            return redirect(url_for("quizzes.index"))

        # クイズを作成
        quiz = Quiz(
            title=title,
            subject_id=subject.id,
            topic=topic,
            level=level,
            user_id=current_user.id,
        )
        db.session.add(quiz)
        db.session.commit()

        # AIを使って問題を生成
        try:
            questions = generate_quiz_questions(
                subject.name, topic, level, num_questions
            )

            # 問題をデータベースに保存
            for q_data in questions:
                question = QuizQuestion(
                    quiz_id=quiz.id,
                    question=q_data.get("question", ""),
                    options=json.dumps(q_data.get("options", [])),
                    answer=q_data.get("answer", ""),
                    explanation=q_data.get("explanation", ""),
                )
                db.session.add(question)

            db.session.commit()

            flash("クイズが作成されました。", "success")
            return redirect(url_for("quizzes.view", quiz_id=quiz.id))

        except Exception as e:
            db.session.rollback()
            flash(f"問題の生成中にエラーが発生しました: {str(e)}", "danger")
            return redirect(url_for("quizzes.index"))

    # 既存のクイズを取得
    quizzes = (
        Quiz.query.filter_by(user_id=current_user.id)
        .order_by(Quiz.created_at.desc())
        .all()
    )

    return render_template("quizzes/index.html", form=form, quizzes=quizzes)


@quizzes_bp.route("/<int:quiz_id>")
@login_required
def view(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # 権限チェック
    if quiz.user_id != current_user.id:
        flash("このクイズにアクセスする権限がありません。", "danger")
        return redirect(url_for("quizzes.index"))

    # 問題を取得
    questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()

    # 選択肢をJSONからデコード
    for question in questions:
        if question.options:
            try:
                question.options_list = json.loads(question.options)
            except:
                question.options_list = []
        else:
            question.options_list = []

    return render_template("quizzes/view.html", quiz=quiz, questions=questions)


@quizzes_bp.route("/<int:quiz_id>/take")
@login_required
def take(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # 権限チェック
    if quiz.user_id != current_user.id:
        flash("このクイズにアクセスする権限がありません。", "danger")
        return redirect(url_for("quizzes.index"))

    # クイズが既に完了している場合
    if quiz.completed_at:
        flash("このクイズは既に完了しています。", "info")
        return redirect(url_for("quizzes.result", quiz_id=quiz.id))

    # 問題を取得
    questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()

    # 選択肢をJSONからデコード
    for question in questions:
        if question.options:
            try:
                question.options_list = json.loads(question.options)
            except:
                question.options_list = []
        else:
            question.options_list = []

    return render_template("quizzes/take.html", quiz=quiz, questions=questions)


@quizzes_bp.route("/<int:quiz_id>/submit", methods=["POST"])
@login_required
def submit(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # 権限チェック
    if quiz.user_id != current_user.id:
        flash("このクイズにアクセスする権限がありません。", "danger")
        return redirect(url_for("quizzes.index"))

    # クイズが既に完了している場合
    if quiz.completed_at:
        flash("このクイズは既に完了しています。", "info")
        return redirect(url_for("quizzes.result", quiz_id=quiz.id))

    # 問題を取得
    questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()

    # 回答を処理
    total_questions = len(questions)
    correct_count = 0

    for question in questions:
        # フォームから回答を取得
        user_answer = request.form.get(f"answer_{question.id}", "")

        # 回答を保存
        question.user_answer = user_answer

        # 正解判定
        question.is_correct = user_answer.strip() == question.answer.strip()

        if question.is_correct:
            correct_count += 1

    # スコアを計算
    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    # クイズを完了としてマーク
    quiz.completed_at = datetime.utcnow()
    quiz.score = score

    db.session.commit()

    return redirect(url_for("quizzes.result", quiz_id=quiz.id))


@quizzes_bp.route("/<int:quiz_id>/result")
@login_required
def result(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # 権限チェック
    if quiz.user_id != current_user.id:
        flash("このクイズにアクセスする権限がありません。", "danger")
        return redirect(url_for("quizzes.index"))

    # クイズが完了していることを確認
    if not quiz.completed_at:
        flash("このクイズはまだ完了していません。", "warning")
        return redirect(url_for("quizzes.take", quiz_id=quiz.id))

    # クイズの問題と回答を取得
    questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()

    # 選択肢をJSONからデコード
    for question in questions:
        if question.options:
            try:
                question.options_list = json.loads(question.options)
            except:
                question.options_list = []
        else:
            question.options_list = []

    return render_template("quizzes/result.html", quiz=quiz, questions=questions)
