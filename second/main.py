table_config = {
    "name": "Заявки",
    "fields": [
        {
            "name": "title",
            "label": "Название",
            "type": "text",
            "required": True,
        },
        {
            "name": "quantity",
            "label": "Количество",
            "type": "int",
            "required": True,
        },
        {
            "name": "price",
            "label": "Цена",
            "type": "float",
            "required": True,
        },
        {
            "name": "client",
            "label": "Клиент",
            "type": "text",
            "required": True,
        },
        {
            "name": "status",
            "label": "Статус",
            "type": "text",
            "required": False,
        }
    ]
}


import csv
from pathlib import Path


data_dir = Path("data")
path = data_dir / "records.csv"


def main() -> None:
    """Точка входа в программу."""

    data_dir.mkdir(parents=True, exist_ok=True)

    records = load_from_csv(path)

    show_menu(records)


def create_record() -> dict:
    """Создание записей."""

    record = {}

    for field in table_config["fields"]:
        name = field["name"]
        label = field["label"]
        required = field["required"]

        while True:
            value = input(f"Введите {label}: ").strip()

            # 1. Проверяем обязательность поля
            if required and not value:
                print("Поле обязательно для заполнения.")
                continue

            # 2. Преобразуем значение в нужный тип
            try:
                if field["type"] == "int" and value:
                    value = int(value)

                elif field["type"] == "float" and value:
                    value = float(value)

            except ValueError:
                print("Ошибка: введите корректное число.")
                continue

            # 3. Все проверки пройдены
            break

        record[name] = value if value != "" else "Нет данных"

    return record


def save_to_csv(records: list[dict], path) -> None:
    """Сохранение записей в CSV-файл."""

    with open(path, "w", newline="", encoding="utf-8-sig") as csvfile:
        headers = [fields["name"] for fields in table_config["fields"]]

        writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=";")

        writer.writeheader()

        writer.writerows(records)


def load_from_csv(path) -> list[dict]:
    """Загрузка записей из CSV-файла."""

    try:
        with open(path, "r", newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            records = list(reader)

            headers = reader.fieldnames

            expected_headers = [field["name"] for field in table_config["fields"]]

            if (
                not headers
                or len(headers) != len(set(headers))
                or not all(header in headers for header in expected_headers)
            ):
                # set(headers) оставляет только уникальные значения.
                # len(headers) — количество всех заголовков.
                # len(set(headers)) — количество уникальных заголовков.
                # Если числа отличаются, значит, есть дубликаты.

                print("Ошибка: структура CSV-файла не соответствует настройкам таблицы.")
                return []

            records_new = []

            for row_number, record in enumerate(records, start=2):

                rec = {}

                for field in table_config["fields"]:
                    field_name = field["name"]
                    field_type = field["type"]
                    value_rec = record[field_name]

                    try:
                        if value_rec:
                            value = convert_value(value_rec, field_type)

                        else:
                            value = "Нет данных"

                    except ValueError as error:
                        raise ValueError(
                            f"Ошибка в строке {row_number}, "
                            f"поле '{field_name}', значение '{value_rec}': {error}"
                        ) from error

                    rec[field_name] = value

                records_new.append(rec)

    except FileNotFoundError:
        return []

    return records_new


def convert_value(value: str, field_type):
    """Преобразование значения в нужный тип."""

    if field_type == "int":
        return int(value)

    elif field_type == "float":
        return float(value)

    elif field_type == "text":
        return value

    else:
        raise ValueError(f"Неподдерживаемый тип поля: {field_type}")


def show_records(records: list[dict]) -> None:
    """Вывод записей заявок."""

    for number, record in enumerate(records, 1):
        print(f"= Заявка №{number}:")

        for field in table_config["fields"]:
            name = field["name"]
            label = field["label"]
            value = record.get(name)

            print(f"    {label}: {value}")


def edit_record(records: list[dict]) -> None:
    """Редактирование существующей записи."""

    if not records:
        print("Нет записей для редактирования.")
        return

    show_records(records)

    while True:
        try:
            number = int(input("Введите номер записи для редактирования: "))

            if 1 <= number <= len(records):
                break

            print("Записи с таким номером нет.")

        except ValueError:
            print("Введите целое число.")

    record = records[number - 1].copy()

    for field in table_config["fields"]:
        name = field["name"]
        label = field["label"]
        old_value = record[name]

        print(f"   {label}: {old_value}")

        while True:
            new_value = input(
                f"Новое значение для поля '{label}' "
                f"(Enter - оставить без изменений): "
            ).strip()

            if not new_value:
                break

            try:
                new_value = convert_value(new_value, field["type"])

            except ValueError:
                print("Ошибка: введено некорректное значение.")
                continue

            record[name] = new_value
            break

    if record == records[number - 1]:
        print("Изменений нет. Сохранять нечего.")
        return

    confirm = input("Сохранить изменения? да/нет: ").strip().lower()

    if confirm == "да":
        records[number - 1] = record
        save_to_csv(records, path)
        print("Изменения сохранены.")

    else:
        print("Изменения отменены.")


def delete_record(records: list[dict]) -> None:
    """Удаление записи."""

    if not records:
        print("Нет записей для удаления.")
        return

    show_records(records)

    while True:
        try:
            number = int(input("Введите номер записи для удаления: "))

            if 1 <= number <= len(records):
                break

            print("Записи с таким номером нет.")

        except ValueError:
            print("Введите целое число.")

    record = records[number - 1].copy()

    print("\nВы выбрали запись:")
    for field in table_config["fields"]:
        name = field["name"]
        label = field["label"]
        print(f"   {label}: {record[name]}")

    confirm = input("Уверены что хотите удалить эту запись? да/нет: ").strip().lower()

    if confirm == "да":
        records.pop(number - 1)
        save_to_csv(records, path)
        print("Запись удалена.")

    else:
        print("Удаление отменено.")


def show_menu(records: list[dict]) -> None:
    """Взаимодействие с пользователем."""

    print("Вас приветствует мини программа ввода/вывода данных.\n")

    while True:
        user_input = input("Для продолжения работы с программой введите:\n"
                           "1 - Показать все записи\n"
                           "2 - Добавить новую запись\n"
                           "3 - Редактировать запись\n"
                           "4 - Удалить запись\n"
                           "5 - Выйти из программы\n"
                           "Ваш выбор: ").strip()

        if user_input == "1":
            print("Количество заявок: ", len(records))
            show_records(records)

        elif user_input == "2":
            print("Заполните данные заявки:\n")
            data = create_record()
            user_input = input("Сохранить заявку? да/нет: ").strip().lower()

            if user_input == "да":
                records.append(data)
                save_to_csv(records, path)
                print("Запись добавлена.")

            else:
                print("Введенные данные не сохранены.")

        elif user_input == "3":
            edit_record(records)

        elif user_input == "4":
            delete_record(records)

        elif user_input == "5":
            print("Вы вышли из программы.\n"
                  "Спасибо за внимание.")
            break

        else:
            print("Неверный ввод.")
            continue


if __name__ == "__main__":
    main()

"""
and value проверяет, что строка не пустая, прежде чем пытаться преобразовать её в число. Это не специальный синтаксис для чисел — так можно проверять любую строку в Python.
"""
