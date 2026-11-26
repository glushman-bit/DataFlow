import pytest

from dataflow.models import DataRecord, DataField
from dataflow.serializers import DataRecordSerializer, DataFieldSerializer
from .config import data_table, data_field


@pytest.mark.django_db
@pytest.mark.parametrize(
    "min_value, max_value, is_valid",
    [
        # Одинаковый часовой пояс, корректный диапазон.
        (
            "2026-11-19T12:00:00+03:00",
            "2026-11-19T13:00:00+03:00",
            True,
        ),
        # Разные часовые пояса, но один и тот же момент времени.
        (
            "2026-11-19T12:00:00+03:00",
            "2026-11-19T10:00:00+01:00",
            True,
        ),
        # Min позже max с учётом часовых поясов.
        (
            "2026-11-19T12:00:00+03:00",
            "2026-11-19T09:30:00+01:00",
            False,
        ),
        # Оба значения без часового пояса.
        (
            "2026-11-19T12:00:00",
            "2026-11-19T13:00:00",
            True,
        ),
        # Только одно значение содержит часовой пояс.
        (
            "2026-11-19T12:00:00+03:00",
            "2026-11-19T13:00:00",
            False,
        ),
        # Min больше max.
        (
            "2026-11-19T14:00:00+03:00",
            "2026-11-19T13:00:00+03:00",
            False,
        ),
    ],
)
def test_data_field_serializer_datetime_timezone(
    min_value,
    max_value,
    is_valid,
):
    """Проверяет валидацию диапазона datetime с часовыми поясами."""

    data = {
        "name": "event_time",
        "label": "Время события",
        "field_type": "datetime",
        "required": False,
        "order": 1,
        "settings": {
            "min": min_value,
            "max": max_value,
        },
    }

    serializer = DataFieldSerializer(data=data)

    assert serializer.is_valid() is is_valid, serializer.errors


@pytest.mark.django_db
def test_data_field_serializer_partial_update_settings(data_table):
    """Проверяет частичное обновление настроек поля."""

    field = DataField.objects.create(
        table=data_table,
        name="event_time",
        label="Время события",
        field_type="datetime",
        required=False,
        order=1,
        settings={
            "min": "2026-11-19T10:00:00+03:00",
            "max": "2026-11-19T14:00:00+03:00",
        },
    )

    serializer = DataFieldSerializer(
        field,
        data={
            "settings": {
                "min": "2026-11-19T11:00:00+03:00",
                "max": "2026-11-19T14:00:00+03:00",
            }
        },
        partial=True,
    )

    assert serializer.is_valid(), serializer.errors

    updated_field = serializer.save()

    assert updated_field.settings == {
        "min": "2026-11-19T11:00:00+03:00",
        "max": "2026-11-19T14:00:00+03:00",
    }


@pytest.mark.django_db
def test_data_field_serializer_partial_update_invalid_settings(data_table):
    """Проверяет валидацию диапазона при частичном обновлении."""

    field = DataField.objects.create(
        table=data_table,
        name="event_time",
        label="Время события",
        field_type="datetime",
        required=False,
        order=1,
        settings={
            "min": "2026-11-19T10:00:00+03:00",
            "max": "2026-11-19T14:00:00+03:00",
        },
    )

    serializer = DataFieldSerializer(
        field,
        data={
            "settings": {
                "min": "2026-11-19T15:00:00+03:00",
                "max": "2026-11-19T14:00:00+03:00",
            }
        },
        partial=True,
    )

    assert not serializer.is_valid()
    assert "settings" in serializer.errors


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


@pytest.mark.parametrize(
    "field_tipe, value",
    [
        ("decimal", "не число"),
        ("integer", 1.5),
        ("date", 123),
        ("date", "2026-02-30"),
        ("datetime", "не дата"),
    ]
)
def test_data_field_serializer_invalid_min_value(field_tipe, value):
    """Проверка отклонения некорректного минимального ограничения."""

    data = {
        "name": "test_field",
        "label": "Тестовое поле",
        "field_type": field_tipe,
        "required": False,
        "order": 1,
        "settings": {
            "min": value,
        },
    }

    serializer = DataFieldSerializer(data=data)

    assert not serializer.is_valid()
    assert "settings" in serializer.errors


@pytest.mark.parametrize(
    "field_type, settings",
    [
        # Некорректные ограничения длины.
        ("text", {"min_length": -1}),
        ("text", {"max_length": True}),

        # Минимальная длина больше максимальной.
        ("text", {"min_length": 20, "max_length": 10}),

        # Некорректное количество знаков после запятой.
        ("decimal", {"decimal_places": True}),
        ("decimal", {"decimal_places": -1}),
        ("decimal", {"decimal_places": 1.5}),

        # Некорректный auto_now.
        ("date", {"auto_now": "true"}),
        ("datetime", {"auto_now": 1}),
    ],
)
def test_data_field_serializer_invalid_type_settings(field_type, settings):
    """Проверка отклонения некорректных настроек типов полей."""

    data = {
        "name": "test_field",
        "label": "Тестовое поле",
        "field_type": field_type,
        "required": False,
        "order": 1,
        "settings": settings,
    }

    serializer = DataFieldSerializer(data=data)

    assert not serializer.is_valid()
    assert "settings" in serializer.errors
