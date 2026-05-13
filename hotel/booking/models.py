from django.db import models
from rooms.models import Room
from users.models import CustomUser


class Services(models.Model):
    name = models.CharField(
        'Название услуги',
        max_length=100,
        null=False,
        unique=True
    )
    cost = models.IntegerField(
        'Стоимость',
        max_length=20,
        null=False,
        default=0
    )
    
    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
    

class Booking(models.Model):
    BOOKING_STATUS = [
        ('sleeping', 'Ожидает'),
        ('active', 'Активна'),
        ('dead', 'Завершена'),
    ]
    client = models.ForeignKey(
        CustomUser,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="client",
        verbose_name='Клиент'
    )
    room = models.ForeignKey(
        Room,
        null=False,
        on_delete=models.CASCADE,
        related_name="room",
        verbose_name="Комната"
    )
    servises = models.ManyToManyField(
        Services,
        related_name="services",
        verbose_name="Услуги"
    )
    booking_date = models.DateField(
        'Дата начала брони',
        blank=True
    )
    expiration_date = models.DateField(
        'Дата окончания брони',
        blank=None,
        null=None,
    )
    status = models.CharField(
        'Статус брони',
        max_length=15,
        choices=BOOKING_STATUS,
        default='sleeping',
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Бронирование'
