import pytest
from django.core.exceptions import ValidationError

from dataflow.models import DataField
from dataflow.services.validation import validate_field_value


@pytest.mark.parametrize(
    "value, expected",
    [
        ("user@example.com", "user@example.com"),
        ("ivan.petrov@gmail.com", "ivan.petrov@gmail.com"),
        ("test+work@example.org", "test+work@example.org"),
        (" user@example.com ", "user@example.com"),
    ],
)
def test_validate_email_success(value, expected):
    """Проверяет корректные адреса электронной почты."""

    field = DataField(field_type="email")

    result = validate_field_value(field, value)

    assert result == expected


@pytest.mark.parametrize(
    "value",
    [
        "invalid",
        "user@",
        "@example.com",
        "user example@example.com",
        "user@example",
    ],
)
def test_validate_email_invalid(value):
    """Проверяет отклонение некорректных адресов."""

    field = DataField(field_type="email")

    with pytest.raises(ValidationError):
        validate_field_value(field, value)


def test_validate_email_empty_optional():
    """Проверяет пустое значение необязательного поля."""

    field = DataField(field_type="email", required=False)

    result = validate_field_value(field, "")

    assert result is None


def test_validate_email_empty_required():
    """Проверяет пустое значение обязательного поля."""

    field = DataField(field_type="email", required=True)

    with pytest.raises(ValidationError):
        validate_field_value(field, "")
