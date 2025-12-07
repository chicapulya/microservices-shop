# Тестирование микросервисов

## Обзор

Проект содержит юнит-тесты для всех микросервисов:
- **User Service** - тесты аутентификации и управления пользователями
- **Product Service** - тесты каталога товаров и категорий
- **Cart Service** - тесты корзины покупок
- **Order Service** - тесты заказов
- **Currency Service** - тесты конвертации валют
- **Discount Service** - тесты скидок и промокодов

## Запуск тестов локально

### Предварительные требования

1. Python 3.11+
2. PostgreSQL 15+
3. Redis 7+

### Настройка окружения

Для каждого сервиса:

```bash
cd services/<service-name>
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Настройка переменных окружения

Создайте файл `.env.test` в корне каждого сервиса:

```env
DATABASE_URL=postgresql://shop_user:shop_password@localhost:5432/test_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=test-secret-key
DEBUG=True
```

### Запуск тестов для конкретного сервиса

```bash
# User Service
cd services/user-service
python manage.py test

# Product Service
cd services/product-service
python manage.py test

# Cart Service
cd services/cart-service
python manage.py test

# Order Service
cd services/order-service
python manage.py test

# Currency Service
cd services/currency-service
python manage.py test

# Discount Service
cd services/discount-service
python manage.py test
```

### Запуск тестов с покрытием кода

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Генерация HTML-отчета
```

### Запуск конкретных тестов

```bash
# Запуск конкретного тестового класса
python manage.py test apps.users.tests.UserModelTest

# Запуск конкретного теста
python manage.py test apps.users.tests.UserModelTest.test_user_creation
```

## CI/CD с GitHub Actions

### Автоматическое тестирование

Тесты запускаются автоматически при:
- Push в ветки `main` или `develop`
- Создании Pull Request в `main` или `develop`

Workflow: `.github/workflows/tests.yml`

Каждый сервис тестируется независимо с:
- Отдельной базой данных PostgreSQL
- Отдельным экземпляром Redis
- Изолированным окружением

### Автоматический деплой

Деплой выполняется автоматически при push в ветку `main`:
1. Сборка Docker-образов для всех сервисов
2. Push образов в GitHub Container Registry
3. Сканирование безопасности с Trivy
4. Деплой в production (если настроен)

Workflow: `.github/workflows/deploy.yml`

### Просмотр результатов

1. Перейдите во вкладку **Actions** вашего GitHub репозитория
2. Выберите нужный workflow run
3. Просмотрите логи каждого job

## Структура тестов

### User Service
- `UserModelTest` - тесты модели User
- `UserProfileModelTest` - тесты модели UserProfile
- `UserAPITest` - тесты API (регистрация, логин, аутентификация)

### Product Service
- `CategoryModelTest` - тесты модели Category (slug generation)
- `ProductModelTest` - тесты модели Product (stock tracking)
- `ProductAPITest` - тесты API (CRUD, фильтрация, поиск)
- `CategoryAPITest` - тесты API категорий

### Cart Service
- `CartModelTest` - тесты модели Cart
- `CartItemModelTest` - тесты модели CartItem
- `CartAPITest` - тесты API (add, update, remove, clear)

### Order Service
- `OrderModelTest` - тесты модели Order
- `OrderItemModelTest` - тесты модели OrderItem
- `OrderAPITest` - тесты API (create, update status, cancel)

### Currency Service
- `CurrencyModelTest` - тесты модели Currency
- `ExchangeRateModelTest` - тесты модели ExchangeRate
- `CurrencyAPITest` - тесты API валют
- `ExchangeRateAPITest` - тесты API конвертации (прямая, обратная, треугольная)

### Discount Service
- `HolidayModelTest` - тесты модели Holiday
- `DiscountModelTest` - тесты модели Discount
- `DiscountCodeModelTest` - тесты модели DiscountCode
- `HolidayAPITest` - тесты API праздников
- `DiscountAPITest` - тесты API скидок
- `DiscountCodeAPITest` - тесты API промокодов

## Настройка секретов для GitHub Actions

### Для деплоя необходимо настроить секреты:

1. Перейдите в **Settings** → **Secrets and variables** → **Actions**
2. Добавьте следующие секреты:

```
DEPLOY_SSH_KEY - SSH ключ для доступа к серверу деплоя
DEPLOY_HOST - IP или домен сервера
DEPLOY_USER - Пользователь для SSH
```

### Для Container Registry:

GitHub автоматически использует `GITHUB_TOKEN` для push в GitHub Container Registry.

## Отладка проблем

### Тесты падают локально

1. Проверьте, что PostgreSQL запущен:
```bash
pg_isready
```

2. Проверьте, что Redis запущен:
```bash
redis-cli ping
```

3. Убедитесь, что база данных создана:
```bash
psql -U shop_user -c "CREATE DATABASE test_db;"
```

### Тесты падают в CI

1. Проверьте логи в GitHub Actions
2. Убедитесь, что все зависимости указаны в `requirements.txt`
3. Проверьте переменные окружения в workflow

### Проблемы с покрытием кода

```bash
# Установите coverage
pip install coverage

# Запустите с подробным выводом
coverage run --source='.' manage.py test -v 2
coverage report -m
```

## Best Practices

1. **Изоляция тестов** - каждый тест должен быть независимым
2. **Использование setUp/tearDown** - для подготовки тестовых данных
3. **Именование тестов** - `test_<что_тестируется>_<ожидаемый_результат>`
4. **Покрытие edge cases** - тестируйте граничные случаи и ошибки
5. **Mock внешних сервисов** - используйте моки для изоляции

## Дополнительные инструменты

### pytest (альтернатива Django test runner)

```bash
pip install pytest pytest-django
pytest
```

### Линтеры

```bash
pip install flake8 black
flake8 .
black --check .
```

### Type checking

```bash
pip install mypy django-stubs
mypy .
```

## Контакты

При возникновении проблем создайте issue в репозитории.
