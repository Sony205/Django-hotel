"""
Тесты для приложения booking.
Покрывают: модели, формы, views, авторизацию.
"""
import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


# Тестирование модели Booking

@pytest.mark.django_db
class TestBookingModel:
    """Тесты модели Booking."""

    def test_booking_creation(self, booking):
        """Бронь создаётся и сохраняется в базе."""
        assert booking.pk is not None

    def test_booking_fields(self, booking, user, room):
        """Поля брони сохраняются корректно."""
        assert booking.client == user
        assert booking.room == room
        assert booking.status == 'sleeping'

    def test_booking_default_status(self, booking):
        """Статус по умолчанию — 'sleeping' (Ожидает)."""
        assert booking.status == 'sleeping'

    def test_booking_status_display(self, booking):
        """Отображение статуса работает корректно."""
        assert booking.get_status_display() == 'Ожидает'

    @pytest.mark.parametrize('status, expected_display', [
        ('sleeping', 'Ожидает'),
        ('active', 'Активна'),
        ('dead', 'Завершена'),
    ])
    def test_booking_status_choices(self, status, expected_display, booking):
        """Параметризованный тест всех статусов брони."""
        booking.status = status
        booking.save()
        booking.refresh_from_db()
        assert booking.get_status_display() == expected_display


# Тестирование формы BookingForm

@pytest.mark.django_db
class TestBookingForm:
    """Тесты формы бронирования."""

    def _valid_data(self):
        """Минимальный набор валидных данных для формы."""
        today = timezone.now().date()
        return {
            'booking_date': today + timedelta(days=1),
            'expiration_date': today + timedelta(days=5),
            'card_expiry': '12/27',
            # servises — ManyToMany, blank=True, не обязателен
        }

    def test_valid_booking_form(self):
        """Форма с корректными данными валидна."""
        from booking.forms import BookingForm
        form = BookingForm(data=self._valid_data())
        assert form.is_valid(), form.errors

    def test_booking_date_in_past(self):
        """Нельзя забронировать на прошедшую дату."""
        from booking.forms import BookingForm
        today = timezone.now().date()
        data = self._valid_data()
        data['booking_date'] = today - timedelta(days=1)
        form = BookingForm(data=data)
        assert not form.is_valid()
        assert 'booking_date' in form.errors

    def test_expiration_before_booking(self):
        """Дата окончания не может быть раньше даты начала."""
        from booking.forms import BookingForm
        today = timezone.now().date()
        data = self._valid_data()
        data['booking_date'] = today + timedelta(days=5)
        data['expiration_date'] = today + timedelta(days=2)
        form = BookingForm(data=data)
        assert not form.is_valid()

    def test_expiration_equals_booking(self):
        """Дата окончания не может совпадать с датой начала."""
        from booking.forms import BookingForm
        today = timezone.now().date()
        same_day = today + timedelta(days=3)
        data = self._valid_data()
        data['booking_date'] = same_day
        data['expiration_date'] = same_day
        form = BookingForm(data=data)
        assert not form.is_valid()

    def test_missing_dates(self):
        """Форма без дат невалидна."""
        from booking.forms import BookingForm
        form = BookingForm(data={})
        assert not form.is_valid()

    # Тесты валидации card_expiry

    def test_card_expiry_missing(self):
        """Форма без card_expiry невалидна."""
        from booking.forms import BookingForm
        data = self._valid_data()
        del data['card_expiry']
        form = BookingForm(data=data)
        assert not form.is_valid()
        assert 'card_expiry' in form.errors

    def test_card_expiry_wrong_format(self):
        """card_expiry без слеша не проходит валидацию."""
        from booking.forms import BookingForm
        data = self._valid_data()
        data['card_expiry'] = '1227'
        form = BookingForm(data=data)
        assert not form.is_valid()
        assert 'card_expiry' in form.errors

    def test_card_expiry_invalid_month(self):
        """Месяц > 12 не проходит валидацию."""
        from booking.forms import BookingForm
        data = self._valid_data()
        data['card_expiry'] = '13/27'
        form = BookingForm(data=data)
        assert not form.is_valid()
        assert 'card_expiry' in form.errors

    def test_card_expiry_expired(self):
        """Просроченная карта (год < 26) не проходит валидацию."""
        from booking.forms import BookingForm
        data = self._valid_data()
        data['card_expiry'] = '12/24'
        form = BookingForm(data=data)
        assert not form.is_valid()
        assert 'card_expiry' in form.errors


# ══════════════════════════════════════════════════════════════════════════════
# Тестирование views бронирования — авторизация
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestBookingViewsAuth:
    """Тесты доступа к views бронирования."""

    def test_anonymous_cannot_access_create_booking(self, client, room):
        """Анонимный пользователь не может создать бронь — редирект на логин."""
        url = reverse('create_booking', kwargs={'room_id': room.pk})
        response = client.get(url)
        assert response.status_code == 302
        assert '/login' in response['Location'] or 'login' in response['Location']

    def test_anonymous_cannot_access_my_bookings(self, client):
        """Анонимный пользователь не может открыть страницу своих броней."""
        url = reverse('my_bookings')
        response = client.get(url)
        assert response.status_code == 302

    def test_auth_user_can_access_my_bookings(self, auth_client):
        """Авторизованный пользователь открывает страницу своих броней."""
        url = reverse('my_bookings')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_auth_user_can_access_create_booking(self, auth_client, room):
        """Авторизованный пользователь может открыть страницу создания брони."""
        url = reverse('create_booking', kwargs={'room_id': room.pk})
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_anonymous_cannot_cancel_booking(self, client, booking):
        """Анонимный пользователь не может отменить бронь."""
        url = reverse('cancel_booking', kwargs={'booking_id': booking.pk})
        response = client.get(url)
        assert response.status_code == 302


# ══════════════════════════════════════════════════════════════════════════════
# Тестирование создания брони
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCreateBookingView:
    """Тесты view создания брони."""

    def test_create_booking_template(self, auth_client, room):
        """Проверка шаблона страницы создания брони."""
        url = reverse('create_booking', kwargs={'room_id': room.pk})
        response = auth_client.get(url)
        assert 'booking/create_booking.html' in [t.name for t in response.templates]

    def test_successful_booking_creation(self, auth_client, room):
        """Успешное создание брони редиректит на страницу 'мои брони'."""
        from booking.models import Booking
        today = timezone.now().date()
        url = reverse('create_booking', kwargs={'room_id': room.pk})
        data = {
            'booking_date': today + timedelta(days=1),
            'expiration_date': today + timedelta(days=4),
            'card_expiry': '12/27',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 302
        assert Booking.objects.count() == 1

    def test_cannot_book_unavailable_room(self, auth_client, unavailable_room):
        """Нельзя забронировать недоступный номер — 404."""
        url = reverse('create_booking', kwargs={'room_id': unavailable_room.pk})
        response = auth_client.get(url)
        assert response.status_code == 404

    def test_my_bookings_template(self, auth_client):
        """Страница 'мои брони' использует правильный шаблон."""
        url = reverse('my_bookings')
        response = auth_client.get(url)
        assert 'booking/my_bookings.html' in [t.name for t in response.templates]

    def test_my_bookings_shows_only_own(self, auth_client, booking, another_user, room):
        """Пользователь видит только свои брони, а не чужие."""
        from booking.models import Booking
        today = timezone.now().date()
        Booking.objects.create(
            client=another_user,
            room=room,
            booking_date=today + timedelta(days=10),
            expiration_date=today + timedelta(days=15),
        )
        url = reverse('my_bookings')
        response = auth_client.get(url)
        bookings_in_context = list(response.context['bookings'])
        assert booking in bookings_in_context
        assert len(bookings_in_context) == 1
