from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from dataflow.models import DataField
from dataflow.services.validation import validate_field_value


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
