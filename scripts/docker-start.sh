#!/bin/bash
# Запуск проекта через Docker Compose

echo "🐳 Запуск link-keeper-flask через Docker Compose..."
docker-compose up -d --build
echo "✅ Проект запущен!"
echo "🌐 Доступен по адресу: http://localhost:8080"
echo "📋 Логи: docker-compose logs -f"
echo "🛑 Остановка: docker-compose down"