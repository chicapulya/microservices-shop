# 🚀 Быстрый старт

## Запуск проекта в Docker

### 1. Убедитесь, что Docker Desktop запущен

### 2. Запустите проект

**Вариант A: Автоматическая инициализация**
```powershell
.\init.ps1
```

**Вариант B: Ручной запуск**
```powershell
docker-compose up -d --build
```

### 3. Откройте браузер

http://localhost:3000

### 4. Проверьте статус

```powershell
docker-compose ps
```

## Остановка проекта

```powershell
docker-compose down
```

## Просмотр логов

```powershell
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f user-service
```

## Доступ к сервисам

- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- User Service: http://localhost:8004
- Product Service: http://localhost:8001
- Cart Service: http://localhost:8002
- Order Service: http://localhost:8003

## Учетные данные по умолчанию

Email: `admin@shop.com`  
Password: `admin123`

## Полная документация

См. [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
