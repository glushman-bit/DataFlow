import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError

from dataflow.services.records import create_record
from .config import data_table


@pytest.mark.django_db
def test_create_record_success(data_table):
    """Проверяет успешное создание записи."""

    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="test_user",
        password="test_password",
    )

    data_table.owner = user
    data_table.save(update_fields=["owner"])

    values = {
        "title": "Покраска деталей",
        "quantity": "25",
        "price": "1500.50",
    }

    record = create_record(user, data_table, values)

    assert record.pk is not None
    assert record.table == data_table
    assert record.values == {
        "title": "Покраска деталей",
        "quantity": 25,
        "price": "1500.50",
    }


@pytest.mark.django_db
def test_create_record_permission_denied(data_table):
    """Проверяет запрет создания записи в чужой таблице."""

    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="another_user",
        password="test_password",
    )

    values = {
        "title": "Покраска деталей",
        "quantity": 25,
        "price": "1500.50",
    }

    with pytest.raises(PermissionDenied):
        create_record(user, data_table, values)


@pytest.mark.django_db
def test_create_record_permission_denied(data_table):
    """Проверяет запрет создания записи в чужой таблице."""

    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="another_user",
        password="test_password",
    )

    values = {
        "title": "Покраска деталей",
        "quantity": 25,
        "price": "1500.50",
    }

    with pytest.raises(PermissionDenied):
        create_record(user, data_table, values)


@pytest.mark.django_db
def test_create_record_validation_error(data_table):
    """Проверяет, что некорректные данные не сохраняются."""

    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="validation_user",
        password="test_password",
    )

    data_table.owner = user
    data_table.save(update_fields=["owner"])

    values = {
        "title": "Покраска деталей",
        "quantity": "много",
        "price": "1500.50",
    }

    records_count = data_table.records.count()

    with pytest.raises(ValidationError):
        create_record(user, data_table, values)

    assert data_table.records.count() == records_count
