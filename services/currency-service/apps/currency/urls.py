from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CurrencyViewSet, ExchangeRateViewSet

router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'rates', ExchangeRateViewSet, basename='exchange-rate')

urlpatterns = [
    path('', include(router.urls)),
]
