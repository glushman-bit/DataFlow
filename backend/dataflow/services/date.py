from datetime import date, datetime

from django.core.exceptions import ValidationError


def get_date_setting(value, setting_name):
    """Проверяет и преобразует настройку даты."""

    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValidationError(
            f"Некорректное значение настройки '{setting_name}'. "
            "Ожидается дата в формате ГГГГ-ММ-ДД."
        )


def get_datetime_setting(value, setting_name):
    """Проверяет и преобразует настройку даты и времени."""

    try:
        return datetime.fromisoformat(value)

    except (ValueError, TypeError):
        raise ValidationError(
            f"Некорректное значение настройки '{setting_name}'. "
            "Ожидается дата и время в формате ISO."
        )


def validate_date(field, value):
    """Проверяет дату и допустимый диапазон."""

    try:
        result = date.fromisoformat(value)

    except (ValueError, TypeError):
        raise ValidationError(
            "Ожидается дата в формате ГГГГ-ММ-ДД."
        )

    settings = field.settings or {}

    min_date = settings.get("min")
    max_date = settings.get("max")

    if min_date:
        if result < get_date_setting(min_date, "min"):
            raise ValidationError(
                f"Дата не может быть раньше {min_date}."
            )

    if max_date:
        if result > get_date_setting(max_date, "max"):
            raise ValidationError(
                f"Дата не может быть позже {max_date}."
            )

    return result.isoformat()


def validate_datetime(field, value):
    """Проверяет дату и время и допустимый диапазон."""

    try:
        result = datetime.fromisoformat(value)

    except (ValueError, TypeError):
        raise ValidationError(
            "Ожидается дата и время в формате ISO."
        )

    settings = field.settings or {}

    min_datetime = settings.get("min")
    max_datetime = settings.get("max")

    if min_datetime:
        if result < get_datetime_setting(min_datetime, "min"):
            raise ValidationError(
                f"Дата и время не могут быть раньше {min_datetime}."
            )

    if max_datetime:
        if result > get_datetime_setting(max_datetime, "max"):
            raise ValidationError(
                f"Дата и время не могут быть позже {max_datetime}."
            )

    return result.isoformat()

