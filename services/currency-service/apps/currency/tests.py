from django.test import TestCase
from decimal import Decimal
from .models import Currency, ExchangeRate


class CurrencyModelTest(TestCase):
    """Тесты модели Currency"""

    def setUp(self):
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            is_active=True
        )

    def test_currency_creation(self):
        """Тест создания валюты"""
        self.assertEqual(self.currency.code, 'USD')
        self.assertEqual(self.currency.name, 'US Dollar')
        self.assertEqual(self.currency.symbol, '$')
        self.assertTrue(self.currency.is_active)

    def test_currency_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.currency), 'USD - US Dollar')

    def test_currency_unique_code(self):
        """Тест уникальности кода валюты"""
        with self.assertRaises(Exception):
            Currency.objects.create(
                code='USD',  # Дублирующий код
                name='Another Dollar',
                symbol='$'
            )


class ExchangeRateModelTest(TestCase):
    """Тесты модели ExchangeRate"""

    def setUp(self):
        Currency.objects.create(code='USD', name='US Dollar', symbol='$')
        Currency.objects.create(code='EUR', name='Euro', symbol='€')
        
        self.rate = ExchangeRate.objects.create(
            base_currency='USD',
            target_currency='EUR',
            rate=Decimal('0.85')
        )

    def test_exchange_rate_creation(self):
        """Тест создания курса обмена"""
        self.assertEqual(self.rate.base_currency, 'USD')
        self.assertEqual(self.rate.target_currency, 'EUR')
        self.assertEqual(self.rate.rate, Decimal('0.85'))

    def test_exchange_rate_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.rate), 'USD/EUR: 0.85')

    def test_unique_currency_pair(self):
        """Тест уникальности пары валют"""
        with self.assertRaises(Exception):
            ExchangeRate.objects.create(
                base_currency='USD',
                target_currency='EUR',
                rate=Decimal('0.90')
            )
