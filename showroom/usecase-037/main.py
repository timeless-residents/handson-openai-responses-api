"""
個人向け学習アシスタント: OpenAI APIを活用して個人学習を支援するWebアプリケーション

このアプリケーションは、以下の機能を提供します：
- 学習者のレベルに応じたコンテンツ生成
- インタラクティブな質問応答
- パーソナライズされた学習計画の作成
- 学習の進捗状況の追跡
- 知識の確認のためのクイズ生成
"""
import os
import json
import time
import uuid
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
import io
import base64
import re
import sqlite3
from functools import wraps
from typing import List, Dict, Any, Tuple, Optional, Union

import nltk
from nltk.tokenize import sent_tokenize
import numpy as np
import matplotlib
matplotlib.use('Agg')  # ヘッドレス環境用設定
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from PIL import Image
import markdown
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash

# 環境変数の読み込み
load_dotenv()

# NLTKのデータをダウンロード
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# アプリケーションの初期化
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key_change_in_production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# データベースの初期化
db = SQLAlchemy(app)

# ログインマネージャーの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OpenAI クライアントの初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# サポートする科目とレベル
SUBJECTS = [
    ('python', 'Python プログラミング'),
    ('javascript', 'JavaScript プログラミング'),
    ('math', '数学'),
    ('physics', '物理学'),
    ('chemistry', '化学'),
    ('biology', '生物学'),
    ('english', '英語'),
    ('history', '歴史'),
    ('economics', '経済学')
]

LEVELS = [
    ('beginner', '初級者'),
    ('intermediate', '中級者'),
    ('advanced', '上級者')
]

# データベースモデル
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # リレーションシップ
    study_sessions = db.relationship('StudySession', backref='user', lazy=True)
    learning_plans = db.relationship('LearningPlan', backref='user', lazy=True)
    notes = db.relationship('Note', backref='user', lazy=True)
    flashcards = db.relationship('Flashcard', backref='user', lazy=True)
    quizzes = db.relationship('Quiz', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # リレーションシップ
    topics = db.relationship('Topic', backref='subject', lazy=True)
    
    def __repr__(self):
        return f'<Subject {self.name}>'

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    level = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    order = db.Column(db.Integer, nullable=False, default=0)
    
    # リレーションシップ
    contents = db.relationship('Content', backref='topic', lazy=True)
    
    def __repr__(self):
        return f'<Topic {self.name} ({self.level})>'

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content_type = db.Column(db.String(20), nullable=False)  # explanation, example, exercise
    text = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(20), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Content {self.title} ({self.content_type})>'

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    
    # リレーションシップ
    subject = db.relationship('Subject', backref='study_sessions')
    topic = db.relationship('Topic', backref='study_sessions')
    
    def __repr__(self):
        return f'<StudySession {self.id} ({self.subject.name})>'

class LearningPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    level = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # リレーションシップ
    subject = db.relationship('Subject', backref='learning_plans')
    plan_items = db.relationship('LearningPlanItem', backref='learning_plan', lazy=True)
    
    def __repr__(self):
        return f'<LearningPlan {self.title}>'

class LearningPlanItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    learning_plan_id = db.Column(db.Integer, db.ForeignKey('learning_plan.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    day_number = db.Column(db.Integer, nullable=False)
    estimated_duration = db.Column(db.Integer, nullable=True)  # 分単位
    completed = db.Column(db.Boolean, default=False)
    
    # リレーションシップ
    topic = db.relationship('Topic', backref='plan_items')
    
    def __repr__(self):
        return f'<LearningPlanItem {self.title} (Day {self.day_number})>'

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    subject = db.relationship('Subject', backref='notes')
    topic = db.relationship('Topic', backref='notes')
    
    def __repr__(self):
        return f'<Note {self.title}>'

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    level = db.Column(db.Integer, default=0)  # 難易度/重要度 (0-5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime, nullable=True)
    next_review = db.Column(db.DateTime, nullable=True)
    
    # リレーションシップ
    subject = db.relationship('Subject', backref='flashcards')
    topic = db.relationship('Topic', backref='flashcards')
    
    def __repr__(self):
        return f'<Flashcard {self.id} ({self.front[:20]}...)>'

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)
    
    # リレーションシップ
    subject = db.relationship('Subject', backref='quizzes')
    topic = db.relationship('Topic', backref='quizzes')
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True)
    
    def __repr__(self):
        return f'<Quiz {self.title}>'

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer_type = db.Column(db.String(20), nullable=False)  # multiple_choice, text, true_false
    correct_answer = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=True)  # JSON形式で選択肢を格納
    explanation = db.Column(db.Text, nullable=True)
    user_answer = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, nullable=True)
    
    def __repr__(self):
        return f'<QuizQuestion {self.id}>'

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    title = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ
    messages = db.relationship('Message', backref='conversation', lazy=True)
    subject = db.relationship('Subject', backref='conversations')
    topic = db.relationship('Topic', backref='conversations')
    
    def __repr__(self):
        return f'<Conversation {self.id}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.id} ({self.role})>'

# フォーム
class LoginForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

class RegistrationForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('パスワード（確認）', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('アカウント作成')

class SubjectSelectionForm(FlaskForm):
    subject = SelectField('科目', choices=SUBJECTS, validators=[DataRequired()])
    level = SelectField('レベル', choices=LEVELS, validators=[DataRequired()])
    submit = SubmitField('開始')

class LearningPlanForm(FlaskForm):
    title = StringField('プラン名', validators=[DataRequired(), Length(max=100)])
    subject = SelectField('科目', choices=SUBJECTS, validators=[DataRequired()])
    level = SelectField('レベル', choices=LEVELS, validators=[DataRequired()])
    goal = TextAreaField('学習目標', validators=[DataRequired()])
    duration = SelectField('学習期間', choices=[
        ('7', '1週間'),
        ('14', '2週間'),
        ('30', '1ヶ月'),
        ('90', '3ヶ月')
    ], validators=[DataRequired()])
    time_per_day = SelectField('1日の学習時間', choices=[
        ('30', '30分'),
        ('60', '1時間'),
        ('90', '1時間30分'),
        ('120', '2時間')
    ], validators=[DataRequired()])
    prior_knowledge = TextAreaField('事前知識（任意）')
    submit = SubmitField('プラン作成')

class NoteForm(FlaskForm):
    title = StringField('タイトル', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('内容', validators=[DataRequired()])
    submit = SubmitField('保存')

class QuizGenerationForm(FlaskForm):
    subject = SelectField('科目', choices=SUBJECTS, validators=[DataRequired()])
    topic = StringField('トピック', validators=[DataRequired()])
    level = SelectField('難易度', choices=LEVELS, validators=[DataRequired()])
    question_count = SelectField('問題数', choices=[
        ('5', '5問'),
        ('10', '10問'),
        ('15', '15問')
    ], validators=[DataRequired()])
    submit = SubmitField('クイズ生成')

# OpenAI APIを使った関数
def generate_response(messages, model="gpt-4-turbo", temperature=0.7, max_tokens=1500):
    """OpenAI APIを使用してレスポンスを生成する"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API エラー: {str(e)}")
        return f"エラーが発生しました: {str(e)}"

def generate_learning_content(subject, topic, level, content_type="explanation"):
    """学習コンテンツを生成する"""
    messages = [
        {"role": "system", "content": f"あなたは{subject}の教師です。{level}レベルの学習者向けに、わかりやすくかつ正確な情報を提供してください。"},
        {"role": "user", "content": f"{topic}について{content_type}を提供してください。"}
    ]
    return generate_response(messages)

def generate_quiz(subject, topic, level, num_questions=5):
    """クイズを生成する"""
    messages = [
        {"role": "system", "content": f"あなたは{subject}の教師です。{level}レベルの学習者向けにクイズを作成してください。各問題には正解と解説を含めてください。"},
        {"role": "user", "content": f"{topic}に関する{num_questions}問のクイズを作成してください。問題、選択肢（4つ）、正解、解説を含めてJSON形式で返してください。"}
    ]
    response = generate_response(messages)
    
    # JSONを抽出して解析
    try:
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response
        
        # 余分な文字を削除
        json_str = re.sub(r'[^\x00-\x7F]+', ' ', json_str)
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"JSON解析エラー: {str(e)}")
        logger.error(f"レスポンス: {response}")
        return []

def generate_flashcards(subject, topic, level, num_cards=10):
    """フラッシュカードを生成する"""
    messages = [
        {"role": "system", "content": f"あなたは{subject}の教師です。{level}レベルの学習者向けにフラッシュカードを作成してください。"},
        {"role": "user", "content": f"{topic}に関する{num_cards}枚のフラッシュカードを作成してください。表面に概念や用語、裏面に説明や定義を含めてJSON形式で返してください。"}
    ]
    response = generate_response(messages)
    
    # JSONを抽出して解析
    try:
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response
        
        # 余分な文字を削除
        json_str = re.sub(r'[^\x00-\x7F]+', ' ', json_str)
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"JSON解析エラー: {str(e)}")
        return []

def generate_learning_plan(subject, level, goal, duration_days, time_per_day, prior_knowledge=""):
    """学習プランを生成する"""
    messages = [
        {"role": "system", "content": f"あなたは{subject}の教育専門家です。学習者の目標とレベルに合わせた最適な学習プランを作成してください。"},
        {"role": "user", "content": f"""
        以下の条件で学習プランを作成してください：
        
        科目: {subject}
        レベル: {level}
        目標: {goal}
        期間: {duration_days}日間
        1日あたりの学習時間: {time_per_day}分
        事前知識: {prior_knowledge}
        
        各日の学習内容、推定時間、トピックのリストをJSON形式で返してください。
        """}
    ]
    response = generate_response(messages, max_tokens=2000)
    
    # JSONを抽出して解析
    try:
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response
        
        # 余分な文字を削除
        json_str = re.sub(r'[^\x00-\x7F]+', ' ', json_str)
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"JSON解析エラー: {str(e)}")
        return {"error": "プランの生成に失敗しました。もう一度お試しください。"}

def summarize_text(text, max_length=500):
    """テキストを要約する"""
    messages = [
        {"role": "system", "content": "あなたは、テキスト要約の専門家です。与えられたテキストを簡潔かつ正確に要約してください。"},
        {"role": "user", "content": f"以下のテキストを{max_length}文字以内で要約してください：\n\n{text}"}
    ]
    return generate_response(messages)

def generate_concept_explanation(subject, concept, level):
    """概念の説明を生成する"""
    messages = [
        {"role": "system", "content": f"あなたは{subject}の教師です。{level}レベルの学習者向けに、概念を明確かつわかりやすく説明してください。例や類推を使用して理解を深めてください。"},
        {"role": "user", "content": f"{concept}について説明してください。"}
    ]
    return generate_response(messages)

def answer_question(subject, question, level, context=""):
    """質問に回答する"""
    messages = [
        {"role": "system", "content": f"あなたは{subject}の教師です。{level}レベルの学習者からの質問に対して、わかりやすく正確に回答してください。"},
        {"role": "user", "content": f"質問: {question}\n\n背景情報: {context}"}
    ]
    return generate_response(messages)

# データ可視化関数
def generate_word_cloud(text):
    """テキストからワードクラウドを生成する"""
    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=100).generate(text)
    
    # 画像をBase64エンコード
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    
    return f"data:image/png;base64,{img_b64}"

def generate_study_time_chart(user_id):
    """学習時間の推移チャートを生成する"""
    # 過去30日間の学習セッションを取得
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    sessions = StudySession.query.filter(
        StudySession.user_id == user_id,
        StudySession.start_time >= thirty_days_ago,
        StudySession.duration_minutes.isnot(None)
    ).all()
    
    # 日付ごとに学習時間を集計
    daily_times = {}
    for session in sessions:
        date_str = session.start_time.strftime('%Y-%m-%d')
        if date_str in daily_times:
            daily_times[date_str] += session.duration_minutes
        else:
            daily_times[date_str] = session.duration_minutes
    
    # データフレームに変換
    if not daily_times:
        return None
    
    df = pd.DataFrame(list(daily_times.items()), columns=['date', 'minutes'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # チャートを作成
    plt.figure(figsize=(10, 5))
    plt.bar(df['date'], df['minutes'], color='skyblue')
    plt.xlabel('日付')
    plt.ylabel('学習時間（分）')
    plt.title('日別学習時間')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 画像をBase64エンコード
    img = io.BytesIO()
    plt.savefig(img, format='PNG')
    plt.close()
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    
    return f"data:image/png;base64,{img_b64}"

def generate_subject_distribution_chart(user_id):
    """科目別の学習時間分布を円グラフで表示"""
    sessions = StudySession.query.filter(
        StudySession.user_id == user_id,
        StudySession.duration_minutes.isnot(None)
    ).all()
    
    # 科目ごとに学習時間を集計
    subject_times = {}
    for session in sessions:
        subject_name = session.subject.name
        if subject_name in subject_times:
            subject_times[subject_name] += session.duration_minutes
        else:
            subject_times[subject_name] = session.duration_minutes
    
    if not subject_times:
        return None
    
    # チャートを作成
    plt.figure(figsize=(8, 8))
    plt.pie(
        subject_times.values(),
        labels=subject_times.keys(),
        autopct='%1.1f%%',
        startangle=90,
        shadow=True
    )
    plt.axis('equal')
    plt.title('科目別学習時間分布')
    
    # 画像をBase64エンコード
    img = io.BytesIO()
    plt.savefig(img, format='PNG')
    plt.close()
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    
    return f"data:image/png;base64,{img_b64}"

# ユーティリティ関数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    """データベースを初期化し、初期データを登録する"""
    with app.app_context():
        db.create_all()
        
        # サポートする科目を登録
        for code, name in SUBJECTS:
            if not Subject.query.filter_by(code=code).first():
                subject = Subject(code=code, name=name)
                db.session.add(subject)
        
        db.session.commit()

# ルート
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('そのユーザー名は既に使用されています。別のユーザー名を選択してください。', 'danger')
            return redirect(url_for('register'))
        
        email_user = User.query.filter_by(email=form.email.data).first()
        if email_user:
            flash('そのメールアドレスは既に登録されています。', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('アカウントが作成されました。ログインしてください。', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('ログインに失敗しました。ユーザー名とパスワードを確認してください。', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # 進行中の学習プラン
    active_plans = LearningPlan.query.filter_by(user_id=current_user.id).order_by(LearningPlan.created_at.desc()).limit(3).all()
    
    # 最近の学習セッション
    recent_sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.start_time.desc()).limit(5).all()
    
    # 最近のノート
    recent_notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.updated_at.desc()).limit(5).all()
    
    # 学習時間チャート
    time_chart = generate_study_time_chart(current_user.id)
    
    # 科目分布チャート
    subject_chart = generate_subject_distribution_chart(current_user.id)
    
    return render_template(
        'dashboard.html',
        active_plans=active_plans,
        recent_sessions=recent_sessions,
        recent_notes=recent_notes,
        time_chart=time_chart,
        subject_chart=subject_chart
    )

@app.route('/subject', methods=['GET', 'POST'])
@login_required
def select_subject():
    form = SubjectSelectionForm()
    if form.validate_on_submit():
        subject_code = form.subject.data
        level = form.level.data
        
        # セッション情報を保存
        session['subject'] = subject_code
        session['level'] = level
        
        # 実際の科目オブジェクトを取得
        subject = Subject.query.filter_by(code=subject_code).first()
        
        # 新しい学習セッションを開始
        study_session = StudySession(
            user_id=current_user.id,
            subject_id=subject.id,
            start_time=datetime.now(datetime.UTC)
        )
        db.session.add(study_session)
        db.session.commit()
        
        # セッションIDを保存
        session['study_session_id'] = study_session.id
        
        return redirect(url_for('learn'))
    
    return render_template('select_subject.html', form=form)

@app.route('/learn')
@login_required
def learn():
    if 'subject' not in session or 'level' not in session:
        return redirect(url_for('select_subject'))
    
    subject_code = session['subject']
    level = session['level']
    
    # 科目情報を取得
    subject = Subject.query.filter_by(code=subject_code).first()
    
    # トピックリストを取得
    topics = Topic.query.filter_by(subject_id=subject.id, level=level).all()
    
    # トピックが存在しない場合はAPIから生成
    if not topics:
        topic_info = generate_initial_topics(subject.name, level)
        topics = []
        for i, topic_data in enumerate(topic_info):
            topic = Topic(
                subject_id=subject.id,
                name=topic_data['name'],
                description=topic_data.get('description', ''),
                level=level,
                order=i
            )
            db.session.add(topic)
            topics.append(topic)
        db.session.commit()
    
    return render_template(
        'learn.html',
        subject=subject,
        level=level,
        topics=topics
    )

@app.route('/learn/<int:topic_id>')
@login_required
def learn_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    
    # 現在の学習セッションを更新
    if 'study_session_id' in session:
        study_session = StudySession.query.get(session['study_session_id'])
        if study_session and study_session.user_id == current_user.id:
            study_session.topic_id = topic_id
            db.session.commit()
    
    # コンテンツを取得
    contents = Content.query.filter_by(topic_id=topic_id).order_by(Content.order).all()
    
    # コンテンツが存在しない場合はAPIから生成
    if not contents:
        contents = []
        
        # 説明を生成
        explanation = generate_learning_content(
            topic.subject.name,
            topic.name,
            topic.level,
            content_type="explanation"
        )
        explanation_content = Content(
            topic_id=topic_id,
            title=f"{topic.name}の概要",
            content_type="explanation",
            text=explanation,
            level=topic.level,
            order=0
        )
        db.session.add(explanation_content)
        contents.append(explanation_content)
        
        # 例を生成
        example = generate_learning_content(
            topic.subject.name,
            topic.name,
            topic.level,
            content_type="example"
        )
        example_content = Content(
            topic_id=topic_id,
            title=f"{topic.name}の例",
            content_type="example",
            text=example,
            level=topic.level,
            order=1
        )
        db.session.add(example_content)
        contents.append(example_content)
        
        # 練習問題を生成
        exercise = generate_learning_content(
            topic.subject.name,
            topic.name,
            topic.level,
            content_type="exercise"
        )
        exercise_content = Content(
            topic_id=topic_id,
            title=f"{topic.name}の練習問題",
            content_type="exercise",
            text=exercise,
            level=topic.level,
            order=2
        )
        db.session.add(exercise_content)
        contents.append(exercise_content)
        
        db.session.commit()
    
    return render_template(
        'topic.html',
        topic=topic,
        contents=contents
    )

@app.route('/ask', methods=['GET', 'POST'])
@login_required
def ask_question():
    # 現在の科目
    subject_code = session.get('subject')
    level = session.get('level')
    
    subject = None
    if subject_code:
        subject = Subject.query.filter_by(code=subject_code).first()
    
    # 全ての会話を取得
    conversations = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.updated_at.desc()).all()
    
    # 選択された会話
    conversation_id = request.args.get('conversation_id')
    current_conversation = None
    
    if conversation_id:
        current_conversation = Conversation.query.get(conversation_id)
        if current_conversation and current_conversation.user_id != current_user.id:
            current_conversation = None
    
    if request.method == 'POST':
        question = request.form.get('question')
        conversation_id = request.form.get('conversation_id')
        
        if not conversation_id or conversation_id == 'new':
            # 新しい会話を作成
            title = f"Q: {question[:30]}..." if len(question) > 30 else f"Q: {question}"
            new_conversation = Conversation(
                user_id=current_user.id,
                subject_id=subject.id if subject else None,
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_conversation)
            db.session.commit()
            conversation_id = new_conversation.id
            current_conversation = new_conversation
        else:
            current_conversation = Conversation.query.get(conversation_id)
            if current_conversation and current_conversation.user_id != current_user.id:
                return jsonify({"error": "無効な会話IDです"})
            
            # 会話の最終更新日時を更新
            current_conversation.updated_at = datetime.utcnow()
            db.session.commit()
        
        # ユーザーメッセージを保存
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=question,
            created_at=datetime.utcnow()
        )
        db.session.add(user_message)
        db.session.commit()
        
        # 回答を生成
        subject_name = subject.name if subject else "一般"
        level_text = level or "intermediate"
        
        # 会話の履歴を取得
        messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
        message_list = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        # システムメッセージを先頭に追加
        message_list.insert(0, {
            "role": "system",
            "content": f"あなたは{subject_name}の教師です。{level_text}レベルの学習者からの質問に対して、わかりやすく正確に回答してください。複雑な概念は簡単な言葉で説明し、必要に応じて例を提供してください。"
        })
        
        # OpenAI APIで回答を生成
        response = generate_response(message_list)
        
        # 応答を保存
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response,
            created_at=datetime.utcnow()
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        # AJAX用のレスポンス
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "id": conversation_id,
                "response": response,
                "conversation_title": current_conversation.title
            })
        
        return redirect(url_for('ask_question', conversation_id=conversation_id))
    
    return render_template(
        'ask.html',
        subject=subject,
        level=level,
        conversations=conversations,
        current_conversation=current_conversation,
        messages=Message.query.filter_by(conversation_id=current_conversation.id).order_by(Message.created_at).all() if current_conversation else []
    )

@app.route('/plan', methods=['GET', 'POST'])
@login_required
def create_learning_plan():
    form = LearningPlanForm()
    
    # 科目選択オプションを動的に設定
    form.subject.choices = [(s.code, s.name) for s in Subject.query.all()]
    
    if form.validate_on_submit():
        subject_code = form.subject.data
        level = form.level.data
        title = form.title.data
        goal = form.goal.data
        duration_days = int(form.duration.data)
        time_per_day = int(form.time_per_day.data)
        prior_knowledge = form.prior_knowledge.data or ""
        
        # 科目情報を取得
        subject = Subject.query.filter_by(code=subject_code).first()
        
        # 学習プランを生成
        plan_data = generate_learning_plan(
            subject.name,
            level,
            goal,
            duration_days,
            time_per_day,
            prior_knowledge
        )
        
        if "error" in plan_data:
            flash(plan_data["error"], "danger")
            return redirect(url_for('create_learning_plan'))
        
        # 学習プランを保存
        start_date = datetime.utcnow().date()
        end_date = start_date + timedelta(days=duration_days)
        
        new_plan = LearningPlan(
            user_id=current_user.id,
            subject_id=subject.id,
            title=title,
            description=goal,
            start_date=start_date,
            end_date=end_date,
            level=level,
            created_at=datetime.utcnow()
        )
        db.session.add(new_plan)
        db.session.commit()
        
        # 学習プランのアイテムを保存
        for day_data in plan_data.get("days", []):
            day_number = day_data.get("day", 0)
            day_title = day_data.get("title", f"Day {day_number}")
            day_description = day_data.get("description", "")
            day_duration = day_data.get("duration", time_per_day)
            
            plan_item = LearningPlanItem(
                learning_plan_id=new_plan.id,
                title=day_title,
                description=day_description,
                day_number=day_number,
                estimated_duration=day_duration,
                completed=False
            )
            db.session.add(plan_item)
        
        db.session.commit()
        
        flash("学習プランが作成されました！", "success")
        return redirect(url_for('view_learning_plan', plan_id=new_plan.id))
    
    return render_template('create_plan.html', form=form)

@app.route('/plan/<int:plan_id>')
@login_required
def view_learning_plan(plan_id):
    plan = LearningPlan.query.get_or_404(plan_id)
    
    # 権限チェック
    if plan.user_id != current_user.id:
        flash("このプランにアクセスする権限がありません。", "danger")
        return redirect(url_for('dashboard'))
    
    # プランアイテムを取得
    plan_items = LearningPlanItem.query.filter_by(learning_plan_id=plan.id).order_by(LearningPlanItem.day_number).all()
    
    # 進捗状況を計算
    total_items = len(plan_items)
    completed_items = sum(1 for item in plan_items if item.completed)
    progress = int((completed_items / total_items) * 100) if total_items > 0 else 0
    
    return render_template(
        'view_plan.html',
        plan=plan,
        plan_items=plan_items,
        progress=progress
    )

@app.route('/plan/<int:plan_id>/complete/<int:item_id>', methods=['POST'])
@login_required
def complete_plan_item(plan_id, item_id):
    plan = LearningPlan.query.get_or_404(plan_id)
    
    # 権限チェック
    if plan.user_id != current_user.id:
        return jsonify({"error": "権限がありません"}), 403
    
    item = LearningPlanItem.query.get_or_404(item_id)
    
    # 項目が該当するプランのものか確認
    if item.learning_plan_id != plan.id:
        return jsonify({"error": "無効な項目です"}), 400
    
    # 完了状態を切り替え
    item.completed = not item.completed
    db.session.commit()
    
    return jsonify({"success": True, "completed": item.completed})

@app.route('/notes')
@login_required
def notes():
    # ユーザーのノートを全て取得
    user_notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.updated_at.desc()).all()
    
    return render_template('notes.html', notes=user_notes)

@app.route('/notes/new', methods=['GET', 'POST'])
@login_required
def new_note():
    form = NoteForm()
    
    if form.validate_on_submit():
        # 科目情報
        subject_id = None
        if 'subject' in session:
            subject_code = session['subject']
            subject = Subject.query.filter_by(code=subject_code).first()
            if subject:
                subject_id = subject.id
        
        new_note = Note(
            user_id=current_user.id,
            subject_id=subject_id or Subject.query.first().id,  # デフォルト値
            title=form.title.data,
            content=form.content.data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_note)
        db.session.commit()
        
        flash("ノートが作成されました！", "success")
        return redirect(url_for('view_note', note_id=new_note.id))
    
    return render_template('edit_note.html', form=form, is_new=True)

@app.route('/notes/<int:note_id>')
@login_required
def view_note(note_id):
    note = Note.query.get_or_404(note_id)
    
    # 権限チェック
    if note.user_id != current_user.id:
        flash("このノートにアクセスする権限がありません。", "danger")
        return redirect(url_for('notes'))
    
    # Markdownをレンダリング
    content_html = markdown.markdown(note.content)
    
    # 単語頻度を解析してワードクラウドを生成
    wordcloud_img = generate_word_cloud(note.content)
    
    return render_template(
        'view_note.html',
        note=note,
        content_html=content_html,
        wordcloud=wordcloud_img
    )

@app.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    
    # 権限チェック
    if note.user_id != current_user.id:
        flash("このノートを編集する権限がありません。", "danger")
        return redirect(url_for('notes'))
    
    form = NoteForm(obj=note)
    
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        note.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash("ノートが更新されました！", "success")
        return redirect(url_for('view_note', note_id=note.id))
    
    return render_template('edit_note.html', form=form, is_new=False, note=note)

@app.route('/notes/<int:note_id>/summarize', methods=['POST'])
@login_required
def summarize_note(note_id):
    note = Note.query.get_or_404(note_id)
    
    # 権限チェック
    if note.user_id != current_user.id:
        return jsonify({"error": "権限がありません"}), 403
    
    # ノートを要約
    summary = summarize_text(note.content)
    
    return jsonify({"summary": summary})

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    form = QuizGenerationForm()
    
    # 科目選択オプションを動的に設定
    form.subject.choices = [(s.code, s.name) for s in Subject.query.all()]
    
    if form.validate_on_submit():
        subject_code = form.subject.data
        topic = form.topic.data
        level = form.level.data
        question_count = int(form.question_count.data)
        
        # 科目情報を取得
        subject = Subject.query.filter_by(code=subject_code).first()
        
        # クイズを生成
        quiz_data = generate_quiz(
            subject.name,
            topic,
            level,
            question_count
        )
        
        if not quiz_data:
            flash("クイズの生成に失敗しました。もう一度お試しください。", "danger")
            return redirect(url_for('create_quiz'))
        
        # クイズを保存
        new_quiz = Quiz(
            user_id=current_user.id,
            subject_id=subject.id,
            title=f"{subject.name} - {topic}",
            description=f"{level}レベルの{topic}に関するクイズ",
            created_at=datetime.utcnow()
        )
        db.session.add(new_quiz)
        db.session.flush()
        
        # クイズの問題を保存
        for question_data in quiz_data.get("questions", []):
            question_text = question_data.get("question", "")
            answer_type = "multiple_choice"
            correct_answer = question_data.get("correct_answer", "")
            options = json.dumps(question_data.get("options", []))
            explanation = question_data.get("explanation", "")
            
            quiz_question = QuizQuestion(
                quiz_id=new_quiz.id,
                question=question_text,
                answer_type=answer_type,
                correct_answer=correct_answer,
                options=options,
                explanation=explanation
            )
            db.session.add(quiz_question)
        
        db.session.commit()
        
        flash("クイズが作成されました！", "success")
        return redirect(url_for('take_quiz', quiz_id=new_quiz.id))
    
    return render_template('create_quiz.html', form=form)

@app.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # 権限チェック
    if quiz.user_id != current_user.id:
        flash("このクイズにアクセスする権限がありません。", "danger")
        return redirect(url_for('dashboard'))
    
    # クイズの問題を取得
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
    
    return render_template(
        'take_quiz.html',
        quiz=quiz,
        questions=questions,
        completed=(quiz.completed_at is not None)
    )

@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # 権限チェック
    if quiz.user_id != current_user.id:
        return jsonify({"error": "権限がありません"}), 403
    
    # クイズの問題を取得
    questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
    
    # 回答をチェック
    correct_count = 0
    total_questions = len(questions)
    
    for question in questions:
        answer_key = f"answer_{question.id}"
        user_answer = request.form.get(answer_key, "")
        
        question.user_answer = user_answer
        question.is_correct = (user_answer == question.correct_answer)
        
        if question.is_correct:
            correct_count += 1
    
    # スコアを計算
    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    
    # クイズを完了としてマーク
    quiz.completed_at = datetime.utcnow()
    quiz.score = score
    
    db.session.commit()
    
    return redirect(url_for('quiz_result', quiz_id=quiz.id))

@app.route('/quiz/<int:quiz_id>/result')
@login_required
def quiz_result(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # 権限チェック
    if quiz.user_id != current_user.id:
        flash("このクイズにアクセスする権限がありません。", "danger")
        return redirect(url_for('dashboard'))
    
    # クイズが完了していることを確認
    if not quiz.completed_at:
        flash("このクイズはまだ完了していません。", "warning")
        return redirect(url_for('take_quiz', quiz_id=quiz.id))
    
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
    
    return render_template(
        'quiz_result.html',
        quiz=quiz,
        questions=questions
    )

@app.route('/flashcards', methods=['GET', 'POST'])
@login_required
def flashcards():
    if request.method == 'POST':
        subject_code = request.form.get('subject')
        topic = request.form.get('topic')
        level = request.form.get('level')
        num_cards = int(request.form.get('num_cards', 10))
        
        # 科目情報を取得
        subject = Subject.query.filter_by(code=subject_code).first()
        if not subject:
            flash("無効な科目です。", "danger")
            return redirect(url_for('flashcards'))
        
        # フラッシュカードを生成
        cards_data = generate_flashcards(
            subject.name,
            topic,
            level,
            num_cards
        )
        
        if not cards_data:
            flash("フラッシュカードの生成に失敗しました。もう一度お試しください。", "danger")
            return redirect(url_for('flashcards'))
        
        # フラッシュカードを保存
        for card_data in cards_data.get("cards", []):
            front = card_data.get("front", "")
            back = card_data.get("back", "")
            
            new_card = Flashcard(
                user_id=current_user.id,
                subject_id=subject.id,
                front=front,
                back=back,
                level=3,  # 中程度の重要度
                created_at=datetime.utcnow(),
                next_review=datetime.utcnow() + timedelta(days=1)  # 明日復習
            )
            db.session.add(new_card)
        
        db.session.commit()
        
        flash(f"{len(cards_data.get('cards', []))}枚のフラッシュカードが作成されました！", "success")
        return redirect(url_for('flashcards'))
    
    # デュー（復習予定）のカードを取得
    due_cards = Flashcard.query.filter(
        Flashcard.user_id == current_user.id,
        Flashcard.next_review <= datetime.utcnow()
    ).order_by(Flashcard.next_review).limit(10).all()
    
    # 最近作成されたカード
    recent_cards = Flashcard.query.filter_by(user_id=current_user.id).order_by(Flashcard.created_at.desc()).limit(10).all()
    
    # 科目別のカード数
    subject_counts = db.session.query(
        Subject.name, db.func.count(Flashcard.id)
    ).join(Flashcard).filter(
        Flashcard.user_id == current_user.id
    ).group_by(Subject.name).all()
    
    return render_template(
        'flashcards.html',
        due_cards=due_cards,
        recent_cards=recent_cards,
        subject_counts=subject_counts,
        subjects=Subject.query.all(),
        levels=LEVELS
    )

@app.route('/flashcards/review/<int:card_id>', methods=['POST'])
@login_required
def review_flashcard(card_id):
    card = Flashcard.query.get_or_404(card_id)
    
    # 権限チェック
    if card.user_id != current_user.id:
        return jsonify({"error": "権限がありません"}), 403
    
    # 復習の評価（0-5）
    rating = int(request.form.get('rating', 3))
    
    # スペースド・リピティション・アルゴリズムを適用
    # 評価が低いほど早く復習、高いほど後で復習
    if rating <= 1:
        delay_days = 1
    elif rating == 2:
        delay_days = 3
    elif rating == 3:
        delay_days = 7
    elif rating == 4:
        delay_days = 14
    else:
        delay_days = 30
    
    # 次の復習日を設定
    card.last_reviewed = datetime.utcnow()
    card.next_review = datetime.utcnow() + timedelta(days=delay_days)
    db.session.commit()
    
    return jsonify({"success": True, "next_review": card.next_review.strftime("%Y-%m-%d")})

@app.route('/stats')
@login_required
def stats():
    # 学習時間チャート
    time_chart = generate_study_time_chart(current_user.id)
    
    # 科目分布チャート
    subject_chart = generate_subject_distribution_chart(current_user.id)
    
    # 学習セッションの総数
    total_sessions = StudySession.query.filter_by(user_id=current_user.id).count()
    
    # 総学習時間
    total_time = db.session.query(db.func.sum(StudySession.duration_minutes)).filter(
        StudySession.user_id == current_user.id,
        StudySession.duration_minutes.isnot(None)
    ).scalar() or 0
    
    # 科目別の学習時間
    subject_times = db.session.query(
        Subject.name, db.func.sum(StudySession.duration_minutes)
    ).join(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.duration_minutes.isnot(None)
    ).group_by(Subject.name).all()
    
    # クイズの平均スコア
    avg_score = db.session.query(db.func.avg(Quiz.score)).filter(
        Quiz.user_id == current_user.id,
        Quiz.score.isnot(None)
    ).scalar() or 0
    
    # 科目別のクイズスコア
    subject_scores = db.session.query(
        Subject.name, db.func.avg(Quiz.score)
    ).join(Quiz).filter(
        Quiz.user_id == current_user.id,
        Quiz.score.isnot(None)
    ).group_by(Subject.name).all()
    
    return render_template(
        'stats.html',
        time_chart=time_chart,
        subject_chart=subject_chart,
        total_sessions=total_sessions,
        total_time=total_time,
        subject_times=subject_times,
        avg_score=avg_score,
        subject_scores=subject_scores
    )

# ヘルパー関数
def generate_initial_topics(subject, level):
    """科目に関する初期トピックリストを生成する"""
    messages = [
        {"role": "system", "content": f"あなたは{subject}の教育専門家です。{level}レベルの学習者向けに、学習するべき主要なトピックを提案してください。"},
        {"role": "user", "content": f"{subject}の{level}レベルの学習者が学ぶべき主要なトピックを10個、簡単な説明と共にリスト形式で提案してください。JSON形式で返してください。"}
    ]
    response = generate_response(messages)
    
    # JSONを抽出して解析
    try:
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response
        
        # 余分な文字を削除
        json_str = re.sub(r'[^\x00-\x7F]+', ' ', json_str)
        topics = json.loads(json_str)
        
        # topics が list 型の場合の対応
        if isinstance(topics, list):
            return topics
        elif isinstance(topics, dict) and "topics" in topics:
            return topics.get("topics", [])
        else:
            logger.error(f"予期しないJSON形式: {topics}")
            return []
    except Exception as e:
        logger.error(f"JSON解析エラー: {str(e)}")
        return []

@app.route('/end_session', methods=['POST'])
@login_required
def end_session():
    if 'study_session_id' in session:
        study_session_id = session.pop('study_session_id')
        study_session = StudySession.query.get(study_session_id)
        
        if study_session and study_session.user_id == current_user.id:
            study_session.end_time = datetime.utcnow()
            
            # 学習時間を計算（分単位）
            duration = (study_session.end_time - study_session.start_time).total_seconds() / 60
            study_session.duration_minutes = int(duration)
            
            db.session.commit()
    
    return redirect(url_for('dashboard'))

@app.route('/api/content/<int:topic_id>', methods=['GET'])
@login_required
def api_get_content(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    
    # コンテンツタイプ
    content_type = request.args.get('type', 'explanation')
    
    # APIからコンテンツを生成
    content = generate_learning_content(
        topic.subject.name,
        topic.name,
        topic.level,
        content_type=content_type
    )
    
    return jsonify({
        "topic": topic.name,
        "content_type": content_type,
        "content": content
    })

@app.route('/api/summarize', methods=['POST'])
@login_required
def api_summarize():
    text = request.json.get('text', '')
    if not text:
        return jsonify({"error": "テキストが提供されていません"}), 400
    
    summary = summarize_text(text)
    return jsonify({"summary": summary})

@app.route('/api/explain', methods=['POST'])
@login_required
def api_explain_concept():
    subject = request.json.get('subject', '一般')
    concept = request.json.get('concept', '')
    level = request.json.get('level', 'intermediate')
    
    if not concept:
        return jsonify({"error": "説明する概念が提供されていません"}), 400
    
    explanation = generate_concept_explanation(subject, concept, level)
    return jsonify({"explanation": explanation})

# メイン関数
def main():
    init_db()
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    main()