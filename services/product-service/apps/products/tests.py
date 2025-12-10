from django.test import TestCase
from decimal import Decimal
from .models import Category, Product


class CategoryModelTest(TestCase):
    """Тесты модели Category"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )

    def test_category_creation(self):
        """Тест создания категории"""
        self.assertEqual(self.category.name, 'Electronics')
        self.assertEqual(self.category.slug, 'electronics')

    def test_category_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.category), 'Electronics')

    def test_category_slug_auto_generation(self):
        """Тест автогенерации slug"""
        category = Category.objects.create(name='Home & Garden')
        self.assertEqual(category.slug, 'home-garden')


class ProductModelTest(TestCase):
    """Тесты модели Product"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        self.product = Product.objects.create(
            name='Laptop',
            description='Gaming laptop',
            price=Decimal('999.99'),
            category=self.category,
            stock_quantity=10
        )

    def test_product_creation(self):
        """Тест создания товара"""
        self.assertEqual(self.product.name, 'Laptop')
        self.assertEqual(self.product.price, Decimal('999.99'))
        self.assertEqual(self.product.stock_quantity, 10)
        self.assertEqual(self.product.category, self.category)

    def test_product_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.product), 'Laptop')

    def test_product_is_in_stock(self):
        """Тест свойства is_in_stock"""
        self.assertTrue(self.product.is_in_stock)
        
        self.product.stock_quantity = 0
        self.assertFalse(self.product.is_in_stock)

    def test_reserve_quantity(self):
        """Тест резервирования количества"""
        result = self.product.reserve_quantity(5)
        self.assertTrue(result)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 5)

    def test_reserve_quantity_insufficient(self):
        """Тест резервирования при недостаточном количестве"""
        result = self.product.reserve_quantity(15)
        self.assertFalse(result)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 10)

    def test_release_quantity(self):
        """Тест освобождения количества"""
        self.product.release_quantity(5)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 15)
