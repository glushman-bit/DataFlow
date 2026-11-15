import pytest
from django.core.exceptions import ValidationError

from dataflow.models import DataField
from dataflow.services.validation import validate_field_value


@pytest.mark.parametrize(
    "value, settings, expected_error",
    [
        ("ab", {"min_length": 3}, "Минимальная длина текста — 3 символов."),
        ("abcdef", {"max_length": 5}, "Максимальная длина текста — 5 символов."),
    ],
)
def test_validate_text_length_error(value, settings, expected_error):
    """Проверяет ограничения минимальной и максимальной длины текста."""

    field = DataField(
        field_type="text",
        settings=settings,
    )

    with pytest.raises(ValidationError) as error:
        validate_field_value(field, value)

    assert expected_error in error.value.messages


@pytest.mark.parametrize(
    "value, settings",
    [
        ("abc", {"min_length": 3}),
        ("abcde", {"max_length": 5}),
        ("abc", {"min_length": 3, "max_length": 5}),
    ],
)
def test_validate_text_length_success(value, settings):
    """Проверяет успешную валидацию граничных значений длины текста."""

    field = DataField(
        field_type="text",
        settings=settings,
    )

    result = validate_field_value(field, value)

    assert result == value


@pytest.mark.parametrize(
    "setting, value",
    [
        ("min_length", -1),
        ("max_length", -1),
        ("min_length", 2.5),
        ("max_length", 2.5),
        ("min_length", "3"),
        ("max_length", "5"),
        ("min_length", True),
        ("max_length", False),
    ],
)
def test_validate_text_invalid_settings(setting, value):
    """Проверяет отклонение некорректных текстовых настроек."""

    field = DataField(
        field_type="text",
        settings={setting: value},
    )

    with pytest.raises(ValidationError) as error:
        validate_field_value(field, "Тест")

    assert f"Некорректная настройка {setting}." in error.value.messages
