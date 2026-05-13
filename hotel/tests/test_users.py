"""
Тесты для приложения users.
Покрывают: модели, валидаторы, формы, views, авторизацию.
"""
import pytest
from django.urls import reverse
from django.core.exceptions import ValidationError


# Тестирование валидаторов

class TestValidators:
    """Тесты валидаторов номера телефона и email."""

    # ── real_number ────────────────────────────────────────────────────────────

    @pytest.mark.parametrize('valid_phone', [
        '+7(999)999-99-99',
        '8(999)999-99-99',
        '+79991234567',
        '89991234567',
        '8 999 999 99 99',
    ])
    def test_valid_phone(self, valid_phone):
        """Корректные номера телефонов проходят валидацию."""
        from users.validators import real_number
        try:
            real_number(valid_phone)
        except ValidationError:
            pytest.fail(f'Валидный номер вызвал ошибку: {valid_phone}')

    @pytest.mark.parametrize('invalid_phone', [
        '123456789',
        '+1234567890',
        'not-a-number',
        '',
        '+7',
    ])
    def test_invalid_phone(self, invalid_phone):
        """Некорректные номера телефонов не проходят валидацию."""
        from users.validators import real_number
        with pytest.raises(ValidationError):
            real_number(invalid_phone)

    # real_email

    @pytest.mark.parametrize('valid_email', [
        'user@gmail.com',
        'user@mail.ru',
        'my-name_123@gmail.com',
    ])
    def test_valid_email(self, valid_email):
        """Корректные email-адреса проходят валидацию."""
        from users.validators import real_email
        try:
            real_email(valid_email)
        except ValidationError:
            pytest.fail(f'Валидный email вызвал ошибку: {valid_email}')

    @pytest.mark.parametrize('invalid_email', [
        'user@yandex.ru',
        'user@hotmail.com',
        'notanemail',
        '',
        '@gmail.com',
    ])
    def test_invalid_email(self, invalid_email):
        """Некорректные email-адреса не проходят валидацию."""
        from users.validators import real_email
        with pytest.raises(ValidationError):
            real_email(invalid_email)


# Тестирование модели CustomUser и AccountInfo

@pytest.mark.django_db
class TestCustomUserModel:
    """Тесты модели CustomUser."""

    def test_user_creation(self, django_user_model):
        """Пользователь создаётся корректно."""
        user = django_user_model.objects.create_user(
            username='newuser',
            password='pass12345'
        )
        assert user.pk is not None
        assert user.username == 'newuser'

    def test_user_is_not_staff_by_default(self, django_user_model):
        """По умолчанию пользователь не является сотрудником."""
        user = django_user_model.objects.create_user(
            username='plainuser',
            password='pass12345'
        )
        assert user.is_staff is False

    def test_user_str(self, django_user_model):
        """__str__ пользователя возвращает username."""
        user = django_user_model.objects.create_user(
            username='struser',
            password='pass12345'
        )
        assert str(user) == 'struser'


@pytest.mark.django_db
class TestAccountInfoModel:
    """Тесты модели AccountInfo."""

    def test_account_info_creation(self, user):
        """AccountInfo создаётся и связывается с пользователем."""
        from users.models import AccountInfo
        info = AccountInfo.objects.create(
            account=user,
            first_name='Иван',
            last_name='Петров',
            phone='+79991234567',
            email='ivan@gmail.com',
        )
        assert info.pk == user.pk
        assert info.first_name == 'Иван'
        assert info.last_name == 'Петров'

    def test_account_info_one_to_one(self, user):
        """Нельзя создать два AccountInfo для одного пользователя."""
        from django.db import IntegrityError
        from users.models import AccountInfo
        AccountInfo.objects.create(
            account=user,
            first_name='Иван',
            last_name='Петров',
            phone='+79991234567',
            email='ivan@gmail.com',
        )
        with pytest.raises(IntegrityError):
            AccountInfo.objects.create(
                account=user,
                first_name='Дубль',
                last_name='Дубль',
                phone='+79997654321',
                email='double@gmail.com',
            )

    def test_account_info_related_name(self, user):
        """Доступ к AccountInfo через related_name 'info' работает."""
        from users.models import AccountInfo
        info = AccountInfo.objects.create(
            account=user,
            first_name='Ольга',
            last_name='Сидорова',
            phone='+79993456789',
            email='olga@mail.ru',
        )
        assert user.info == info

    def test_birthday_optional(self, user):
        """Поле birthday необязательно."""
        from users.models import AccountInfo
        info = AccountInfo.objects.create(
            account=user,
            first_name='Алексей',
            last_name='Николаев',
            phone='+79994567890',
            email='alex@gmail.com',
            birthday=None,
        )
        assert info.birthday is None


# Тестирование формы RegisterForm

@pytest.mark.django_db
class TestRegisterForm:
    """Тесты формы регистрации."""

    def _valid_data(self):
        return {
            'username': 'formuser',
            'first_name': 'Тест',
            'last_name': 'Тестов',
            'password1': 'StrongPass321!',
            'password2': 'StrongPass321!',
            'phone': '+79991112233',
            'email': 'formuser@gmail.com',
        }

    def test_valid_register_form(self):
        """Форма с корректными данными валидна."""
        from users.forms import RegisterForm
        form = RegisterForm(data=self._valid_data())
        assert form.is_valid(), form.errors

    def test_passwords_mismatch(self):
        """Несовпадающие пароли делают форму невалидной."""
        from users.forms import RegisterForm
        data = self._valid_data()
        data['password2'] = 'WrongPass999!'
        form = RegisterForm(data=data)
        assert not form.is_valid()
        assert 'password2' in form.errors

    def test_invalid_phone_in_form(self):
        """Неверный телефон делает форму невалидной."""
        from users.forms import RegisterForm
        data = self._valid_data()
        data['phone'] = '123'
        form = RegisterForm(data=data)
        assert not form.is_valid()

    def test_invalid_email_in_form(self):
        """Email не с gmail/mail делает форму невалидной."""
        from users.forms import RegisterForm
        data = self._valid_data()
        data['email'] = 'user@yandex.ru'
        form = RegisterForm(data=data)
        assert not form.is_valid()

    def test_duplicate_email(self, user):
        """Повторный email не проходит валидацию формы."""
        from users.forms import RegisterForm
        from users.models import AccountInfo
        AccountInfo.objects.create(
            account=user,
            first_name='X',
            last_name='Y',
            phone='+79990000001',
            email='taken@gmail.com',
        )
        data = self._valid_data()
        data['email'] = 'taken@gmail.com'
        data['username'] = 'newuser2'
        form = RegisterForm(data=data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_duplicate_phone(self, user):
        """Повторный телефон не проходит валидацию формы."""
        from users.forms import RegisterForm
        from users.models import AccountInfo
        AccountInfo.objects.create(
            account=user,
            first_name='X',
            last_name='Y',
            phone='+79991112233',
            email='unique99@gmail.com',
        )
        data = self._valid_data()
        data['username'] = 'newuser3'
        data['email'] = 'another@gmail.com'
        form = RegisterForm(data=data)
        assert not form.is_valid()
        assert 'phone' in form.errors

    def test_register_form_saves_account_info(self):
        """Сохранение формы создаёт пользователя и AccountInfo."""
        from users.forms import RegisterForm
        from users.models import AccountInfo
        form = RegisterForm(data=self._valid_data())
        assert form.is_valid(), form.errors
        user = form.save()
        assert AccountInfo.objects.filter(account=user).exists()
        info = AccountInfo.objects.get(account=user)
        assert info.email == 'formuser@gmail.com'


# Тестирование views: регистрация, логин, логаут, профиль

@pytest.mark.django_db
class TestRegisterView:
    """Тесты страницы регистрации."""

    def test_register_page_status_200(self, client):
        """Страница регистрации открывается (200)."""
        url = reverse('register')
        response = client.get(url)
        assert response.status_code == 200

    def test_register_page_template(self, client):
        """Страница регистрации использует нужный шаблон."""
        url = reverse('register')
        response = client.get(url)
        assert 'registration/register.html' in [t.name for t in response.templates]

    def test_register_page_has_form(self, client):
        """На странице регистрации есть форма."""
        url = reverse('register')
        response = client.get(url)
        assert 'form' in response.context

    def test_successful_register_redirects(self, client):
        """Успешная регистрация делает редирект."""
        url = reverse('register')
        data = {
            'username': 'reguser',
            'first_name': 'Рег',
            'last_name': 'Юзер',
            'password1': 'StrongPass321!',
            'password2': 'StrongPass321!',
            'phone': '+79995556677',
            'email': 'reguser@gmail.com',
        }
        response = client.post(url, data)
        assert response.status_code == 302


@pytest.mark.django_db
class TestLoginView:
    """Тесты страницы входа."""

    def test_login_page_status_200(self, client):
        """Страница логина открывается (200)."""
        url = reverse('login')
        response = client.get(url)
        assert response.status_code == 200

    def test_login_page_template(self, client):
        """Страница логина использует нужный шаблон."""
        url = reverse('login')
        response = client.get(url)
        assert 'registration/login.html' in [t.name for t in response.templates]

    def test_login_page_has_form(self, client):
        """На странице логина есть форма."""
        url = reverse('login')
        response = client.get(url)
        assert 'form' in response.context

    def test_successful_login_redirects(self, client, user):
        """Правильные данные — редирект после входа."""
        url = reverse('login')
        response = client.post(url, {
            'username': 'testuser',
            'password': 'testpass123',
        })
        assert response.status_code == 302

    def test_wrong_credentials_no_redirect(self, client, user):
        """Неверные данные не делают редирект."""
        url = reverse('login')
        response = client.post(url, {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        assert response.status_code == 200


@pytest.mark.django_db
class TestProfileView:
    """Тесты страницы профиля."""

    def test_anonymous_cannot_access_profile(self, client):
        """Анонимный пользователь не может открыть профиль — редирект."""
        url = reverse('profile')
        response = client.get(url)
        assert response.status_code == 302
        assert 'login' in response['Location']

    def test_auth_user_can_access_profile(self, auth_client):
        """Авторизованный пользователь открывает профиль (200)."""
        url = reverse('profile')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_profile_template(self, auth_client):
        """Страница профиля использует нужный шаблон."""
        url = reverse('profile')
        response = auth_client.get(url)
        assert 'profile.html' in [t.name for t in response.templates]

    def test_profile_context_has_user(self, auth_client, user):
        """В контексте профиля есть объект пользователя."""
        url = reverse('profile')
        response = auth_client.get(url)
        assert response.context['user'] == user
