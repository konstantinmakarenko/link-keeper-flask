#!/bin/sh
# Временно отключаем миграции, пока не исправим Alembic
# flask db upgrade

# Запускаем Gunicorn
exec gunicorn --workers 1 --bind 0.0.0.0:5000 "app:create_app()"