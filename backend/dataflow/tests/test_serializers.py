from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from rest_framework import serializers

from dataflow.serializers import DataTableSerializer, DataFieldSerializer, DataRecordSerializer
from .config import data_table
from ..models import DataRecord


@pytest.mark.django_db
def test_data_table_serializer_create():
    """Проверяет создание таблицы через сериализатор."""

    user = get_user_model().objects.create_user(
        username="serializer_user",
        password="test_password",
    )

    data = {
        "name": "Новая таблица",
        "settings": {
            "view": "table",
        },
    }

    serializer = DataTableSerializer(data=data)

    assert serializer.is_valid(), serializer.errors

    table = serializer.save(owner=user)

    assert table.name == "Новая таблица"
    assert table.settings == {"view": "table"}
    assert table.owner == user


def test_data_table_serializer_invalid_data():
    """Проверяет отклонение некорректных данных."""

    data = {
        "settings": {
            "view": "table",
        }
    }

    serializer = DataTableSerializer(data=data)

    assert not serializer.is_valid()
    assert "name" in serializer.errors


@pytest.mark.django_db
def test_data_field_serializer_create(data_table):
    """Проверяет создание поля через сериализатор."""

    data = {
        "name": "status",
        "label": "Статус",
        "field_type": "text",
        "required": True,
        "order": 1,
        "settings": {},
    }

    serializer = DataFieldSerializer(data=data)

    assert serializer.is_valid(), serializer.errors

    field = serializer.save(table=data_table)

    assert field.name == "status"
    assert field.label == "Статус"
    assert field.field_type == "text"
    assert field.required is True
    assert field.table == data_table


def test_data_field_serializer_invalid_data():
    """Проверяет отклонение некорректных данных."""

    data = {
        "name": "status",
        "field_type": "text",
    }

    serializer = DataFieldSerializer(data=data)

    assert not serializer.is_valid()
    assert "label" in serializer.errors


@pytest.mark.django_db
def test_data_record_serializer_create(data_table):
    """Проверяет создание записи через сериализатор."""

    data = {
        "values": {
            "title": "Покраска деталей",
            "quantity": "10",
            "price": "1500.50",
        },
    }

    request = SimpleNamespace(user=data_table.owner)

    serializer = DataRecordSerializer(
        data=data,
        context={
            "table": data_table,
            "request": request,
        },
    )

    assert serializer.is_valid(), serializer.errors

    record = serializer.save()

    assert record.table == data_table
    assert record.values["title"] == "Покраска деталей"
    assert record.values["quantity"] == 10
    assert record.values["price"] == "1500.50"

"""
В отличие от предыдущих сериализаторов, DataRecordSerializer использует context.
- table — таблица, в которую добавляем запись.
- request — объект с пользователем, от имени которого создаётся запись.
SimpleNamespace позволяет создать простой объект с атрибутом user, не создавая полноценный HTTP-запрос.
Мы проверяем не только создание записи, но и результат работы validate_record_values() и преобразование 
Decimal в строку перед сохранением в JSONField.
"""


@pytest.mark.django_db
def test_data_record_serializer_invalid_values(data_table):
    """Проверяет отклонение некорректных значений."""

    data = {
        "values": {
            "title": "Покраска деталей",
            "quantity": "много",
            "price": "1500.50",
        },
    }

    serializer = DataRecordSerializer(
        data=data,
        context={"table": data_table},
    )

    assert not serializer.is_valid()
    assert "values" in serializer.errors


def test_data_record_serializer_without_table():
    """Проверяет ошибку при отсутствии таблицы в context."""

    data = {
        "values": {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": "1500.50",
        },
    }

    serializer = DataRecordSerializer(data=data)

    assert not serializer.is_valid()
    assert "values" in serializer.errors


@pytest.mark.django_db
def test_data_record_serializer_without_request(data_table):
    """Проверяет ошибку при отсутствии request в context."""

    data = {
        "values": {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": "1500.50",
        },
    }

    serializer = DataRecordSerializer(
        data=data,
        context={"table": data_table},
    )

    assert serializer.is_valid(), serializer.errors

    with pytest.raises(serializers.ValidationError):
        serializer.save()

"""
- Данные корректны — is_valid() возвращает True.
- При вызове save() запускается create().
- create() обнаруживает отсутствие request и выдаёт ожидаемую ошибку.
"""


@pytest.mark.django_db
def test_data_record_serializer_update(data_table):
    """Проверяет обновление записи через сериализатор."""

    record = DataRecord.objects.create(
        table=data_table,
        values={
            "title": "Старая заявка",
            "quantity": 5,
            "price": "1000.00",
        },
    )

    data = {
        "values": {
            "title": "Новая заявка",
            "quantity": 10,
            "price": "2500.50",
        },
    }

    serializer = DataRecordSerializer(
        instance=record,
        data=data,
        context={"table": data_table},
    )

    assert serializer.is_valid(), serializer.errors

    updated_record = serializer.save()

    assert updated_record.values["title"] == "Новая заявка"
    assert updated_record.values["quantity"] == 10
    assert updated_record.values["price"] == "2500.50"


@pytest.mark.django_db
def test_data_record_serializer_patch_merge(data_table):
    """Проверяет объединение значений при частичном обновлении."""

    record = DataRecord.objects.create(
        table=data_table,
        values={
            "title": "Старая заявка",
            "quantity": 5,
            "price": "1000.00",
        },
    )

    data = {
        "values": {
            "title": "Обновлённая заявка",
        },
    }

    serializer = DataRecordSerializer(
        instance=record,
        data=data,
        partial=True,
        context={"table": data_table},
    )

    assert serializer.is_valid(), serializer.errors

    updated_record = serializer.save()

    assert updated_record.values["title"] == "Обновлённая заявка"
    assert updated_record.values["quantity"] == 5
    assert updated_record.values["price"] == "1000.00"

"""
- partial=True включает режим частичного обновления.
- Передаём только title.
- quantity и price должны сохраниться из старой записи.
"""


@pytest.mark.django_db
def test_data_record_serializer_put_requires_all_fields(data_table):
    """Проверяет обязательность всех полей при PUT."""

    record = DataRecord.objects.create(
        table=data_table,
        values={
            "title": "Старая заявка",
            "quantity": 5,
            "price": "1000.00",
        },
    )

    data = {
        "values": {
            "title": "Новая заявка",
        },
    }

    serializer = DataRecordSerializer(
        instance=record,
        data=data,
        context={"table": data_table},
    )

    assert not serializer.is_valid()
    assert "values" in serializer.errors