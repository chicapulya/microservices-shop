from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response
from decimal import Decimal
from typing import Any
from .models import Currency, ExchangeRate


class CurrencyModelTest(TestCase):
    """Test Currency model"""

    def setUp(self):
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            is_active=True
        )

    def test_currency_creation(self):
        """Test creating a currency"""
        self.assertEqual(self.currency.code, 'USD')
        self.assertEqual(self.currency.name, 'US Dollar')
        self.assertEqual(self.currency.symbol, '$')
        self.assertTrue(self.currency.is_active)

    def test_currency_str(self):
        """Test currency string representation"""
        self.assertEqual(str(self.currency), 'USD - US Dollar')

    def test_currency_unique_code(self):
        """Test that currency code must be unique"""
        with self.assertRaises(Exception):
            Currency.objects.create(
                code='USD',
                name='Another Dollar',
                symbol='$'
            )


class ExchangeRateModelTest(TestCase):
    """Test ExchangeRate model"""

    def setUp(self):
        self.usd = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$'
        )
        self.eur = Currency.objects.create(
            code='EUR',
            name='Euro',
            symbol='€'
        )
        self.rate = ExchangeRate.objects.create(
            base_currency=self.usd,
            target_currency=self.eur,
            rate=Decimal('0.92')
        )

    def test_exchange_rate_creation(self):
        """Test creating an exchange rate"""
        self.assertEqual(self.rate.base_currency, self.usd)
        self.assertEqual(self.rate.target_currency, self.eur)
        self.assertEqual(self.rate.rate, Decimal('0.92'))

    def test_exchange_rate_str(self):
        """Test exchange rate string representation"""
        self.assertEqual(str(self.rate), '1 USD = 0.920000 EUR')

    def test_unique_currency_pair(self):
        """Test that base/target currency pair must be unique"""
        with self.assertRaises(Exception):
            ExchangeRate.objects.create(
                base_currency=self.usd,
                target_currency=self.eur,
                rate=Decimal('0.95')
            )


class CurrencyAPITest(APITestCase):
    """Test Currency API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.usd = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            is_active=True
        )
        self.eur = Currency.objects.create(
            code='EUR',
            name='Euro',
            symbol='€',
            is_active=True
        )

    def test_get_currencies_list(self):
        """Test retrieving currencies list"""
        response: Response = self.client.get('/api/currency/currencies/')  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # type: ignore

    def test_get_active_currencies(self):
        """Test retrieving only active currencies"""
        Currency.objects.create(
            code='GBP',
            name='British Pound',
            symbol='£',
            is_active=False
        )
        response: Response = self.client.get('/api/currency/currencies/active/')  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # type: ignore


class ExchangeRateAPITest(APITestCase):
    """Test ExchangeRate API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.usd = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$'
        )
        self.eur = Currency.objects.create(
            code='EUR',
            name='Euro',
            symbol='€'
        )
        self.gbp = Currency.objects.create(
            code='GBP',
            name='British Pound',
            symbol='£'
        )
        self.usd_eur = ExchangeRate.objects.create(
            base_currency=self.usd,
            target_currency=self.eur,
            rate=Decimal('0.92')
        )
        self.usd_gbp = ExchangeRate.objects.create(
            base_currency=self.usd,
            target_currency=self.gbp,
            rate=Decimal('0.79')
        )

    def test_get_exchange_rates_list(self):
        """Test retrieving exchange rates list"""
        response: Response = self.client.get('/api/currency/rates/')  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # type: ignore

    def test_get_latest_rates(self):
        """Test retrieving latest rates for a base currency"""
        response: Response = self.client.get('/api/currency/rates/latest/?base=USD')  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # type: ignore

    def test_convert_currency(self):
        """Test currency conversion"""
        data = {
            'amount': 100,
            'from_currency': 'USD',
            'to_currency': 'EUR'
        }
        response = self.client.post(
            '/api/currency/rates/convert/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['original_amount'], '100.00')  # type: ignore
        self.assertEqual(response.data['converted_amount'], '92.00')  # type: ignore
        self.assertEqual(response.data['from_currency'], 'USD')  # type: ignore
        self.assertEqual(response.data['to_currency'], 'EUR')  # type: ignore

    def test_convert_same_currency(self):
        """Test converting to the same currency"""
        data = {
            'amount': 100,
            'from_currency': 'USD',
            'to_currency': 'USD'
        }
        response = self.client.post(
            '/api/currency/rates/convert/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['original_amount'], '100.00')  # type: ignore
        self.assertEqual(response.data['converted_amount'], '100.00')  # type: ignore

    def test_convert_inverse_rate(self):
        """Test conversion with inverse rate"""
        data = {
            'amount': 92,
            'from_currency': 'EUR',
            'to_currency': 'USD'
        }
        response = self.client.post(
            '/api/currency/rates/convert/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 92 EUR / 0.92 = 100 USD
        self.assertAlmostEqual(
            float(response.data['converted_amount']),  # type: ignore
            100.0,
            places=2
        )

    def test_convert_triangular(self):
        """Test triangular conversion through USD"""
        data = {
            'amount': 100,
            'from_currency': 'EUR',
            'to_currency': 'GBP'
        }
        response = self.client.post(
            '/api/currency/rates/convert/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 100 EUR -> USD (100/0.92) -> GBP (result * 0.79)
        self.assertIsNotNone(response.data['converted_amount'])  # type: ignore
