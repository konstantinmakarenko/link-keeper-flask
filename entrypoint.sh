#!/bin/sh
# Запускаем миграции перед стартом приложения
flask db upgrade

# Запускаем Gunicorn
exec gunicorn --workers 1 --bind 0.0.0.0:5000 "app:create_app()"