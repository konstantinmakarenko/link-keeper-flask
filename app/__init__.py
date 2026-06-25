"""
Фабрика приложения Flask.
Здесь создаётся экземпляр приложения, настраиваются БД, Redis, сессии.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from redis import Redis
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Создаём экземпляры расширений (глобальные объекты)
db = SQLAlchemy()
login_manager = LoginManager()
session = Session()

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
    login_manager.login_view = 'routes.login'  # Куда перенаправлять неавторизованных
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'

    session.init_app(app)

    # --- Регистрация Blueprint ---
    from .routes import routes_bp
    app.register_blueprint(routes_bp)

    return app