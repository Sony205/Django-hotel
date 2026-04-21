from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import real_number, real_email


class CustomUser(AbstractUser):
    pass


class AccountInfo(models.Model):
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
    account = models.OneToOneField(
        CustomUser,
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
    birthday = models.DateField(
        'Дата рождения',
        blank=True,
        null=True
    )
