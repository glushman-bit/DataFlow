from django.core.exceptions import PermissionDenied
from decimal import Decimal

from dataflow.models import DataRecord, DataTable
from dataflow.services.validation import validate_record_values


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
