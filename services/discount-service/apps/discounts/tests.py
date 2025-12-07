from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from apps.discounts.models import Holiday, Discount, DiscountCode


class HolidayModelTest(TestCase):
    """Тесты для модели Holiday"""
    
    def setUp(self):
        self.holiday = Holiday.objects.create(
            name='New Year Sale',
            holiday_type='new_year',
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=5),
            discount_percentage=Decimal('20.00'),
            is_active=True,
            description='New Year discount'
        )
    
    def test_holiday_creation(self):
        """Тест создания праздника"""
        self.assertEqual(self.holiday.name, 'New Year Sale')
        self.assertEqual(self.holiday.discount_percentage, Decimal('20.00'))
        self.assertTrue(self.holiday.is_active)
    
    def test_holiday_string_representation(self):
        """Тест строкового представления"""
        expected = f"New Year Sale (20.00%)"
        self.assertEqual(str(self.holiday), expected)
    
    def test_is_currently_active(self):
        """Тест проверки активности праздника"""
        self.assertTrue(self.holiday.is_currently_active())
        
        # Праздник в прошлом
        past_holiday = Holiday.objects.create(
            name='Past Sale',
            holiday_type='custom',
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=5),
            discount_percentage=Decimal('15.00'),
            is_active=True
        )
        self.assertFalse(past_holiday.is_currently_active())


class DiscountModelTest(TestCase):
    """Тесты для модели Discount"""
    
    def setUp(self):
        self.holiday = Holiday.objects.create(
            name='Test Holiday',
            holiday_type='custom',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            discount_percentage=Decimal('25.00'),
            is_active=True
        )
        
        self.discount = Discount.objects.create(
            product_id=1,
            holiday=self.holiday,
            original_price=Decimal('100.00'),
            is_active=True
        )
    
    def test_discount_creation(self):
        """Тест создания скидки"""
        self.assertEqual(self.discount.product_id, 1)
        self.assertEqual(self.discount.original_price, Decimal('100.00'))
        self.assertTrue(self.discount.is_active)
    
    def test_automatic_discounted_price_calculation(self):
        """Тест автоматического расчета цены со скидкой"""
        # 25% скидка от 100 = 75
        self.assertEqual(self.discount.discounted_price, Decimal('75.00'))
    
    def test_unique_together_constraint(self):
        """Тест уникальности комбинации product_id и holiday"""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Discount.objects.create(
                product_id=1,
                holiday=self.holiday,
                original_price=Decimal('200.00')
            )


class DiscountCodeModelTest(TestCase):
    """Тесты для модели DiscountCode"""
    
    def setUp(self):
        self.code = DiscountCode.objects.create(
            code='SUMMER2024',
            discount_percentage=Decimal('30.00'),
            valid_from=timezone.now() - timedelta(days=1),
            valid_to=timezone.now() + timedelta(days=10),
            usage_limit=100,
            usage_count=0,
            is_active=True,
            min_purchase_amount=Decimal('50.00')
        )
    
    def test_discount_code_creation(self):
        """Тест создания промокода"""
        self.assertEqual(self.code.code, 'SUMMER2024')
        self.assertEqual(self.code.discount_percentage, Decimal('30.00'))
        self.assertEqual(self.code.usage_count, 0)
    
    def test_is_valid(self):
        """Тест проверки валидности промокода"""
        self.assertTrue(self.code.is_valid())
        
        # Неактивный промокод
        self.code.is_active = False
        self.assertFalse(self.code.is_valid())
        self.code.is_active = True
        
        # Достигнут лимит использований
        self.code.usage_count = 100
        self.assertFalse(self.code.is_valid())
    
    def test_use_code(self):
        """Тест использования промокода"""
        initial_count = self.code.usage_count
        result = self.code.use_code()
        self.assertTrue(result)
        self.assertEqual(self.code.usage_count, initial_count + 1)


class HolidayAPITest(APITestCase):
    """Тесты для API праздников"""
    
    def setUp(self):
        self.holiday_data = {
            'name': 'Christmas Sale',
            'holiday_type': 'christmas',
            'start_date': (timezone.now() + timedelta(days=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(days=10)).isoformat(),
            'discount_percentage': '15.00',
            'is_active': True,
            'description': 'Christmas discount'
        }
        
        self.active_holiday = Holiday.objects.create(
            name='Active Holiday',
            holiday_type='custom',
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=5),
            discount_percentage=Decimal('20.00'),
            is_active=True
        )
    
    def test_create_holiday(self):
        """Тест создания праздника через API"""
        response = self.client.post('/api/holidays/', self.holiday_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Holiday.objects.count(), 2)
    
    def test_list_holidays(self):
        """Тест получения списка праздников"""
        response = self.client.get('/api/holidays/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # type: ignore
    
    def test_get_active_holidays(self):
        """Тест получения активных праздников"""
        response = self.client.get('/api/holidays/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # type: ignore


class DiscountAPITest(APITestCase):
    """Тесты для API скидок"""
    
    def setUp(self):
        self.holiday = Holiday.objects.create(
            name='Test Holiday',
            holiday_type='custom',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            discount_percentage=Decimal('25.00'),
            is_active=True
        )
        
        self.discount = Discount.objects.create(
            product_id=1,
            holiday=self.holiday,
            original_price=Decimal('100.00'),
            is_active=True
        )
    
    def test_list_discounts(self):
        """Тест получения списка скидок"""
        response = self.client.get('/api/discounts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_discount_by_product(self):
        """Тест получения скидки для товара"""
        response = self.client.get('/api/discounts/by_product/', {'product_id': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DiscountCodeAPITest(APITestCase):
    """Тесты для API промокодов"""
    
    def setUp(self):
        self.code = DiscountCode.objects.create(
            code='TEST2024',
            discount_percentage=Decimal('30.00'),
            valid_from=timezone.now() - timedelta(days=1),
            valid_to=timezone.now() + timedelta(days=10),
            usage_limit=100,
            usage_count=0,
            is_active=True,
            min_purchase_amount=Decimal('50.00')
        )
    
    def test_validate_discount_code(self):
        """Тест валидации промокода"""
        response: Response = self.client.post('/api/discount-codes/validate/', {  # type: ignore
            'code': 'TEST2024',
            'order_amount': '100.00'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_apply_discount_code(self):
        """Тест применения промокода"""
        initial_count = self.code.usage_count
        response: Response = self.client.post('/api/discount-codes/apply/', {  # type: ignore
            'code': 'TEST2024',
            'order_amount': '100.00'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.code.refresh_from_db()
        self.assertEqual(self.code.usage_count, initial_count + 1)
