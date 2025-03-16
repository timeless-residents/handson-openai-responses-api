"""
ダッシュボード関連ルート: ダッシュボード、統計、データリセット機能
"""

from datetime import datetime, timedelta
import json
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .. import db
from ..models import (
    Subject,
    Quiz,
    Note,
    Flashcard,
    StudySession,
    LearningPlan,
    Conversation,
    Message,
    QuizQuestion,
    LearningPlanItem,
)
from ..utils import format_datetime, generate_wordcloud

# ロギングの設定
logger = logging.getLogger(__name__)

# Blueprintの作成
dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("index.html")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = current_user.id

    # 最近の進捗情報を取得
    recent_quizzes = (
        Quiz.query.filter_by(user_id=user_id)
        .order_by(Quiz.created_at.desc())
        .limit(5)
        .all()
    )
    recent_notes = (
        Note.query.filter_by(user_id=user_id)
        .order_by(Note.updated_at.desc())
        .limit(5)
        .all()
    )
    recent_sessions = (
        StudySession.query.filter_by(user_id=user_id)
        .order_by(StudySession.start_time.desc())
        .limit(5)
        .all()
    )

    # 学習プランの進捗
    active_plans = (
        LearningPlan.query.filter_by(user_id=user_id)
        .order_by(LearningPlan.created_at.desc())
        .limit(3)
        .all()
    )
    for plan in active_plans:
        # 完了したアイテムの割合を計算
        completed_items = len([item for item in plan.items if item.completed])
        total_items = len(plan.items)
        plan.progress = int(
            (completed_items / total_items * 100) if total_items > 0 else 0
        )

    # 科目ごとの学習時間（過去30日間）
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    study_sessions = StudySession.query.filter(
        StudySession.user_id == user_id, StudySession.start_time >= thirty_days_ago
    ).all()

    # 科目ごとに学習時間を集計
    subject_times = {}
    for session in study_sessions:
        subject_name = session.subject.name
        duration = session.duration_minutes or 0

        if subject_name in subject_times:
            subject_times[subject_name] += duration
        else:
            subject_times[subject_name] = duration

    # 総学習時間を計算
    total_study_time = sum(subject_times.values())

    # クイズの平均スコア
    completed_quizzes = Quiz.query.filter(
        Quiz.user_id == user_id, Quiz.completed_at.isnot(None)
    ).all()

    avg_score = 0
    if completed_quizzes:
        avg_score = sum(quiz.score or 0 for quiz in completed_quizzes) / len(
            completed_quizzes
        )

    return render_template(
        "dashboard.html",
        recent_quizzes=recent_quizzes,
        recent_notes=recent_notes,
        recent_sessions=recent_sessions,
        active_plans=active_plans,
        subject_times=subject_times,
        total_study_time=total_study_time,
        avg_score=avg_score,
        format_datetime=format_datetime,
    )


@dashboard_bp.route("/reset_data", methods=["GET", "POST"])
@login_required
def reset_data():
    if request.method == "POST":
        data_type = request.form.get("data_type", "all")

        try:
            # 現在のユーザーのデータのみを削除
            user_id = current_user.id

            if data_type == "quizzes" or data_type == "all":
                # クイズの問題を先に削除（外部キー制約のため）
                quiz_ids = [
                    quiz.id for quiz in Quiz.query.filter_by(user_id=user_id).all()
                ]
                if quiz_ids:
                    QuizQuestion.query.filter(
                        QuizQuestion.quiz_id.in_(quiz_ids)
                    ).delete(synchronize_session="fetch")
                    Quiz.query.filter_by(user_id=user_id).delete()

            if data_type == "flashcards" or data_type == "all":
                Flashcard.query.filter_by(user_id=user_id).delete()

            if data_type == "notes" or data_type == "all":
                Note.query.filter_by(user_id=user_id).delete()

            if data_type == "sessions" or data_type == "all":
                StudySession.query.filter_by(user_id=user_id).delete()

            if data_type == "plans" or data_type == "all":
                # 学習プランのアイテムを先に削除（外部キー制約のため）
                plan_ids = [
                    plan.id
                    for plan in LearningPlan.query.filter_by(user_id=user_id).all()
                ]
                if plan_ids:
                    LearningPlanItem.query.filter(
                        LearningPlanItem.learning_plan_id.in_(plan_ids)
                    ).delete(synchronize_session="fetch")
                    LearningPlan.query.filter_by(user_id=user_id).delete()

            if data_type == "conversations" or data_type == "all":
                # メッセージを先に削除（外部キー制約のため）
                conv_ids = [
                    conv.id
                    for conv in Conversation.query.filter_by(user_id=user_id).all()
                ]
                if conv_ids:
                    Message.query.filter(Message.conversation_id.in_(conv_ids)).delete(
                        synchronize_session="fetch"
                    )
                    Conversation.query.filter_by(user_id=user_id).delete()

            db.session.commit()
            flash("選択したデータが正常にリセットされました。", "success")

        except Exception as e:
            db.session.rollback()
            logger.error(f"データリセットエラー: {str(e)}")
            flash(f"データのリセット中にエラーが発生しました: {str(e)}", "danger")

        return redirect(url_for("dashboard.dashboard"))

    return render_template("reset_data.html")


@dashboard_bp.route("/admin/reset_database", methods=["GET", "POST"])
@login_required
def admin_reset_database():
    # 管理者権限チェック（仮にemail='admin@example.com'とする）
    if current_user.email != "admin@example.com":
        flash("管理者権限が必要です。", "danger")
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "reset_all_data":
            try:
                # すべてのテーブルを削除して再作成
                db.drop_all()
                db.create_all()

                # 初期データを再登録
                from ..config import SUBJECTS

                for code, name in SUBJECTS:
                    subject = Subject(code=code, name=name)
                    db.session.add(subject)
                db.session.commit()

                flash("データベースが完全にリセットされました。", "success")
            except Exception as e:
                db.session.rollback()
                logger.error(f"データベースリセットエラー: {str(e)}")
                flash(
                    f"データベースのリセット中にエラーが発生しました: {str(e)}",
                    "danger",
                )

        return redirect(url_for("dashboard.admin_reset_database"))

    return render_template("admin_reset_database.html")
