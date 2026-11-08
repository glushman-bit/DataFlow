import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from dataflow.models import DataTable, DataRecord
from dataflow.services import get_user_table, get_user_records, update_record
from .config import data_table


@pytest.mark.django_db
def test_get_user_table_success(data_table):
    """Проверяет получение собственной таблицы."""

    user = data_table.owner

    result = get_user_table(user, data_table.pk)

    assert result == data_table
    assert result.owner == user


@pytest.mark.django_db
def test_get_user_table_not_found(data_table):
    """Проверяет невозможность получить чужую таблицу."""

    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="other_user",
        password="test_password",
    )

    with pytest.raises(DataTable.DoesNotExist):
        get_user_table(user, data_table.pk)


@pytest.mark.django_db
def test_get_user_records_success(data_table):
    """Проверяет получение записей собственной таблицы."""

    user = data_table.owner

    DataRecord.objects.create(
        table=data_table,
        values={
            "title": "Покраска деталей",
            "quantity": 10,
            "price": "1500.50",
        },
    )

    DataRecord.objects.create(
        table=data_table,
        values={
            "title": "Обработка деталей",
            "quantity": 5,
            "price": "1000.00",
        },
    )

    records = get_user_records(user, data_table.pk)

    assert records.count() == 2
    assert all(record.table == data_table for record in records)


@pytest.mark.django_db
def test_get_user_records_not_found(data_table):
    """Проверяет запрет получения записей чужой таблицы."""

    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="records_user",
        password="test_password",
    )

    with pytest.raises(DataTable.DoesNotExist):
        get_user_records(user, data_table.pk)
