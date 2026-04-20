from django.db import models
from rooms.models import Account, Room


class Booking(models.Model):
    BOOKING_STATUS = [
        ('sleeping', 'Ожидает'),
        ('active', 'Активна'),
        ('dead', 'Завершена'),
    ]
    client = models.ForeignKey(
        Account,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="rooms",
        verbose_name='Клиент'
    )
    room = models.ForeignKey(
        Room,
        null=False,
        on_delete=models.CASCADE,
        related_name="client",
        verbose_name="Комната"
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
