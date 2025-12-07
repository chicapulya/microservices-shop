from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from .models import Category, Product


class CategoryModelTest(TestCase):
    """Test Category model"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )

    def test_category_creation(self):
        """Test creating a category"""
        self.assertEqual(self.category.name, 'Electronics')
        self.assertEqual(self.category.slug, 'electronics')

    def test_category_str(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), 'Electronics')

    def test_category_slug_auto_generation(self):
        """Test that slug is auto-generated from name"""
        category = Category.objects.create(name='Home & Garden')
        self.assertEqual(category.slug, 'home-garden')


class ProductModelTest(TestCase):
    """Test Product model"""

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
        """Test creating a product"""
        self.assertEqual(self.product.name, 'Laptop')
        self.assertEqual(self.product.price, Decimal('999.99'))
        self.assertEqual(self.product.category, self.category)

    def test_product_str(self):
        """Test product string representation"""
        self.assertEqual(str(self.product), 'Laptop')

    def test_product_is_in_stock(self):
        """Test is_in_stock property"""
        self.assertTrue(self.product.is_in_stock)
        
        self.product.stock_quantity = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock)


class ProductAPITest(APITestCase):
    """Test Product API endpoints"""

    def setUp(self):
        self.client = APIClient()
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

    def test_get_products_list(self):
        """Test retrieving products list"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_product_detail(self):
        """Test retrieving a single product"""
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Laptop')

    def test_filter_products_by_category(self):
        """Test filtering products by category"""
        response = self.client.get(f'/api/products/?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_products(self):
        """Test searching products"""
        response = self.client.get('/api/products/?search=Laptop')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class CategoryAPITest(APITestCase):
    """Test Category API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )

    def test_get_categories_list(self):
        """Test retrieving categories list"""
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_category_detail(self):
        """Test retrieving a single category"""
        response = self.client.get(f'/api/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Electronics')

