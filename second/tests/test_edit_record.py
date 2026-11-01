from second import main


def test_edit_record(monkeypatch):
    """успешное редактирование с подтверждением."""
    records = [
        {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": 1500.0,
            "client": "Иван Петров",
            "status": "Новая",
        }
    ]

    answers = iter([
        "1",                  # Номер записи
        "Новая покраска",     # Новое название
        "",                   # Количество — без изменений
        "",                   # Цена — без изменений
        "",                   # Клиент — без изменений
        "",                   # Статус — без изменений
        "да",                 # Подтверждение
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    save_calls = []

    def fake_save_to_csv(records, filename):
        save_calls.append([record.copy() for record in records])

    monkeypatch.setattr(main, "save_to_csv", fake_save_to_csv)

    main.edit_record(records)

    assert records[0]["title"] == "Новая покраска"
    assert records[0]["quantity"] == 10
    assert len(save_calls) == 1
    assert save_calls[0][0]["title"] == "Новая покраска"


def test_edit_record_cancel(monkeypatch):
    """Отмена изменений редактирования записи."""
    records = [
        {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": 1500.0,
            "client": "Иван Петров",
            "status": "Новая",
        }
    ]

    answers = iter([
        "1",
        "Новая покраска",
        "",
        "",
        "",
        "",
        "нет",
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    save_calls = []

    def fake_save_to_csv(records, filename):
        save_calls.append([record.copy() for record in records])

    monkeypatch.setattr(main, "save_to_csv", fake_save_to_csv)

    main.edit_record(records)

    assert records[0]["title"] == "Покраска деталей"
    assert save_calls == []


def test_edit_record_no_changes(monkeypatch, capsys):
    """пользователь ничего не меняет."""
    records = [
        {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": 1500.0,
            "client": "Иван Петров",
            "status": "Новая",
        }
    ]

    answers = iter(["1", "", "", "", "", ""])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    save_calls = []

    def fake_save_to_csv(records, filename):
        save_calls.append(records.copy())

    monkeypatch.setattr(main, "save_to_csv", fake_save_to_csv)

    main.edit_record(records)

    captured = capsys.readouterr()

    assert "Изменений нет. Сохранять нечего." in captured.out
    assert save_calls == []
    assert records[0]["title"] == "Покраска деталей"


def test_edit_record_empty(capsys):
    """Проверка пустого списка записей."""
    records = []

    main.edit_record(records)

    captured = capsys.readouterr()

    assert "Нет записей для редактирования." in captured.out
    assert records == []


def test_edit_record_invalid_value(monkeypatch, capsys):
    """при редактировании числового поля пользователь вводит некорректное значение, затем исправляет его."""
    records = [
        {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": 1500.0,
            "client": "Иван Петров",
            "status": "Новая",
        }
    ]

    answers = iter([
        "1",       # Номер записи
        "",        # Название
        "2",       # Количество
        "abc",     # Некорректная цена
        "2000",    # Исправленная цена
        "",        # Клиент
        "",        # Статус
        "да",      # Подтверждение
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    save_calls = []

    def fake_save_to_csv(records, filename):
        save_calls.append([record.copy() for record in records])

    monkeypatch.setattr(main, "save_to_csv", fake_save_to_csv)

    main.edit_record(records)

    captured = capsys.readouterr()

    assert "Ошибка: введено некорректное значение." in captured.out
    assert records[0]["price"] == 2000.0
    assert records[0]["quantity"] == 2
    assert len(save_calls) == 1


def test_edit_record_invalid_number(monkeypatch, capsys):
    """неверный номер записи."""
    records = [
        {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": 1500.0,
            "client": "Иван Петров",
            "status": "Новая",
        }
    ]

    answers = iter([
        "abc",  # Не число
        "5",    # Такого номера нет
        "1",    # Корректный номер
        "",     # Название
        "",     # Количество
        "",     # Цена
        "",     # Клиент
        "",     # Статус
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    main.edit_record(records)

    captured = capsys.readouterr()

    assert "Введите целое число." in captured.out
    assert "Записи с таким номером нет." in captured.out
    assert "Изменений нет. Сохранять нечего." in captured.out