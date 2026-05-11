"""
Тесты для приложения rooms.
Покрывают: модели, views, авторизацию.
"""
import pytest
from django.urls import reverse


# Тестирование модели Room

@pytest.mark.django_db
class TestRoomModel:
    """Тесты модели Room."""

    def test_room_creation(self, room):
        """Объект комнаты создаётся корректно."""
        assert room.pk is not None

    def test_room_fields(self, room):
        """Поля комнаты сохраняются правильно."""
        assert room.number == '101'
        assert room.room_type == 'standard'
        assert str(room.price_per_night) == '2500.00'
        assert room.capacity == 2
        assert room.is_available is True

    def test_room_default_values(self):
        """Проверка значений по умолчанию."""
        from rooms.models import Room
        room = Room.objects.create(
            number='999',
            price_per_night='1000.00',
        )
        assert room.room_type == 'standard'
        assert room.capacity == 1
        assert room.is_available is True

    def test_room_str(self, room):
        """Метод __str__ возвращает читаемое название."""
        assert 'Комната' in str(room)
        assert '101' in str(room)
        assert 'Стандарт' in str(room)

    @pytest.mark.parametrize('room_type, expected_display', [
        ('standard', 'Стандарт'),
        ('comfort', 'Комфорт'),
        ('lux', 'Люкс'),
    ])
    def test_room_type_display(self, room_type, expected_display):
        """Параметризованный тест: отображение типа комнаты."""
        from rooms.models import Room
        room = Room.objects.create(
            number=f'test-{room_type}',
            room_type=room_type,
            price_per_night='3000.00',
        )
        assert room.get_room_type_display() == expected_display

    def test_room_unique_number(self, room):
        """Нельзя создать две комнаты с одинаковым номером."""
        from django.db import IntegrityError
        from rooms.models import Room
        with pytest.raises(IntegrityError):
            Room.objects.create(
                number='101',
                price_per_night='1000.00',
            )


# Тестирование views комнат

@pytest.mark.django_db
class TestRoomViews:
    """Тесты представлений (views) приложения rooms."""

    # room_list

    def test_room_list_status_200(self, client, room):
        """Страница списка комнат возвращает статус 200."""
        url = reverse('room_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_room_list_template(self, client, room):
        """Используется корректный шаблон для списка комнат."""
        url = reverse('room_list')
        response = client.get(url)
        assert 'rooms/room_list.html' in [t.name for t in response.templates]

    def test_room_list_shows_available_rooms(self, client, room, unavailable_room):
        """В списке отображаются только доступные комнаты."""
        url = reverse('room_list')
        response = client.get(url)
        rooms_in_context = list(response.context['rooms'])
        assert room in rooms_in_context
        assert unavailable_room not in rooms_in_context

    # room_detail

    def test_room_detail_status_200(self, client, room):
        """Страница детали комнаты возвращает статус 200."""
        url = reverse('room_detail', kwargs={'room_id': room.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_room_detail_template(self, client, room):
        """Используется корректный шаблон для детали комнаты."""
        url = reverse('room_detail', kwargs={'room_id': room.pk})
        response = client.get(url)
        assert 'rooms/room_detail.html' in [t.name for t in response.templates]

    def test_room_detail_context(self, client, room):
        """В контексте передаётся правильная комната."""
        url = reverse('room_detail', kwargs={'room_id': room.pk})
        response = client.get(url)
        assert response.context['room'] == room

    def test_room_detail_404_for_nonexistent(self, client):
        """Несуществующая комната возвращает 404."""
        url = reverse('room_detail', kwargs={'room_id': 99999})
        response = client.get(url)
        assert response.status_code == 404
