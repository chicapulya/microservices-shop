from django.contrib import admin
from .models import Holiday, Discount, DiscountCode


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'holiday_type', 'discount_percentage', 'start_date', 'end_date', 'is_active']
    list_filter = ['holiday_type', 'is_active', 'start_date']
    search_fields = ['name', 'description']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'holiday_type', 'description')
        }),
        ('Период действия', {
            'fields': ('start_date', 'end_date')
        }),
        ('Скидка', {
            'fields': ('discount_percentage', 'is_active')
        }),
    )


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'holiday', 'original_price', 'discounted_price', 'is_active', 'created_at']
    list_filter = ['holiday', 'is_active', 'created_at']
    search_fields = ['product_id']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Товар', {
            'fields': ('product_id', 'holiday')
        }),
        ('Цены', {
            'fields': ('original_price', 'discounted_price')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['discounted_price']


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'valid_from', 'valid_to', 'usage_count', 'usage_limit', 'is_active']
    list_filter = ['is_active', 'valid_from', 'valid_to']
    search_fields = ['code']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Промокод', {
            'fields': ('code', 'discount_percentage')
        }),
        ('Период действия', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Ограничения', {
            'fields': ('usage_limit', 'usage_count', 'min_purchase_amount', 'is_active')
        }),
    )
    
    readonly_fields = ['usage_count']
