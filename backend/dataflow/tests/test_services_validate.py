from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from dataflow.models import DataField
from dataflow.services import validate_field_value, validate_record_values

from .config import data_table

@pytest.mark.parametrize(
    "field_type, value, expected",
    [
        ("text", "Покраска деталей", "Покраска деталей"),
        ("integer", "25", 25),
        ("integer", 100, 100),
        ("decimal", "1500.50", Decimal("1500.50")),
        ("decimal", 2000, Decimal("2000")),
    ],
)
def test_validate_field_value_success(field_type, value, expected):
    """Проверяет успешную валидацию значений."""

    field = DataField(field_type=field_type)

    result = validate_field_value(field, value)

    assert result == expected
    assert type(result) is type(expected)


@pytest.mark.parametrize(
    "field_type, value",
    [
        ("text", 123),
        ("integer", "abc"),
        ("integer", 12.5),
        ("integer", True),
        ("decimal", "abc"),
        ("decimal", True),
        ("unknown", "тест"),
    ],
)
def test_validate_field_value_error(field_type, value):
    """Проверяет отклонение некорректных значений."""

    field = DataField(field_type=field_type)

    with pytest.raises(ValidationError):
        validate_field_value(field, value)


@pytest.mark.django_db
def test_validate_record_values_success(data_table):
    """Проверяет успешную валидацию записи."""

    values = {
        "title": "Покраска деталей",
        "quantity": "25",
        "price": "1500.50",
    }

    result = validate_record_values(data_table, values)

    assert result == {
        "title": "Покраска деталей",
        "quantity": 25,
        "price": Decimal("1500.50"),
    }


@pytest.mark.django_db
def test_validate_record_values_required_field_missing(data_table):
    """Проверяет отсутствие обязательного поля."""

    values = {
        "title": "Покраска деталей",
    }

    with pytest.raises(ValidationError) as error:
        validate_record_values(data_table, values)

    assert "quantity" in error.value.message_dict


@pytest.mark.django_db
def test_validate_record_values_unknown_field(data_table):
    """Проверяет передачу несуществующего поля."""

    values = {
        "title": "Покраска деталей",
        "quantity": 25,
        "unknown": "Тест",
    }

    with pytest.raises(ValidationError) as error:
        validate_record_values(data_table, values)

    assert "unknown" in error.value.message_dict


@pytest.mark.django_db
def test_validate_record_values_invalid_type(data_table):
    """Проверяет некорректный тип значения."""

    values = {
        "title": "Покраска деталей",
        "quantity": "много",
    }

    with pytest.raises(ValidationError) as error:
        validate_record_values(data_table, values)

    assert "quantity" in error.value.message_dict


@pytest.mark.django_db
def test_validate_record_values_not_dict(data_table):
    """Проверяет, что values должен быть словарём."""

    values = ["Покраска деталей", 25, "1500.50"]

    with pytest.raises(ValidationError) as error:
        validate_record_values(data_table, values)

    assert "Значения записи должны быть словарём." in error.value.messages


@pytest.mark.django_db
def test_validate_record_values_required_field_empty(data_table):
    """Проверяет пустое обязательное поле."""

    values = {
        "title": "Покраска деталей",
        "quantity": "",
        "price": "1500.50",
    }

    with pytest.raises(ValidationError) as error:
        validate_record_values(data_table, values)

    assert "quantity" in error.value.message_dict


@pytest.mark.django_db
def test_validate_record_values_optional_field_empty(data_table):
    """Проверяет пустое необязательное поле."""

    values = {
        "title": "Покраска деталей",
        "quantity": "25",
        "price": "",
    }

    result = validate_record_values(data_table, values)

    assert result == {
        "title": "Покраска деталей",
        "quantity": 25,
        "price": None,
    }
