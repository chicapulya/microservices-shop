from django.db import models
from decimal import Decimal


class ExchangeRate(models.Model):
    """Модель курсов валют"""
    base_currency = models.CharField(max_length=3, default='USD', verbose_name='Базовая валюта')
    target_currency = models.CharField(max_length=3, verbose_name='Целевая валюта')
    rate = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        verbose_name='Курс обмена'
    )
    last_updated = models.DateTimeField(auto_now=True, verbose_name='Последнее обновление')
    
    class Meta:
        verbose_name = 'Курс валюты'
        verbose_name_plural = 'Курсы валют'
        unique_together = ['base_currency', 'target_currency']
        ordering = ['base_currency', 'target_currency']
    
    def __str__(self):
        return f"{self.base_currency}/{self.target_currency}: {self.rate}"


class Currency(models.Model):
    """Модель поддерживаемых валют"""
    code = models.CharField(max_length=3, unique=True, verbose_name='Код валюты')
    name = models.CharField(max_length=100, verbose_name='Название')
    symbol = models.CharField(max_length=10, verbose_name='Символ')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    
    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
