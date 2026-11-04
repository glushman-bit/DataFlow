from second import main


def test_show_menu_exit(monkeypatch, capsys):
    """пользователь выбирает пункт 5."""

    inputs = iter(["5"])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.show_menu([])

    captured = capsys.readouterr()

    assert "Вы вышли из программы." in captured.out
    assert "Спасибо за внимание." in captured.out


def test_show_menu_show_records(monkeypatch):
    """Проверка пункта 1 и 5 меню."""

    inputs = iter(["1", "5"])
    shown_records = []

    records = [
        {"title": "Покраска деталей"},
        {"title": "Обработка деталей"}
    ]

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(
        main,
        "show_records",
        lambda data: shown_records.append(data),
    )

    main.show_menu(records)

    assert shown_records == [records]


def test_show_menu_add_record(monkeypatch):
    """Проверяем пункт 2, выбор "да", и пункт 5."""

    inputs = iter(["2", "да", "5"])

    records = []
    new_record = {
        "title": "Покраска деталей",
        "quantity": 10,
        "price": 1500.0,
        "client": "Иван Петров",
        "status": "Новая",
    }

    saved_data = []

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "create_record", lambda: new_record)
    monkeypatch.setattr(
        main,
        "save_to_csv",
        lambda data, path: saved_data.append(data.copy()),
    )

    main.show_menu(records)

    assert records == [new_record]
    assert saved_data == [[new_record]]

"""
Выбираем пункт 2.
Подменяем create_record(), чтобы не вводить поля вручную.
Подтверждаем сохранение ответом да.
Проверяем, что запись добавлена в исходный список.
Проверяем, что save_to_csv() получил обновлённый список.
"""


def test_show_menu_cancel_add_record(monkeypatch, capsys):
    """Проверка добавления записи."""

    inputs = iter(["2", "нет", "5"])

    records = []
    new_record = {"title": "Покраска деталей"}
    save_calls = []

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(main, "create_record", lambda: new_record)
    monkeypatch.setattr(
        main,
        "save_to_csv",
        lambda data, path: save_calls.append(data),
    )

    main.show_menu(records)

    captured = capsys.readouterr()

    assert records == []
    assert save_calls == []
    assert "Введенные данные не сохранены." in captured.out


def test_show_menu_edit_record(monkeypatch):
    """Проверка удаления."""

    inputs = iter(["3", "5"])
    records = [{"title": "Покраска деталей"}]
    edited_records = []

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(
        main,
        "edit_record",
        lambda data: edited_records.append(data),
    )

    main.show_menu(records)

    assert edited_records == [records]


def test_show_menu_delete_record(monkeypatch):
    inputs = iter(["4", "5"])
    records = [{"title": "Покраска деталей"}]
    deleted_records = []

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(
        main,
        "delete_record",
        lambda data: deleted_records.append(data),
    )

    main.show_menu(records)

    assert deleted_records == [records]


def test_show_menu_invalid_input(monkeypatch, capsys):
    """Проверка на неверный ввод."""

    inputs = iter(["abc", "5"])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.show_menu([])

    captured = capsys.readouterr()

    assert "Неверный ввод." in captured.out
