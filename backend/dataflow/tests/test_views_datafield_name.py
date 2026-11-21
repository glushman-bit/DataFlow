from dataflow.models import DataField
from dataflow.tests.config import DataFieldViewSetTests


class DataFieldTestFieldName(DataFieldViewSetTests):
    """Класс проверки создания полей."""

    def test_data_field_create_invalid_name(self):
        """Проверка отклонения поля с некорректным техническим именем."""

        data = {
            "name": "Client",
            "label": "Клиент",
            "field_type": "text",
            "required": False,
            "order": 2,
        }

        response = self.client.post(
            f"/api/tables/{self.table.id}/fields/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

        self.assertFalse(
            DataField.objects.filter(
                table=self.table,
                name="Client",
            ).exists()
        )


    def test_data_field_create_duplicate_name(self):
        """Проверка запрета повторного технического имени."""

        data = {
            "name": "title",
            "label": "Другое название",
            "field_type": "text",
            "required": False,
            "order": 2,
        }

        response = self.client.post(
            f"/api/tables/{self.table.id}/fields/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

        self.assertEqual(
            DataField.objects.filter(table=self.table).count(),
            1,
        )


    def test_data_field_create_duplicate_label(self):
        """Проверка запрета повторного отображаемого названия."""

        data = {
            "name": "another_title",
            "label": "название",
            "field_type": "text",
            "required": False,
            "order": 2,
        }

        response = self.client.post(
            f"/api/tables/{self.table.id}/fields/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("label", response.data)

        self.assertEqual(
            DataField.objects.filter(table=self.table).count(),
            1,
        )


    def test_data_field_update_duplicate_label(self):
        """Проверка запрета повторного отображаемого названия при обновлении."""

        DataField.objects.create(
            table=self.table,
            name="price",
            label="Цена",
            field_type="decimal",
        )

        field = self.table.fields.get(name="title")

        data = {
            "label": "цена",
        }

        response = self.client.patch(
            f"/api/tables/{self.table.id}/fields/{field.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("label", response.data)

        field.refresh_from_db()
        self.assertEqual(field.label, "Название")


    def test_data_field_update_duplicate_name(self):
        """Проверка запрета повторного технического имени при обновлении."""

        DataField.objects.create(
            table=self.table,
            name="price",
            label="Цена",
            field_type="decimal",
        )

        field = self.table.fields.get(name="title")

        data = {
            "name": "price",
        }

        response = self.client.patch(
            f"/api/tables/{self.table.id}/fields/{field.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

        field.refresh_from_db()
        self.assertEqual(field.name, "title")


    def test_data_field_update_without_changing_names(self):
        """Проверка обновления поля без изменения его имён."""

        field = self.table.fields.get(name="title")

        data = {
            "required": True,
            "order": 5,
        }

        response = self.client.patch(
            f"/api/tables/{self.table.id}/fields/{field.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "title")
        self.assertEqual(response.data["label"], "Название")
        self.assertTrue(response.data["required"])
        self.assertEqual(response.data["order"], 5)


    def test_data_field_create_name_strips_whitespace(self):
        """Проверка удаления пробелов по краям технического имени."""

        data = {
            "name": "  client  ",
            "label": "Клиент",
            "field_type": "text",
            "required": False,
            "order": 2,
        }

        response = self.client.post(
            f"/api/tables/{self.table.id}/fields/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "client")

        self.assertTrue(
            DataField.objects.filter(
                table=self.table,
                name="client",
            ).exists()
        )


    def test_data_field_create_label_strips_whitespace(self):
        """Проверка удаления пробелов по краям отображаемого названия."""

        data = {
            "name": "client",
            "label": "  Клиент  ",
            "field_type": "text",
            "required": False,
            "order": 2,
        }

        response = self.client.post(
            f"/api/tables/{self.table.id}/fields/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["label"], "Клиент")

        self.assertTrue(
            DataField.objects.filter(
                table=self.table,
                name="client",
                label="Клиент",
            ).exists()
        )


    def test_data_field_create_name_too_long(self):
        """Проверка ограничения длины технического имени."""

        data = {
            "name": "a" * 51,
            "label": "Длинное имя",
            "field_type": "text",
            "required": False,
            "order": 2,
        }

        response = self.client.post(
            f"/api/tables/{self.table.id}/fields/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

        self.assertEqual(
            DataField.objects.filter(table=self.table).count(),
            1,
        )


    def test_data_field_create_label_too_long(self):
        """Проверка ограничения длины отображаемого названия."""

        data = {
            "name": "long_label",
            "label": "А" * 256,
            "field_type": "text",
            "required": False,
            "order": 2,
        }

        response = self.client.post(
            f"/api/tables/{self.table.id}/fields/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("label", response.data)

        self.assertEqual(
            DataField.objects.filter(table=self.table).count(),
            1,
        )
