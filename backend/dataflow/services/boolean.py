from django.core.exceptions import ValidationError


def validate_boolean(field, value):
    """Проверяет логическое значение."""

    if not isinstance(value, bool):
        raise ValidationError("Ожидается логическое значение.")

    return value
