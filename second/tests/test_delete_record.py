from second import main
# from second.tests.config import records, records_empty




def test_delete_record(monkeypatch):
    """успешное удаление записи."""

    records = [
        {
            "title": "",
            "quantity": 10,
            "price": 1500,
            "client": "Иван Петрович",
            "status": "Новая",
        }
    ]

    answer = iter(["1", "да"])

    monkeypatch.setattr("builtins.input", lambda _: next(answer))

    # Эксперимент
    # def fake_input(prompt):
    #     print(f"Программа спрашивает: {prompt}")
    #     answer = next(answers)
    #     print(f"Пользователь вводит: {answer}")
    #     return answer
    #
    # monkeypatch.setattr("builtins.input", fake_input)

    saved_calls = []

    def fake_save_to_csv(records, filename):
        saved_calls.append(records.copy())

    monkeypatch.setattr(main, "save_to_csv", fake_save_to_csv)

    main.delete_record(records)

    assert records == []
    assert saved_calls == [[]]

"""
import main — импортируем модуль с нашей функцией.
monkeypatch — временно подменяем поведение функций и объектов.
iter(["1", "да"]) — имитируем ввод номера записи и подтверждения удаления.
fake_save_to_csv() — подменяем настоящее сохранение в CSV, чтобы тест не изменял твой файл.
assert records == [] — проверяем, что запись действительно удалена.
assert saved_records == [] — проверяем, что сохранение вызвано с пустым списком.
"""


def test_delete_record_cancel(monkeypatch):
    """пользователь отменяет удаление записи."""
    records = [
        {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": 1500,
            "client": "Иван Петров",
            "status": "Новая",
        }
    ]

    answers = iter(["1", "нет"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    saved_records = []

    def fake_save_to_csv(records, filename):
        saved_records.extend(records)

    monkeypatch.setattr(main, "save_to_csv", fake_save_to_csv)
    main.delete_record(records)

    assert len(records) == 1
    assert records[0]["title"] == "Покраска деталей"
    assert saved_records == []

"""
len(records) == 1 — запись осталась в списке.
records[0]["title"] == "Покраска деталей" — убедились, что это именно исходная запись.
saved_records == [] — сохранение не вызывалось.
"""


def test_delete_record_empty(monkeypatch, capsys):
    """попытка удалить запись, когда список пуст."""

    records = []

    main.delete_record(records)
    captured = capsys.readouterr()

    assert records == []
    assert "Нет записей для удаления" in captured.out


def test_delete_record_invalid_number(monkeypatch, capsys):
    """пользователь вводит некорректный номер, а затем правильный."""

    records = [
        {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": 1500.0,
            "client": "Иван Петров",
            "status": "Новая",
        }
    ]

    answers = iter(["abc", "1", "да"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(main, "save_to_csv", lambda records, filename: None)

    main.delete_record(records)
    captured = capsys.readouterr()

    assert records == []
    assert "Введите целое число." in captured.out


def test_delete_record_out_of_range_number(monkeypatch, capsys):
    """пользователь вводит некорректный номер, а затем правильный."""

    records = [
        {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": 1500.0,
            "client": "Иван Петров",
            "status": "Новая",
        }
    ]

    answers = iter(["5", "1", "да"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(main, "save_to_csv", lambda records, filename: None)

    main.delete_record(records)
    captured = capsys.readouterr()

    assert records == []
    assert "Записи с таким номером нет." in captured.out