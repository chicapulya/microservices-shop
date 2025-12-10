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

# Создание суперпользователей для всех сервисов
Write-Host "👤 Создание администраторов для всех сервисов..." -ForegroundColor Yellow

# User Service - суперпользователь
$createUserScript = @"
from apps.users.models import User
if not User.objects.filter(email='admin@shop.com').exists():
    User.objects.create_superuser(
        email='admin@shop.com',
        password='admin123',
        username='admin'
    )
    print('User Service: Администратор создан')
else:
    print('User Service: Администратор уже существует')
"@
$createUserScript | docker-compose exec -T user-service python manage.py shell

# Product Service - суперпользователь
$createProductAdminScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shop.com', 'admin123')
    print('Product Service: Администратор создан')
else:
    print('Product Service: Администратор уже существует')
"@
$createProductAdminScript | docker-compose exec -T product-service python manage.py shell

# Cart Service - суперпользователь
$createCartAdminScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shop.com', 'admin123')
    print('Cart Service: Администратор создан')
else:
    print('Cart Service: Администратор уже существует')
"@
$createCartAdminScript | docker-compose exec -T cart-service python manage.py shell

# Order Service - суперпользователь
$createOrderAdminScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shop.com', 'admin123')
    print('Order Service: Администратор создан')
else:
    print('Order Service: Администратор уже существует')
"@
$createOrderAdminScript | docker-compose exec -T order-service python manage.py shell

# Currency Service - суперпользователь
$createCurrencyAdminScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shop.com', 'admin123')
    print('Currency Service: Администратор создан')
else:
    print('Currency Service: Администратор уже существует')
"@
$createCurrencyAdminScript | docker-compose exec -T currency-service python manage.py shell

# Discount Service - суперпользователь
$createDiscountAdminScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shop.com', 'admin123')
    print('Discount Service: Администратор создан')
else:
    print('Discount Service: Администратор уже существует')
"@
$createDiscountAdminScript | docker-compose exec -T discount-service python manage.py shell

# Создание валют
Write-Host "💱 Создание списка валют..." -ForegroundColor Yellow
$createCurrenciesScript = @"
from apps.currency.models import Currency, ExchangeRate

# Создание валют
currencies_data = [
    {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
    {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
    {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},
    {'code': 'RUB', 'name': 'Russian Ruble', 'symbol': '₽'},
    {'code': 'KZT', 'name': 'Kazakhstani Tenge', 'symbol': '₸'},
    {'code': 'UAH', 'name': 'Ukrainian Hryvnia', 'symbol': '₴'},
    {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥'},
    {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥'},
]

for curr_data in currencies_data:
    currency, created = Currency.objects.get_or_create(
        code=curr_data['code'],
        defaults={'name': curr_data['name'], 'symbol': curr_data['symbol']}
    )
    if created:
        print(f"Валюта создана: {curr_data['code']}")

# Создание курсов обмена (базовая валюта USD)
exchange_rates = [
    {'target': 'EUR', 'rate': 0.92},
    {'target': 'GBP', 'rate': 0.79},
    {'target': 'RUB', 'rate': 97.50},
    {'target': 'KZT', 'rate': 495.00},
    {'target': 'UAH', 'rate': 41.50},
    {'target': 'JPY', 'rate': 149.50},
    {'target': 'CNY', 'rate': 7.24},
]

for rate_data in exchange_rates:
    rate, created = ExchangeRate.objects.get_or_create(
        base_currency='USD',
        target_currency=rate_data['target'],
        defaults={'rate': rate_data['rate']}
    )
    if created:
        print(f"Курс создан: USD/{rate_data['target']} = {rate_data['rate']}")

print('Валюты и курсы обмена настроены')
"@
$createCurrenciesScript | docker-compose exec -T currency-service python manage.py shell

# Создание категорий и товаров
Write-Host "📦 Создание категорий и товаров..." -ForegroundColor Yellow
$createProductsScript = @"
from apps.products.models import Category, Product
from decimal import Decimal

# Создание категорий
categories_data = [
    {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
    {'name': 'Clothing', 'description': 'Fashion and apparel'},
    {'name': 'Books', 'description': 'Books and literature'},
    {'name': 'Home & Garden', 'description': 'Home decor and garden supplies'},
    {'name': 'Sports', 'description': 'Sports equipment and accessories'},
]

categories = {}
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categories[cat_data['name']] = category
    if created:
        print(f"Категория создана: {cat_data['name']}")

# Создание товаров
products_data = [
    # Electronics
    {'name': 'iPhone 15 Pro', 'description': 'Latest Apple smartphone with A17 Pro chip', 'price': Decimal('999.99'), 'category': 'Electronics', 'stock_quantity': 50, 'image_url': 'https://picsum.photos/seed/iphone/400/400'},
    {'name': 'MacBook Pro 14', 'description': 'Professional laptop with M3 Pro chip', 'price': Decimal('1999.99'), 'category': 'Electronics', 'stock_quantity': 30, 'image_url': 'https://picsum.photos/seed/macbook/400/400'},
    {'name': 'AirPods Pro 2', 'description': 'Wireless earbuds with active noise cancellation', 'price': Decimal('249.99'), 'category': 'Electronics', 'stock_quantity': 100, 'image_url': 'https://picsum.photos/seed/airpods/400/400'},
    {'name': 'Samsung Galaxy S24', 'description': 'Premium Android smartphone', 'price': Decimal('899.99'), 'category': 'Electronics', 'stock_quantity': 45, 'image_url': 'https://picsum.photos/seed/samsung/400/400'},
    {'name': 'Sony WH-1000XM5', 'description': 'Premium noise-canceling headphones', 'price': Decimal('349.99'), 'category': 'Electronics', 'stock_quantity': 60, 'image_url': 'https://picsum.photos/seed/sony/400/400'},
    
    # Clothing
    {'name': 'Nike Air Max 90', 'description': 'Classic sneakers with Air cushioning', 'price': Decimal('129.99'), 'category': 'Clothing', 'stock_quantity': 80, 'image_url': 'https://picsum.photos/seed/nike/400/400'},
    {'name': 'Levis 501 Jeans', 'description': 'Original fit denim jeans', 'price': Decimal('79.99'), 'category': 'Clothing', 'stock_quantity': 120, 'image_url': 'https://picsum.photos/seed/levis/400/400'},
    {'name': 'North Face Jacket', 'description': 'Waterproof outdoor jacket', 'price': Decimal('199.99'), 'category': 'Clothing', 'stock_quantity': 40, 'image_url': 'https://picsum.photos/seed/northface/400/400'},
    
    # Books
    {'name': 'Clean Code', 'description': 'A Handbook of Agile Software Craftsmanship by Robert C. Martin', 'price': Decimal('39.99'), 'category': 'Books', 'stock_quantity': 200, 'image_url': 'https://picsum.photos/seed/cleancode/400/400'},
    {'name': 'The Pragmatic Programmer', 'description': 'Your Journey to Mastery by David Thomas', 'price': Decimal('49.99'), 'category': 'Books', 'stock_quantity': 150, 'image_url': 'https://picsum.photos/seed/pragmatic/400/400'},
    {'name': 'Design Patterns', 'description': 'Elements of Reusable Object-Oriented Software', 'price': Decimal('54.99'), 'category': 'Books', 'stock_quantity': 100, 'image_url': 'https://picsum.photos/seed/patterns/400/400'},
    
    # Home & Garden
    {'name': 'Dyson V15 Detect', 'description': 'Cordless vacuum cleaner with laser detection', 'price': Decimal('749.99'), 'category': 'Home & Garden', 'stock_quantity': 25, 'image_url': 'https://picsum.photos/seed/dyson/400/400'},
    {'name': 'Philips Hue Starter Kit', 'description': 'Smart LED lighting system', 'price': Decimal('179.99'), 'category': 'Home & Garden', 'stock_quantity': 70, 'image_url': 'https://picsum.photos/seed/hue/400/400'},
    {'name': 'iRobot Roomba j7+', 'description': 'Self-emptying robot vacuum', 'price': Decimal('599.99'), 'category': 'Home & Garden', 'stock_quantity': 35, 'image_url': 'https://picsum.photos/seed/roomba/400/400'},
    
    # Sports
    {'name': 'Yoga Mat Premium', 'description': 'Non-slip exercise mat 6mm thick', 'price': Decimal('49.99'), 'category': 'Sports', 'stock_quantity': 150, 'image_url': 'https://picsum.photos/seed/yoga/400/400'},
    {'name': 'Fitbit Charge 6', 'description': 'Advanced fitness tracker with GPS', 'price': Decimal('159.99'), 'category': 'Sports', 'stock_quantity': 90, 'image_url': 'https://picsum.photos/seed/fitbit/400/400'},
    {'name': 'Dumbbell Set 20kg', 'description': 'Adjustable dumbbell set for home gym', 'price': Decimal('89.99'), 'category': 'Sports', 'stock_quantity': 60, 'image_url': 'https://picsum.photos/seed/dumbbell/400/400'},
]

for prod_data in products_data:
    product, created = Product.objects.get_or_create(
        name=prod_data['name'],
        defaults={
            'description': prod_data['description'],
            'price': prod_data['price'],
            'category': categories[prod_data['category']],
            'stock_quantity': prod_data['stock_quantity'],
            'image_url': prod_data['image_url'],
        }
    )
    if created:
        print(f"Товар создан: {prod_data['name']}")

print(f'Всего категорий: {Category.objects.count()}')
print(f'Всего товаров: {Product.objects.count()}')
"@
$createProductsScript | docker-compose exec -T product-service python manage.py shell

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
