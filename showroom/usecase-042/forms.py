from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    SubmitField,
    DateTimeField,
    FieldList,
    FormField,
)
from wtforms.validators import DataRequired, Optional
from disaster_data import DISASTER_TYPES, ALERT_LEVELS, TARGET_GROUPS, LANGUAGES


class EvacuationCenterForm(FlaskForm):
    name = StringField("避難所名", validators=[DataRequired()])
    address = StringField("住所", validators=[DataRequired()])


class EmergencyContactForm(FlaskForm):
    name = StringField("名称", validators=[DataRequired()])
    contact = StringField("連絡先", validators=[DataRequired()])


class DisasterInfoForm(FlaskForm):
    disaster_type = SelectField(
        "災害種別",
        choices=[(k, v) for k, v in DISASTER_TYPES.items()],
        validators=[DataRequired()],
    )
    alert_level = SelectField(
        "警戒レベル",
        choices=[(k, v) for k, v in ALERT_LEVELS.items()],
        validators=[DataRequired()],
    )
    title = StringField("タイトル", validators=[DataRequired()])
    description = TextAreaField("詳細説明", validators=[DataRequired()])
    affected_areas = TextAreaField(
        "影響地域（改行区切り）", validators=[DataRequired()]
    )
    evacuation_centers = TextAreaField(
        "避難所（名称:住所 形式、改行区切り）", validators=[Optional()]
    )
    start_time = DateTimeField(
        "発生/開始時刻", format="%Y-%m-%d %H:%M", validators=[DataRequired()]
    )
    estimated_end_time = DateTimeField(
        "推定終了時刻", format="%Y-%m-%d %H:%M", validators=[Optional()]
    )
    instructions = TextAreaField("指示事項", validators=[DataRequired()])
    emergency_contacts = TextAreaField(
        "緊急連絡先（名称:連絡先 形式、改行区切り）", validators=[DataRequired()]
    )
    submit = SubmitField("保存")


class MessageGenerationForm(FlaskForm):
    target_group = SelectField(
        "対象グループ",
        choices=[(k, v) for k, v in TARGET_GROUPS.items()],
        validators=[DataRequired()],
    )
    language = SelectField(
        "言語",
        choices=[(k, v) for k, v in LANGUAGES.items()],
        validators=[DataRequired()],
    )
    custom_instructions = TextAreaField(
        "追加指示（オプション）", validators=[Optional()]
    )
    submit = SubmitField("メッセージ生成")


class MultiSourceAnalysisForm(FlaskForm):
    source1 = TextAreaField("情報源1", validators=[DataRequired()])
    source2 = TextAreaField("情報源2", validators=[DataRequired()])
    source3 = TextAreaField("情報源3（オプション）", validators=[Optional()])
    source4 = TextAreaField("情報源4（オプション）", validators=[Optional()])
    submit = SubmitField("情報分析")


class SocialMediaForm(FlaskForm):
    platform = SelectField(
        "プラットフォーム",
        choices=[
            ("twitter", "Twitter/X"),
            ("facebook", "Facebook"),
            ("instagram", "Instagram"),
            ("line", "LINE"),
        ],
        validators=[DataRequired()],
    )
    character_limit = StringField(
        "文字数制限", default="280", validators=[DataRequired()]
    )
    submit = SubmitField("投稿作成")
