#!/bin/bash
# Скрипт для запуска проекта в режиме разработки

echo "🚀 Запуск link-keeper-flask..."

# Проверяем, что .env существует
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Копируем из .env.example..."
    cp .env.example .env
    echo "✅ .env создан. Отредактируйте его при необходимости."
fi

# Запускаем через docker-compose
docker-compose up -d

echo "✅ Проект запущен!"
echo "🌐 Веб-интерфейс: http://localhost:8080"
echo "📦 Для просмотра логов: docker-compose logs -f"
echo "🛑 Для остановки: ./scripts/stop.sh"