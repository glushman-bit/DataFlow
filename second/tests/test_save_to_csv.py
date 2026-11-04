import csv
from second.main import save_to_csv, table_config


def test_save_to_csv_success(tmp_path):
    """Успешное сохранение записей в CSV."""

    records = [
        {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": 1500.50,
            "client": "Иван Петров",
            "status": "Новая",
        },
        {
            "title": "Обработка деталей",
            "quantity": 5,
            "price": 1000.00,
            "client": "Алексей Иванов",
            "status": "В работе",
        },
    ]

    filename = tmp_path / "test_save_to_csv.csv"

    save_to_csv(records, filename)

    assert filename.exists()

    with open(filename, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        save_records = list(reader)

    assert len(save_records) == 2
    assert save_records[0]["title"] == "Покраска деталей"
    assert save_records[0]["quantity"] == '10'
    assert save_records[1]["status"] == "В работе"

"""    
tmp_path — встроенная фикстура pytest. Она предоставляет временную директорию, 
поэтому тест не затрагивает реальные данные проекта.
После чтения CSV значения будут строками. Например, quantity 
станет "10", а не 10. Это нормальное поведение csv.DictReader.
"""


def test_save_to_scv_empty_records(tmp_path):
    """Сохранение пустого списка записей."""

    filename = tmp_path / "test_empty.csv"

    save_to_csv([], filename)

    assert filename.exists()

    with open(filename, encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, delimiter=";")
        header = next(reader)

    assert header == [field["name"] for field in table_config["fields"]]

"""
csv.reader() — когда нужно просто прочитать строки и проверить заголовки.
csv.DictReader() — когда нужно загружать записи и работать с ними как со словарями.
"""