import pytest
from django.contrib.auth import get_user_model

from dataflow.models import DataRecord, DataTable
from dataflow.services import delete_record
from .config import data_table


@pytest.mark.django_db
def test_delete_record_success(data_table):
    """Проверяет успешное удаление записи."""

    user = data_table.owner

    record = DataRecord.objects.create(
        table=data_table,
        values={
            "title": "Заявка на удаление",
            "quantity": 5,
            "price": "1000.00",
        },
    )

    record_id = record.pk

    delete_record(
        user=user,
        table_id=data_table.pk,
        record_id=record_id,
    )

    assert not DataRecord.objects.filter(pk=record_id).exists()


@pytest.mark.django_db
def test_delete_record_not_found(data_table):
    """Проверяет запрет удаления записи из чужой таблицы."""

    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="delete_user",
        password="test_password",
    )

    record = DataRecord.objects.create(
        table=data_table,
        values={
            "title": "Чужая заявка",
            "quantity": 5,
            "price": "1000.00",
        },
    )

    with pytest.raises(DataTable.DoesNotExist):
        delete_record(
            user=user,
            table_id=data_table.pk,
            record_id=record.pk,
        )

    assert DataRecord.objects.filter(pk=record.pk).exists()