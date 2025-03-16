"""
ノート関連ルート: ノートの作成、表示、編集、削除機能
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import Subject, Note
from ..forms import AddNoteForm
from ..utils import markdown_to_html, generate_wordcloud, extract_key_terms

# Blueprintの作成
notes_bp = Blueprint("notes", __name__, url_prefix="/notes")


@notes_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = AddNoteForm()

    # 科目のリストを設定
    subjects = Subject.query.all()
    form.subject.choices = [(s.code, s.name) for s in subjects]

    if form.validate_on_submit():
        title = form.title.data
        subject_code = form.subject.data
        topic = form.topic.data
        content = form.content.data

        # 科目情報を取得
        subject = Subject.query.filter_by(code=subject_code).first()
        if not subject:
            flash("無効な科目です。", "danger")
            return redirect(url_for("notes.index"))

        # ノートを作成
        note = Note(
            title=title,
            content=content,
            subject_id=subject.id,
            topic=topic,
            user_id=current_user.id,
        )

        db.session.add(note)
        db.session.commit()

        flash("ノートが作成されました。", "success")
        return redirect(url_for("notes.view", note_id=note.id))

    # 既存のノートを取得
    notes = (
        Note.query.filter_by(user_id=current_user.id)
        .order_by(Note.updated_at.desc())
        .all()
    )

    # 科目ごとにノートを整理
    notes_by_subject = {}
    for note in notes:
        if note.subject.name not in notes_by_subject:
            notes_by_subject[note.subject.name] = []
        notes_by_subject[note.subject.name].append(note)

    return render_template(
        "notes/index.html", form=form, notes_by_subject=notes_by_subject
    )


@notes_bp.route("/<int:note_id>")
@login_required
def view(note_id):
    note = Note.query.get_or_404(note_id)

    # 権限チェック
    if note.user_id != current_user.id:
        flash("このノートにアクセスする権限がありません。", "danger")
        return redirect(url_for("notes.index"))

    # Markdownを変換
    note_html = markdown_to_html(note.content)

    # ワードクラウドを生成
    wordcloud_img = generate_wordcloud(note.content)

    # キーワードを抽出
    key_terms = extract_key_terms([note.content], 10)

    return render_template(
        "notes/view.html",
        note=note,
        note_html=note_html,
        wordcloud_img=wordcloud_img,
        key_terms=key_terms,
    )


@notes_bp.route("/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit(note_id):
    note = Note.query.get_or_404(note_id)

    # 権限チェック
    if note.user_id != current_user.id:
        flash("このノートを編集する権限がありません。", "danger")
        return redirect(url_for("notes.index"))

    form = AddNoteForm()

    # 科目のリストを設定
    subjects = Subject.query.all()
    form.subject.choices = [(s.code, s.name) for s in subjects]

    if request.method == "GET":
        # フォームに現在の値をセット
        form.title.data = note.title
        form.subject.data = note.subject.code
        form.topic.data = note.topic
        form.content.data = note.content

    if form.validate_on_submit():
        # ノートを更新
        note.title = form.title.data
        note.topic = form.topic.data
        note.content = form.content.data

        # 科目を更新
        subject_code = form.subject.data
        subject = Subject.query.filter_by(code=subject_code).first()
        if not subject:
            flash("無効な科目です。", "danger")
            return redirect(url_for("notes.edit", note_id=note.id))

        note.subject_id = subject.id
        note.updated_at = datetime.utcnow()

        db.session.commit()

        flash("ノートが更新されました。", "success")
        return redirect(url_for("notes.view", note_id=note.id))

    return render_template("notes/edit.html", form=form, note=note)


@notes_bp.route("/<int:note_id>/delete", methods=["POST"])
@login_required
def delete(note_id):
    note = Note.query.get_or_404(note_id)

    # 権限チェック
    if note.user_id != current_user.id:
        flash("このノートを削除する権限がありません。", "danger")
        return redirect(url_for("notes.index"))

    db.session.delete(note)
    db.session.commit()

    flash("ノートが削除されました。", "success")
    return redirect(url_for("notes.index"))


@notes_bp.route("/search")
@login_required
def search():
    query = request.args.get("query", "")

    if not query:
        return redirect(url_for("notes.index"))

    # ノートを検索
    search_term = f"%{query}%"
    notes = (
        Note.query.filter(
            Note.user_id == current_user.id,
            (
                Note.title.like(search_term)
                | Note.content.like(search_term)
                | Note.topic.like(search_term)
            ),
        )
        .order_by(Note.updated_at.desc())
        .all()
    )

    return render_template("notes/search.html", notes=notes, query=query)


@notes_bp.route("/by_topic/<subject_code>/<topic>")
@login_required
def by_topic(subject_code, topic):
    # 科目を取得
    subject = Subject.query.filter_by(code=subject_code).first_or_404()

    # トピックに関連するノートを取得
    notes = (
        Note.query.filter_by(
            user_id=current_user.id, subject_id=subject.id, topic=topic
        )
        .order_by(Note.updated_at.desc())
        .all()
    )

    return render_template(
        "notes/by_topic.html", notes=notes, subject=subject, topic=topic
    )
