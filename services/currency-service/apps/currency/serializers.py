from rest_framework import serializers
from .models import ExchangeRate, Currency
from decimal import Decimal


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol', 'is_active']


class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = ['id', 'base_currency', 'target_currency', 'rate', 'last_updated']
        read_only_fields = ['last_updated']


class ConvertSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)


class ConvertResponseSerializer(serializers.Serializer):
    original_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    converted_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    exchange_rate = serializers.DecimalField(max_digits=18, decimal_places=6)
    timestamp = serializers.DateTimeField()
