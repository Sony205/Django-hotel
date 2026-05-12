from django import forms
from django.utils import timezone

from .models import Booking


class BookingForm(forms.ModelForm):
    card_expiry = forms.CharField(
        max_length=5,
        required=True
    )
    class Meta:
        model = Booking
        fields = ['booking_date', 'expiration_date', 'servises']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
            'servises': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'booking_date': 'Дата заезда',
            'expiration_date': 'Дата выезда',
            'servises': 'Дополнительные услуги',
        }

    def clean_booking_date(self):
        booking_date = self.cleaned_data.get('booking_date')

        if booking_date and booking_date < timezone.now().date():
            raise forms.ValidationError('Нельзя забронировать номер на прошедшую дату.')

        return booking_date

    def clean_card_expiry(self):
        value = self.cleaned_data.get('card_expiry')

        if '/' not in value:
            raise forms.ValidationError(
                'Введите срок действия в формате ММ/ГГ.'
            )

        month, year = value.split('/')

        if not month.isdigit() or not year.isdigit():
            raise forms.ValidationError(
                'Срок действия карты указан неверно.'
            )

        month = int(month)
        year = int(year)

        if month < 1 or month > 12:
            raise forms.ValidationError(
                'Месяц должен быть от 01 до 12.'
            )

        if year < 26:
            raise forms.ValidationError(
                'Карта просрочена.'
            )

        return value

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        expiration_date = cleaned_data.get('expiration_date')

        if booking_date and expiration_date:
            if expiration_date <= booking_date:
                raise forms.ValidationError(
                    'Дата выезда должна быть позже даты заезда.'
                )

        return cleaned_data