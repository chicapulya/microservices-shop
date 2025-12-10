from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class Holiday(models.Model):
    """Модель праздника для автоматических скидок"""
    HOLIDAY_TYPES = [
        ('new_year', 'Новый Год'),
        ('christmas', 'Рождество'),
        ('easter', 'Пасха'),
        ('black_friday', 'Черная Пятница'),
        ('valentines', 'День Святого Валентина'),
        ('womens_day', 'Международный Женский День'),
        ('cyber_monday', 'Киберпонедельник'),
        ('summer_sale', 'Летняя Распродажа'),
        ('custom', 'Кастомный Праздник'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название праздника')
    holiday_type = models.CharField(
        max_length=50, 
        choices=HOLIDAY_TYPES, 
        verbose_name='Тип праздника'
    )
    start_date = models.DateTimeField(verbose_name='Дата начала')
    end_date = models.DateTimeField(verbose_name='Дата окончания')
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Процент скидки'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Праздник'
        verbose_name_plural = 'Праздники'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.discount_percentage}%)"
    
    def is_currently_active(self):
        """Проверка активности праздника на данный момент"""
        now = timezone.now()
        return (
            self.is_active and 
            self.start_date <= now <= self.end_date
        )


class Discount(models.Model):
    """Модель скидки на конкретный товар"""
    product_id = models.IntegerField(verbose_name='ID товара')
    holiday = models.ForeignKey(
        Holiday, 
        on_delete=models.CASCADE, 
        related_name='discounts',
        verbose_name='Праздник'
    )
    original_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Оригинальная цена'
    )
    discounted_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Цена со скидкой'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
        ordering = ['-created_at']
        unique_together = ['product_id', 'holiday']
    
    def __str__(self):
        return f"Товар {self.product_id}: {self.original_price} → {self.discounted_price}"
    
    def save(self, *args, **kwargs):
        """Автоматический расчет цены со скидкой"""
        if self.original_price and self.holiday:
            discount_amount = self.original_price * (self.holiday.discount_percentage / 100)
            self.discounted_price = self.original_price - discount_amount
        super().save(*args, **kwargs)


class DiscountCode(models.Model):
    """Промокоды для дополнительных скидок"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Промокод')
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Процент скидки'
    )
    valid_from = models.DateTimeField(verbose_name='Действителен с')
    valid_to = models.DateTimeField(verbose_name='Действителен до')
    usage_limit = models.IntegerField(
        default=None, 
        null=True, 
        blank=True,
        verbose_name='Лимит использований'
    )
    usage_count = models.IntegerField(default=0, verbose_name='Использований')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Минимальная сумма покупки'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%)"
    
    def is_valid(self):
        """Проверка валидности промокода"""
        now = timezone.now()
        if not self.is_active:
            return False
        if not (self.valid_from <= now <= self.valid_to):
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True
    
    def use_code(self):
        """Использование промокода"""
        if self.is_valid():
            self.usage_count += 1
            self.save()
            return True
        return False
