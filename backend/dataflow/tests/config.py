import pytest
from django.contrib.auth import get_user_model

from dataflow.models import DataTable, DataField
from rest_framework.test import APITestCase


class DataFieldViewSetTests(APITestCase):

    def setUp(self):
        """Подготовка данных перед каждым тестом."""

        User = get_user_model()

        self.user = User.objects.create_user(
            username="field_user",
            password="test_password",
        )

        self.table = DataTable.objects.create(
            owner=self.user,
            name="Моя таблица",
        )

        DataField.objects.create(
            table=self.table,
            name="title",
            label="Название",
            field_type="text",
        )

        self.client.force_authenticate(user=self.user)


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


@pytest.fixture
def data_field():
    """Тестовые данные поля."""

    data = {
        "name": "customer",
        "label": "Клиент",
        "field_type": "text",
        "required": False,
        "order": 1,
        "settings": {},
    }

    return data


