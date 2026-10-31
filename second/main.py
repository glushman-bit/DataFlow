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

            records_new = []

            for record in records:

                rec = {}

                for field in table_config["fields"]:
                    field_name = field["name"]
                    field_type = field["type"]
                    value_rec = record[field_name]

                    if value_rec:
                        value = convert_value(value_rec, field_type)

                    else:
                        value = "Нет данных"

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

    else:
        return value


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


def show_menu(records: list[dict]) -> None:
    """Взаимодействие с пользователем."""

    print("Вас приветствует мини программа ввода/вывода данных.\n")

    while True:
        user_input = input("Для продолжения работы с программой введите:\n"
                           "1 - Показать все записи\n"
                           "2 - Добавить новую запись\n"
                           "3 - Выйти из программы\n"
                           "4 - Редактировать запись\n"
                           "Ваш выбор: ")

        if user_input == "1":
            print("Количество заявок: ", len(records))
            show_records(records)

        elif user_input == "2":
            print("Заполните данные заявки:\n")
            data = create_record()
            user_input = input("Сохранить заявку? да/нет: ")

            if user_input == "да":
                records.append(data)
                save_to_csv(records, path)
                print("Запись добавлена.")

            else:
                print("Введенные данные не сохранены.")

        elif user_input == "3":
            print("Вы вышли из программы.\n"
                  "Спасибо за внимание.")
            break

        elif user_input == "4":
            edit_record(records)

        else:
            print("Неверный ввод.")
            continue


if __name__ == "__main__":
    main()

"""
and value проверяет, что строка не пустая, прежде чем пытаться преобразовать её в число. Это не специальный синтаксис для чисел — так можно проверять любую строку в Python.
"""
