import pytest
from django.utils import timezone
from datetime import timedelta


# Фикстуры для пользователей

@pytest.fixture
def user(django_user_model):
    """Создаёт обычного пользователя."""
    return django_user_model.objects.create_user(
        username='testuser',
        password='testpass123',
        email='user@gmail.com'
    )


@pytest.fixture
def another_user(django_user_model):
    """Создаёт второго пользователя."""
    return django_user_model.objects.create_user(
        username='anotheruser',
        password='testpass123'
    )


@pytest.fixture
def auth_client(client, user):
    """Возвращает авторизованный клиент обычного пользователя."""
    client.force_login(user)
    return client


# Фикстуры для комнат

@pytest.fixture
def room():
    """Создаёт доступную комнату."""
    from rooms.models import Room
    return Room.objects.create(
        number='101',
        room_type='standard',
        price_per_night='2500.00',
        capacity=2,
        description='Стандартный номер',
        is_available=True,
    )


@pytest.fixture
def unavailable_room():
    """Создаёт недоступную комнату."""
    from rooms.models import Room
    return Room.objects.create(
        number='202',
        room_type='lux',
        price_per_night='8000.00',
        capacity=3,
        is_available=False,
    )


# Фикстуры для броней

@pytest.fixture
def booking(user, room):
    """Создаёт активную бронь."""
    from booking.models import Booking
    today = timezone.now().date()
    return Booking.objects.create(
        client=user,
        room=room,
        booking_date=today + timedelta(days=1),
        expiration_date=today + timedelta(days=5),
        status='sleeping',
    )
