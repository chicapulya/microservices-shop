from django.contrib import admin
from .models import Currency, ExchangeRate


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['base_currency', 'target_currency', 'rate', 'last_updated']
    list_filter = ['base_currency', 'target_currency']
    search_fields = ['base_currency', 'target_currency']
    readonly_fields = ['last_updated']
