from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError


def validate_integer(field, value):
    """Проверяет целое число и его настройки."""

    if isinstance(value, bool):
        raise ValidationError("Ожидается целое число.")

    try:
        result = int(value)

        if isinstance(value, (float, Decimal)) and value != result:
            raise ValidationError("Ожидается целое число.")

        return validate_numeric_limits(field, result)

    except (ValueError, TypeError, OverflowError):
        raise ValidationError("Ожидается целое число.")


def validate_decimal(field, value):
    """Проверяет десятичное число и его настройки."""

    if isinstance(value, bool):
        raise ValidationError("Ожидается десятичное число.")

    try:
        result = Decimal(str(value))

        if not result.is_finite():
            raise ValidationError("Число должно быть конечным.")

        validate_numeric_limits(field, result)

        return validate_decimal_places(field, result)

    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError("Ожидается десятичное число.")


def validate_numeric_limits(field, value):
    """Проверяет минимальное и максимальное значения."""

    settings = field.settings or {}

    for setting, error_message in [
        ("min", "Значение меньше допустимого минимума."),
        ("max", "Значение больше допустимого максимума."),
    ]:
        limit = settings.get(setting)

        if limit is None:
            continue

        try:
            limit = Decimal(str(limit))

        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(f"Некорректная настройка {setting}.")

        if not limit.is_finite():
            raise ValidationError(f"Некорректная настройка {setting}.")

        if setting == "min" and value < limit:
            raise ValidationError(error_message)

        if setting == "max" and value > limit:
            raise ValidationError(error_message)

    return value


def validate_decimal_places(field, value):
    """Проверяет количество знаков после запятой."""

    settings = field.settings or {}
    decimal_places = settings.get("decimal_places")

    if decimal_places is None:
        return value

    if (
        isinstance(decimal_places, bool)
        or not isinstance(decimal_places, int)
        or decimal_places < 0
    ):
        raise ValidationError("Некорректная настройка decimal_places.")

    actual_places = max(0, -value.as_tuple().exponent)

    if actual_places > decimal_places:
        raise ValidationError(
            f"Допускается не более {decimal_places} знаков после запятой."
        )

    return value
