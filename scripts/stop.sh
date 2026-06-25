#!/bin/bash
# Скрипт для остановки проекта

echo "🛑 Остановка link-keeper-flask..."
docker-compose down
echo "✅ Проект остановлен"