import pytest
from django.core.exceptions import ValidationError

from dataflow.models import DataField
from dataflow.services.validation import validate_field_value


@pytest.mark.parametrize(
    "value, settings, is_valid",
    [
        ("2026-11-09", {"min": "2026-11-10"}, False),
        ("2026-11-21", {"max": "2026-11-20"}, False),
        (
            "2026-11-15",
            {"min": "2026-11-10", "max": "2026-11-20"},
            True,
        ),
        ("2026-11-10", {"min": "2026-11-10"}, True),
        ("2026-11-20", {"max": "2026-11-20"}, True),
    ],
)
def test_validate_date_range(value, settings, is_valid):
    """Проверяет ограничения минимальной и максимальной даты."""

    field = DataField(
        field_type="date",
        settings=settings,
    )

    if is_valid:
        assert validate_field_value(field, value) == value
    else:
        with pytest.raises(ValidationError):
            validate_field_value(field, value)


@pytest.mark.parametrize(
    "value, settings, is_valid",
    [
        (
            "2026-11-14T14:59:59",
            {"min": "2026-11-14T15:00:00"},
            False,
        ),
        (
            "2026-11-14T15:00:01",
            {"max": "2026-11-14T15:00:00"},
            False,
        ),
        (
            "2026-11-14T15:30:00",
            {
                    "min": "2026-11-14T15:00:00",
                    "max": "2026-11-14T16:00:00",
            },
            True,
        ),
        (
            "2026-11-14T15:00:00",
            {"min": "2026-11-14T15:00:00"},
            True,
        ),
        (
            "2026-11-14T16:00:00",
            {"max": "2026-11-14T16:00:00"},
            True,
        ),
    ],
)
def test_validate_datetime_range(value, settings, is_valid):
    """Проверяет ограничения минимальной и максимальной даты и времени."""

    field = DataField(
        field_type="datetime",
        settings=settings,
    )

    if is_valid:
        assert validate_field_value(field, value) == value

    else:
        with pytest.raises(ValidationError):
            validate_field_value(field, value)


@pytest.mark.parametrize(
    "settings",
    [
        {"min": "14.11.2026"},
        {"max": "не дата"},
    ],
)
def test_validate_date_invalid_settings(settings):
    """Проверяет отклонение некорректных настроек даты."""

    field = DataField(
        field_type="date",
        settings=settings,
    )

    with pytest.raises(ValidationError):
        validate_field_value(field, "2026-11-15")


@pytest.mark.parametrize(
    "settings",
    [
        {"min": "14.11.2026 15:00"},
        {"max": "не дата"},
    ],
)
def test_validate_datetime_invalid_settings(settings):
    """Проверяет отклонение некорректных настроек даты и времени."""

    field = DataField(
        field_type="datetime",
        settings=settings,
    )

    with pytest.raises(ValidationError):
        validate_field_value(field, "2026-11-15T15:00:00")
