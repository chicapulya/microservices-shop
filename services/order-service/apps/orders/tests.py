from django.test import TestCase
from decimal import Decimal
from .models import Order, OrderItem


class OrderModelTest(TestCase):
    """Тесты модели Order"""

    def setUp(self):
        self.order = Order.objects.create(
            user_id=1,
            total_amount=Decimal('199.98'),
            status='pending',
            shipping_address='123 Test St, Test City',
            user_email='test@example.com',
            user_name='Test User'
        )

    def test_order_creation(self):
        """Тест создания заказа"""
        self.assertEqual(self.order.user_id, 1)
        self.assertEqual(self.order.total_amount, Decimal('199.98'))
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(self.order.shipping_address, '123 Test St, Test City')
        self.assertEqual(self.order.user_email, 'test@example.com')
        self.assertEqual(self.order.user_name, 'Test User')

    def test_order_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.order), f"Order #{self.order.pk} by User #{self.order.user_id}")

    def test_items_count(self):
        """Тест подсчета количества элементов"""
        OrderItem.objects.create(
            order=self.order,
            product_id=1,
            product_name='Product 1',
            price=Decimal('99.99'),
            quantity=2
        )
        OrderItem.objects.create(
            order=self.order,
            product_id=2,
            product_name='Product 2',
            price=Decimal('49.99'),
            quantity=1
        )
        self.assertEqual(self.order.items_count, 2)

    def test_total_quantity(self):
        """Тест подсчета общего количества товаров"""
        OrderItem.objects.create(
            order=self.order,
            product_id=1,
            product_name='Product 1',
            price=Decimal('99.99'),
            quantity=2
        )
        OrderItem.objects.create(
            order=self.order,
            product_id=2,
            product_name='Product 2',
            price=Decimal('49.99'),
            quantity=3
        )
        self.assertEqual(self.order.total_quantity, 5)

    def test_calculate_total(self):
        """Тест расчета общей суммы"""
        OrderItem.objects.create(
            order=self.order,
            product_id=1,
            product_name='Product 1',
            price=Decimal('99.99'),
            quantity=2
        )
        OrderItem.objects.create(
            order=self.order,
            product_id=2,
            product_name='Product 2',
            price=Decimal('49.99'),
            quantity=1
        )
        total = self.order.calculate_total()
        self.assertEqual(total, Decimal('249.97'))
        self.assertEqual(self.order.total_amount, Decimal('249.97'))


class OrderItemModelTest(TestCase):
    """Тесты модели OrderItem"""

    def setUp(self):
        self.order = Order.objects.create(
            user_id=1,
            total_amount=Decimal('199.98'),
            status='pending',
            shipping_address='123 Test St',
            user_email='test@example.com',
            user_name='Test User'
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product_id=1,
            product_name='Test Product',
            price=Decimal('99.99'),
            quantity=2
        )

    def test_order_item_creation(self):
        """Тест создания элемента заказа"""
        self.assertEqual(self.order_item.product_id, 1)
        self.assertEqual(self.order_item.product_name, 'Test Product')
        self.assertEqual(self.order_item.price, Decimal('99.99'))
        self.assertEqual(self.order_item.quantity, 2)

    def test_order_item_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.order_item), '2x Test Product')

    def test_order_item_subtotal(self):
        """Тест расчета подсуммы"""
        expected_subtotal = Decimal('99.99') * 2
        self.assertEqual(self.order_item.subtotal, expected_subtotal)
