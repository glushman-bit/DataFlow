import pytest
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError

from dataflow.models import DataTable


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
