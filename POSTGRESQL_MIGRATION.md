# Миграция на PostgreSQL завершена ✅

## Что изменилось

### База данных
- **Было:** SQLite (файлы в /app/db/*.db)
- **Стало:** PostgreSQL 15-alpine

### Структура БД
Каждый микросервис использует **отдельную базу данных**:
- `user_db` - для user-service
- `product_db` - для product-service
- `cart_db` - для cart-service
- `order_db` - для order-service

### Учетные данные
- **Пользователь БД:** shop_user
- **Пароль:** shop_password
- **Хост:** postgres (внутри Docker) или localhost:5432 (извне)

### Админ-панели
Для каждого сервиса создан superuser:
- **Логин:** admin
- **Пароль:** admin

**URL админок:**
- User Service: http://localhost:8004/admin/
- Product Service: http://localhost:8001/admin/
- Cart Service: http://localhost:8002/admin/
- Order Service: http://localhost:8003/admin/

## Быстрый запуск

```powershell
# Запустить все контейнеры
docker-compose up -d

# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f

# Остановить
docker-compose down

# Остановить с удалением данных
docker-compose down -v
```

## Подключение к PostgreSQL

### Из контейнера
```bash
docker-compose exec postgres psql -U shop_user -d user_db
```

### Извне Docker
```
Host: localhost
Port: 5432
User: shop_user
Password: shop_password
Database: user_db (или product_db, cart_db, order_db)
```

## Проверка данных

```powershell
# Список всех БД
docker-compose exec postgres psql -U shop_user -d postgres -c "\l"

# Список таблиц в user_db
docker-compose exec postgres psql -U shop_user -d user_db -c "\dt"

# Список пользователей в user_db
docker-compose exec postgres psql -U shop_user -d user_db -c "SELECT username, email, is_staff, is_superuser FROM users_user;"
```

## Миграции

Все миграции применяются автоматически при запуске контейнеров.

Для применения новых миграций вручную:
```powershell
docker-compose exec user-service python manage.py migrate
docker-compose exec product-service python manage.py migrate
docker-compose exec cart-service python manage.py migrate
docker-compose exec order-service python manage.py migrate
```

## Бэкап и восстановление

### Бэкап
```powershell
docker-compose exec postgres pg_dump -U shop_user user_db > backup_user_db.sql
docker-compose exec postgres pg_dump -U shop_user product_db > backup_product_db.sql
docker-compose exec postgres pg_dump -U shop_user cart_db > backup_cart_db.sql
docker-compose exec postgres pg_dump -U shop_user order_db > backup_order_db.sql
```

### Восстановление
```powershell
cat backup_user_db.sql | docker-compose exec -T postgres psql -U shop_user -d user_db
```

## Преимущества PostgreSQL

✅ Production-ready СУБД  
✅ Поддержка транзакций  
✅ Лучшая производительность при многопользовательской нагрузке  
✅ Поддержка репликации и масштабирования  
✅ Расширенные типы данных (JSON, массивы и т.д.)  
✅ Полная поддержка ACID  

## Troubleshooting

### Контейнер postgres не запускается
```powershell
docker-compose logs postgres
```

### Ошибки подключения к БД
```powershell
# Проверить, что postgres здоров
docker-compose exec postgres pg_isready -U shop_user

# Проверить переменные окружения
docker-compose exec user-service printenv | Select-String DATABASE
```

### Пересоздать БД с нуля
```powershell
docker-compose down -v  # Удалит все данные!
docker-compose up -d    # Создаст чистые БД
```
