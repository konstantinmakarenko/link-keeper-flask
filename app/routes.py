"""
Роуты Flask — обработка HTTP-запросов.
Здесь логика: регистрация, вход, управление ссылками, поиск.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from . import db
from .models import User, Link
from .forms import RegistrationForm, LoginForm, LinkForm, SearchForm
from .services import (
    get_cached_links, increment_link_clicks, get_user_stats,
    process_tags, search_links
)

# Создаём Blueprint — модуль маршрутов
routes_bp = Blueprint('routes', __name__)


@routes_bp.route('/')
def index():
    """Главная страница — показывает популярные публичные ссылки"""
    popular_links = get_cached_links(limit=10)
    return render_template('index.html', links=popular_links)


@routes_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Хешируем пароль
        hashed_password = generate_password_hash(form.password.data)

        # Создаём пользователя
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )

        # Если это первый пользователь — делаем его админом
        if User.query.count() == 0:
            user.is_admin = True
            flash('Вы зарегистрированы как администратор!', 'success')

        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('routes.login'))

    return render_template('register.html', form=form)


@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в систему"""
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Добро пожаловать, {user.username}!', 'success')

            # Перенаправляем на страницу, куда хотел попасть пользователь
            next_page = request.args.get('next')
            return redirect(next_page or url_for('routes.dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')

    return render_template('login.html', form=form)


@routes_bp.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('routes.index'))


@routes_bp.route('/dashboard')
@login_required
def dashboard():
    """Личный кабинет — список ссылок пользователя"""
    # Получаем все ссылки пользователя (сортировка по дате)
    links = Link.query.filter_by(user_id=current_user.id).order_by(
        Link.created_at.desc()
    ).all()

    # Статистика
    stats = get_user_stats(current_user.id)

    return render_template('dashboard.html', links=links, stats=stats)


@routes_bp.route('/link/add', methods=['GET', 'POST'])
@login_required
def add_link():
    """Добавление новой ссылки"""
    form = LinkForm()
    if form.validate_on_submit():
        # Обрабатываем теги
        tags = process_tags(form.tags.data)

        # Создаём ссылку
        link = Link(
            title=form.title.data,
            url=form.url.data,
            description=form.description.data,
            is_public=form.is_public.data,
            author=current_user
        )

        # Добавляем теги
        link.tags.extend(tags)

        db.session.add(link)
        db.session.commit()

        # Сбрасываем кэш популярных ссылок
        from .services import get_redis
        get_redis().delete('popular_links')

        flash('Ссылка успешно добавлена!', 'success')
        return redirect(url_for('routes.dashboard'))

    return render_template('add_link.html', form=form)


@routes_bp.route('/link/<int:link_id>')
def view_link(link_id):
    """Просмотр ссылки — увеличиваем счётчик кликов и редиректим"""
    link = Link.query.get_or_404(link_id)

    # Если ссылка приватная и не принадлежит текущему пользователю
    if not link.is_public and (not current_user.is_authenticated or current_user.id != link.user_id):
        flash('Эта ссылка приватная', 'warning')
        return redirect(url_for('routes.index'))

    # Увеличиваем счётчик кликов
    increment_link_clicks(link_id)

    return redirect(link.url)


@routes_bp.route('/link/<int:link_id>/toggle-favorite', methods=['POST'])
@login_required
def toggle_favorite(link_id):
    """Переключение статуса 'избранное' у ссылки"""
    link = Link.query.get_or_404(link_id)

    if link.user_id != current_user.id:
        flash('Вы не можете редактировать эту ссылку', 'danger')
        return redirect(url_for('routes.dashboard'))

    link.is_favorite = not link.is_favorite
    db.session.commit()

    status = 'добавлена в избранное' if link.is_favorite else 'удалена из избранного'
    flash(f'Ссылка {status}', 'success')
    return redirect(url_for('routes.dashboard'))


@routes_bp.route('/link/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_link(link_id):
    """Удаление ссылки (только для владельца или админа)"""
    link = Link.query.get_or_404(link_id)

    if link.user_id != current_user.id and not current_user.is_admin:
        flash('Вы не можете удалить эту ссылку', 'danger')
        return redirect(url_for('routes.dashboard'))

    db.session.delete(link)
    db.session.commit()

    # Сбрасываем кэш
    from .services import get_redis
    get_redis().delete('popular_links')

    flash('Ссылка удалена', 'success')
    return redirect(url_for('routes.dashboard'))


@routes_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Поиск ссылок"""
    form = SearchForm()
    results = []
    query = ''

    if form.validate_on_submit() or request.args.get('q'):
        query = form.query.data or request.args.get('q', '')

        # Если пользователь авторизован — ищем по его ссылкам + публичным
        if current_user.is_authenticated:
            results = search_links(query, current_user.id)
        else:
            results = search_links(query)

    return render_template('search.html', form=form, results=results, query=query)


@routes_bp.route('/about')
def about():
    """Страница 'О проекте'"""
    return render_template('about.html')