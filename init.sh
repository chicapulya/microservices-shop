#!/bin/bash
# Скрипт для инициализации проекта в Docker

echo "🚀 Инициализация Microservices Shop..."

# Проверка, что Docker запущен
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker не запущен. Пожалуйста, запустите Docker Desktop."
    exit 1
fi

echo "✅ Docker запущен"

# Остановка и удаление старых контейнеров
echo "🧹 Очистка старых контейнеров..."
docker-compose down -v

# Сборка образов
echo "🔨 Сборка Docker образов..."
docker-compose build

# Запуск контейнеров
echo "🚢 Запуск контейнеров..."
docker-compose up -d

# Ожидание запуска Redis
echo "⏳ Ожидание запуска Redis..."
sleep 5

# Ожидание запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Создание суперпользователя в user-service
echo "👤 Создание администратора..."
docker-compose exec -T user-service python manage.py shell << EOF
from apps.users.models import User
if not User.objects.filter(email='admin@shop.com').exists():
    User.objects.create_superuser(
        email='admin@shop.com',
        password='admin123',
        username='admin'
    )
    print('Администратор создан: admin@shop.com / admin123')
else:
    print('Администратор уже существует')
EOF

# Загрузка тестовых данных товаров (если есть fixtures)
echo "📦 Загрузка тестовых данных..."
# docker-compose exec -T product-service python manage.py loaddata products.json

echo ""
echo "✅ Инициализация завершена!"
echo ""
echo "📍 Доступ к приложению:"
echo "   Frontend:        http://localhost:3000"
echo "   API Gateway:     http://localhost:8000"
echo "   User Service:    http://localhost:8004"
echo "   Product Service: http://localhost:8001"
echo "   Cart Service:    http://localhost:8002"
echo "   Order Service:   http://localhost:8003"
echo ""
echo "👤 Учетные данные администратора:"
echo "   Email:    admin@shop.com"
echo "   Password: admin123"
echo ""
echo "📝 Полезные команды:"
echo "   Логи:              docker-compose logs -f"
echo "   Остановка:         docker-compose down"
echo "   Перезапуск:        docker-compose restart"
echo ""
