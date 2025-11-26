from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import (
    CartSerializer, AddToCartSerializer,
    UpdateCartItemSerializer, CartItemSerializer
)
from .services import ProductService
import logging

logger = logging.getLogger(__name__)


class IsAuthenticatedCustom:
    """Custom permission class that checks if user_id is set by middleware"""

    def has_permission(self, request, view):
        return hasattr(request, 'user_id') and request.user_id is not None


class CartView(generics.RetrieveAPIView):
    """Получение корзины пользователя"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticatedCustom]

    def get_object(self):
        logger.info(f"Getting cart for user {self.request.user_id}")
        cart, created = Cart.objects.get_or_create(user_id=self.request.user_id)
        if created:
            logger.info(f"Created new cart for user {self.request.user_id}")
        return cart


# ================================
#   ДОБАВЛЕНИЕ ТОВАРА В КОРЗИНУ
# ================================
@api_view(['POST'])
@permission_classes([IsAuthenticatedCustom])
def add_to_cart(request):
    """Добавление товара в корзину"""
    logger.info(f"Add to cart request from user {request.user_id}: {request.data}")

    serializer = AddToCartSerializer(data=request.data)

    if not serializer.is_valid():
        logger.error(f"Add to cart validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    product_id = serializer.validated_data['product_id']
    quantity = serializer.validated_data['quantity']

    # Получаем корзину пользователя
    cart, created = Cart.objects.get_or_create(user_id=request.user_id)
    logger.info(f"Cart for user {request.user_id}: {'created' if created else 'found'}")

    # Проверка доступности товара
    if not ProductService.check_availability(product_id, quantity):
        logger.warning(f"Product {product_id} not available in quantity {quantity}")
        return Response({
            'error': 'Product is not available in requested quantity'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Получаем данные о продукте
    product_data = ProductService.get_product(product_id)
    if not product_data:
        logger.warning(f"Product {product_id} not found")
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Добавляем или обновляем товар в корзине
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=product_id,
        defaults={
            'quantity': quantity,
            'price': product_data['price'],
            'product_name': product_data['name']
        }
    )

    if not created:
        # Если товар уже есть в корзине — увеличиваем количество
        new_quantity = cart_item.quantity + quantity

        if not ProductService.check_availability(product_id, new_quantity):
            return Response({
                'error': 'Not enough stock available'
            }, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = new_quantity
        cart_item.save()

        logger.info(f"Updated cart item {cart_item.id} quantity to {new_quantity}")
    else:
        logger.info(f"Created new cart item {cart_item.id}")

    return Response({
        'message': 'Product added to cart successfully',
        'cart_item': CartItemSerializer(cart_item).data
    }, status=status.HTTP_201_CREATED)
