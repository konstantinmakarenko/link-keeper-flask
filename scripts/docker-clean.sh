#!/bin/bash
# Полная очистка (контейнеры, тома, образы)

echo "⚠️  Это удалит все контейнеры, тома и образы проекта!"
read -p "Продолжить? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down -v --rmi all
    echo "✅ Очистка завершена"
else
    echo "Операция отменена"
fi