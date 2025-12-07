"""
URL configuration for discount service.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/discounts/', include('apps.discounts.urls')),
]
