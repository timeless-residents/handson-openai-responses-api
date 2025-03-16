"""
学習プラン関連ルート: プランの作成、表示、更新機能
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import Subject, LearningPlan, LearningPlanItem
from ..forms import CreatePlanForm
from ..ai_helpers import generate_learning_plan
from ..utils import markdown_to_html

# Blueprintの作成
plans_bp = Blueprint("plans", __name__, url_prefix="/plans")


@plans_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = CreatePlanForm()

    # 科目のリストを設定
    subjects = Subject.query.all()
    form.subject.choices = [(s.code, s.name) for s in subjects]

    if form.validate_on_submit():
        title = form.title.data
        subject_code = form.subject.data
        level = form.level.data
        description = form.description.data

        # 科目を取得
        subject = Subject.query.filter_by(code=subject_code).first()
        if not subject:
            flash("無効な科目です。", "danger")
            return redirect(url_for("plans.index"))

        # AIを使って学習プランを生成
        try:
            plan_data = generate_learning_plan(subject.name, None, level)

            # 学習プランをデータベースに保存
            learning_plan = LearningPlan(
                title=title or plan_data.get("title", f"{subject.name}の学習プラン"),
                description=description or plan_data.get("description", ""),
                subject_id=subject.id,
                user_id=current_user.id,
                level=level,
            )

            db.session.add(learning_plan)
            db.session.commit()

            # プランのアイテムを保存
            for item_data in plan_data.get("items", []):
                item = LearningPlanItem(
                    learning_plan_id=learning_plan.id,
                    title=item_data.get("title", ""),
                    description=item_data.get("description", ""),
                    order=item_data.get("order", 0),
                )
                db.session.add(item)

            db.session.commit()

            flash("学習プランが作成されました。", "success")
            return redirect(url_for("plans.view", plan_id=learning_plan.id))

        except Exception as e:
            db.session.rollback()
            flash(f"学習プランの生成中にエラーが発生しました: {str(e)}", "danger")
            return redirect(url_for("plans.index"))

    # 既存の学習プランを取得
    plans = (
        LearningPlan.query.filter_by(user_id=current_user.id)
        .order_by(LearningPlan.created_at.desc())
        .all()
    )

    return render_template("plans/index.html", form=form, plans=plans)


@plans_bp.route("/<int:plan_id>")
@login_required
def view(plan_id):
    plan = LearningPlan.query.get_or_404(plan_id)

    # 権限チェック
    if plan.user_id != current_user.id:
        flash("この学習プランにアクセスする権限がありません。", "danger")
        return redirect(url_for("plans.index"))

    # プランの項目を取得して順番に並べる
    items = (
        LearningPlanItem.query.filter_by(learning_plan_id=plan.id)
        .order_by(LearningPlanItem.order)
        .all()
    )

    # 進捗計算
    total_items = len(items)
    completed_items = len([item for item in items if item.completed])
    progress = int((completed_items / total_items * 100) if total_items > 0 else 0)

    # Markdownを変換
    plan.description_html = markdown_to_html(plan.description)
    for item in items:
        item.description_html = markdown_to_html(item.description)

    return render_template("plans/view.html", plan=plan, items=items, progress=progress)


@plans_bp.route("/<int:plan_id>/update_item", methods=["POST"])
@login_required
def update_item(plan_id):
    plan = LearningPlan.query.get_or_404(plan_id)

    # 権限チェック
    if plan.user_id != current_user.id:
        return jsonify({"status": "error", "message": "権限がありません。"}), 403

    item_id = request.form.get("item_id")
    completed = request.form.get("completed") == "true"

    # 項目を更新
    item = LearningPlanItem.query.get_or_404(item_id)

    # 項目が指定されたプランに属することを確認
    if item.learning_plan_id != plan.id:
        return jsonify({"status": "error", "message": "項目が見つかりません。"}), 404

    item.completed = completed
    db.session.commit()

    # 進捗を計算
    total_items = LearningPlanItem.query.filter_by(learning_plan_id=plan.id).count()
    completed_items = LearningPlanItem.query.filter_by(
        learning_plan_id=plan.id, completed=True
    ).count()
    progress = int((completed_items / total_items * 100) if total_items > 0 else 0)

    return jsonify(
        {
            "status": "success",
            "item_id": item_id,
            "completed": completed,
            "progress": progress,
        }
    )


@plans_bp.route("/<int:plan_id>/delete", methods=["POST"])
@login_required
def delete(plan_id):
    plan = LearningPlan.query.get_or_404(plan_id)

    # 権限チェック
    if plan.user_id != current_user.id:
        flash("この学習プランを削除する権限がありません。", "danger")
        return redirect(url_for("plans.index"))

    try:
        # プランの項目を削除
        LearningPlanItem.query.filter_by(learning_plan_id=plan.id).delete()

        # プランを削除
        db.session.delete(plan)
        db.session.commit()

        flash("学習プランが削除されました。", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"学習プランの削除中にエラーが発生しました: {str(e)}", "danger")

    return redirect(url_for("plans.index"))
