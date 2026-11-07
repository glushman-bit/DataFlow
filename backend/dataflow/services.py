from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation


def validate_record_values(table, values):
    """Проверяет значения записи по структуре пользовательской таблицы."""

    if not isinstance(values, dict):
        raise ValidationError("Значения записи должны быть словарём.")

    fields = table.fields.all()

    errors = {}
    validated_values = {}

    # Получаем имена полей, размещенных в таблице
    allowed_fields = {field.name for field in fields}

    # Проверяем неизвестные поля
    for name in values:
        if name not in allowed_fields:
            errors[name] = "Такого поля нет в таблице."

    # Проверяем обязательные поля
    for field in fields:
        value = values.get(field.name)

        if field.required and value in (None, ""):
            errors[field.name] = "Поле обязательно для заполнения."

        elif field.name in values:
            validated_values[field.name] = value

    if errors:
        raise ValidationError(errors)

    return validated_values


def validate_field_value(field, value):
    """Проверяет и преобразует значение согласно типу поля."""

    if field.field_type == "text":
        if not isinstance(value, str):
            raise ValidationError("Ожидается текст.")

        return value

    if field.field_type == "integer":
        if isinstance(value, bool):
            raise ValidationError("Ожидается целое число.")

        try:
            return int(value)

        except (ValueError, TypeError):
            raise ValidationError("Ожидается целое число.")

    if field.field_type == "decimal":
        if isinstance(value, bool):
            raise ValidationError("Ожидается десятичное число.")

        try:
            return Decimal(value)

        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError("Ожидается десятичное число.")

    raise ValidationError("Неизвестный тип поля.")
