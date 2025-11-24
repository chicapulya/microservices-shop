from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product
from django.db import models


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    ordering = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=models.Count('products')
        )

    def product_count(self, obj):
        return obj.product_count
    product_count.short_description = 'Количество товаров'
    product_count.admin_order_field = 'product_count'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity',
                    'in_stock', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'category__name')
    list_editable = ('is_active', 'price', 'stock_quantity')
    readonly_fields = ('created_at', 'updated_at', 'in_stock_preview', 'image_preview')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Основное', {
            'fields': ('name', 'category', 'description', 'image_url', 'image_preview')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'stock_quantity', 'is_active', 'in_stock_preview')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # --- Превью изображения (readonly) ---
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-height: 150px; border-radius: 8px;" />',
                obj.image_url
            )
        return "(Нет изображения)"
    image_preview.short_description = 'Превью'

    # --- Наличие (цветной текст) ---
    def in_stock(self, obj):
        color = "green" if obj.is_in_stock else "red"
        status = "В наличии" if obj.is_in_stock else "Нет в наличии"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    in_stock.short_description = 'Наличие'
    in_stock.admin_order_field = 'stock_quantity'

    # --- Булево поле только для чтения ---
    def in_stock_preview(self, obj):
        return obj.is_in_stock
    in_stock_preview.short_description = 'На складе'
    in_stock_preview.boolean = True
