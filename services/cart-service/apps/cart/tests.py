from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from .models import Cart, CartItem


class CartModelTest(TestCase):
    """Test Cart model"""

    def setUp(self):
        self.cart = Cart.objects.create(user_id=1)

    def test_cart_creation(self):
        """Test creating a cart"""
        self.assertEqual(self.cart.user_id, 1)
        self.assertIsNotNone(self.cart.created_at)

    def test_cart_str(self):
        """Test cart string representation"""
        self.assertEqual(str(self.cart), f"Cart for user {self.cart.user_id}")


class CartItemModelTest(TestCase):
    """Test CartItem model"""

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
        """Test creating a cart item"""
        self.assertEqual(self.cart_item.product_id, 1)
        self.assertEqual(self.cart_item.quantity, 2)
        self.assertEqual(self.cart_item.price, Decimal('99.99'))

    def test_cart_item_subtotal(self):
        """Test cart item subtotal calculation"""
        expected_subtotal = Decimal('99.99') * 2
        self.assertEqual(self.cart_item.subtotal, expected_subtotal)

    def test_cart_item_str(self):
        """Test cart item string representation"""
        self.assertEqual(
            str(self.cart_item),
            f"{self.cart_item.quantity}x Test Product in cart {self.cart.id}"
        )


class CartAPITest(APITestCase):
    """Test Cart API endpoints"""

    def setUp(self):
        self.client = APIClient()
        # Mock authentication by setting user_id in session
        self.user_id = 1

    def test_get_cart(self):
        """Test retrieving user's cart"""
        # Create a cart for testing
        cart = Cart.objects.create(user_id=self.user_id)
        CartItem.objects.create(
            cart=cart,
            product_id=1,
            product_name='Test Product',
            price=Decimal('99.99'),
            quantity=1
        )

        response = self.client.get(
            '/api/cart/',
            HTTP_X_USER_ID=str(self.user_id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)

    def test_add_to_cart(self):
        """Test adding item to cart"""
        data = {
            'product_id': 1,
            'product_name': 'Test Product',
            'price': '99.99',
            'quantity': 2
        }
        response = self.client.post(
            '/api/cart/add/',
            data,
            HTTP_X_USER_ID=str(self.user_id)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        cart = Cart.objects.create(user_id=self.user_id)
        cart_item = CartItem.objects.create(
            cart=cart,
            product_id=1,
            product_name='Test Product',
            price=Decimal('99.99'),
            quantity=1
        )

        data = {'quantity': 5}
        response = self.client.patch(
            f'/api/cart/items/{cart_item.id}/',
            data,
            HTTP_X_USER_ID=str(self.user_id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_remove_from_cart(self):
        """Test removing item from cart"""
        cart = Cart.objects.create(user_id=self.user_id)
        cart_item = CartItem.objects.create(
            cart=cart,
            product_id=1,
            product_name='Test Product',
            price=Decimal('99.99'),
            quantity=1
        )

        response = self.client.delete(
            f'/api/cart/items/{cart_item.id}/',
            HTTP_X_USER_ID=str(self.user_id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_clear_cart(self):
        """Test clearing entire cart"""
        cart = Cart.objects.create(user_id=self.user_id)
        CartItem.objects.create(
            cart=cart,
            product_id=1,
            product_name='Product 1',
            price=Decimal('99.99'),
            quantity=1
        )
        CartItem.objects.create(
            cart=cart,
            product_id=2,
            product_name='Product 2',
            price=Decimal('49.99'),
            quantity=2
        )

        response = self.client.delete(
            '/api/cart/clear/',
            HTTP_X_USER_ID=str(self.user_id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(cart.items.count(), 0)

