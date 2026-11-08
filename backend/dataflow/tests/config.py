import pytest

from dataflow.models import DataTable, DataField


@pytest.fixture
def data_table(db, django_user_model):
    """Создаёт тестовую таблицу с несколькими типами полей."""

    user = django_user_model.objects.create_user(
        username="tester",
        password="test_password",
    )

    table = DataTable.objects.create(
        owner=user,
        name="Тестовая таблица",
    )

    DataField.objects.create(
        table=table,
        name="title",
        label="Название",
        field_type="text",
        required=True,
    )

    DataField.objects.create(
        table=table,
        name="quantity",
        label="Количество",
        field_type="integer",
        required=True,
    )

    DataField.objects.create(
        table=table,
        name="price",
        label="Цена",
        field_type="decimal",
        required=False,
    )

    return table