from django.contrib.auth import get_user_model

from dataflow.models import DataRecord, DataField, DataTable
from rest_framework.test import APITestCase




class DataRecordViewSetTests(APITestCase):

    def setUp(self):
        """Подготовка данных перед каждым тестом."""

        User = get_user_model()

        self.user = User.objects.create_user(
            username="record_user",
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
            required=True,
        )

        DataField.objects.create(
            table=self.table,
            name="quantity",
            label="Количество",
            field_type="integer",
            required=True,
        )

        self.record = DataRecord.objects.create(
            table=self.table,
            values={
                "title": "Тестовая заявка",
                "quantity": 10,
            },
        )

        self.client.force_authenticate(user=self.user)

    def test_data_record_list_authenticated(self):
        """Проверка получения списка записей."""

        response = self.client.get(
            f"/api/tables/{self.table.id}/records/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]["values"]["title"],
            "Тестовая заявка",
        )

        self.assertEqual(
            response.data[0]["values"]["quantity"],
            10,
        )

    def test_data_record_create_authenticated(self):
        """Проверка создания новой записи."""

        data = {
            "values": {
                "title": "Новая заявка",
                "quantity": 25,
            }
        }

        response = self.client.post(
            f"/api/tables/{self.table.id}/records/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.data["values"]["title"],
            "Новая заявка",
        )

        self.assertEqual(
            response.data["values"]["quantity"],
            25,
        )

        self.assertEqual(
            DataRecord.objects.filter(table=self.table).count(),
            2,
        )

    def test_data_record_update_authenticated(self):
        """Проверка частичного обновления записи."""

        data = {
            "values": {
                "title": "Обновлённая заявка",
            }
        }

        response = self.client.patch(
            f"/api/tables/{self.table.id}/records/{self.record.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["values"]["title"],
            "Обновлённая заявка",
        )

        # Проверяем, что quantity сохранилось.
        self.assertEqual(
            response.data["values"]["quantity"],
            10,
        )

        self.record.refresh_from_db()

        self.assertEqual(
            self.record.values["title"],
            "Обновлённая заявка",
        )

    def test_data_record_update_put(self):
        """Проверка полного обновления записи."""

        data = {
            "values": {
                "title": "Полностью обновлённая заявка",
                "quantity": 50,
            }
        }

        response = self.client.put(
            f"/api/tables/{self.table.id}/records/{self.record.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["values"]["title"],
            "Полностью обновлённая заявка",
        )

        self.assertEqual(
            response.data["values"]["quantity"],
            50,
        )

        self.record.refresh_from_db()

        self.assertEqual(
            self.record.values["quantity"],
            50,
        )

    def test_data_record_delete_authenticated(self):
        """Проверка удаления записи."""

        response = self.client.delete(
            f"/api/tables/{self.table.id}/records/{self.record.id}/"
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            DataRecord.objects.filter(pk=self.record.id).exists()
        )

    def test_data_record_list_foreign_table(self):
        """Проверка доступа к записям чужой таблицы."""

        User = get_user_model()
        another_user = User.objects.create_user(
            username="another_user",
            password="test_password",
        )

        another_table = DataTable.objects.create(
            owner=another_user,
            name="Чужая таблица",
        )

        DataRecord.objects.create(
            table=another_table,
            values={"title": "Чужая заявка"},
        )

        response = self.client.get(
            f"/api/tables/{another_table.id}/records/"
        )

        self.assertEqual(response.status_code, 404)

    def test_data_record_detail_foreign_record(self):
        """Проверка доступа к чужой записи."""

        another_user = get_user_model().objects.create_user(
            username="another_user",
            password="test_password",
        )

        another_table = DataTable.objects.create(
            owner=another_user,
            name="Чужая таблица",
        )

        foreign_record = DataRecord.objects.create(
            table=another_table,
            values={
                "title": "Чужая заявка",
                "quantity": 50,
            },
        )

        response = self.client.get(
            f"/api/tables/{self.table.id}/records/{foreign_record.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_data_record_list_unauthenticated(self):
        """Проверка запрета доступа без авторизации."""

        self.client.force_authenticate(user=None)

        response = self.client.get(
            f"/api/tables/{self.table.id}/records/"
        )

        self.assertEqual(response.status_code, 401)

    def test_data_record_create_unauthenticated(self):
        """Проверка запрета создания записи без авторизации."""

        self.client.force_authenticate(user=None)

        response = self.client.post(
            f"/api/tables/{self.table.id}/records/",
            {
                "values": {
                    "title": "Новая заявка",
                    "quantity": 25,
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

        self.assertEqual(
            DataRecord.objects.filter(table=self.table).count(),
            1,
        )

    def test_data_record_update_unauthenticated(self):
        """Проверка запрета обновления записи без авторизации."""

        self.client.force_authenticate(user=None)

        response = self.client.patch(
            f"/api/tables/{self.table.id}/records/{self.record.id}/",
            {
                "values": {
                    "title": "Изменённая заявка",
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

        self.record.refresh_from_db()

        self.assertEqual(
            self.record.values["title"],
            "Тестовая заявка",
        )

    def test_data_record_delete_unauthenticated(self):
        """Проверка запрета удаления записи без авторизации."""

        self.client.force_authenticate(user=None)

        response = self.client.delete(
            f"/api/tables/{self.table.id}/records/{self.record.id}/"
        )

        self.assertEqual(response.status_code, 401)

        self.assertTrue(
            DataRecord.objects.filter(pk=self.record.id).exists()
        )