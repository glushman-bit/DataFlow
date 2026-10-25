# expenses = [
#     "Еда, 1200, 3",
#     "Транспорт, 500, 5",
#     "Кафе, 800, 2",
#     "Еда, 700, 2",
#     "Транспорт, 300, 3",
#     "Кафе, 600, 1",
#     "Развлечения, 1500, 1",
# ]

expenses = [
    "Еда, 50, 3",
    "Транспорт, 0, 2",
    "Кафе, много, 2",
    {"1": 6},
    "Еда, 700",
    "Развлечения, -1500, 1",
    23,
    " , 122, 4",
    "Кафе, 40, 1",
    6754,
]


def analyze_expenses(expenses: list) -> tuple[dict, list]:
    """Обработка исходного списка"""

    category = {}

    errors = []

    if not isinstance(expenses, list):
        raise TypeError("Ожидается список расходов.")

    for expense in expenses:

        if not isinstance(expense, str):
            print("Ошибка: Данные не являются строкой:", expense)
            errors.append(expense)
            continue

        if not expense.strip():
            print("Ошибка: Пустая строка:", expense)
            errors.append(expense)
            continue

        parts = expense.split(",")

        if len(parts) == 3:
            name = parts[0].strip().capitalize()  #
            price = parts[1].strip()
            quantity = parts[2].strip()

            if not name:
                print("Ошибка: Название категории не указано")
                errors.append(expense)
                continue

            try:
                price = int(price)
                quantity = int(quantity)

            except ValueError as e:
                print(f"Ошибка данных в строке: {e}")
                errors.append(expense)
                continue

            if price < 0:
                print("Ошибка: цена не может быть меньше 0:", expense)
                errors.append(expense)
                continue

            if quantity <= 0:
                print("Ошибка: количество не может быть меньше 0 или равно 0:", expense)
                errors.append(expense)
                continue

            if name not in category:
                category[name] = {
                    "total": price,
                    "count": quantity,
                }

            else:
                category[name]["total"] += price
                category[name]["count"] += quantity

        else:
            print("Ошибка: Не корректная строка:", expense)
            errors.append(expense)

    return category, errors


# isinstance(expenses, list) проверяет тип входного аргумента.
# isinstance(expense, str) отдельно отсекает элементы неправильного типа.
# not expense.strip() обнаруживает строки, состоящие из пробелов.
# try/except ValueError перехватывает ошибки преобразования в int.
# continue не позволяет некорректной записи попасть в расчёты.
# errors.append(expense) сохраняет исходные данные для итогового отчёта.
# Категории правильно объединяются по названию.


def calculate_total(expenses_by_category: dict) -> int:
    """Подсчёт всех расходов"""

    grand_total = sum(product["total"] for product in expenses_by_category.values())

    return grand_total


def print_report(expenses_by_category: dict) -> None:
    """Вывод отчёта и поиск самой затратной категории"""

    grand_total = sum(product["total"] for product in expenses_by_category.values())

    print("=" * 50)
    print("Отчет о покупках")
    print("")

    if not expenses_by_category:
        print("Нет данных для отчета.")
        print("=" * 50)
        return

    if grand_total != 0:

        most_expensive = max(expenses_by_category, key=lambda name: expenses_by_category[name]["total"])
        max_price = expenses_by_category[most_expensive]["total"]

        print(f"{'Категория':<15}{'Покупок':>10}{'Сумма':>20}{'Доля':>12}")
        print("-" * 50)

        for name in sorted(expenses_by_category):
            data = expenses_by_category[name]
            total = data['total']

            procent = (total / grand_total) * 100

            total_text = f"{total:,}".replace(",", " ")

            print(f"{name:<12}{data['count']:>9} шт.{total_text:>17} руб. {procent:>10.2f}%")

        print("")
        print("Общая сумма:", grand_total, "руб.")
        print("")
        print(f"Категория с наибольшей суммой расходов: {most_expensive} -> сумма: {max_price} руб.")

        print("=" * 50)

    else:
        print("Общая сумма расходов равна нулю.")
        print("=" * 50)


def main():
    expenses_by_category, errors = analyze_expenses(expenses)
    print_report(expenses_by_category)

    print("Строки с ошибками:", len(errors))
    for error in errors:
        print(f"- {error}")


if __name__ == "__main__":
    main()
