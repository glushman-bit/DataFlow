from django.core.exceptions import ValidationError, PermissionDenied
from decimal import Decimal, InvalidOperation
from datetime import datetime, date

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

            return validate_numeric_limits(field, result)

        except (ValueError, TypeError, OverflowError):
            raise ValidationError("Ожидается целое число.")

    if field.field_type == "decimal":
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

    if field.field_type == "date":

        try:
            result = date.fromisoformat(value)
            return result.isoformat()

        except (ValueError, TypeError):
            raise ValidationError("Ожидается дата в формате ГГГГ-ММ-ДД.")

    if field.field_type == "datetime":

        try:
            result = datetime.fromisoformat(value)
            return result.isoformat()

        except (ValueError, TypeError):
            raise ValidationError("Ожидается дата и время в формате ISO.")

    if field.field_type == "boolean":

        if not isinstance(value, bool):
            raise ValidationError("Ожидается логическое значение.")

        return value

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

    actual_places = max(0, -value.as_tuple().exponent)  # as_tuple().exponent — он позволяет определить количество знаков после запятой без округления числа

    if actual_places > decimal_places:
        raise ValidationError(
            f"Допускается не более {decimal_places} знаков после запятой."
        )

    return value
