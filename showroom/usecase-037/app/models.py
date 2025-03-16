"""
データベースモデル: アプリケーションで使用するデータベースモデルを定義
"""

from datetime import datetime
from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # リレーションシップ
    learning_plans = db.relationship("LearningPlan", backref="user", lazy=True)
    quizzes = db.relationship("Quiz", backref="user", lazy=True)
    flashcards = db.relationship("Flashcard", backref="user", lazy=True)
    notes = db.relationship("Note", backref="user", lazy=True)
    study_sessions = db.relationship("StudySession", backref="user", lazy=True)
    conversations = db.relationship("Conversation", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

    # リレーションシップ
    topics = db.relationship("Topic", backref="subject", lazy=True)

    def __repr__(self):
        return f"<Subject {self.name}>"


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    
    # コンテンツキャッシュ関連のフィールド
    content_cache = db.Column(db.Text)  # メインコンテンツのキャッシュ
    examples_cache = db.Column(db.Text)  # 例題のキャッシュ
    summary_cache = db.Column(db.Text)  # 要約のキャッシュ
    assessment_cache = db.Column(db.Text)  # 評価問題のキャッシュ
    cache_updated_at = db.Column(db.DateTime)  # キャッシュの最終更新日時

    def __repr__(self):
        return f"<Topic {self.name} ({self.level})>"


class LearningPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # リレーションシップ
    subject = db.relationship("Subject")
    items = db.relationship("LearningPlanItem", backref="learning_plan", lazy=True)

    def __repr__(self):
        return f"<LearningPlan {self.title}>"


class LearningPlanItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    learning_plan_id = db.Column(
        db.Integer, db.ForeignKey("learning_plan.id"), nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<LearningPlanItem {self.title}>"


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    topic = db.Column(db.String(100))
    level = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    score = db.Column(db.Float)

    # リレーションシップ
    subject = db.relationship("Subject")
    questions = db.relationship("QuizQuestion", backref="quiz", lazy=True)

    def __repr__(self):
        return f"<Quiz {self.title}>"


class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON文字列として選択肢を保存
    answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)

    def __repr__(self):
        return f"<QuizQuestion {self.question[:30]}...>"


class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    topic = db.Column(db.String(100))
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime)
    familiarity = db.Column(db.Integer, default=0)  # 0-5のスケール

    # リレーションシップ
    subject = db.relationship("Subject")

    def __repr__(self):
        return f"<Flashcard {self.front[:30]}...>"


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    topic = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # リレーションシップ
    subject = db.relationship("Subject")

    def __repr__(self):
        return f"<Note {self.title}>"


class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    topic = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    notes = db.Column(db.Text)

    # リレーションシップ
    subject = db.relationship("Subject")

    def __repr__(self):
        return f"<StudySession {self.subject.name} {self.start_time}>"


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))
    topic = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # リレーションシップ
    subject = db.relationship("Subject")
    messages = db.relationship("Message", backref="conversation", lazy=True)

    def __repr__(self):
        return f"<Conversation {self.title}>"


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer, db.ForeignKey("conversation.id"), nullable=False
    )
    role = db.Column(db.String(20), nullable=False)  # "user" または "assistant"
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.role} {self.created_at}>"
