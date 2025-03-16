"""
認証関連ルート: ログイン、登録、ログアウト機能
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from ..models import User
from ..forms import LoginForm, RegisterForm

# Blueprintの作成
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # 既にログインしている場合はダッシュボードにリダイレクト
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # ユーザーを検索
        user = User.query.filter_by(email=email).first()

        # ユーザーが存在し、パスワードが一致する場合
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("ログインしました。", "success")

            # next パラメータがある場合はそこにリダイレクト
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))
        else:
            flash("メールアドレスまたはパスワードが間違っています。", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # 既にログインしている場合はダッシュボードにリダイレクト
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # ユーザーが既に存在するか確認
        user_by_email = User.query.filter_by(email=email).first()
        user_by_username = User.query.filter_by(username=username).first()

        if user_by_email:
            flash("このメールアドレスは既に登録されています。", "danger")
        elif user_by_username:
            flash("このユーザー名は既に使用されています。", "danger")
        else:
            # 新しいユーザーを作成
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
            )

            # データベースに追加
            db.session.add(new_user)
            db.session.commit()

            flash("アカウントが作成されました。ログインしてください。", "success")
            return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトしました。", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/account", methods=["GET"])
@login_required
def account():
    return render_template("account.html")


@auth_bp.route("/account/delete", methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method == "POST":
        password = request.form.get("password")

        # パスワード検証
        if not check_password_hash(current_user.password, password):
            flash("パスワードが正しくありません。", "danger")
            return redirect(url_for("auth.delete_account"))

        try:
            user_id = current_user.id

            # 関連データをすべて削除（外部キー制約を考慮した順序で）
            # 外部キーの関係は models.py の定義を参照
            from ..models import (
                Quiz,
                QuizQuestion,
                Flashcard,
                Note,
                StudySession,
                LearningPlan,
                LearningPlanItem,
                Conversation,
                Message,
            )

            # まず関連データを削除
            quiz_ids = [quiz.id for quiz in Quiz.query.filter_by(user_id=user_id).all()]
            if quiz_ids:
                QuizQuestion.query.filter(QuizQuestion.quiz_id.in_(quiz_ids)).delete(
                    synchronize_session="fetch"
                )

            plan_ids = [
                plan.id for plan in LearningPlan.query.filter_by(user_id=user_id).all()
            ]
            if plan_ids:
                LearningPlanItem.query.filter(
                    LearningPlanItem.learning_plan_id.in_(plan_ids)
                ).delete(synchronize_session="fetch")

            conv_ids = [
                conv.id for conv in Conversation.query.filter_by(user_id=user_id).all()
            ]
            if conv_ids:
                Message.query.filter(Message.conversation_id.in_(conv_ids)).delete(
                    synchronize_session="fetch"
                )

            # ユーザーの直接データを削除
            Quiz.query.filter_by(user_id=user_id).delete()
            Flashcard.query.filter_by(user_id=user_id).delete()
            Note.query.filter_by(user_id=user_id).delete()
            StudySession.query.filter_by(user_id=user_id).delete()
            LearningPlan.query.filter_by(user_id=user_id).delete()
            Conversation.query.filter_by(user_id=user_id).delete()

            # 最後にユーザーを削除
            logout_user()
            User.query.filter_by(id=user_id).delete()

            db.session.commit()
            flash("アカウントが削除されました。", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            flash(f"アカウントの削除中にエラーが発生しました: {str(e)}", "danger")
            return redirect(url_for("auth.delete_account"))

    return render_template("delete_account.html")
