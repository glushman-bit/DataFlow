from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation

from dataflow.models import DataRecord


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

        if value in (None, ""):
            if field.required:
                errors[field.name] = "Поле обязательно для заполнения."

            elif field.name in values:
                validated_values[field.name] = None

            continue

        if field.name not in values:
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


def create_record(table, values):
    """Проверяет и сохраняет новую запись."""

    validated_values = validate_record_values(table, values)

    # Подготавливаем значения для сохранения в JSONField
    json_values = {
        name: str(value) if isinstance(value, Decimal) else value
        for name, value in validated_values.items()
    }

    return DataRecord.objects.create(
        table=table,
        values=json_values,
    )
