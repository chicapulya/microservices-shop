from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HolidayViewSet, DiscountViewSet, DiscountCodeViewSet

router = DefaultRouter()
router.register(r'holidays', HolidayViewSet, basename='holiday')
router.register(r'products', DiscountViewSet, basename='discount')
router.register(r'codes', DiscountCodeViewSet, basename='discount-code')

urlpatterns = [
    path('', include(router.urls)),
]
