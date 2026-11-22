from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def validate_url_value(field, value):
    """Проверяет адрес ссылки."""

    if value in (None, ""):
        if field.required:
            raise ValidationError("Поле обязательно для заполнения.")
        return None

    if not isinstance(value, str):
        raise ValidationError("Ссылка должна быть текстом.")

    value = value.strip()

    validator = URLValidator(schemes=["http", "https"])

    try:
        validator(value)
    except ValidationError:
        raise ValidationError("Введите корректную ссылку.")

    return value
