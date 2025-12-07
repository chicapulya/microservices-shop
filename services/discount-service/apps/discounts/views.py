from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Holiday, Discount, DiscountCode
from .serializers import (
    HolidaySerializer, 
    DiscountSerializer, 
    DiscountCodeSerializer,
    ApplyDiscountCodeSerializer
)


class HolidayViewSet(viewsets.ModelViewSet):
    """ViewSet для управления праздниками"""
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить активные праздники на данный момент"""
        now = timezone.now()
        active_holidays = Holiday.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
        serializer = self.get_serializer(active_holidays, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Получить предстоящие праздники"""
        now = timezone.now()
        upcoming_holidays = Holiday.objects.filter(
            is_active=True,
            start_date__gt=now
        ).order_by('start_date')[:5]
        serializer = self.get_serializer(upcoming_holidays, many=True)
        return Response(serializer.data)


class DiscountViewSet(viewsets.ModelViewSet):
    """ViewSet для управления скидками на товары"""
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """Получить скидки для конкретного товара"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        discounts = Discount.objects.filter(
            product_id=product_id,
            is_active=True,
            holiday__is_active=True,
            holiday__start_date__lte=timezone.now(),
            holiday__end_date__gte=timezone.now()
        )
        serializer = self.get_serializer(discounts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Рассчитать скидку для товара"""
        product_id = request.data.get('product_id')
        original_price = request.data.get('original_price')
        
        if not product_id or not original_price:
            return Response(
                {'error': 'product_id and original_price are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Найти активные скидки для товара
        now = timezone.now()
        active_discount = Discount.objects.filter(
            product_id=product_id,
            is_active=True,
            holiday__is_active=True,
            holiday__start_date__lte=now,
            holiday__end_date__gte=now
        ).first()
        
        if active_discount:
            return Response({
                'product_id': product_id,
                'original_price': original_price,
                'discounted_price': active_discount.discounted_price,
                'discount_percentage': active_discount.holiday.discount_percentage,
                'holiday': active_discount.holiday.name
            })
        
        return Response({
            'product_id': product_id,
            'original_price': original_price,
            'discounted_price': original_price,
            'discount_percentage': 0,
            'holiday': None
        })


class DiscountCodeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления промокодами"""
    queryset = DiscountCode.objects.all()
    serializer_class = DiscountCodeSerializer
    
    @action(detail=False, methods=['post'])
    def validate_code(self, request):
        """Проверить валидность промокода"""
        code = request.data.get('code')
        if not code:
            return Response(
                {'error': 'code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            discount_code = DiscountCode.objects.get(code=code.upper())
            if discount_code.is_valid():
                serializer = self.get_serializer(discount_code)
                return Response({
                    'valid': True,
                    'discount': serializer.data
                })
            else:
                return Response({
                    'valid': False,
                    'error': 'Промокод недействителен или истек срок действия'
                })
        except DiscountCode.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Промокод не найден'
            })
    
    @action(detail=False, methods=['post'])
    def apply(self, request):
        """Применить промокод к покупке"""
        serializer = ApplyDiscountCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        code: str = serializer.validated_data['code']  # type: ignore
        total_amount = serializer.validated_data['total_amount']  # type: ignore
        
        try:
            discount_code = DiscountCode.objects.get(code=code.upper())
            
            if not discount_code.is_valid():
                return Response({
                    'success': False,
                    'error': 'Промокод недействителен или истек срок действия'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if total_amount < discount_code.min_purchase_amount:
                return Response({
                    'success': False,
                    'error': f'Минимальная сумма покупки: {discount_code.min_purchase_amount}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Применить промокод
            if discount_code.use_code():
                discount_amount = total_amount * (discount_code.discount_percentage / 100)
                final_amount = total_amount - discount_amount
                
                return Response({
                    'success': True,
                    'code': discount_code.code,
                    'original_amount': total_amount,
                    'discount_amount': discount_amount,
                    'final_amount': final_amount,
                    'discount_percentage': discount_code.discount_percentage
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Не удалось применить промокод'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except DiscountCode.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Промокод не найден'
            }, status=status.HTTP_404_NOT_FOUND)
