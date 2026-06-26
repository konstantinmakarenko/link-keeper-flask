"""
Формы для работы с пользователями и ссылками.
Используем WTForms для валидации данных.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, URL, Optional
from flask_login import current_user
from .models import User, Tag


class RegistrationForm(FlaskForm):
    """Форма регистрации нового пользователя"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Имя пользователя обязательно'),
        Length(min=3, max=80, message='Имя должно быть от 3 до 80 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен'),
        Length(min=6, message='Пароль должен быть минимум 6 символов')
    ])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, field):
        """Проверяем, что username не занят"""
        if User.query.filter_by(username=field.data).first():
            raise ValueError('Это имя пользователя уже занято')

    def validate_email(self, field):
        """Проверяем, что email не занят"""
        if User.query.filter_by(email=field.data).first():
            raise ValueError('Этот email уже зарегистрирован')


class LoginForm(FlaskForm):
    """Форма входа в систему"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Введите имя пользователя')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль')
    ])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class LinkForm(FlaskForm):
    """Форма добавления/редактирования ссылки"""
    title = StringField('Название', validators=[
        DataRequired(message='Название обязательно'),
        Length(max=200, message='Название не должно превышать 200 символов')
    ])
    url = StringField('URL', validators=[
        DataRequired(message='URL обязателен'),
        URL(message='Введите корректный URL (начинается с http:// или https://)')
    ])
    description = TextAreaField('Описание', validators=[
        Optional(),
        Length(max=500, message='Описание не должно превышать 500 символов')
    ])
    tags = StringField('Теги (через запятую)', validators=[
        Optional(),
        Length(max=200, message='Слишком много тегов')
    ])
    is_public = BooleanField('Публичная ссылка', default=True)
    submit = SubmitField('Сохранить')


class SearchForm(FlaskForm):
    """Форма поиска ссылок"""
    query = StringField('Поиск', validators=[
        DataRequired(message='Введите поисковый запрос')
    ])
    submit = SubmitField('Найти')