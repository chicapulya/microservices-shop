# PowerShell скрипт для инициализации проекта в Docker

Write-Host "🚀 Инициализация Microservices Shop..." -ForegroundColor Green

# Проверка, что Docker запущен
try {
    docker info > $null 2>&1
    Write-Host "✅ Docker запущен" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker не запущен. Пожалуйста, запустите Docker Desktop." -ForegroundColor Red
    exit 1
}

# Остановка и удаление старых контейнеров
Write-Host "🧹 Очистка старых контейнеров..." -ForegroundColor Yellow
docker-compose down -v

# Сборка образов
Write-Host "🔨 Сборка Docker образов..." -ForegroundColor Yellow
docker-compose build

# Запуск контейнеров
Write-Host "🚢 Запуск контейнеров..." -ForegroundColor Yellow
docker-compose up -d

# Ожидание запуска Redis
Write-Host "⏳ Ожидание запуска Redis..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Ожидание запуска сервисов
Write-Host "⏳ Ожидание запуска сервисов..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Создание суперпользователя в user-service
Write-Host "👤 Создание администратора..." -ForegroundColor Yellow
$createUserScript = @"
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
"@

$createUserScript | docker-compose exec -T user-service python manage.py shell

Write-Host ""
Write-Host "✅ Инициализация завершена!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Доступ к приложению:" -ForegroundColor Cyan
Write-Host "   Frontend:        http://localhost:3000" -ForegroundColor White
Write-Host "   API Gateway:     http://localhost:8000" -ForegroundColor White
Write-Host "   User Service:    http://localhost:8004" -ForegroundColor White
Write-Host "   Product Service: http://localhost:8001" -ForegroundColor White
Write-Host "   Cart Service:    http://localhost:8002" -ForegroundColor White
Write-Host "   Order Service:   http://localhost:8003" -ForegroundColor White
Write-Host ""
Write-Host "👤 Учетные данные администратора:" -ForegroundColor Cyan
Write-Host "   Email:    admin@shop.com" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "📝 Полезные команды:" -ForegroundColor Cyan
Write-Host "   Логи:              docker-compose logs -f" -ForegroundColor White
Write-Host "   Остановка:         docker-compose down" -ForegroundColor White
Write-Host "   Перезапуск:        docker-compose restart" -ForegroundColor White
Write-Host ""
