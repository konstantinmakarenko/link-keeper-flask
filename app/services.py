"""
Сервисный слой — бизнес-логика приложения.
Здесь работа с БД, кэширование, вспомогательные функции.
"""

import redis
from flask import current_app
from sqlalchemy import func
from datetime import datetime, timedelta
from . import db
from .models import User, Link, Tag


def get_redis():
    """Возвращает клиент Redis из конфигурации приложения"""
    return current_app.config['SESSION_REDIS']


def get_cached_links(limit=10):
    """
    Получает популярные ссылки из кэша Redis.
    Если кэш пуст — загружает из БД и сохраняет в кэш.
    """
    redis_client = get_redis()
    cache_key = 'popular_links'

    # Пробуем получить из кэша
    cached = redis_client.get(cache_key)
    if cached:
        import json
        return json.loads(cached)

    # Если кэша нет — загружаем из БД
    links = Link.query.filter_by(is_public=True).order_by(
        Link.clicks.desc()
    ).limit(limit).all()

    # Превращаем в словари для JSON-сериализации
    result = [{
        'id': link.id,
        'title': link.title,
        'url': link.url,
        'description': link.description,
        'clicks': link.clicks,
        'created_at': link.created_at.isoformat(),
        'author': link.author.username,
        'tags': [tag.name for tag in link.tags]
    } for link in links]

    # Сохраняем в кэш на 5 минут
    import json
    redis_client.setex(cache_key, 300, json.dumps(result))

    return result


def increment_link_clicks(link_id):
    """Увеличивает счётчик кликов по ссылке и сбрасывает кэш"""
    link = Link.query.get(link_id)
    if link:
        link.clicks += 1
        db.session.commit()
        # Сбрасываем кэш популярных ссылок
        get_redis().delete('popular_links')
        return True
    return False


def get_user_stats(user_id):
    """
    Возвращает статистику пользователя:
    - всего ссылок
    - публичных ссылок
    - избранных ссылок
    - количество тегов
    """
    user_links = Link.query.filter_by(user_id=user_id)

    stats = {
        'total': user_links.count(),
        'public': user_links.filter_by(is_public=True).count(),
        'favorite': user_links.filter_by(is_favorite=True).count(),
        'tags': db.session.query(func.count(db.distinct(link_tags.c.tag_id))).select_from(
            Link
        ).join(link_tags).filter(Link.user_id == user_id).scalar() or 0
    }
    return stats


def get_or_create_tag(tag_name):
    """Получает или создаёт тег по имени (регистронезависимо)"""
    tag = Tag.query.filter(func.lower(Tag.name) == func.lower(tag_name)).first()
    if not tag:
        tag = Tag(name=tag_name.lower())
        db.session.add(tag)
        db.session.commit()
    return tag


def process_tags(tag_string):
    """
    Превращает строку с тегами (через запятую) в список объектов Tag.
    Пример: "python, flask, docker" → [Tag('python'), Tag('flask'), Tag('docker')]
    """
    if not tag_string:
        return []

    tag_names = [t.strip() for t in tag_string.split(',') if t.strip()]
    tags = []
    for name in tag_names:
        tag = get_or_create_tag(name)
        tags.append(tag)
    return tags


def search_links(query, user_id=None):
    """
    Поиск ссылок по названию, описанию или тегам.
    Если user_id указан — ищем только его ссылки.
    Иначе — ищем по всем публичным ссылкам.
    """
    search_term = f'%{query}%'

    # Базовый запрос
    if user_id:
        links_query = Link.query.filter_by(user_id=user_id)
    else:
        links_query = Link.query.filter_by(is_public=True)

    # Поиск по названию или описанию
    links = links_query.filter(
        db.or_(
            Link.title.ilike(search_term),
            Link.description.ilike(search_term)
        )
    ).order_by(Link.created_at.desc()).all()

    # Дополнительно ищем по тегам (если есть совпадения)
    tag_links = Link.query.join(link_tags).join(Tag).filter(
        Tag.name.ilike(search_term)
    )
    if user_id:
        tag_links = tag_links.filter_by(user_id=user_id)
    else:
        tag_links = tag_links.filter_by(is_public=True)

    # Объединяем результаты (без дубликатов)
    result = list(links)
    for link in tag_links:
        if link not in result:
            result.append(link)

    return result