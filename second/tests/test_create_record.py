from second.main import create_record, table_config


def test_create_record_success(monkeypatch):
    """Успешное создание записи."""

    inputs = iter([
        "Покраска деталей",
        "10",
        "1500.50",
        "Иван Петров",
        "Новая",
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    record = create_record()

    assert record == {
        "title": "Покраска деталей",
        "quantity": 10,
        "price": 1500.50,
        "client": "Иван Петров",
        "status": "Новая",
    }

    assert isinstance(record["quantity"], int)
    assert isinstance(record["price"], float)


def test_create_record_required_field_empty(monkeypatch, capsys):
    """"""

    inputs = iter([
        "",   # пустое поле
        "Покраска деталей",
        "10",
        "1500.50",
        "Иван Петров",
        "Новая",
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    record = create_record()
    captured = capsys.readouterr()

    assert record["title"] == "Покраска деталей"
    assert "Поле обязательно для заполнения." in captured.out


def test_create_record_invalid_data(monkeypatch, capsys):
    """Повторный ввод при некорректном целом дробном числе."""

    inputs = iter([
        "",       # пустое поле
        "Покраска деталей",
        "",       # пустое поле
        "no",     # некорректное число
        "10",
        "no",     # некорректное число
        "1500.50",
        "Иван Петров",
        "Новая",
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    record = create_record()
    captured = capsys.readouterr()

    assert record["title"] == "Покраска деталей"
    assert "Поле обязательно для заполнения." in captured.out

    assert record["quantity"] == 10
    assert "Поле обязательно для заполнения." in captured.out
    assert isinstance(record["quantity"], int)
    assert "Ошибка: введите корректное число." in captured.out

    assert record["price"] == 1500.5
    assert isinstance(record["price"], float)
    assert "Ошибка: введите корректное число." in captured.out


def test_create_record_optional_field_empty(monkeypatch):
    """Пустое необязательное поле."""

    monkeypatch.setitem(table_config["fields"][4], "required", False)
    # monkeypatch.setitem() временно изменяет значение в словаре.
    inputs = iter([
        "Покраска деталей",
        "10",
        "1500.50",
        "Иван Петров",
        "",
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    record = create_record()

    assert record["status"] == "Нет данных"
