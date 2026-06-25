"""
Модели данных (SQLAlchemy ORM).
Соответствуют таблицам в PostgreSQL.
"""

from flask_login import UserMixin
from datetime import datetime
from . import db

# Промежуточная таблица для связи "многие-ко-многим" (ссылка ↔ тег)
link_tags = db.Table('link_tags',
    db.Column('link_id', db.Integer, db.ForeignKey('links.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """Модель пользователя"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    links = db.relationship('Link', backref='author', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Link(db.Model):
    """Модель ссылки"""
    __tablename__ = 'links'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    is_favorite = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=True)  # Видна всем или только автору
    clicks = db.Column(db.Integer, default=0)  # Счётчик переходов
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Внешние ключи
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Связи (многие-ко-многим с тегами)
    tags = db.relationship('Tag', secondary=link_tags, lazy='subquery',
                          backref=db.backref('links', lazy=True))

    def __repr__(self):
        return f'<Link {self.title}>'


class Tag(db.Model):
    """Модель тега"""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'