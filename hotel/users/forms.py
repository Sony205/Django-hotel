from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, AccountInfo


class RegisterForm(UserCreationForm):
    phone = forms.CharField(label='Номер телефона')
    # email = forms.EmailField(label='Email')
    birthday = forms.DateField(label='Дата рождения', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        """Проверка, что email не используется"""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже зарегистрирован')
        return email

    def clean_phone(self):
        """Проверка, что телефон не используется"""
        phone = self.cleaned_data.get('phone')
        if AccountInfo.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Этот номер телефона уже зарегистрирован')
        return phone

    def save(self, commit=True):
        user = super().save(commit=commit)
        AccountInfo.objects.create(
            account=user,
            first_name=self.cleaned_data.get('first_name', ''),
            last_name=self.cleaned_data.get('last_name', ''),
            phone=self.cleaned_data['phone'],
            birthday=self.cleaned_data.get('birthday'),
        )
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs['class'] = 'form-control'
