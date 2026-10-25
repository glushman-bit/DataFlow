from first.gpt_analyze_purches import calculate_total, analyze_expenses, print_report
import pytest

def test_calculate_total():
    """Тест на подсчет суммы."""
    expenses_by_category = {
        "Еда": {"total": 300, "count": 3},
        "Кафе": {"total": 500, "count": 1},
        "Транспорт": {"total": 0, "count": 2},
    }

    result = calculate_total(expenses_by_category)

    assert result == 800


def test_analyze_expenses_valid_data():
    """Тест на валидные данные."""
    expenses = [
        "Еда, 1200, 1",
        "Кафе, 500, 2",
        "Еда, 300, 3",
    ]

    expenses_by_category, errors = analyze_expenses(expenses)

    assert expenses_by_category == {
        "Еда": {"total": 1500, "count": 4},
        "Кафе": {"total": 500, "count": 2},
    }
    assert errors == []

# Категория «Еда» встречается дважды, поэтому проверяем, что значения правильно объединяются.
# Сумма категории «Еда» должна составить \(1200 + 300 = 1500\).
# Количество должно составить \(3 + 1 = 4\).
# Все записи корректны, поэтому список errors должен быть пустым.

def test_analyze_expenses_invalid_data():
    expenses = [
        "Кафе, много, 2",
        "Еда, 700",
        123,
    ]

    expenses_by_category, errors = analyze_expenses(expenses)

    assert expenses_by_category =={}
    assert len(errors) == 3

# Запись	             Что проверяем
# "Кафе, много, 2"	 Невозможно преобразовать цену в целое число
# "Еда, 700"	         Недостаточно полей
# 123	                 Запись не является строкой

def test_analyse_expenses_empty_data():
    """Тест при пустых данных ввода."""
    expenses_by_category, errors = analyze_expenses([])

    assert expenses_by_category == {}
    assert errors == []

# что функция корректно обрабатывает отсутствие расходов: не
# падает с исключением и возвращает два пустых контейнера.

def test_analyze_expenses_wrong_argument_type():
    """Тест вывода ошибки TypeError."""
    with pytest.raises(TypeError, match="Ожидается список расходов."):
        analyze_expenses("Еда, 500, 2")

# pytest.raises(TypeError) проверяет, что возникло исключение нужного типа.
# match=... дополнительно проверяет текст сообщения об ошибке.
# Если исключение не возникнет или сообщение не совпадёт, тест провалится.

def test_analyze_expenses_mixed_data():
    """Тест при вводе корректных и некорректных данных."""
    expenses = [
        "Еда, 1200, 2",
        "Кафе, много, 1",
        "Транспорт, 300, 3",
        "Еда, 500",
    ]
    expenses_by_category, errors = analyze_expenses(expenses)

    assert expenses_by_category == {
        "Еда": {"total": 1200, "count": 2},
        "Транспорт": {"total": 300, "count": 3},
    }
    assert len(errors) == 2

# Корректные записи обрабатываются, даже если в списке есть ошибки.
# Некорректные записи не попадают в итоговый словарь.
# Обе ошибки сохраняются в списке errors.
# Расчёты по корректным записям остаются правильными.

# def test_analyze_expenses_invalid_values(capsys):
#     expenses = [
#         "Еда, -100, 2",
#         "Транспорт, 300, 0",
#     ]
#     expenses_by_category, errors = analyze_expenses(expenses)
#
#     captured = capsys.readouterr()
#
#     assert expenses_by_category == {}
#     assert len(errors) == 2
#     assert "цена" in captured.out.lower()
#     assert "количество" in captured.out.lower()

# отрицательная цена отклоняется;
# нулевое количество отклоняется;
# ни одна некорректная запись не попадает в результат.
# capsys проверяет вывод в консоль

def test_calculate_total_empty_data():
    expenses = {}

    result = calculate_total(expenses)

    assert result == 0

# когда расходов нет, общая сумма должна быть равна нулю.

# def test_analyze_expenses_wrong_data(capsys):
#     expenses = [
#         " , 100, 2",
#         "Еда, 200, 1"
#     ]
#     expenses_by_category, errors = analyze_expenses(expenses)
#     captured = capsys.readouterr()
#
#     assert expenses_by_category == {"Еда": {"total": 200, "count": 1}}
#     assert len(errors) == 1
#     assert errors[0] == " , 100, 2"
#     assert "Название категории не указано" in captured.out

# Проверка	             Что подтверждает
# assert expenses_by_category == {"Еда": {"total": 200, "count": 1}}
#                        Некорректная запись не попала в результат, а корректная обработана правильно.
# assert len(errors) == 1
#                        Найдена ровно одна ошибка.
# assert errors[0] == " , 100, 2"
#                        В список ошибок попала исходная строка, а не изменённая версия.
# assert "Название" in captured.out
#                        В консоли появилось сообщение об отсутствии названия категории.

def test_print_report_empty_data(capsys):
    """Проверка поведения функции при пустых данных."""
    print_report({})
    captured = capsys.readouterr()

    assert "Нет данных для отчета." in captured.out


def test_print_report_valid_data(capsys):
    """Проверка вывода отчета при корректных данных."""
    expenses_by_category = {
        "Еда": {"total": 1500, "count": 4},
        "Кафе": {"total": 500, "count": 1},
    }

    print_report(expenses_by_category)
    captured = capsys.readouterr()

    assert "Еда" in captured.out
    assert "Кафе" in captured.out
    assert "Общая сумма: 2000" in captured.out
    assert "Еда -> сумма: 1500" in captured.out


def test_print_report_zero_total(capsys):
    expenses_by_category = {
        "Еда": {"total": 0, "count": 4},
    }

    print_report(expenses_by_category)
    captured = capsys.readouterr()

    assert "Общая сумма расходов равна нулю." in captured.out
    assert "Нет данных для отчета." not in captured.out


import first.gpt_analyze_purches as analyzer

def test_main(capsys, monkeypatch):
    test_expenses = [
        "Еда, 100, 2",
        "Кафе, 50, 1",
        "Транспорт, -100, 1"
    ]
    monkeypatch.setattr(analyzer, "expenses", test_expenses)
    analyzer.main()
    captured = capsys.readouterr()

    assert "Общая сумма: 150" in captured.out
    # assert "Строки с ошибками:" in captured.out
    assert "Строки с ошибками: 1" in captured.out
    assert "Еда" in captured.out
    assert "Кафе" in captured.out


@pytest.mark.parametrize("expense, expected_error", [
    (" , 100, 2", "Ошибка: Название категории не указано"),
    ("Еда, -100, 2", "Ошибка: цена не может быть меньше 0:"),
    ("Еда, 100, 0", "Ошибка: количество не может быть меньше 0 или равно 0:"),
    ("Еда, 100, -1", "Ошибка: количество не может быть меньше 0 или равно 0:"),
    ("Еда, сто, два", "Ошибка данных в строке:"),
    ("   ", "Ошибка: Пустая строка:")
])
def test_analyze_expenses_invalid_records(expense, expected_error, capsys):
    _, errors = analyze_expenses([expense])
    captured = capsys.readouterr()

    assert expected_error in captured.out
    assert len(errors) == 1

