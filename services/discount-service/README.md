# Микросервис системы скидок

## Описание

Discount Service - микросервис для управления скидками на праздники и промокодами.

## Возможности

### 1. Праздничные скидки
- Автоматические скидки на определенные праздники
- Поддержка популярных праздников (Новый Год, Черная Пятница, День Святого Валентина и др.)
- Настройка периода действия скидки
- Настройка процента скидки (0-100%)

### 2. Промокоды
- Создание промокодов с уникальными кодами
- Ограничение количества использований
- Установка минимальной суммы покупки
- Период действия промокода

### 3. Скидки на товары
- Привязка скидок к конкретным товарам
- Автоматический расчет цены со скидкой
- Управление активностью скидок

## API Endpoints

### Праздники

**GET /api/discounts/holidays/**
- Список всех праздников

**GET /api/discounts/holidays/active/**
- Активные праздники на данный момент

**GET /api/discounts/holidays/upcoming/**
- Предстоящие праздники (следующие 5)

**POST /api/discounts/holidays/**
```json
{
  "name": "Новый Год 2026",
  "holiday_type": "new_year",
  "start_date": "2025-12-25T00:00:00Z",
  "end_date": "2026-01-10T23:59:59Z",
  "discount_percentage": 25.00,
  "description": "Новогодняя распродажа"
}
```

### Скидки на товары

**GET /api/discounts/products/**
- Список всех скидок

**GET /api/discounts/products/by_product/?product_id=123**
- Получить активные скидки для товара

**POST /api/discounts/products/calculate/**
```json
{
  "product_id": 123,
  "original_price": 1000.00
}
```
Ответ:
```json
{
  "product_id": 123,
  "original_price": 1000.00,
  "discounted_price": 750.00,
  "discount_percentage": 25.00,
  "holiday": "Новый Год 2026"
}
```

### Промокоды

**POST /api/discounts/codes/validate_code/**
```json
{
  "code": "WINTER2026"
}
```

**POST /api/discounts/codes/apply/**
```json
{
  "code": "WINTER2026",
  "total_amount": 5000.00
}
```
Ответ:
```json
{
  "success": true,
  "code": "WINTER2026",
  "original_amount": 5000.00,
  "discount_amount": 500.00,
  "final_amount": 4500.00,
  "discount_percentage": 10.00
}
```

## Модели данных

### Holiday (Праздник)
- **name** - название праздника
- **holiday_type** - тип (new_year, black_friday, valentines, и др.)
- **start_date** - дата начала
- **end_date** - дата окончания
- **discount_percentage** - процент скидки (0-100)
- **is_active** - активен ли праздник

### Discount (Скидка на товар)
- **product_id** - ID товара из product-service
- **holiday** - связанный праздник
- **original_price** - оригинальная цена
- **discounted_price** - цена со скидкой (рассчитывается автоматически)
- **is_active** - активна ли скидка

### DiscountCode (Промокод)
- **code** - уникальный код промокода
- **discount_percentage** - процент скидки
- **valid_from** - действителен с
- **valid_to** - действителен до
- **usage_limit** - лимит использований (опционально)
- **usage_count** - количество использований
- **min_purchase_amount** - минимальная сумма покупки
- **is_active** - активен ли промокод

## Доступ

**URL:** http://localhost:8005
**Админка:** http://localhost:8005/admin/
**Логин:** admin
**Пароль:** admin

## Через API Gateway

Все запросы доступны через API Gateway:
**URL:** http://localhost:8000/api/discounts/...

## Примеры использования

### Создать праздник "Черная Пятница"
```bash
curl -X POST http://localhost:8000/api/discounts/holidays/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Черная Пятница 2025",
    "holiday_type": "black_friday",
    "start_date": "2025-11-28T00:00:00Z",
    "end_date": "2025-11-30T23:59:59Z",
    "discount_percentage": 50.00,
    "description": "Мега распродажа!"
  }'
```

### Создать промокод
```bash
curl -X POST http://localhost:8000/api/discounts/codes/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SAVE20",
    "discount_percentage": 20.00,
    "valid_from": "2025-12-01T00:00:00Z",
    "valid_to": "2025-12-31T23:59:59Z",
    "min_purchase_amount": 1000.00,
    "usage_limit": 100
  }'
```

### Проверить промокод
```bash
curl -X POST http://localhost:8000/api/discounts/codes/validate_code/ \
  -H "Content-Type: application/json" \
  -d '{"code": "SAVE20"}'
```

## Интеграция с другими сервисами

Discount Service может быть интегрирован с:
- **Product Service** - для получения информации о товарах
- **Cart Service** - для применения скидок в корзине
- **Order Service** - для применения промокодов при оформлении заказа

## База данных

Использует PostgreSQL (база `discount_db`), все миграции применяются автоматически при запуске.

## Типы праздников

- `new_year` - Новый Год
- `christmas` - Рождество
- `easter` - Пасха
- `black_friday` - Черная Пятница
- `valentines` - День Святого Валентина
- `womens_day` - Международный Женский День
- `cyber_monday` - Киберпонедельник
- `summer_sale` - Летняя Распродажа
- `custom` - Кастомный Праздник
