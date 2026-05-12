import re
from django.core.exceptions import ValidationError


def real_number(value) -> None:
    regex = r'^\+?[78]{1}[\s\(]{,2}\d{3}[\s\)]{,2}\d{3}[\s-]?\d{2}[\s-]?\d{2}'
    match = re.match(regex, value)
    if match is None:
        raise ValidationError(
            'Номер телефона должен иметь вид:\n+7 или 8(999)999-99-99'
        )


def real_email(value) -> None:
    regex = r'^[a-zA-Z0-9\-\_]+\@(gmail\.com|mail\.ru)'
    match = re.match(regex, value)
    if match is None:
        raise ValidationError(
            'Используйте gmail или mail'
        )
