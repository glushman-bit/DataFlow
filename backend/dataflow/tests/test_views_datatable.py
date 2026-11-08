import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from dataflow.models import DataTable


@pytest.mark.django_db
def test_data_table_list_authenticated():
    """Проверяет получение списка таблиц авторизованным пользователем."""

    user = get_user_model().objects.create_user(
        username="api_user",
        password="test_password",
    )

    DataTable.objects.create(
        owner=user,
        name="Моя таблица",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/tables/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Моя таблица"

"""
- APIClient() имитирует HTTP-клиент, например Postman.
- force_authenticate() авторизует пользователя для тестового запроса.
- client.get() отправляет GET-запрос к API.
- response.status_code проверяет HTTP-статус.
- response.data содержит данные ответа.
"""

@pytest.mark.django_db
def test_data_table_list_only_own_tables():
    """Проверяет, что пользователь видит только свои таблицы."""

    User = get_user_model()

    user_1 = User.objects.create_user(
        username="user_1",
        password="test_password",
    )
    user_2 = User.objects.create_user(
        username="user_2",
        password="test_password",
    )

    DataTable.objects.create(
        owner=user_1,
        name="Таблица пользователя 1",
    )
    DataTable.objects.create(
        owner=user_2,
        name="Таблица пользователя 2",
    )

    client = APIClient()
    client.force_authenticate(user=user_1)

    response = client.get("/api/tables/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Таблица пользователя 1"


@pytest.mark.django_db
def test_data_table_create_authenticated():
    """Проверка создания таблицы через POST-запрос."""

    user = get_user_model().objects.create_user(
        username="creator",
        password="test_password",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        "name": "Новая таблица",
        "settings": {"view": "table"},
    }

    response = client.post(
        "/api/tables/",
        data,
        format="json",
    )

    assert response.status_code == 201
    assert response.data["name"] == "Новая таблица"

    assert DataTable.objects.filter(
        owner=user,
        name="Новая таблица",
    ).exists()

"""
- Авторизованный пользователь отправляет POST-запрос.
- API возвращает 201 Created — таблица успешно создана.
- Название в ответе соответствует отправленному.
- Таблица действительно появилась в БД и принадлежит нужному пользователю.
"""

@pytest.mark.django_db
def test_data_table_list_unauthenticated():
    """API не позволяет создавать таблицы без авторизации."""

    client = APIClient()

    response = client.get("/api/tables/")

    assert response.status_code == 401

"""
- Создаём клиент без авторизации.
- Отправляем GET-запрос.
- Ожидаем 401 Unauthorized — доступ запрещён, поскольку пользователь не передал JWT-токен.
"""


@pytest.mark.django_db
def test_data_table_create_unauthenticated():
    """Проверим создание таблицы без авторизации."""

    client = APIClient()

    data = {
        "name": "Чужая таблица",
        "settings": {"view": "table"},
    }

    response = client.post(
        "/api/tables/",
        data,
        format="json",
    )

    assert response.status_code == 401
    assert not DataTable.objects.filter(name="Чужая таблица").exists()

"""
- Неавторизованный пользователь получает 401.
- Таблица не появляется в базе данных.
"""


@pytest.mark.django_db
def test_data_table_update_authenticated():
    """Проверим обновление таблицы через PATCH."""

    user = get_user_model().objects.create_user(
        username="editor",
        password="test_password",
    )

    table = DataTable.objects.create(
        owner=user,
        name="Старая таблица",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        "name": "Обновлённая таблица",
    }

    response = client.patch(
        f"/api/tables/{table.id}/",
        data,
        format="json",
    )

    assert response.status_code == 200
    assert response.data["name"] == "Обновлённая таблица"

    table.refresh_from_db()
    assert table.name == "Обновлённая таблица"

"""
- PATCH позволяет изменить только отдельные поля.
- Мы передаём только name, не затрагивая settings.
- refresh_from_db() перечитывает объект из базы, чтобы проверить фактически сохранённое значение.
"""


@pytest.mark.django_db
def test_data_table_update_another_table():
    """Пользователь не может изменить чужую таблицу."""

    User = get_user_model()

    owner = User.objects.create_user(
        username="owner",
        password="test_password",
    )
    other_user = User.objects.create_user(
        username="other",
        password="test_password",
    )

    table = DataTable.objects.create(
        owner=owner,
        name="Таблица владельца",
    )

    client = APIClient()
    client.force_authenticate(user=other_user)

    response = client.patch(
        f"/api/tables/{table.id}/",
        {"name": "Изменённая таблица"},
        format="json",
    )

    assert response.status_code == 404

    table.refresh_from_db()
    assert table.name == "Таблица владельца"


@pytest.mark.django_db
def test_data_table_delete_authenticated():
    """Удаление собственной таблицы через DELETE."""

    user = get_user_model().objects.create_user(
        username="deleter",
        password="test_password",
    )

    table = DataTable.objects.create(
        owner=user,
        name="Таблица для удаления",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(f"/api/tables/{table.id}/")

    assert response.status_code == 204
    assert not DataTable.objects.filter(pk=table.id).exists()

"""
- Пользователь может удалить свою таблицу.
- API возвращает 204 No Content — запрос выполнен успешно, тело ответа отсутствует.
- Таблица действительно удалена из базы данных.
"""


@pytest.mark.django_db
def test_data_table_delete_foreign_table():
    """Пользователь не должен иметь возможность удалить чужую таблицу."""

    User = get_user_model()

    owner = User.objects.create_user(
        username="table_owner",
        password="test_password",
    )
    other_user = User.objects.create_user(
        username="other_user",
        password="test_password",
    )

    table = DataTable.objects.create(
        owner=owner,
        name="Таблица владельца",
    )

    client = APIClient()
    client.force_authenticate(user=other_user)

    response = client.delete(f"/api/tables/{table.id}/")

    assert response.status_code == 404   # Чужой пользователь получает 404.
    assert DataTable.objects.filter(pk=table.id).exists()  # Таблица остаётся в базе данных.


@pytest.mark.django_db
def test_data_table_update_put():
    """PUT — полное обновление таблицы."""

    user = get_user_model().objects.create_user(
        username="put_user",
        password="test_password",
    )

    table = DataTable.objects.create(
        owner=user,
        name="Старая таблица",
        settings={"view": "list"},
    )

    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        "name": "Новая таблица",
        "settings": {"view": "table"},
    }

    response = client.put(
        f"/api/tables/{table.id}/",
        data,
        format="json",
    )

    assert response.status_code == 200
    assert response.data["name"] == "Новая таблица"
    assert response.data["settings"] == {"view": "table"}

    table.refresh_from_db()
    assert table.name == "Новая таблица"
    assert table.settings == {"view": "table"}
