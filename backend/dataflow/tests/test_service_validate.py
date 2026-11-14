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
        ("date", "2026-11-14", "2026-11-14"),
        ("datetime", "2026-11-14T15:30:00", "2026-11-14T15:30:00"),
        ("boolean", True, True),
        ("integer", "50", 50),
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
        ("date", "14.11.2026"),
        ("datetime", "не дата"),
        ("boolean", "да"),
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


@pytest.mark.parametrize("empty_value", [None, "", "   "])
@pytest.mark.django_db
def test_validate_record_values_required_field_empty(data_table, empty_value):
    """Проверяет пустое обязательное поле."""

    values = {
        "title": "Покраска деталей",
        "quantity": empty_value,
        "price": "1500.50",
    }

    with pytest.raises(ValidationError) as error:
        validate_record_values(data_table, values)

    assert "quantity" in error.value.message_dict


@pytest.mark.parametrize("empty_value", [None, "", "   "])
@pytest.mark.django_db
def test_validate_record_values_optional_field_empty(data_table, empty_value):
    """Проверяет пустое необязательное поле."""

    values = {
        "title": "Покраска деталей",
        "quantity": "25",
        "price": empty_value,
    }

    result = validate_record_values(data_table, values)

    assert result == {
        "title": "Покраска деталей",
        "quantity": 25,
        "price": None,
    }


@pytest.mark.parametrize(
    "value, expected_error",
    [
        ("0", "Значение меньше допустимого минимума."),
        ("101", "Значение больше допустимого максимума."),
    ],
)
def test_validate_integer_limits(value, expected_error):
    """Проверяет минимальное и максимальное значения целого числа."""

    field = DataField(
        field_type="integer",
        settings={"min": 1, "max": 100},
    )

    with pytest.raises(ValidationError) as error:
        validate_field_value(field, value)

    assert expected_error in error.value.messages


@pytest.mark.parametrize(
    "value, expected_error",
    [
        ("-1", "Значение меньше допустимого минимума."),
        ("1001", "Значение больше допустимого максимума."),
    ],
)
def test_validate_decimal_limits(value, expected_error):
    """Проверяет минимальное и максимальное значения десятичного числа."""

    field = DataField(
        field_type="decimal",
        settings={"min": 0, "max": 1000},
    )

    with pytest.raises(ValidationError) as error:
        validate_field_value(field, value)

    assert expected_error in error.value.messages


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1500", Decimal("1500")),
        ("1500.5", Decimal("1500.5")),
        ("1500.50", Decimal("1500.50")),
    ],
)
def test_validate_decimal_places_success(value, expected):
    """Проверяет допустимое количество знаков после запятой."""

    field = DataField(
        field_type="decimal",
        settings={"decimal_places": 2},
    )

    result = validate_field_value(field, value)

    assert result == expected


def test_validate_decimal_places_error():
    """Проверяет отклонение лишних знаков после запятой."""

    field = DataField(
        field_type="decimal",
        settings={"decimal_places": 2},
    )

    with pytest.raises(ValidationError) as error:
        validate_field_value(field, "1500.555")

    assert "Допускается не более 2 знаков после запятой." in error.value.messages


@pytest.mark.parametrize(
    "settings",
    [
        {"min": "abc"},
        {"max": "abc"},
        {"min": "NaN"},
        {"max": "Infinity"},
    ]
)
def test_validate_numeric_limits_invalid_settings(settings):
    """Проверяет некорректные настройки числовых ограничений."""

    field = DataField(
        field_type="integer",
        settings=settings,
    )

    with pytest.raises(ValidationError) as error:
        validate_field_value(field, 50)

    assert "Некорректная настройка" in error.value.messages[0]


@pytest.mark.parametrize(
    "decimal_places",
    [
        -1,
        1.5,
        "2",
        True,
    ],
)
def test_validate_decimal_places_invalid_settings(decimal_places):
    """Проверяет некорректную настройку количества знаков после запятой."""

    field = DataField(
        field_type="decimal",
        settings={"decimal_places": decimal_places},
    )

    with pytest.raises(ValidationError) as error:
        validate_field_value(field, "1500.50")

    assert "Некорректная настройка decimal_places." in error.value.messages


@pytest.mark.parametrize(
    "value",
    [
        "NaN",
        "Infinity",
        "-Infinity",
    ]
)
def test_validate_decimal_not_finite(value):
    """Проверяет отклонение бесконечных и неопределённых чисел."""

    field = DataField(field_type="decimal")

    with pytest.raises(ValidationError) as error:
        validate_field_value(field, value)

    assert "Число должно быть конечным." in error.value.messages
