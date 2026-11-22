import pytest

from .config import data_table, data_field
from ..models import DataField, DataTable
from ..serializers import DataFieldSerializer


@pytest.mark.parametrize(
    "name",
    [
        "Client",
        "имя",
        "client name",
        "client-name",
        "2client",
        "client.name",
        "client@name",
        "     ",
    ],
)
def test_data_field_serializer_invalid_name(name):
    """Проверяет отклонение технических имен с недопустимым форматом."""

    data = {
        "name": name,
        # Остальные параметры не обязательны
    }

    serializer = DataFieldSerializer(data=data)

    assert not serializer.is_valid()
    assert "name" in serializer.errors


@pytest.mark.parametrize(
    "name",
    [
        "client",
        "client_name",
        "client2",
        "field123",
        "  client  ",
    ],
)
def test_data_field_serializer_valid_name(name):
    """Проверяет допустимые технические имена."""

    data = {
        "name": name,
        "label": "Тестовое поле",
        "field_type": "text",
        "required": False,
        "order": 1,
        "settings": {},
    }

    serializer = DataFieldSerializer(data=data)

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_data_field_serializer_duplicate_name(data_table):
    """Проверяет запрет повторного технического имени в таблице."""

    DataField.objects.create(
        table=data_table,
        name="client",
        label="Клиент",
        field_type="text",
    )

    data = {
        "name": "client",
    }

    serializer = DataFieldSerializer(
        data=data,
        context={"table": data_table},
    )

    assert not serializer.is_valid()
    assert "name" in serializer.errors


@pytest.mark.django_db
def test_data_field_serializer_same_name_in_different_tables(data_table, data_field):
    """Разрешает одинаковые технические имена в разных таблицах."""

    user = data_table.owner

    another_table = DataTable.objects.create(
        owner=user,
        name="Другая таблица",
    )

    DataField.objects.create(
        table=data_table,
        name="client",
        label="Клиент",
        field_type="text",
    )

    serializer = DataFieldSerializer(
        data=data_field,
        context={"table": another_table},
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_data_field_serializer_update_same_name(data_table):
    """Разрешает сохранить прежнее техническое имя при редактировании."""

    field = DataField.objects.create(
        table=data_table,
        name="client",
        label="Клиент",
        field_type="text",
    )

    serializer = DataFieldSerializer(
        instance=field,
        data={"name": "client"},
        partial=True,
        context={"table": data_table},
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_data_field_serializer_update_duplicate_name(data_table):
    """Запрещает использовать имя другого поля при редактировании."""

    DataField.objects.create(
        table=data_table,
        name="client",
        label="Клиент",
        field_type="text",
    )

    field = DataField.objects.create(
        table=data_table,
        name="product",
        label="Товар",
        field_type="text",
    )

    serializer = DataFieldSerializer(
        instance=field,
        data={"name": "client"},
        partial=True,
        context={"table": data_table},
    )

    assert not serializer.is_valid()
    assert "name" in serializer.errors


@pytest.mark.django_db
def test_data_field_serializer_duplicate_label(data_table, data_field):
    """Запрещает повторное отображаемое название в таблице."""

    DataField.objects.create(
        table=data_table,
        name="client",
        label="Клиент",
        field_type="text",
    )

    serializer = DataFieldSerializer(
        data=data_field,
        context={"table": data_table},
    )

    assert not serializer.is_valid()
    assert "label" in serializer.errors


@pytest.mark.django_db
def test_data_field_serializer_duplicate_label_case_insensitive(data_table, data_field):
    """Запрещает повтор названия без учёта регистра."""

    DataField.objects.create(
        table=data_table,
        name="client",
        label="Клиент",
        field_type="text",
    )

    serializer = DataFieldSerializer(
        data=data_field,
        context={"table": data_table},
    )

    assert not serializer.is_valid()
    assert "label" in serializer.errors


@pytest.mark.django_db
def test_data_field_serializer_same_label_in_different_tables(data_table, data_field):
    """Разрешает одинаковые названия в разных таблицах."""

    from dataflow.models import DataTable

    another_table = DataTable.objects.create(
        owner=data_table.owner,
        name="Другая таблица",
    )

    DataField.objects.create(
        table=data_table,
        name="client",
        label="Клиент",
        field_type="text",
    )

    serializer = DataFieldSerializer(
        data=data_field,
        context={"table": another_table},
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_data_field_serializer_update_same_label(data_table):
    """Разрешает сохранить прежнее название при обновлении поля."""

    field = DataField.objects.create(
        table=data_table,
        name="client",
        label="Клиент",
        field_type="text",
    )

    serializer = DataFieldSerializer(
        field,
        data={"label": "Клиент"},
        context={"table": data_table},
        partial=True,
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_data_field_serializer_update_duplicate_label(data_table):
    """Запрещает изменить название на уже занятое."""

    DataField.objects.create(
        table=data_table,
        name="client",
        label="Клиент",
        field_type="text",
    )

    field = DataField.objects.create(
        table=data_table,
        name="product",
        label="Товар",
        field_type="text",
    )

    serializer = DataFieldSerializer(
        field,
        data={"label": "Клиент"},
        context={"table": data_table},
        partial=True,
    )

    assert not serializer.is_valid()
    assert "label" in serializer.errors


def test_data_field_serializer_empty_label(data_table):
    """Проверка на пустую строку имени или строку из пробелов."""

    serializer = DataFieldSerializer(
        data={
            "name": "client",
            "label": "    ",
            "field_type": "text",
        },
        context={"table": data_table},
    )

    assert not serializer.is_valid()
    assert "label" in serializer.errors
