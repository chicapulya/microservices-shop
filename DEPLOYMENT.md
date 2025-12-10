# Деплой микросервисов

## Обзор

Проект поддерживает два способа деплоя:
1. **Локальный деплой** с Docker Compose
2. **CI/CD деплой** через GitHub Actions

## Локальный деплой с Docker Compose

### Предварительные требования

- Docker 20.10+
- Docker Compose 2.0+

### Быстрый старт

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd microservices-shop-master
```

2. Создайте файл `.env` в корне проекта:
```env
# Database
POSTGRES_USER=shop_user
POSTGRES_PASSWORD=shop_password
POSTGRES_DB=shop_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Services URLs
USER_SERVICE_URL=http://user-service:8004
PRODUCT_SERVICE_URL=http://product-service:8001
CART_SERVICE_URL=http://cart-service:8002
ORDER_SERVICE_URL=http://order-service:8003
CURRENCY_SERVICE_URL=http://currency-service:8006
DISCOUNT_SERVICE_URL=http://discount-service:8005

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
```

3. Запустите все сервисы:
```bash
docker-compose up -d
```

4. Проверьте статус сервисов:
```bash
docker-compose ps
```

5. Просмотрите логи:
```bash
docker-compose logs -f
```

### Доступные сервисы

После запуска сервисы доступны по адресам:

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **User Service**: http://localhost:8004
- **Product Service**: http://localhost:8001
- **Cart Service**: http://localhost:8002
- **Order Service**: http://localhost:8003
- **Currency Service**: http://localhost:8006
- **Discount Service**: http://localhost:8005
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Управление сервисами

```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Перезапуск конкретного сервиса
docker-compose restart user-service

# Просмотр логов конкретного сервиса
docker-compose logs -f user-service

# Масштабирование сервиса
docker-compose up -d --scale product-service=3

# Пересборка образов
docker-compose build

# Пересборка и запуск
docker-compose up -d --build
```

### Инициализация данных

После первого запуска необходимо создать суперпользователя:

```bash
# User Service
docker-compose exec user-service python manage.py createsuperuser

# Product Service (для админки)
docker-compose exec product-service python manage.py createsuperuser
```

Загрузка тестовых данных:

```bash
# Валюты
docker-compose exec currency-service python manage.py loaddata initial_currencies

# Категории товаров
docker-compose exec product-service python manage.py loaddata initial_categories
```

## CI/CD деплой через GitHub Actions

### Настройка GitHub Container Registry

1. Создайте Personal Access Token с правами `write:packages`:
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token
   - Выберите `write:packages` и `read:packages`

2. Добавьте токен в секреты репозитория:
   - Repository → Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `GITHUB_TOKEN` (создается автоматически)

### Автоматический деплой

При push в ветку `main`:

1. **Build & Push** - сборка Docker-образов для всех сервисов
2. **Security Scan** - сканирование уязвимостей с Trivy
3. **Deploy** - деплой на production сервер (если настроен)

### Настройка секретов для деплоя

В Settings → Secrets and variables → Actions добавьте:

```
DEPLOY_SSH_KEY - SSH приватный ключ для доступа к серверу
DEPLOY_HOST - IP адрес или домен сервера
DEPLOY_USER - Пользователь SSH (например, ubuntu)
```

### Ручной запуск деплоя

1. Перейдите в Actions
2. Выберите workflow "Build and Deploy"
3. Нажмите "Run workflow"
4. Выберите ветку и запустите

### Pull образов из GitHub Container Registry

```bash
# Логин в GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull конкретного сервиса
docker pull ghcr.io/YOUR_USERNAME/microservices-shop/user-service:latest

# Запуск с образом из registry
docker run -d ghcr.io/YOUR_USERNAME/microservices-shop/user-service:latest
```

## Деплой на production сервер

### Подготовка сервера

1. Установите Docker и Docker Compose:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo apt-get install docker-compose-plugin
```

2. Настройте SSH доступ:
```bash
# Добавьте публичный ключ в authorized_keys
cat ~/.ssh/id_rsa.pub | ssh user@server 'cat >> ~/.ssh/authorized_keys'
```

3. Клонируйте репозиторий на сервере:
```bash
git clone <repository-url>
cd microservices-shop-master
```

4. Создайте production `.env` файл:
```env
DEBUG=False
SECRET_KEY=<strong-production-secret-key>
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
# ... остальные настройки
```

5. Запустите сервисы:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Настройка NGINX

Создайте конфигурацию NGINX для проксирования:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Настройка SSL с Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Мониторинг и логи

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f user-service

# Последние 100 строк
docker-compose logs --tail=100 user-service
```

### Здоровье сервисов

```bash
# Проверка статуса
docker-compose ps

# Health check для конкретного сервиса
curl http://localhost:8004/health/
```

### Использование ресурсов

```bash
# Статистика по контейнерам
docker stats

# Использование диска
docker system df
```

## Резервное копирование

### База данных

```bash
# Backup
docker-compose exec postgres pg_dump -U shop_user shop_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U shop_user shop_db < backup.sql
```

### Volumes

```bash
# Backup volumes
docker run --rm -v shop_postgres-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres-data-backup.tar.gz /data

# Restore volumes
docker run --rm -v shop_postgres-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-data-backup.tar.gz -C /
```

## Troubleshooting

### Порты заняты

```bash
# Проверить, что использует порт
lsof -i :8000
netstat -ano | findstr :8000  # Windows

# Изменить порты в docker-compose.yml
```

### Проблемы с миграциями

```bash
# Ручное применение миграций
docker-compose exec user-service python manage.py migrate

# Откат миграций
docker-compose exec user-service python manage.py migrate app_name migration_name
```

### Очистка Docker

```bash
# Удалить неиспользуемые образы
docker image prune -a

# Удалить неиспользуемые volumes
docker volume prune

# Полная очистка системы
docker system prune -a --volumes
```

### Перезапуск зависших контейнеров

```bash
# Перезапуск всех
docker-compose restart

# Принудительная пересборка
docker-compose up -d --force-recreate --build
```

## Production Best Practices

1. **Переменные окружения** - используйте секреты для sensitive данных
2. **Логирование** - настройте централизованное логирование (ELK, Grafana Loki)
3. **Мониторинг** - используйте Prometheus + Grafana
4. **Backup** - автоматизируйте резервное копирование БД
5. **SSL/TLS** - всегда используйте HTTPS в production
6. **Health Checks** - настройте health checks для всех сервисов
7. **Resource Limits** - установите лимиты CPU и памяти
8. **Security Scanning** - регулярно сканируйте образы на уязвимости

## Контакты

При возникновении проблем создайте issue в репозитории.
