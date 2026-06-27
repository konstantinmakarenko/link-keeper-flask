"""
Фабрика приложения Flask.
Здесь создаётся экземпляр приложения, настраиваются БД, Redis, сессии.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_session import Session
from flask_migrate import Migrate
from redis import Redis
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Создаём экземпляры расширений (глобальные объекты)
db = SQLAlchemy()
login_manager = LoginManager()
session = Session()
migrate = Migrate()


@login_manager.user_loader
def load_user(user_id):
    """Загружает пользователя по ID для Flask-Login"""
    from .models import User
    return User.query.get(int(user_id))


def create_app():
    """Фабрика приложения — создаёт и настраивает Flask-приложение"""

    app = Flask(__name__)

    # --- Конфигурация ---
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Настройка Redis для сессий
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = Redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'session:'

    # --- Инициализация расширений ---
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'

    session.init_app(app)

    # Инициализация миграций (Alembic)
    migrate.init_app(app, db)

    # --- Регистрация Blueprint ---
    from .routes import routes_bp
    app.register_blueprint(routes_bp)

    return app