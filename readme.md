# Microservices Shop

Современный интернет-магазин, построенный на микросервисной архитектуре с использованием Django, Vue.js и Docker.

## 📋 Содержание

- [Обзор](#обзор)
- [Архитектура](#архитектура)
- [Микросервисы](#микросервисы)
- [Технологии](#технологии)
- [Быстрый старт](#быстрый-старт)
- [Тестирование](#тестирование)
- [Деплой](#деплой)
- [API документация](#api-документация)

## 🎯 Обзор

Полнофункциональный интернет-магазин с:
- ✅ Регистрацией и аутентификацией пользователей (JWT)
- ✅ Каталогом товаров с поиском и фильтрацией
- ✅ Корзиной покупок
- ✅ Системой заказов
- ✅ Конвертацией валют (7 валют)
- ✅ Системой скидок и промокодов
- ✅ Event-driven архитектурой (Redis)
- ✅ CI/CD с GitHub Actions
- ✅ Юнит-тестами для всех сервисов

## 🏗️ Архитектура

```
┌─────────────┐
│   Frontend  │ (Vue.js + Vite)
│   Port 3000 │
└──────┬──────┘
       │
┌──────▼──────────┐
│   API Gateway   │ (Django + Middleware)
│    Port 8000    │
└──────┬──────────┘
       │
       ├─────────────────────────────────────────┐
       │                                         │
┌──────▼────────┐  ┌──────────────┐  ┌─────────▼────────┐
│ User Service  │  │Cart Service  │  │Product Service   │
│   Port 8004   │  │  Port 8002   │  │   Port 8001      │
└───────────────┘  └──────────────┘  └──────────────────┘
       │                  │                    │
┌──────▼────────┐  ┌──────▼──────┐  ┌─────────▼────────┐
│Order Service  │  │Currency Svc │  │ Discount Service │
│  Port 8003    │  │ Port 8006   │  │   Port 8005      │
└───────────────┘  └─────────────┘  └──────────────────┘
       │                                       │
       └───────────────┬───────────────────────┘
                       │
            ┌──────────▼──────────┐
            │    PostgreSQL       │
            │     Port 5432       │
            └─────────────────────┘
                       │
            ┌──────────▼──────────┐
            │      Redis          │
            │     Port 6379       │
            └─────────────────────┘
```

## 🔧 Микросервисы

### 1. **User Service** (Port 8004)
- Регистрация и аутентификация
- JWT токены
- Профили пользователей
- REST API: `/api/users/`, `/api/auth/`

### 2. **Product Service** (Port 8001)
- Управление товарами и категориями
- Поиск и фильтрация
- Обработка событий из Discount Service
- REST API: `/api/products/`, `/api/categories/`

### 3. **Cart Service** (Port 8002)
- Корзина покупок
- Добавление/удаление товаров
- Расчет стоимости
- REST API: `/api/cart/`

### 4. **Order Service** (Port 8003)
- Создание заказов
- Управление статусами
- История заказов
- REST API: `/api/orders/`

### 5. **Currency Service** (Port 8006)
- 7 валют (USD, EUR, GBP, RUB, JPY, CNY, UAH)
- Прямая, обратная и треугольная конвертация
- Управление курсами обмена
- REST API: `/api/currencies/`, `/api/exchange-rates/`

### 6. **Discount Service** (Port 8005)
- Праздничные скидки
- Промокоды
- Автоматический расчет цен
- REST API: `/api/holidays/`, `/api/discounts/`, `/api/discount-codes/`

### 7. **API Gateway** (Port 8000)
- Единая точка входа
- Маршрутизация запросов
- JWT аутентификация middleware
- Проксирование в микросервисы

### 8. **Frontend** (Port 3000)
- Vue 3 + Vite
- Pinia для state management
- Vue Router для навигации
- Axios для HTTP запросов

## 💻 Технологии

### Backend
- **Python 3.11**
- **Django 5.2.5**
- **Django REST Framework 3.15.2**
- **PostgreSQL 15**
- **Redis 7**
- **JWT Authentication**

### Frontend
- **Vue.js 3.5.13**
- **Vite 6.0.3**
- **Pinia** (state management)
- **Vue Router**
- **Axios**

### DevOps
- **Docker & Docker Compose**
- **GitHub Actions** (CI/CD)
- **Trivy** (security scanning)

## 🚀 Быстрый старт

### Предварительные требования
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd microservices-shop-master
```

2. **Создайте `.env` файл:**
```bash
cp .env.example .env
```

Отредактируйте `.env`:
```env
POSTGRES_USER=shop_user
POSTGRES_PASSWORD=shop_password
POSTGRES_DB=shop_db
REDIS_HOST=redis
REDIS_PORT=6379
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

3. **Запустите все сервисы:**
```bash
docker-compose up -d
```

4. **Проверьте статус:**
```bash
docker-compose ps
```

5. **Откройте браузер:**
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000

### Первоначальная настройка

Создайте суперпользователя:
```bash
docker-compose exec user-service python manage.py createsuperuser
```

Загрузите тестовые данные:
```bash
docker-compose exec currency-service python manage.py loaddata initial_currencies
docker-compose exec product-service python manage.py loaddata initial_categories
```

## 🧪 Тестирование

Проект содержит **43 юнит-теста** для 6 микросервисов.

### Запуск всех тестов локально

```bash
# User Service
cd services/user-service && python manage.py test

# Product Service
cd services/product-service && python manage.py test

# Cart Service
cd services/cart-service && python manage.py test

# Order Service
cd services/order-service && python manage.py test

# Currency Service
cd services/currency-service && python manage.py test

# Discount Service
cd services/discount-service && python manage.py test
```

### CI/CD с GitHub Actions

Тесты запускаются автоматически при:
- Push в `main` или `develop`
- Pull Request в `main` или `develop`

Каждый сервис тестируется независимо с отдельной БД и Redis.

📖 **Подробная документация:** [TESTING.md](TESTING.md)

## 🌐 Деплой

### Локальный деплой

```bash
docker-compose up -d
```

### Production деплой

1. **GitHub Actions автоматически:**
   - Собирает Docker образы
   - Сканирует на уязвимости (Trivy)
   - Пушит в GitHub Container Registry
   - Деплоит на сервер (если настроен)

2. **Ручной деплой:**
```bash
# Pull образы из registry
docker pull ghcr.io/YOUR_USERNAME/microservices-shop/user-service:latest

# Запуск с production настройками
docker-compose -f docker-compose.prod.yml up -d
```

📖 **Подробная документация:** [DEPLOYMENT.md](DEPLOYMENT.md)

## 📚 API Документация

### Authentication

```bash
# Регистрация
POST /api/auth/register/
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}

# Логин
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "password123"
}
# Response: { "access": "...", "refresh": "..." }
```

### Products

```bash
# Список товаров
GET /api/products/

# Поиск
GET /api/products/?search=laptop

# Фильтр по категории
GET /api/products/?category=1

# Детали товара
GET /api/products/1/
```

### Cart

```bash
# Корзина пользователя
GET /api/cart/

# Добавить в корзину
POST /api/cart/items/
{
  "product_id": 1,
  "quantity": 2
}

# Обновить количество
PATCH /api/cart/items/1/
{
  "quantity": 3
}

# Удалить из корзины
DELETE /api/cart/items/1/

# Очистить корзину
POST /api/cart/clear/
```

### Orders

```bash
# Создать заказ
POST /api/orders/
{
  "shipping_address": "123 Main St",
  "payment_method": "card"
}

# История заказов
GET /api/orders/

# Детали заказа
GET /api/orders/1/

# Отменить заказ
POST /api/orders/1/cancel/
```

### Currency

```bash
# Список валют
GET /api/currencies/

# Конвертация
POST /api/exchange-rates/convert/
{
  "from_currency": "USD",
  "to_currency": "EUR",
  "amount": 100
}
```

### Discounts

```bash
# Активные праздничные скидки
GET /api/holidays/active/

# Проверить промокод
POST /api/discount-codes/validate/
{
  "code": "SUMMER2024",
  "order_amount": 100.00
}

# Применить промокод
POST /api/discount-codes/apply/
{
  "code": "SUMMER2024",
  "order_amount": 100.00
}
```

## 🔐 Безопасность

- ✅ JWT аутентификация
- ✅ CORS настроен
- ✅ Environment variables для секретов
- ✅ Trivy security scanning в CI
- ✅ Django security middleware
- ✅ PostgreSQL с аутентификацией

## 📊 Мониторинг

### Логи

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f user-service

# Последние 100 строк
docker-compose logs --tail=100 user-service
```

### Health checks

```bash
# User Service
curl http://localhost:8004/health/

# Product Service
curl http://localhost:8001/health/

# API Gateway
curl http://localhost:8000/health/
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📝 Лицензия

Этот проект распространяется под лицензией MIT.

## 📧 Контакты

При возникновении вопросов создайте issue в репозитории.

---

**Статус проекта:** ✅ Production Ready

**Версия:** 1.0.0

**Последнее обновление:** 2024


Отлично! Теперь у меня есть полное понимание проекта. Составлю подробное описание.

# 📋 Полное описание проекта Microservices Shop

## 🏗️ Архитектура проекта

Это **e-commerce приложение**, построенное на **микросервисной архитектуре** с использованием:
- **Backend**: Django REST Framework (Python)
- **Frontend**: Vue.js 3 + Vite
- **Межсервисное взаимодействие**: Redis Pub/Sub + HTTP REST API
- **Базы данных**: SQLite (для каждого микросервиса своя БД)
- **Контейнеризация**: Docker + Docker Compose

---

## 🐳 Быстрый запуск с Docker (РЕКОМЕНДУЕТСЯ)

### Предварительные требования
- Docker Desktop установлен и запущен

### Запуск проекта

```powershell
# 1. Автоматическая инициализация (создание БД, администратора)
.\init.ps1

# ИЛИ вручную:

# 2. Запуск всех сервисов
docker-compose up -d --build

# 3. Просмотр логов
docker-compose logs -f
```

### Доступ к приложению
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Админ**: admin@shop.com / admin123

📖 **Подробная документация**: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

---

## 💻 Локальный запуск (без Docker)

## 🔧 Компоненты системы

### 1️⃣ **API Gateway** (порт 8000)

**Назначение**: Единая точка входа для всех клиентских запросов

**Ключевые файлы**:

#### settings.py
```python
MICROSERVICES = {
    'user-service': 'http://localhost:8004',
    'product-service': 'http://localhost:8001',
    'cart-service': 'http://localhost:8002',
    'order-service': 'http://localhost:8003',
}
RATE_LIMIT_REQUESTS_PER_MINUTE = 100
```
- Конфигурация адресов всех микросервисов
- Настройка CORS для взаимодействия с фронтендом
- Лимит запросов: 100 запросов/минуту

#### views.py
**Класс `ProxyView`** - главный механизм маршрутизации:

1. **Определение сервиса** (`get_service_name`):
   - `/api/auth/`, `/api/users/` → user-service
   - `/api/products/`, `/api/categories/` → product-service
   - `/api/cart/` → cart-service
   - `/api/orders/` → order-service

2. **Проксирование запроса** (`proxy_request`):
   - Копирует заголовки (Authorization, Content-Type)
   - Пересылает тело запроса (JSON)
   - Возвращает ответ от микросервиса

#### middleware.py
**`RateLimitMiddleware`** - защита от DDoS:
- Использует Redis кеш для подсчета запросов
- Ограничение по IP-адресу
- При превышении лимита → HTTP 429 (Too Many Requests)
- Добавляет заголовки `X-RateLimit-Limit` и `X-RateLimit-Remaining`

---

### 2️⃣ **User Service** (порт 8004)

**Назначение**: Управление пользователями и аутентификация

**База данных**: user.db

#### models.py
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'  # Вход по email, не username
    
class UserProfile(models.Model):
    user = OneToOneField(User)
    phone = CharField(max_length=20)
    address = TextField()
    date_of_birth = DateField()
```
- Кастомная модель пользователя с email в качестве логина
- Профиль с дополнительной информацией

#### views.py

**`login_view`**:
```python
# Принимает: {"email": "...", "password": "..."}
# Возвращает: {"access": "JWT...", "refresh": "JWT...", "user": {...}}
```
- Использует JWT токены (библиотека `simplejwt`)
- Access token живет 60 минут
- Refresh token живет 7 дней

**`refresh_token`**:
- Обновление access token через refresh token

**Настройки JWT** (settings.py):
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

---

### 3️⃣ **Product Service** (порт 8001)

**Назначение**: Управление каталогом товаров

**База данных**: product.db

#### models.py

**`Category`**:
```python
name = CharField(max_length=100, unique=True)
slug = SlugField()  # Автоматически генерируется из name
```

**`Product`**:
```python
name = CharField(max_length=200)
price = DecimalField(max_digits=10, decimal_places=2)
category = ForeignKey(Category)
stock_quantity = IntegerField(default=0)
image_url = URLField()
is_active = BooleanField(default=True)
```

**Методы управления запасами**:
- `reserve_quantity(quantity)` - резервирует товар при заказе
- `release_quantity(quantity)` - возвращает товар при отмене заказа

#### views.py

**`ProductListView`**:
- Фильтрация: по категории, цене (min/max), наличию
- Поиск: по названию и описанию
- Сортировка: по имени, цене, дате создания

**`reserve_product`** (POST `/api/products/{id}/reserve/`):
```python
# Запрос: {"quantity": 2}
# Ответ: {"success": true, "remaining_stock": 8}
```

**`release_product`** (POST `/api/products/{id}/release/`):
- Восстанавливает запасы после отмены заказа

#### event_handlers.py
**Слушатель событий Redis**:
```python
def handle_event(event_data):
    if event_type == 'order.cancelled':
        # Восстанавливаем товары при отмене заказа
        for item in order_items:
            product.release_quantity(item['quantity'])
```
- Подписывается на канал `events` в Redis
- Реагирует на события `order.cancelled`
- Работает в фоновом потоке

---

### 4️⃣ **Cart Service** (порт 8002)

**Назначение**: Управление корзиной покупок

**База данных**: cart.db

#### models.py

**`Cart`**:
```python
user_id = IntegerField(unique=True)  # Связь с user-service
total_amount = @property  # Автоматически рассчитывается
total_items = @property   # Общее количество товаров
```

**`CartItem`**:
```python
cart = ForeignKey(Cart, related_name='items')
product_id = IntegerField()  # ID из product-service
quantity = PositiveIntegerField(default=1)
price = DecimalField()        # Цена на момент добавления
product_name = CharField()    # Кеш названия
```
- `unique_together = ['cart', 'product_id']` - один товар только раз в корзине

#### services.py

**`ProductService`**:
```python
get_product(product_id) → Dict
    # Запрос к product-service за информацией о товаре
    
check_availability(product_id, quantity) → bool
    # Проверка наличия товара на складе
```

**`UserService`**:
```python
get_user_from_token(token) → Dict
    # Получение профиля пользователя из user-service
```

#### event_handlers.py
**Слушатель событий**:
```python
def handle_event(event_data):
    if event_type == 'order.created':
        # Очищаем корзину после оформления заказа
        cart = Cart.objects.get(user_id=user_id)
        cart.clear()
```
- Реагирует на событие `order.created`
- Автоматически очищает корзину после создания заказа

---

### 5️⃣ **Order Service** (порт 8003)

**Назначение**: Управление заказами

**База данных**: order.db

#### models.py

**`Order`**:
```python
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]
user_id = IntegerField()
status = CharField(choices=STATUS_CHOICES, default='pending')
total_amount = DecimalField()
shipping_address = TextField()
user_email = EmailField()
user_name = CharField()
```

**`OrderItem`**:
```python
order = ForeignKey(Order, related_name='items')
product_id = IntegerField()
product_name = CharField()  # Кеш названия
quantity = PositiveIntegerField()
price = DecimalField()      # Цена на момент заказа
```

#### views.py

**`create_order`** - сложный процесс создания заказа:

```python
@transaction.atomic  # Все или ничего
def create_order(request):
    # 1. Получаем корзину через CartService
    cart_data = CartService.get_user_cart(user_id, token)
    
    # 2. Получаем профиль пользователя через UserService
    user_data = UserService.get_user_from_token(token)
    
    # 3. Резервируем товары через ProductService
    ProductService.reserve_products(items_to_reserve)
    
    # 4. Создаем заказ
    order = Order.objects.create(...)
    
    # 5. Создаем позиции заказа
    for item in cart_data['items']:
        OrderItem.objects.create(...)
    
    # 6. Публикуем событие 'order.created' в Redis
    event_bus.publish('order.created', {...})
    
    # 7. Возвращаем данные заказа
```

**Обработка ошибок**:
- Если резервирование не удалось → откатываем транзакцию
- Товары не списываются, заказ не создается

---

### 6️⃣ **Shared Utilities** (utils.py)

**Общий код для всех микросервисов**

#### `EventBus` - система событий

**Публикация событий**:
```python
EventBus.publish('order.created', {
    'order_id': 123,
    'user_id': 456,
    'items': [...]
})
```
- Публикует в Redis канал `events`
- Формат: `{type, data, timestamp}`

**Подписка на события**:
```python
EventBus.subscribe(callback_function)
```
- Слушает канал `events`
- Вызывает callback для каждого события

#### `ServiceCommunication` - HTTP взаимодействие

```python
ServiceCommunication.make_request(
    service='product-service',
    endpoint='/api/products/1/',
    method='GET',
    headers={'Authorization': 'Bearer ...'}
)
```
- Централизованная логика HTTP-запросов между сервисами
- Обработка ошибок и таймаутов

---

### 7️⃣ **Frontend** (Vue.js 3)

**Порт**: 3000 (dev server)

#### **Технологический стек**:
- **Vue 3** - фреймворк
- **Vue Router** - маршрутизация
- **Pinia** - state management (вместо Vuex)
- **Axios** - HTTP клиент
- **Vite** - сборщик и dev server

#### vite.config.js
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // API Gateway
      changeOrigin: true
    }
  }
}
```
- Все запросы `/api/*` проксируются на API Gateway

#### api.js
**Axios interceptor** - автоматическое добавление токена:

```javascript
// Request interceptor
api.interceptors.request.use((config) => {
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

// Response interceptor - обновление токена
api.interceptors.response.use(null, async (error) => {
  if (error.response?.status === 401) {
    // Пробуем обновить токен
    const refreshed = await authStore.refreshAccessToken()
    if (refreshed) {
      // Повторяем запрос с новым токеном
      return api(originalRequest)
    }
    // Logout если обновление не удалось
    authStore.logout()
  }
})
```

#### index.js
**Navigation guards**:
```javascript
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })  // Редирект на login
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'home' })   // Редирект на home
  } else {
    next()
  }
})
```

#### auth.js
**Pinia store для аутентификации**:

```javascript
const token = ref(localStorage.getItem('access_token'))
const refreshToken = ref(localStorage.getItem('refresh_token'))

async function login(credentials) {
  const response = await authService.login(credentials)
  token.value = response.data.access
  localStorage.setItem('access_token', response.data.access)
}

async function refreshAccessToken() {
  const response = await authService.refresh(refreshToken.value)
  token.value = response.data.access
  localStorage.setItem('access_token', response.data.access)
}
```

#### **Страницы** (`src/views/`):
- `HomeView.vue` - главная страница
- `CatalogView.vue` - каталог товаров
- `ProductView.vue` - детали товара
- `CartView.vue` - корзина
- `OrdersView.vue` - список заказов (требует авторизации)
- `OrderDetailView.vue` - детали заказа
- `LoginView.vue` / `RegisterView.vue` - авторизация
- `ProfileView.vue` - профиль пользователя

---

## 🔄 Поток данных в системе

### Пример 1: Создание заказа

```
1. Frontend → API Gateway: POST /api/orders/create
   Headers: Authorization: Bearer JWT_TOKEN
   Body: {shipping_address, customer_info}

2. API Gateway → Order Service: Проксирование запроса
   
3. Order Service:
   a) HTTP → Cart Service: GET /api/cart/ (получить корзину)
   b) HTTP → User Service: GET /api/users/profile/ (получить профиль)
   c) HTTP → Product Service: POST /api/products/reserve/ (зарезервировать товары)
   d) Создать Order и OrderItems в БД
   e) Redis Pub/Sub → Publish 'order.created'
   f) Вернуть данные заказа

4. Cart Service слушает Redis:
   - Получает событие 'order.created'
   - Очищает корзину пользователя

5. Order Service → API Gateway → Frontend: Ответ с данными заказа
```

### Пример 2: Отмена заказа

```
1. Frontend → API Gateway → Order Service: PATCH /api/orders/{id}/
   Body: {status: 'cancelled'}

2. Order Service:
   a) Обновить статус заказа
   b) Redis Pub/Sub → Publish 'order.cancelled' + items[]

3. Product Service слушает Redis:
   - Получает событие 'order.cancelled'
   - Восстанавливает stock_quantity для каждого товара
```

---

## 🔑 Ключевые особенности архитектуры

### ✅ **Преимущества**:

1. **Независимость сервисов**:
   - Каждый микросервис имеет свою БД
   - Можно развертывать и масштабировать отдельно

2. **Event-Driven архитектура**:
   - Redis Pub/Sub для асинхронных событий
   - Слабая связанность между сервисами

3. **API Gateway паттерн**:
   - Единая точка входа
   - Централизованная защита (rate limiting)
   - CORS конфигурация

4. **JWT Authentication**:
   - Stateless токены
   - Refresh token rotation
   - Автоматическое обновление на фронтенде

5. **Транзакционная целостность**:
   - `@transaction.atomic` в критических операциях
   - Откат при ошибках

### ⚠️ **Недостатки текущей реализации**:

1. **Синхронные HTTP вызовы**:
   - Order Service блокируется на время запросов к другим сервисам
   - Если Product Service упадет → заказ не создастся

2. **Отсутствие Circuit Breaker**:
   - Нет механизма защиты от каскадных падений

3. **Нет распределенных транзакций**:
   - Saga pattern не реализован
   - Если резервирование товаров успешно, но БД Order Service упадет → товары останутся зарезервированными

4. **SQLite в production**:
   - Не подходит для высоких нагрузок
   - Нужен PostgreSQL/MySQL

5. **Отсутствие Service Discovery**:
   - Хардкод адресов сервисов в конфигах
   - Нужен Consul/Eureka

---

## 🚀 Как запускается проект

### Backend:
```powershell
# Для каждого микросервиса:
cd services/user-service
python manage.py migrate
python manage.py runserver 8004

cd services/product-service
python manage.py migrate
python manage.py loaddata products.json  # Загрузка тестовых данных
python manage.py runserver 8001

cd services/cart-service
python manage.py migrate
python manage.py runserver 8002

cd services/order-service
python manage.py migrate
python manage.py runserver 8003

cd api-gateway
python manage.py runserver 8000
```

### Frontend:
```powershell
cd frontend
npm install
npm run dev  # Запуск на порту 3000
```

### Redis:
```powershell
redis-server  # Порт 6379
```

---

## 📊 Диаграмма архитектуры

```
┌─────────────┐
│   Browser   │
│  (Vue.js)   │
└──────┬──────┘
       │ HTTP /api/*
       ▼
┌─────────────────┐
│  API Gateway    │ ◄─── Rate Limiting Middleware
│   (Port 8000)   │ ◄─── CORS Configuration
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│  User  │ │Product │ │  Cart  │ │ Order  │
│Service │ │Service │ │Service │ │Service │
│ :8004  │ │ :8001  │ │ :8002  │ │ :8003  │
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    │          │          │          │
    ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│user.db │ │prod.db │ │cart.db │ │order.db│
└────────┘ └────────┘ └────────┘ └────────┘
    │          │          │          │
    └──────────┴──────────┴──────────┘
                   │
              ┌────▼────┐
              │  Redis  │ ◄─── Event Bus
              │ Pub/Sub │      (order.created, order.cancelled)
              └─────────┘
```

---

Это полноценная микросервисная архитектура e-commerce приложения с разделением ответственности, событийно-ориентированным взаимодействием и современным фронтендом на Vue.js 3.