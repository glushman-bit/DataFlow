import csv
import pytest
from second.main import load_from_csv, table_config


def test_load_from_csv_success(tmp_path):
    """Успешное чтение данных из csv файла."""

    file_path = tmp_path / "records.csv"

    records = [
        {
            "title": "Покраска деталей",
            "quantity": 10,
            "price": 1500.0,
            "client": "Иван Петров",
            "status": "Новая",
        },
        {
            "title": "Обработка деталей",
            "quantity": 5,
            "price": 1000.0,
            "client": "Алексей Иванов",
            "status": "В работе",
        },
    ]

    # Создаём тестовый CSV-файл
    with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[field["name"] for field in table_config["fields"]],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(records)

    result = load_from_csv(file_path)

    assert len(result) == 2

    assert result[0]["title"] == "Покраска деталей"
    assert result[0]["quantity"] == 10
    assert result[0]["price"] == 1500.0
    assert result[1]["client"] == "Алексей Иванов"
    assert result[1]["status"] == "В работе"


def test_load_from_csv_file_not_found(tmp_path):
    """Проверяем отсутствие файла."""

    file_path = tmp_path / "missing.csv"

    result = load_from_csv(file_path)

    assert len(result) == 0
    assert result == []


def test_load_from_csv_wrong_headers(tmp_path, capsys):
    """Проверяем не соответствие заголовков."""

    file_path = tmp_path / "wrong.csv"

    with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["title", "count", "price", "client", "status"])
        writer.writerow(["Покраска деталей", 10, 1500.0, "Иван Петров", "Новая"])

    result = load_from_csv(file_path)

    captured = capsys.readouterr()

    assert result == []
    assert "Ошибка: структура CSV-файла не соответствует настройкам таблицы." in captured.out


def test_load_from_csv_empty_records(tmp_path):
    """файл существует, заголовки корректные, но строк с данными нет."""

    file_path = tmp_path / "empty.csv"

    with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[field["name"] for field in table_config["fields"]],
            delimiter=";",
        )

        writer.writeheader()

    result = load_from_csv(file_path)

    assert result == []


def test_load_from_csv_duplicate_headers(tmp_path, capsys):
    """Проверка дубликатов в заголовках."""

    file_path = tmp_path / "duplicate.csv"

    with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["title", "quantity", "price", "client", "status", "title"])
        writer.writerow([
            "Покраска деталей", 10, 1500.0,
            "Иван Петров", "Новая", "Другая запись"
        ])

    result = load_from_csv(file_path)

    captured = capsys.readouterr()

    assert result == []
    assert "Ошибка: структура CSV-файла не соответствует настройкам таблицы." in captured.out


def test_load_from_csv_invalid_number(tmp_path):
    """Проверяем некорректные числовые данные."""

    file_path = tmp_path / "invalid.csv"

    with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[field["name"] for field in table_config["fields"]],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerow({
            "title": "Покраска деталей",
            "quantity": "много",
            "price": "1500.0",
            "client": "Иван Петров",
            "status": "Новая",
        })

    with pytest.raises(ValueError):
        load_from_csv(file_path)


@pytest.mark.parametrize(
    "records, expected_error",
    [
        (
            [
                {
                    "title": "Покраска деталей",
                    "quantity": "много",
                    "price": "1500.0",
                    "client": "Иван Петров",
                    "status": "Новая",
                }
            ],
            "Ошибка в строке 2",
        ),
        (
            [
                {
                    "title": "Покраска деталей",
                    "quantity": "5",
                    "price": "1500.0",
                    "client": "Иван Петров",
                    "status": "Новая",
                },
                {
                    "title": "Обработка деталей",
                    "quantity": "5",
                    "price": "дорого",
                    "client": "Алексей Иванов",
                    "status": "Новая",
                },
            ],
            "Ошибка в строке 3",
        ),
    ],
)
def test_load_from_csv_invalid_number_error(tmp_path, records, expected_error):
    """Проверяем варианты ошибок."""

    file_path = tmp_path / "invalid.csv"

    with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[field["name"] for field in table_config["fields"]],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(records)

    with pytest.raises(ValueError) as error:
        load_from_csv(file_path)

    assert expected_error in str(error.value)



