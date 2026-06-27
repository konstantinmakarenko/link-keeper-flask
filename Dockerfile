# Используем официальный образ Python 3.12-slim как основу
FROM python:3.12-slim

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями сначала (для кэширования слоёв Docker)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения в контейнер
COPY . .

# Создаём пользователя appuser (без прав root) для безопасности
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Переключаемся на пользователя appuser
USER appuser

# Открываем порт 5000 (Flask/Gunicorn)
EXPOSE 5000

# Команда запуска приложения через Gunicorn
# --workers 1 (внутри контейнера, репликация на уровне docker-compose)
# --bind 0.0.0.0:5000 (слушаем все интерфейсы)
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:5000", "app:create_app()"]