# 🏗️ Архитектура проекта в Docker

## Общая схема

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Docker Host (Windows)                      │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │           Docker Network: shop-network                     │   │
│  │                                                            │   │
│  │  ┌───────────┐                                            │   │
│  │  │  Browser  │                                            │   │
│  │  │   :3000   │◄──── http://localhost:3000                │   │
│  │  └─────┬─────┘                                            │   │
│  │        │                                                   │   │
│  │        ▼                                                   │   │
│  │  ┌──────────────┐                                         │   │
│  │  │   Frontend   │  Vue.js 3 + Vite                        │   │
│  │  │  Container   │  Port: 3000                             │   │
│  │  │              │  Image: node:18-alpine                  │   │
│  │  └──────┬───────┘                                         │   │
│  │         │                                                  │   │
│  │         │ HTTP Proxy /api → api-gateway:8000             │   │
│  │         ▼                                                  │   │
│  │  ┌──────────────┐                                         │   │
│  │  │ API Gateway  │  Django REST Framework                  │   │
│  │  │  Container   │  Port: 8000                             │   │
│  │  │              │  • Rate Limiting                        │   │
│  │  │              │  • Request Routing                      │   │
│  │  │              │  • CORS Handling                        │   │
│  │  └──────┬───────┘                                         │   │
│  │         │                                                  │   │
│  │    ┌────┴────┬──────────┬──────────┬──────────┐          │   │
│  │    │         │          │          │          │           │   │
│  │    ▼         ▼          ▼          ▼          ▼           │   │
│  │  ┌────┐  ┌────────┐ ┌──────┐  ┌──────┐  ┌───────┐       │   │
│  │  │User│  │Product │ │ Cart │  │Order │  │ Redis │       │   │
│  │  │Svc │  │Service │ │ Svc  │  │ Svc  │  │       │       │   │
│  │  │8004│  │  8001  │ │ 8002 │  │ 8003 │  │ 6379  │       │   │
│  │  └─┬──┘  └───┬────┘ └──┬───┘  └──┬───┘  └───┬───┘       │   │
│  │    │         │         │         │          │            │   │
│  │    │         │         │         │          │            │   │
│  │    │         │         └─────────┼──────────┤            │   │
│  │    │         │                   │      Pub/Sub Events   │   │
│  │    │         │                   │                        │   │
│  │    ▼         ▼                   ▼                        │   │
│  │  ┌────┐  ┌────────┐          ┌──────┐                   │   │
│  │  │user│  │product │          │order │                   │   │
│  │  │-db │  │  -db   │          │ -db  │                   │   │
│  │  └────┘  └────────┘          └──────┘                   │   │
│  │  Volume   Volume              Volume                     │   │
│  │                                                           │   │
│  │  ┌────────┐                                              │   │
│  │  │cart-db │                                              │   │
│  │  └────────┘                                              │   │
│  │   Volume                                                  │   │
│  │                                                           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Exposed Ports:                                                  │
│  • 3000  → Frontend                                              │
│  • 8000  → API Gateway                                           │
│  • 8001  → Product Service                                       │
│  • 8002  → Cart Service                                          │
│  • 8003  → Order Service                                         │
│  • 8004  → User Service                                          │
│  • 6379  → Redis                                                 │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Взаимодействие сервисов

### 1. Аутентификация пользователя

```
Frontend → API Gateway → User Service
                          ↓
                      user-db (JWT token)
                          ↓
Frontend ← API Gateway ← User Service (access + refresh token)
```

### 2. Получение списка товаров

```
Frontend → API Gateway → Product Service
                          ↓
                      product-db (SELECT)
                          ↓
Frontend ← API Gateway ← Product Service (JSON)
```

### 3. Добавление товара в корзину

```
Frontend → API Gateway → Cart Service
                          ↓
                     [HTTP Request]
                          ↓
                    Product Service → product-db (check availability)
                          ↓
                    Cart Service → cart-db (INSERT)
                          ↓
Frontend ← API Gateway ← Cart Service (updated cart)
```

### 4. Создание заказа (сложный поток)

```
Frontend → API Gateway → Order Service
                          ↓
                     ┌────┴────┐
                     │         │
                [HTTP]     [HTTP]
                     │         │
                     ▼         ▼
               Cart Service  User Service
                     │         │
               cart-db     user-db
                     │         │
                     └────┬────┘
                          ▼
                    Order Service
                          ↓
                   [HTTP Request]
                          ↓
                   Product Service → reserve items
                          ↓
                    Order Service
                          │
                    ┌─────┴─────┐
                    │           │
              order-db      Redis Pub/Sub
             (CREATE)      (publish "order.created")
                    │           │
                    │           └─────────┐
                    │                     ▼
                    │               Cart Service
                    │              (subscribe → clear cart)
                    │
                    ▼
Frontend ← API Gateway ← Order Service (order details)
```

### 5. Отмена заказа

```
Frontend → API Gateway → Order Service
                          ↓
                    order-db (UPDATE status)
                          ↓
                    Redis Pub/Sub
                  (publish "order.cancelled")
                          ↓
                    Product Service
                   (subscribe → restore stock)
                          ↓
                    product-db (UPDATE quantity)
                          ↓
Frontend ← API Gateway ← Order Service (confirmation)
```

## Технологический стек каждого контейнера

### Frontend Container
- **Base Image:** `node:18-alpine`
- **Framework:** Vue.js 3
- **Build Tool:** Vite
- **State Management:** Pinia
- **HTTP Client:** Axios
- **Router:** Vue Router

### API Gateway Container
- **Base Image:** `python:3.11-slim`
- **Framework:** Django 5.2
- **Features:**
  - Request proxying
  - Rate limiting (100 req/min)
  - CORS handling
  - Redis caching

### User Service Container
- **Base Image:** `python:3.11-slim`
- **Framework:** Django 5.2 + DRF
- **Auth:** JWT (simplejwt)
- **DB:** SQLite (user.db)
- **Features:**
  - User registration
  - Login/logout
  - Profile management
  - Token refresh

### Product Service Container
- **Base Image:** `python:3.11-slim`
- **Framework:** Django 5.2 + DRF
- **DB:** SQLite (product.db)
- **Features:**
  - Product CRUD
  - Category management
  - Stock management
  - Search & filtering
  - Event listening (order.cancelled)

### Cart Service Container
- **Base Image:** `python:3.11-slim`
- **Framework:** Django 5.2 + DRF
- **DB:** SQLite (cart.db)
- **Features:**
  - Add/remove items
  - Update quantities
  - Calculate totals
  - Event listening (order.created)

### Order Service Container
- **Base Image:** `python:3.11-slim`
- **Framework:** Django 5.2 + DRF
- **DB:** SQLite (order.db)
- **Features:**
  - Create orders
  - Order status management
  - Event publishing (order.created, order.cancelled)
  - Transaction management

### Redis Container
- **Base Image:** `redis:7-alpine`
- **Purpose:**
  - Event bus (Pub/Sub)
  - Rate limiting cache
  - Session storage (future)

## Docker Volumes

```
┌─────────────────────────────────────────┐
│         Docker Host Filesystem          │
│                                          │
│  /var/lib/docker/volumes/                │
│                                          │
│  ├── user-db/                            │
│  │   └── _data/                          │
│  │       └── user.db         ← SQLite    │
│  │                                        │
│  ├── product-db/                         │
│  │   └── _data/                          │
│  │       └── product.db      ← SQLite    │
│  │                                        │
│  ├── cart-db/                            │
│  │   └── _data/                          │
│  │       └── cart.db         ← SQLite    │
│  │                                        │
│  └── order-db/                           │
│      └── _data/                          │
│          └── order.db        ← SQLite    │
│                                          │
└──────────────────────────────────────────┘

Volumes сохраняются при:
✅ docker-compose restart
✅ docker-compose down
✅ docker-compose up

Volumes удаляются при:
❌ docker-compose down -v
```

## Сетевая конфигурация

```
shop-network (bridge driver)
│
├── shop-frontend        (172.18.0.2)
├── shop-api-gateway     (172.18.0.3)
├── shop-user-service    (172.18.0.4)
├── shop-product-service (172.18.0.5)
├── shop-cart-service    (172.18.0.6)
├── shop-order-service   (172.18.0.7)
└── shop-redis           (172.18.0.8)

Каждый контейнер может обращаться к другому по имени:
• http://user-service:8004
• http://product-service:8001
• redis://redis:6379
```

## Порядок запуска (dependencies)

```
1. Redis (healthcheck)
   ↓
2. User Service, Product Service (parallel)
   ↓
3. Cart Service (depends on User + Product)
   ↓
4. Order Service (depends on all above)
   ↓
5. API Gateway (depends on all microservices)
   ↓
6. Frontend (depends on API Gateway)
```

## Переменные окружения

### Общие для всех Python сервисов
```bash
REDIS_HOST=redis
REDIS_PORT=6379
DJANGO_SETTINGS_MODULE=config.settings
DEBUG=True
```

### Service URLs (для межсервисного взаимодействия)
```bash
USER_SERVICE_URL=http://user-service:8004
PRODUCT_SERVICE_URL=http://product-service:8001
CART_SERVICE_URL=http://cart-service:8002
ORDER_SERVICE_URL=http://order-service:8003
```

### Frontend
```bash
VITE_API_URL=http://api-gateway:8000
```

---

**Все контейнеры взаимодействуют через внутреннюю Docker сеть, а пользователь обращается к ним через проброшенные порты на localhost.**
