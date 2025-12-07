from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from .models import Order, OrderItem


class OrderModelTest(TestCase):
    """Test Order model"""

    def setUp(self):
        self.order = Order.objects.create(
            user_id=1,
            total_amount=Decimal('199.98'),
            status='pending',
            shipping_address='123 Test St, Test City',
            customer_name='Test User',
            customer_email='test@example.com',
            customer_phone='+1234567890'
        )

    def test_order_creation(self):
        """Test creating an order"""
        self.assertEqual(self.order.user_id, 1)
        self.assertEqual(self.order.total_amount, Decimal('199.98'))
        self.assertEqual(self.order.status, 'pending')

    def test_order_str(self):
        """Test order string representation"""
        self.assertEqual(str(self.order), f"Order #{self.order.id} by user {self.order.user_id}")


class OrderItemModelTest(TestCase):
    """Test OrderItem model"""

    def setUp(self):
        self.order = Order.objects.create(
            user_id=1,
            total_amount=Decimal('199.98'),
            status='pending',
            shipping_address='123 Test St',
            customer_name='Test User',
            customer_email='test@example.com'
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product_id=1,
            product_name='Test Product',
            price=Decimal('99.99'),
            quantity=2
        )

    def test_order_item_creation(self):
        """Test creating an order item"""
        self.assertEqual(self.order_item.product_id, 1)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, Decimal('99.99'))

    def test_order_item_subtotal(self):
        """Test order item subtotal calculation"""
        expected_subtotal = Decimal('99.99') * 2
        self.assertEqual(self.order_item.subtotal, expected_subtotal)

    def test_order_item_str(self):
        """Test order item string representation"""
        self.assertEqual(
            str(self.order_item),
            f"{self.order_item.quantity}x Test Product"
        )


class OrderAPITest(APITestCase):
    """Test Order API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user_id = 1
        self.order = Order.objects.create(
            user_id=self.user_id,
            total_amount=Decimal('199.98'),
            status='pending',
            shipping_address='123 Test St',
            customer_name='Test User',
            customer_email='test@example.com',
            customer_phone='+1234567890'
        )
        OrderItem.objects.create(
            order=self.order,
            product_id=1,
            product_name='Test Product',
            price=Decimal('99.99'),
            quantity=2
        )

    def test_get_orders_list(self):
        """Test retrieving user's orders"""
        response = self.client.get(
            '/api/orders/',
            HTTP_X_USER_ID=str(self.user_id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_order_detail(self):
        """Test retrieving a single order"""
        response = self.client.get(
            f'/api/orders/{self.order.id}/',
            HTTP_X_USER_ID=str(self.user_id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)

    def test_create_order(self):
        """Test creating a new order"""
        data = {
            'total_amount': '299.99',
            'shipping_address': '456 New St',
            'customer_name': 'New User',
            'customer_email': 'new@example.com',
            'customer_phone': '+1987654321',
            'items': [
                {
                    'product_id': 2,
                    'product_name': 'New Product',
                    'price': '149.99',
                    'quantity': 2
                }
            ]
        }
        response = self.client.post(
            '/api/orders/',
            data,
            format='json',
            HTTP_X_USER_ID=str(self.user_id)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)

    def test_update_order_status(self):
        """Test updating order status"""
        data = {'status': 'shipped'}
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            data,
            HTTP_X_USER_ID=str(self.user_id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'shipped')

    def test_cancel_order(self):
        """Test canceling an order"""
        response = self.client.post(
            f'/api/orders/{self.order.id}/cancel/',
            HTTP_X_USER_ID=str(self.user_id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'cancelled')

