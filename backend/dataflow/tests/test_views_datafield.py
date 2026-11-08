from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from dataflow.models import DataTable, DataField


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

    def test_data_field_list_authenticated(self):
        """Проверка получения списка полей."""

        response = self.client.get(
            f"/api/tables/{self.table.id}/fields/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "title")
        self.assertEqual(response.data[0]["label"], "Название")


    def test_data_field_list_foreign_table(self):
        """Проверка недоступности полей чужой таблицы."""

        another_user = get_user_model().objects.create_user(
            username="another_user",
            password="test_password",
        )

        another_table = DataTable.objects.create(
            owner=another_user,
            name="Чужая таблица",
        )

        DataField.objects.create(
            table=another_table,
            name="price",
            label="Цена",
            field_type="decimal",
        )

        response = self.client.get(
            f"/api/tables/{another_table.id}/fields/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)


    def test_data_field_create_authenticated(self):
        """Проверка создания нового поля."""

        data = {
            "name": "price",
            "label": "Цена",
            "field_type": "decimal",
            "required": True,
            "order": 2,
        }

        response = self.client.post(
            f"/api/tables/{self.table.id}/fields/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "price")

        self.assertTrue(
            DataField.objects.filter(
                table=self.table,
                name="price",
            ).exists()
        )

# """
# - self.client.post() отправляет POST-запрос. format="json" указывает
# DRF использовать JSON.
# - assertTrue(...exists()) проверяет, что поле действительно появилось
# в базе данных, а не просто вернулось в ответе API.
# """

    def test_data_field_update_authenticated(self):
        """Проверка частичного обновления поля."""

        field = self.table.fields.get(name="title")

        data = {
            "label": "Новое название",
            "required": True,
        }

        response = self.client.patch(
            f"/api/tables/{self.table.id}/fields/{field.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["label"], "Новое название")
        self.assertTrue(response.data["required"])

        field.refresh_from_db()

        self.assertEqual(field.label, "Новое название")
        self.assertTrue(field.required)

# """
# - self.table.fields.get(...) — получаем поле через обратную связь
# related_name="fields".
# - refresh_from_db() — обновляем объект из базы, чтобы проверить именно
# сохранённые изменения, а не локальное состояние Python-объекта.
# """

    def test_data_field_delete_authenticated(self):
        """Проверка удаления поля."""

        field = self.table.fields.get(name="title")

        response = self.client.delete(
            f"/api/tables/{self.table.id}/fields/{field.id}/"
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            DataField.objects.filter(pk=field.id).exists()
        )

# """
# - API вернул 204 No Content — запрос выполнен успешно, тело ответа отсутствует.
# - assertFalse(...exists()) — поля действительно больше нет в базе.
# """


