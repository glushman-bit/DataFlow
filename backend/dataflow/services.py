from django.core.exceptions import ValidationError, PermissionDenied
from decimal import Decimal, InvalidOperation

from dataflow.models import DataRecord, DataTable


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
            result = int(value)

            if isinstance(value, (float, Decimal)) and value != result:
                raise ValidationError("Ожидается целое число.")

            return result

        except (ValueError, TypeError, OverflowError):
            raise ValidationError("Ожидается целое число.")

    if field.field_type == "decimal":
        if isinstance(value, bool):
            raise ValidationError("Ожидается десятичное число.")

        try:
            return Decimal(value)

        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError("Ожидается десятичное число.")

    raise ValidationError("Неизвестный тип поля.")


def create_record(user, table, values):
    """Проверяет права доступа, валидирует и сохраняет запись."""

    if table.owner_id != user.pk:
        raise PermissionDenied(
            "У вас нет доступа к этой таблице."
        )

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


def get_user_table(user, table_id):
    """Возвращает таблицу, принадлежащую пользователю."""

    return DataTable.objects.get(
        pk=table_id,
        owner=user,
    )


def get_user_records(user, table_id):
    """Возвращает записи из таблицы пользователя."""

    table = get_user_table(user, table_id)

    return table.records.all()


def update_record(user, table_id, record_id, values):
    """Проверяет права доступа, валидирует и обновляет запись."""

    table = get_user_table(user, table_id)

    record = table.records.get(pk=record_id)

    validated_values = validate_record_values(table, values)

    json_values = {
        name: str(value) if isinstance(value, Decimal) else value
        for name, value in validated_values.items()
    }

    record.values = json_values
    record.save(update_fields=["values", "updated_at"])

    return record


def delete_record(user, table_id, record_id):
    """Проверяет права доступа и удаляет запись."""

    table = get_user_table(user, table_id)

    record = table.records.get(pk=record_id)

    record.delete()
