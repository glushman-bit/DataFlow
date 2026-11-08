import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from dataflow.models import DataRecord, DataTable
from dataflow.services import update_record
from .config import data_table


@pytest.mark.django_db
def test_update_record_success(data_table):
    """Проверяет успешное обновление записи."""

    user = data_table.owner

    record = DataRecord.objects.create(
        table=data_table,
        values={
            "title": "Старая заявка",
            "quantity": 5,
            "price": "1000.00",
        },
    )

    updated_record = update_record(
        user=user,
        table_id=data_table.pk,
        record_id=record.pk,
        values={
            "title": "Новая заявка",
            "quantity": "10",
            "price": "2500.50",
        },
    )

    assert updated_record.pk == record.pk
    assert updated_record.values == {
        "title": "Новая заявка",
        "quantity": 10,
        "price": "2500.50",
    }


@pytest.mark.django_db
def test_update_record_validation_error(data_table):
    """Проверяет, что при ошибке валидации запись не изменяется."""

    user = data_table.owner

    record = DataRecord.objects.create(
        table=data_table,
        values={
            "title": "Старая заявка",
            "quantity": 5,
            "price": "1000.00",
        },
    )

    with pytest.raises(ValidationError):
        update_record(
            user=user,
            table_id=data_table.pk,
            record_id=record.pk,
            values={
                "title": "Новая заявка",
                "quantity": "много",
                "price": "2500.50",
            },
        )

    record.refresh_from_db()

    assert record.values == {
        "title": "Старая заявка",
        "quantity": 5,
        "price": "1000.00",
    }


@pytest.mark.django_db
def test_update_record_not_found(data_table):
    """Проверяет запрет обновления записи из чужой таблицы."""

    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="update_user",
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
        update_record(
            user=user,
            table_id=data_table.pk,
            record_id=record.pk,
            values={
                "title": "Изменённая заявка",
                "quantity": 10,
                "price": "2000.00",
            },
        )
