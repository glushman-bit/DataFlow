from django.core.exceptions import ValidationError

from .boolean import validate_boolean
from .date import validate_date, validate_datetime
from .email import validate_email_value
from .numeric import validate_integer, validate_decimal
from .text import validate_text
from .phone import validate_phone
from .url import validate_url_value


def validate_record_values(table, values):
    """Проверяет структуру и значения записи."""

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

    # Проверяем обязательность и типы значений
    for field in fields:
        value = values.get(field.name)

        is_empty = (
            value is None
            or (isinstance(value, str) and not value.strip())
        )

        if is_empty:
            if field.required:
                errors[field.name] = "Поле обязательно для заполнения."

            elif field.name in values:
                validated_values[field.name] = None

            continue

        try:
            validated_values[field.name] = validate_field_value(
                field, value,
            )

        except ValidationError as error:
            errors[field.name] = error.messages[0]

    if errors:
        raise ValidationError(errors)

    return validated_values


def validate_field_value(field, value):
    """Проверяет и преобразует значение согласно типу поля."""

    if field.field_type == "text":
        return validate_text(field, value)

    if field.field_type == "integer":
        return validate_integer(field, value)

    if field.field_type == "decimal":
        return validate_decimal(field, value)

    if field.field_type == "date":
        return validate_date(field, value)

    if field.field_type == "datetime":
        return validate_datetime(field, value)

    if field.field_type == "boolean":
        return validate_boolean(field, value)

    if field.field_type == "phone":
        return validate_phone(field, value)

    if field.field_type == "email":
        return validate_email_value(field, value)

    if field.field_type == "url":
        return validate_url_value(field, value)

    raise ValidationError("Неизвестный тип поля.")
