from django.db import models


class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('standard', 'Стандарт'),
        ('comfort', 'Комфорт'),
        ('lux', 'Люкс'),
    ]

    number = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Номер комнаты'
    )
    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default='standard',
        verbose_name='Тип комнаты'
    )
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за ночь'
    )
    capacity = models.PositiveIntegerField(
        default=1,
        verbose_name='Вместимость'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name='Доступен для бронирования'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'
        ordering = ['number']

    def __str__(self):
        return f'Комната {self.number} ({self.get_room_type_display()})'
