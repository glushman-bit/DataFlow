import pytest
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError

from dataflow.models import DataTable, DataField, DataRecord

User = get_user_model()


@pytest.mark.django_db        # разрешает тесту обращаться к базе данных.
def test_create_data_table():
    """Проверяет создание пользовательской таблицы."""

    user = User.objects.create_user(
        username='Ivan',
        password='test-password'
    )
    table = DataTable.objects.create(
        owner=user,
        name='Заявки'
    )

    assert table.pk is not None
    assert table.name == 'Заявки'
    assert table.owner == user
    assert table.settings == {}


@pytest.mark.django_db
def test_data_table_name_unique_per_owner():
    """Один пользователь не может создать две таблицы с одинаковым именем."""

    user = User.objects.create_user(
        username='Ivan',
        password='test-password'
    )

    DataTable.objects.create(owner=user, name='Заявки')

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            # transaction.atomic() - При нарушении ограничения PostgreSQL
            # выбрасывает IntegrityError. Вложенная транзакция позволяет
            # перехватить ошибку, не нарушая работу внешней транзакции теста.
            DataTable.objects.create(owner=user, name='Заявки')


@pytest.mark.django_db
def test_different_users_can_have_tables_with_same_name():
    """Разные пользователи могут иметь таблицы с одинаковыми именами."""

    user1 = User.objects.create_user(
        username='Ivan',
        password='test-password'
    )
    user2 = User.objects.create_user(
        username='Alex',
        password='test-password'
    )

    table1 = DataTable.objects.create(owner=user1, name='Заявки')
    table2 = DataTable.objects.create(owner=user2, name='Заявки')

    assert table1.pk != table2.pk
    assert table1.name == table2.name
    assert table1.owner != table2.owner


@pytest.mark.django_db
def test_create_data_field():
    """Проверяет создание поля пользовательской таблицы."""

    user = User.objects.create_user(
        username="ivan",
        password="test-password",
    )
    table = DataTable.objects.create(
        owner=user,
        name="Заявки",
    )
    field = DataField.objects.create(
        table=table,
        name="title",
        label="Название заявки",
        field_type="text",
        required=True,
        order=1,
    )

    assert field.pk is not None
    assert field.table == table
    assert field.name == "title"
    assert field.label == "Название заявки"
    assert field.field_type == "text"
    assert field.required is True
    assert field.order == 1
    assert field.settings == {}


@pytest.mark.django_db
def test_data_field_name_unique_per_table():
    """Имена полей должны быть уникальными внутри таблицы."""

    user = User.objects.create_user(
        username='Ivan',
        password='test-password'
    )
    table = DataTable.objects.create(
        owner=user,
        name='Заявки'
    )
    DataField.objects.create(
        table=table,
        name='title',
        label='Название'
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            DataField.objects.create(
                table=table,
                name='title',
                label='Другое название'
            )


@pytest.mark.django_db
def test_different_tables_can_have_fields_with_same_name():
    """Разные таблицы могут иметь поля с одинаковыми именами."""

    user = User.objects.create_user(
        username="ivan",
        password="test-password",
    )
    table1 = DataTable.objects.create(
        owner=user,
        name="Заявки",
    )
    table2 = DataTable.objects.create(
        owner=user,
        name="Клиенты",
    )
    field1 = DataField.objects.create(
        table=table1,
        name="title",
        label="Название заявки",
    )
    field2 = DataField.objects.create(
        table=table2,
        name="title",
        label="Название клиента",
    )

    assert field1.pk != field2.pk
    assert field1.name == field2.name
    assert field1.table != field2.table


@pytest.mark.django_db
def test_create_data_record():
    """Проверяет создание записи с данными в JSONField."""

    user = User.objects.create_user(
        username="ivan",
        password="test-password",
    )

    table = DataTable.objects.create(
        owner=user,
        name="Заявки",
    )

    DataField.objects.create(
        table=table,
        name="title",
        label="Название заявки",
        field_type="text",
        required=True,
        order=1,
    )

    values = {
        "title": "Покраска деталей",
        "quantity": 10,
        "price": "1500.50",
    }

    record = DataRecord.objects.create(
        table=table,
        values=values,
    )

    assert record.pk is not None
    assert record.table == table
    assert record.values == values
    assert record.values["title"] == "Покраска деталей"
    assert record.values["quantity"] == 10
    assert record.values["price"] == "1500.50"
