from django.db import models
from .validators import real_number, real_email


class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('standard', 'Стандарт'),
        ('comfort', 'Комфорт'),
        ('lux', 'Люкс'),
    ]

    number = models.CharField(
        'Номер комнаты',
        max_length=10,
        unique=True
    )
    room_type = models.CharField(
        'Тип комнаты',
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default='standard',
    )
    price_per_night = models.DecimalField(
        'Цена за ночь',
        max_digits=10,
        decimal_places=2,
    )
    capacity = models.PositiveIntegerField(
        'Вместимость',
        default=1,
    )
    description = models.TextField(
        'Описание',
        blank=True,
    )
    is_available = models.BooleanField(
        'Доступен для бронирования',
        default=True
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )
    images = models.ImageField(
        default=None,
    )

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'
        ordering = ['number']

    def __str__(self):
        return f'Комната {self.number} ({self.get_room_type_display()})'


class Account(models.Model):
    first_name = models.CharField(
        'Имя',
        max_length=100,
        blank=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=100,
        blank=False
    )


class AccountInfo(models.Model):
    account = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        related_name='info',
        primary_key=True,
        verbose_name='Аккаунт'
    )
    phone = phone = models.CharField(
        'Номер телефона',
        max_length=30,
        blank=False,
        unique=True,
        validators=[real_number]
    )
    email = models.TextField(
        'Почта',
        blank=False,
        unique=True,
        validators=[real_email]
    )
