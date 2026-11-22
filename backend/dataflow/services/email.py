from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def validate_email_value(field, value):
    """Проверяет адрес электронной почты."""

    if value in (None, ""):

        if field.required:
            raise ValidationError("Поле обязательно для заполнения.")

        return None

    if not isinstance(value, str):
        raise ValidationError("Адрес электронной почты должен быть текстом.")

    value = value.strip()

    try:
        validate_email(value)

    except ValidationError:
        raise ValidationError("Введите корректный адрес электронной почты.")

    return value
