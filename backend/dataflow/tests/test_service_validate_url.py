import pytest
from django.core.exceptions import ValidationError

from dataflow.models import DataField
from dataflow.services.validation import validate_field_value


@pytest.mark.parametrize(
    "value, expected",
    [
        ("https://example.com", "https://example.com"),
        ("http://example.com", "http://example.com"),
        ("https://www.google.com/search?q=test",
         "https://www.google.com/search?q=test"),
        (" https://example.com ", "https://example.com"),
    ],
)
def test_validate_url_success(value, expected):
    """Проверяет корректные ссылки."""

    field = DataField(field_type="url")

    result = validate_field_value(field, value)

    assert result == expected


@pytest.mark.parametrize(
    "value",
    [
        "example.com",
        "not-a-url",
        "https://",
        "http://example",
        "ftp://example.com",
    ],
)
def test_validate_url_invalid(value):
    """Проверяет отклонение некорректных ссылок."""

    field = DataField(field_type="url")

    with pytest.raises(ValidationError):
        validate_field_value(field, value)


def test_validate_url_empty_optional():
    """Проверяет пустое значение необязательного поля."""

    field = DataField(field_type="url", required=False)

    result = validate_field_value(field, "")

    assert result is None


def test_validate_url_empty_required():
    """Проверяет пустое значение обязательного поля."""

    field = DataField(field_type="url", required=True)

    with pytest.raises(ValidationError):
        validate_field_value(field, "")