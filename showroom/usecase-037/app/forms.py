"""
フォーム定義: Flask-WTFormsを使用したフォームの定義
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    TextAreaField,
    IntegerField,
    BooleanField,
    DateField,
    TimeField,
    DateTimeField,
    HiddenField,
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from .config import SUBJECTS, LEVELS


class LoginForm(FlaskForm):
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    submit = SubmitField("ログイン")


class RegisterForm(FlaskForm):
    username = StringField(
        "ユーザー名", validators=[DataRequired(), Length(min=3, max=20)]
    )
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    password = PasswordField("パスワード", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "パスワード（確認）", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("登録")


class CreatePlanForm(FlaskForm):
    title = StringField("タイトル", validators=[DataRequired()])
    subject = SelectField("科目", validators=[DataRequired()], choices=SUBJECTS)
    level = SelectField("レベル", validators=[DataRequired()], choices=LEVELS)
    description = TextAreaField("説明")
    submit = SubmitField("作成")


class AddNoteForm(FlaskForm):
    title = StringField("タイトル", validators=[DataRequired()])
    subject = SelectField("科目", validators=[DataRequired()], choices=SUBJECTS)
    topic = StringField("トピック", validators=[DataRequired()])
    content = TextAreaField("内容", validators=[DataRequired()])
    submit = SubmitField("保存")


class CreateQuizForm(FlaskForm):
    title = StringField("タイトル", validators=[DataRequired()])
    subject = SelectField("科目", validators=[DataRequired()], choices=SUBJECTS)
    topic = StringField("トピック", validators=[DataRequired()])
    level = SelectField("レベル", validators=[DataRequired()], choices=LEVELS)
    num_questions = IntegerField("問題数", validators=[DataRequired()])
    submit = SubmitField("クイズを作成")


class FlashcardForm(FlaskForm):
    subject = SelectField("科目", validators=[DataRequired()], choices=SUBJECTS)
    topic = StringField("トピック", validators=[DataRequired()])
    level = SelectField("レベル", validators=[DataRequired()], choices=LEVELS)
    num_cards = IntegerField("カード数", validators=[DataRequired()])
    submit = SubmitField("フラッシュカードを作成")


class StudySessionForm(FlaskForm):
    subject = SelectField("科目", validators=[DataRequired()], choices=SUBJECTS)
    topic = StringField("トピック", validators=[DataRequired()])
    duration = IntegerField("時間（分）", validators=[DataRequired()])
    notes = TextAreaField("メモ")
    submit = SubmitField("セッションを記録")


class ConversationForm(FlaskForm):
    title = StringField("タイトル", validators=[DataRequired()])
    subject = SelectField("科目", validators=[DataRequired()], choices=SUBJECTS)
    topic = StringField("トピック")
    submit = SubmitField("会話を開始")


class MessageForm(FlaskForm):
    content = TextAreaField("メッセージ", validators=[DataRequired()])
    submit = SubmitField("送信")


class ResetDataForm(FlaskForm):
    data_type = SelectField(
        "削除するデータ",
        choices=[
            ("all", "すべてのデータ"),
            ("quizzes", "クイズ"),
            ("flashcards", "フラッシュカード"),
            ("notes", "ノート"),
            ("sessions", "学習セッション"),
            ("plans", "学習プラン"),
            ("conversations", "AI会話"),
        ],
    )
    confirm = BooleanField("削除を確認します", validators=[DataRequired()])
    submit = SubmitField("データをリセット")
