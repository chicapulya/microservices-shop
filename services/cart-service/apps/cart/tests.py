from django.test import TestCase
from decimal import Decimal
from .models import Cart, CartItem


class CartModelTest(TestCase):
    """Тесты модели Cart"""

    def setUp(self):
        self.cart = Cart.objects.create(user_id=1)

    def test_cart_creation(self):
        """Тест создания корзины"""
        self.assertEqual(self.cart.user_id, 1)
        self.assertIsNotNone(self.cart.created_at)

    def test_cart_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.cart), f"Cart for user {self.cart.user_id}")

    def test_cart_total_amount(self):
        """Тест расчета общей суммы"""
        CartItem.objects.create(
            cart=self.cart,
            product_id=1,
            product_name='Product 1',
            price=Decimal('10.00'),
            quantity=2
        )
        CartItem.objects.create(
            cart=self.cart,
            product_id=2,
            product_name='Product 2',
            price=Decimal('15.00'),
            quantity=1
        )
        self.assertEqual(self.cart.total_amount, Decimal('35.00'))

    def test_cart_total_items(self):
        """Тест подсчета общего количества товаров"""
        CartItem.objects.create(
            cart=self.cart,
            product_id=1,
            product_name='Product 1',
            price=Decimal('10.00'),
            quantity=2
        )
        CartItem.objects.create(
            cart=self.cart,
            product_id=2,
            product_name='Product 2',
            price=Decimal('15.00'),
            quantity=3
        )
        self.assertEqual(self.cart.total_items, 5)

    def test_cart_clear(self):
        """Тест очистки корзины"""
        CartItem.objects.create(
            cart=self.cart,
            product_id=1,
            product_name='Product 1',
            price=Decimal('10.00'),
            quantity=2
        )
        self.cart.clear()
        self.assertEqual(self.cart.items.count(), 0)


class CartItemModelTest(TestCase):
    """Тесты модели CartItem"""

    def setUp(self):
        self.cart = Cart.objects.create(user_id=1)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product_id=1,
            product_name='Test Product',
            price=Decimal('99.99'),
            quantity=2
        )

    def test_cart_item_creation(self):
        """Тест создания элемента корзины"""
        self.assertEqual(self.cart_item.product_id, 1)
        self.assertEqual(self.cart_item.quantity, 2)
        self.assertEqual(self.cart_item.price, Decimal('99.99'))

    def test_cart_item_subtotal(self):
        """Тест расчета подсуммы"""
        expected_subtotal = Decimal('99.99') * 2
        self.assertEqual(self.cart_item.subtotal, expected_subtotal)

    def test_cart_item_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.cart_item), '2x Test Product')

    def test_cart_item_unique_together(self):
        """Тест уникальности комбинации cart + product_id"""
        with self.assertRaises(Exception):
            CartItem.objects.create(
                cart=self.cart,
                product_id=1,  # Тот же product_id
                product_name='Another Product',
                price=Decimal('50.00'),
                quantity=1
            )
