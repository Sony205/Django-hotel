from django import forms
from django.utils import timezone

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'expiration_date']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_booking_date(self):
        booking_date = self.cleaned_data.get('booking_date')

        if booking_date and booking_date < timezone.now().date():
            raise forms.ValidationError('Нельзя забронировать номер на прошедшую дату.')

        return booking_date

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        expiration_date = cleaned_data.get('expiration_date')

        if booking_date and expiration_date:
            if expiration_date <= booking_date:
                raise forms.ValidationError(
                    'Дата окончания должна быть позже даты начала.'
                )

        return cleaned_data