import pytest
from django.core.exceptions import ValidationError

from dataflow.models import DataField
from dataflow.services.validation import validate_field_value


@pytest.mark.parametrize(
    "value, expected",
    [
        ("+79991234567", "+79991234567"),
        ("+14155552671", "+14155552671"),
    ],
)
def test_validate_phone_success(value, expected):
    """Проверяет корректные международные номера."""

    field = DataField(field_type="phone")

    result = validate_field_value(field, value)

    assert result == expected


@pytest.mark.parametrize(
    "value",
    [
        "123",
        "abcdefgh",
        "+799912345678999",
        "79991234567",
    ],
)
def test_validate_phone_invalid(value):
    """Проверяет отклонение некорректных номеров."""

    field = DataField(field_type="phone")

    with pytest.raises(ValidationError):
        validate_field_value(field, value)


def test_validate_phone_empty_optional():
    """Проверяет пустое значение необязательного поля."""

    field = DataField(field_type="phone", required=False)

    result = validate_field_value(field, "")

    assert result is None


def test_validate_phone_empty_required():
    """Проверяет пустое значение обязательного поля."""

    field = DataField(field_type="phone", required=True)

    with pytest.raises(ValidationError):
        validate_field_value(field, "")
