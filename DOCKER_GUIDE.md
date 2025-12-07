# 🐳 Запуск Microservices Shop на Docker

## Предварительные требования

- Docker Desktop установлен и запущен
- Docker Compose доступен (входит в Docker Desktop)

## 🚀 Быстрый старт

### 1. Сборка и запуск всех сервисов

```powershell
# Запуск всех контейнеров в фоновом режиме
docker-compose up -d --build
```

Эта команда:
- Соберет Docker образы для всех сервисов
- Запустит контейнеры в правильном порядке (с учетом зависимостей)
- Выполнит миграции БД для каждого сервиса

### 2. Проверка статуса

```powershell
# Посмотреть запущенные контейнеры
docker-compose ps

# Посмотреть логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f user-service
docker-compose logs -f api-gateway
docker-compose logs -f frontend
```

### 3. Доступ к приложению

После успешного запуска:

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **User Service**: http://localhost:8004
- **Product Service**: http://localhost:8001
- **Cart Service**: http://localhost:8002
- **Order Service**: http://localhost:8003
- **Redis**: localhost:6379

## 📦 Управление контейнерами

### Остановка всех сервисов

```powershell
docker-compose down
```

### Остановка с удалением volumes (БД будут очищены)

```powershell
docker-compose down -v
```

### Перезапуск конкретного сервиса

```powershell
docker-compose restart user-service
```

### Пересборка конкретного сервиса

```powershell
docker-compose up -d --build user-service
```

## 🔧 Полезные команды

### Выполнение Django команд внутри контейнера

```powershell
# Создать суперпользователя в user-service
docker-compose exec user-service python manage.py createsuperuser

# Загрузить тестовые данные в product-service
docker-compose exec product-service python manage.py loaddata products.json

# Применить миграции
docker-compose exec user-service python manage.py migrate
```

### Зайти в контейнер

```powershell
# Bash в контейнере user-service
docker-compose exec user-service /bin/bash

# Shell Django
docker-compose exec user-service python manage.py shell
```

### Просмотр логов Redis

```powershell
docker-compose logs -f redis
```

## 🗄️ База данных

Каждый микросервис имеет свою SQLite БД, которая хранится в Docker volumes:

- `user-db` - база данных пользователей
- `product-db` - база данных товаров
- `cart-db` - база данных корзин
- `order-db` - база данных заказов

Данные сохраняются между перезапусками контейнеров.

### Очистка баз данных

```powershell
# Остановить контейнеры и удалить volumes
docker-compose down -v

# Запустить заново
docker-compose up -d
```

## 🔍 Диагностика проблем

### Проверка здоровья Redis

```powershell
docker-compose exec redis redis-cli ping
# Должен вернуть: PONG
```

### Проверка сетевого взаимодействия

```powershell
# Проверить, видит ли cart-service product-service
docker-compose exec cart-service ping product-service
```

### Просмотр всех контейнеров

```powershell
docker ps -a
```

### Просмотр использования ресурсов

```powershell
docker stats
```

## 📝 Структура проекта

```
microservices-shop-master/
├── docker-compose.yml          # Оркестрация всех сервисов
├── api-gateway/
│   ├── Dockerfile             # Образ для API Gateway
│   └── ...
├── services/
│   ├── user-service/
│   │   ├── Dockerfile
│   │   └── ...
│   ├── product-service/
│   │   ├── Dockerfile
│   │   └── ...
│   ├── cart-service/
│   │   ├── Dockerfile
│   │   └── ...
│   └── order-service/
│       ├── Dockerfile
│       └── ...
└── frontend/
    ├── Dockerfile
    └── ...
```

## 🌐 Переменные окружения

Все сервисы настроены через переменные окружения в `docker-compose.yml`:

- `REDIS_HOST` - хост Redis (redis)
- `REDIS_PORT` - порт Redis (6379)
- `USER_SERVICE_URL` - URL user-service
- `PRODUCT_SERVICE_URL` - URL product-service
- `CART_SERVICE_URL` - URL cart-service
- `ORDER_SERVICE_URL` - URL order-service

## 🔄 Обновление кода

При изменении кода:

1. **Backend (Python)**: Изменения применяются автоматически благодаря volumes
2. **Frontend (Vue.js)**: Vite в режиме dev применит изменения автоматически

Если нужна пересборка:

```powershell
docker-compose up -d --build <service-name>
```

## ⚡ Production режим

Для production развертывания:

1. Измените `DEBUG=False` в переменных окружения
2. Замените SQLite на PostgreSQL
3. Используйте Gunicorn вместо Django dev server
4. Добавьте Nginx для статики
5. Настройте HTTPS

## 🐛 Устранение неполадок

### Проблема: Контейнер постоянно перезапускается

```powershell
# Посмотреть логи
docker-compose logs <service-name>
```

### Проблема: Порт уже занят

Убедитесь, что порты 3000, 8000-8004, 6379 свободны:

```powershell
# Остановить локальные серверы
# Или измените порты в docker-compose.yml
```

### Проблема: Сервисы не видят друг друга

```powershell
# Проверить сеть
docker network ls
docker network inspect microservices-shop-master_shop-network
```

## 📚 Дополнительная информация

- Docker Compose документация: https://docs.docker.com/compose/
- Django в Docker: https://docs.docker.com/samples/django/
- Vue.js в Docker: https://vuejs.org/guide/scaling-up/tooling.html#docker
