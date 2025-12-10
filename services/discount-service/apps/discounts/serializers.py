from rest_framework import serializers
from .models import Holiday, Discount, DiscountCode


class HolidaySerializer(serializers.ModelSerializer):
    is_currently_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Holiday
        fields = [
            'id', 'name', 'holiday_type', 'start_date', 'end_date',
            'discount_percentage', 'is_active', 'description',
            'is_currently_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_currently_active(self, obj):
        return obj.is_currently_active()


class DiscountSerializer(serializers.ModelSerializer):
    holiday_name = serializers.CharField(source='holiday.name', read_only=True)
    discount_percentage = serializers.DecimalField(
        source='holiday.discount_percentage', 
        max_digits=5, 
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Discount
        fields = [
            'id', 'product_id', 'holiday', 'holiday_name',
            'original_price', 'discounted_price', 'discount_percentage',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['discounted_price', 'created_at', 'updated_at']


class DiscountCodeSerializer(serializers.ModelSerializer):
    is_code_valid = serializers.SerializerMethodField(method_name='get_is_code_valid')
    remaining_uses = serializers.SerializerMethodField(method_name='get_remaining_uses')
    
    class Meta:
        model = DiscountCode
        fields = [
            'id', 'code', 'discount_percentage', 'valid_from', 'valid_to',
            'usage_limit', 'usage_count', 'is_active', 'min_purchase_amount',
            'is_code_valid', 'remaining_uses', 'created_at', 'updated_at'
        ]
        read_only_fields = ['usage_count', 'created_at', 'updated_at']
    
    def get_is_code_valid(self, obj):
        return obj.is_valid()
    
    def get_remaining_uses(self, obj):
        if obj.usage_limit:
            return max(0, obj.usage_limit - obj.usage_count)
        return None


class ApplyDiscountCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
