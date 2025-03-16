"""
統計関連ルート: 学習統計、進捗、可視化機能
"""

import io
import base64
import logging
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend globally
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 日本語フォント設定
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
import numpy as np
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import StudySession, Quiz, Note, Flashcard, Subject
from ..utils import format_datetime

# ロギングの設定
logger = logging.getLogger(__name__)

# Blueprintの作成
stats_bp = Blueprint("stats", __name__, url_prefix="/stats")


@stats_bp.route("/")
@login_required
def index():
    # 過去の期間ごとのデータを取得
    periods = {
        "week": datetime.utcnow() - timedelta(days=7),
        "month": datetime.utcnow() - timedelta(days=30),
        "year": datetime.utcnow() - timedelta(days=365),
    }

    stats = {}

    # 学習時間の統計
    total_study_time = (
        StudySession.query.filter_by(user_id=current_user.id)
        .with_entities(db.func.sum(StudySession.duration_minutes))
        .scalar()
        or 0
    )

    # 期間ごとの学習時間
    period_times = {}
    for period_name, start_date in periods.items():
        time = (
            StudySession.query.filter(
                StudySession.user_id == current_user.id,
                StudySession.start_time >= start_date,
            )
            .with_entities(db.func.sum(StudySession.duration_minutes))
            .scalar()
            or 0
        )
        period_times[period_name] = time

    stats["study_time"] = {"total": total_study_time, "periods": period_times}

    # クイズの統計
    total_quizzes = Quiz.query.filter_by(user_id=current_user.id).count()
    completed_quizzes = Quiz.query.filter(
        Quiz.user_id == current_user.id, Quiz.completed_at.isnot(None)
    ).count()

    # 平均スコア
    avg_score = (
        db.session.query(db.func.avg(Quiz.score))
        .filter(Quiz.user_id == current_user.id, Quiz.completed_at.isnot(None))
        .scalar()
        or 0
    )

    stats["quizzes"] = {
        "total": total_quizzes,
        "completed": completed_quizzes,
        "avg_score": round(avg_score, 1),
    }

    # ノートの統計
    total_notes = Note.query.filter_by(user_id=current_user.id).count()

    # 期間ごとのノート数
    period_notes = {}
    for period_name, start_date in periods.items():
        count = Note.query.filter(
            Note.user_id == current_user.id, Note.created_at >= start_date
        ).count()
        period_notes[period_name] = count

    stats["notes"] = {"total": total_notes, "periods": period_notes}

    # フラッシュカードの統計
    total_flashcards = Flashcard.query.filter_by(user_id=current_user.id).count()
    reviewed_flashcards = Flashcard.query.filter(
        Flashcard.user_id == current_user.id, Flashcard.last_reviewed.isnot(None)
    ).count()

    stats["flashcards"] = {"total": total_flashcards, "reviewed": reviewed_flashcards}

    # 学習の強度マップを生成
    intensity_map = generate_intensity_map()

    # 科目ごとの学習時間グラフを生成
    subject_time_chart = generate_subject_time_chart()

    # クイズスコアの推移グラフを生成
    quiz_score_chart = generate_quiz_score_chart()

    return render_template(
        "stats/index.html",
        stats=stats,
        intensity_map=intensity_map,
        subject_time_chart=subject_time_chart,
        quiz_score_chart=quiz_score_chart,
    )


@stats_bp.route("/api/study_time")
@login_required
def api_study_time():
    # 期間を取得
    period = request.args.get("period", "month")

    if period == "week":
        days = 7
    elif period == "month":
        days = 30
    elif period == "year":
        days = 365
    else:
        days = 30  # デフォルト

    start_date = datetime.utcnow() - timedelta(days=days)

    # 日ごとの学習時間を集計
    query = (
        db.session.query(
            db.func.date(StudySession.start_time).label("date"),
            db.func.sum(StudySession.duration_minutes).label("duration"),
        )
        .filter(
            StudySession.user_id == current_user.id,
            StudySession.start_time >= start_date,
        )
        .group_by("date")
        .order_by("date")
        .all()
    )

    # 結果を整形
    dates = []
    durations = []

    for date, duration in query:
        dates.append(date.strftime("%Y-%m-%d"))
        durations.append(duration)

    return jsonify({"dates": dates, "durations": durations})


def generate_intensity_map():
    """過去6ヶ月間の学習強度マップを生成"""
    start_date = datetime.utcnow() - timedelta(days=180)

    # 日ごとの学習時間を集計
    study_sessions = StudySession.query.filter(
        StudySession.user_id == current_user.id, StudySession.start_time >= start_date
    ).all()

    # 日付ごとの学習時間を集計
    daily_minutes = {}

    for session in study_sessions:
        date_str = session.start_time.strftime("%Y-%m-%d")
        minutes = session.duration_minutes or 0

        if date_str in daily_minutes:
            daily_minutes[date_str] += minutes
        else:
            daily_minutes[date_str] = minutes

    # 6ヶ月間の全日付を生成
    all_dates = []
    current_date = start_date
    end_date = datetime.utcnow()

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        all_dates.append(date_str)
        current_date += timedelta(days=1)

    # 各日の学習時間（分）
    values = [daily_minutes.get(date, 0) for date in all_dates]

    try:
        # ヒートマップ生成のためのデータ整形
        weeks = len(all_dates) // 7 + 1
        data = np.zeros((7, weeks))

        for i, date_str in enumerate(all_dates):
            date = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = date.weekday()  # 0=月曜日, 6=日曜日
            week = i // 7
            data[weekday, week] = daily_minutes.get(date_str, 0)

        # プロット生成 - non-interactive backend to avoid GUI thread issues
        plt.switch_backend('Agg')  # Use non-interactive backend
        
        # 毎回フォント設定を再適用
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
        plt.rcParams['font.size'] = 10
        
        fig = plt.figure(figsize=(10, 4))
        ax = fig.add_subplot(111)
        im = ax.imshow(data, cmap="YlGn")

        # 軸ラベル - 日本語対応
        ax.set_yticks(np.arange(7))
        weekday_labels = ["月", "火", "水", "木", "金", "土", "日"]
        ax.set_yticklabels(weekday_labels)

        # 月のラベルを追加
        month_positions = []
        month_labels = []
        current_date = start_date
        current_week = 0

        while current_date <= end_date:
            if current_date.day == 1 or (current_date == start_date):
                month_positions.append(current_week)
                month_labels.append(current_date.strftime("%m月"))

            current_date += timedelta(days=7)
            current_week += 1

        ax.set_xticks(month_positions)
        ax.set_xticklabels(month_labels)

        # フォントサイズを調整して日本語を見やすくする
        plt.rcParams['font.size'] = 10
        
        # カラーバー
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label("学習時間（分）", fontsize=10)

        # タイトル
        plt.title("学習強度マップ（過去6ヶ月）", fontsize=12)

        # 画像をバイト列に変換
        img_data = io.BytesIO()
        plt.savefig(img_data, format="png", bbox_inches="tight")
        img_data.seek(0)
        plt.close()

        # Base64エンコード
        encoded = base64.b64encode(img_data.read()).decode("utf-8")

        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        logger.error(f"学習強度マップ生成エラー: {str(e)}")
        return None


def generate_subject_time_chart():
    """科目ごとの学習時間の円グラフを生成"""
    # 科目ごとの学習時間を集計
    query = (
        db.session.query(
            Subject.name, db.func.sum(StudySession.duration_minutes).label("duration")
        )
        .join(Subject, Subject.id == StudySession.subject_id)
        .filter(StudySession.user_id == current_user.id)
        .group_by(Subject.name)
        .all()
    )

    # 結果を整形
    labels = []
    sizes = []

    for name, duration in query:
        if duration > 0:
            labels.append(name)
            sizes.append(duration)

    # データがない場合
    if not sizes:
        return None

    try:
        # 円グラフの生成 - non-interactive backend to avoid GUI thread issues
        plt.switch_backend('Agg')  # Use non-interactive backend
        
        # 毎回フォント設定を再適用
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
        plt.rcParams['font.size'] = 10
        
        fig, ax = plt.subplots(figsize=(8, 6))

        # パステルカラーを使用
        colors = plt.cm.Pastel1(np.arange(len(labels)) % 8)

        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
        ax.axis("equal")  # アスペクト比を1:1に

        plt.title("科目ごとの学習時間", fontsize=12)

        # 画像をバイト列に変換
        img_data = io.BytesIO()
        plt.savefig(img_data, format="png", bbox_inches="tight")
        img_data.seek(0)
        plt.close()

        # Base64エンコード
        encoded = base64.b64encode(img_data.read()).decode("utf-8")

        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        logger.error(f"科目ごとの学習時間グラフ生成エラー: {str(e)}")
        return None


def generate_quiz_score_chart():
    """クイズスコアの推移グラフを生成"""
    # 完了したクイズを取得
    quizzes = (
        Quiz.query.filter(
            Quiz.user_id == current_user.id, Quiz.completed_at.isnot(None)
        )
        .order_by(Quiz.completed_at)
        .limit(20)
        .all()
    )

    # データがない場合
    if not quizzes:
        return None

    try:
        # データを整形
        dates = [quiz.completed_at.strftime("%m/%d") for quiz in quizzes]
        scores = [quiz.score or 0 for quiz in quizzes]

        # グラフの生成 - non-interactive backend to avoid GUI thread issues
        plt.switch_backend('Agg')  # Use non-interactive backend
        
        # 毎回フォント設定を再適用
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
        plt.rcParams['font.size'] = 10
        
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(dates, scores, "o-", color="#3498db")
        ax.set_ylim(0, 100)

        # x軸のラベルを調整（混雑を避けるため）
        if len(dates) > 10:
            plt.xticks(rotation=45, ha="right")
            # 表示するラベルを間引く
            step = len(dates) // 10 + 1
            ax.set_xticks(ax.get_xticks()[::step])

        # グリッド線
        ax.grid(True, linestyle="--", alpha=0.7)

        # ラベル - 日本語フォント対応
        ax.set_xlabel("日付", fontsize=10)
        ax.set_ylabel("スコア", fontsize=10)
        plt.title("クイズスコアの推移", fontsize=12)

        # レイアウト調整
        plt.tight_layout()

        # 画像をバイト列に変換
        img_data = io.BytesIO()
        plt.savefig(img_data, format="png", bbox_inches="tight")
        img_data.seek(0)
        plt.close()

        # Base64エンコード
        encoded = base64.b64encode(img_data.read()).decode("utf-8")

        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        logger.error(f"クイズスコアのグラフ生成エラー: {str(e)}")
        return None
