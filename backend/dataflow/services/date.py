from datetime import date, datetime

from django.core.exceptions import ValidationError


def validate_date(field, value):
    """Проверяет дату."""

    try:
        result = date.fromisoformat(value)
        return result.isoformat()

    except (ValueError, TypeError):
        raise ValidationError(
            "Ожидается дата в формате ГГГГ-ММ-ДД."
        )


def validate_datetime(field, value):
    """Проверяет дату и время."""

    try:
        result = datetime.fromisoformat(value)
        return result.isoformat()

    except (ValueError, TypeError):
        raise ValidationError(
            "Ожидается дата и время в формате ISO."
        )
