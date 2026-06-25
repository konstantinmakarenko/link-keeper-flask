#!/bin/bash
# Скрипт для настройки виртуального окружения

echo "🐍 Настройка виртуального окружения..."

# Проверяем, существует ли .venv
if [ -d ".venv" ]; then
    echo "⚠️  Виртуальное окружение уже существует. Удалите .venv для пересоздания."
else
    # Пробуем python3.12
    if command -v python3.12 &> /dev/null; then
        python3.12 -m venv .venv
    elif command -v py &> /dev/null; then
        py -3.12 -m venv .venv
    else
        echo "❌ Python 3.12 не найден! Установите его вручную."
        exit 1
    fi
    echo "✅ Виртуальное окружение создано"
fi

# Активируем и устанавливаем зависимости
echo "📦 Установка зависимостей..."
source .venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Готово! Для активации выполните:"
echo "   source .venv/Scripts/activate"