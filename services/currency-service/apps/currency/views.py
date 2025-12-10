from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
from decimal import Decimal
import requests
from .models import ExchangeRate, Currency
from .serializers import (
    ExchangeRateSerializer,
    CurrencySerializer,
    ConvertSerializer,
    ConvertResponseSerializer
)


class CurrencyViewSet(viewsets.ModelViewSet):
    """ViewSet для управления валютами"""
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить список активных валют"""
        currencies = Currency.objects.filter(is_active=True)
        serializer = self.get_serializer(currencies, many=True)
        return Response(serializer.data)


class ExchangeRateViewSet(viewsets.ModelViewSet):
    """ViewSet для управления курсами валют"""
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Получить последние курсы валют"""
        base = request.query_params.get('base', 'USD')
        rates = ExchangeRate.objects.filter(base_currency=base)
        serializer = self.get_serializer(rates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_rates(self, request):
        """Обновить курсы валют из внешнего источника"""
        base = request.data.get('base', 'USD')
        
        # Здесь можно интегрировать реальный API (например, exchangerate-api.com)
        # Для демонстрации используем фиксированные курсы
        default_rates = {
            'EUR': Decimal('0.92'),
            'GBP': Decimal('0.79'),
            'JPY': Decimal('149.50'),
            'CNY': Decimal('7.24'),
            'RUB': Decimal('92.50'),
            'UAH': Decimal('36.50'),
        }
        
        updated_count = 0
        for currency_code, rate in default_rates.items():
            exchange_rate, created = ExchangeRate.objects.update_or_create(
                base_currency=base,
                target_currency=currency_code,
                defaults={'rate': rate}
            )
            updated_count += 1
        
        return Response({
            'success': True,
            'base_currency': base,
            'updated_count': updated_count,
            'message': f'Updated {updated_count} exchange rates'
        })
    
    @action(detail=False, methods=['post'])
    def convert(self, request):
        """Конвертировать сумму из одной валюты в другую"""
        serializer = ConvertSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        amount = serializer.validated_data['amount']  # type: ignore
        from_currency = serializer.validated_data['from_currency'].upper()  # type: ignore
        to_currency = serializer.validated_data['to_currency'].upper()  # type: ignore
        
        # Если валюты одинаковые
        if from_currency == to_currency:
            return Response({
                'original_amount': amount,
                'converted_amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'exchange_rate': Decimal('1.0'),
                'timestamp': timezone.now()
            })
        
        # Поиск курса обмена
        try:
            # Прямой курс
            exchange_rate = ExchangeRate.objects.get(
                base_currency=from_currency,
                target_currency=to_currency
            )
            rate = exchange_rate.rate
        except ExchangeRate.DoesNotExist:
            try:
                # Обратный курс
                exchange_rate = ExchangeRate.objects.get(
                    base_currency=to_currency,
                    target_currency=from_currency
                )
                rate = Decimal('1') / exchange_rate.rate
            except ExchangeRate.DoesNotExist:
                # Конвертация через USD
                try:
                    from_to_usd = ExchangeRate.objects.get(
                        base_currency='USD',
                        target_currency=from_currency
                    )
                    usd_to_target = ExchangeRate.objects.get(
                        base_currency='USD',
                        target_currency=to_currency
                    )
                    rate = usd_to_target.rate / from_to_usd.rate
                except ExchangeRate.DoesNotExist:
                    return Response({
                        'error': f'Exchange rate not found for {from_currency} to {to_currency}'
                    }, status=status.HTTP_404_NOT_FOUND)
        
        converted_amount = amount * rate
        
        return Response({
            'original_amount': str(amount),
            'converted_amount': str(converted_amount.quantize(Decimal('0.01'))),
            'from_currency': from_currency,
            'to_currency': to_currency,
            'exchange_rate': str(rate),
            'timestamp': timezone.now()
        })
