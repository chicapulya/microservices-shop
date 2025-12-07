from rest_framework import serializers
from .models import Category, Product
import requests
from django.conf import settings
from decimal import Decimal

class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'products_count', 'created_at']

    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()
    

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    discounted_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    has_discount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'category', 'category_name',
            'stock_quantity', 'image_url', 'is_active', 'is_in_stock',
            'discounted_price', 'discount_percentage', 'has_discount',
            'created_at', 'updated_at'
        ]
    
    def get_discount_info(self, obj):
        """Получить информацию о скидке из discount-service"""
        # Кэшируем результат чтобы не делать несколько запросов
        if not hasattr(self, '_discount_cache'):
            self._discount_cache = {}
        
        if obj.id in self._discount_cache:
            return self._discount_cache[obj.id]
        
        try:
            discount_url = f"{settings.DISCOUNT_SERVICE_URL}/api/discounts/products/by_product/"
            response = requests.get(discount_url, params={'product_id': obj.id}, timeout=2)
            if response.status_code == 200:
                discounts = response.json()
                if discounts and len(discounts) > 0:
                    self._discount_cache[obj.id] = discounts[0]
                    return discounts[0]
        except Exception as e:
            print(f"Error getting discount info: {e}")
            pass
        
        self._discount_cache[obj.id] = None
        return None
    
    def get_discounted_price(self, obj):
        """Получить цену со скидкой"""
        discount_info = self.get_discount_info(obj)
        if discount_info:
            return str(discount_info.get('discounted_price', obj.price))
        return str(obj.price)
    
    def get_discount_percentage(self, obj):
        """Получить процент скидки"""
        discount_info = self.get_discount_info(obj)
        if discount_info:
            return float(discount_info.get('discount_percentage', 0))
        return 0
    
    def get_has_discount(self, obj):
        """Проверить наличие скидки"""
        discount_info = self.get_discount_info(obj)
        return discount_info is not None

class ProductDetailSerializer(ProductSerializer):
    category = CategorySerializer(read_only=True)

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'category',
            'stock_quantity', 'image_url', 'is_active'
        ]