import pytest

from second.main import convert_value


@pytest.mark.parametrize(
    "value, field_type, expected",
    [
        ("10", "int", 10),
        ("1500.5", "float", 1500.5),
        ("25", "int", 25),
        ("100", "float", 100.0),
    ]
)
def test_convert_value_success(value, field_type, expected):
    """Проверяем успешное преобразование значений."""

    result = convert_value(value, field_type)

    assert result == expected
    assert type(result) is type(expected)


@pytest.mark.parametrize(
    "value, field_type",
    [
        ("много", "int"),
        ("дорого", "float"),
        ("10.5", "int"),
        ("abc", "float"),
    ]
)
def test_convert_value_invalid(value, field_type):
    """Проверяем некорректные значения."""

    with pytest.raises(ValueError):
        convert_value(value, field_type)


@pytest.mark.parametrize(
    "value, field_type",
    [
        ("2026-11-04", "date"),
    ]
)
def test_convert_value_date(value, field_type):
    """Проверяем некорректный тип данных."""

    with pytest.raises(ValueError, match="Неподдерживаемый тип поля"):
        convert_value(value, field_type)


def test_convert_value_empty():
    """Проверяем на пустое значение."""

    result = convert_value("", "text")

    assert result == ""
    assert isinstance(result, str)
    assert type(result) is type("")
