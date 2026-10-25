"""
Реализуй:

def filter_messages(raw: str, *, min_length: int = 10) -> str:
Что должна делать функция

Сначала, как и раньше:

Нормализовать переносы \r\n и \r.
Разбить текст на строки.
Убрать лишние пробелы и табуляции.
Удалить пустые строки.
Убрать имя и : из каждой строки.

После этого появляется новое условие:

Оставить только сообщения, длина которых не меньше min_length символов.

Например:

Привет! Как дела?
Всё хорошо!
Отлично! До встречи.
Спасибо!
Ок.
Хорошо, увидимся завтра!

При:

min_length=10

нужно оставить только достаточно длинные сообщения.
"""

raw = """   Иван:   Привет!    Как дела?   \r\n
        Анна:   Всё хорошо!     \r\n\r\n
        Петр:    Отлично!    До встречи.
        \r\n
        Анна:   Спасибо!   \r\n
        Иван:   Ок.
        Анна:   Хорошо, увидимся завтра!
        """


def filter_messages(raw: str, *, min_length: int = 10) -> str:
    """Фильтрация сообщений по длине."""

    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    clean_lines = []

    for line in lines:
        parts = line.split(":", 1)
        
        if len(parts) == 2:
            message = " ".join(parts[1].split())

            if len(message) >= min_length:
                clean_lines.append((parts[0].strip() + ": " + message))

    return "\n".join(clean_lines)


print(f"----filter_messages----\n{filter_messages(raw)}")


def message_stats(raw: str) -> dict[str, int]:
    """Статистика количества сообщений."""

    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.strip().split("\n")

    # lines_new = []
    #
    # for line in lines:
    #     line = line.split()
    #     if line:
    #         line = " ".join(line)
    #         lines_new.append(line)
    #
    # return "\n".join(lines_new)

    stats = {}

    for line in lines:
        parts = line.split(":", 1)

        if len(parts) == 2:
            name = parts[0].strip()  # получаем ключ для словаря
            message = parts[1].strip()  # получаем значение для словаря
            # stats[name] = message         # создаем словарь "название словаря[ключ]=значение

            if name not in stats:
                # stats[name] = 1              # добавляем имя в словарь если его нет и ставим ему значение 1
                stats[name] = [message]  # добавляем сообщение в словарь если его нет

            else:
                # stats[name] += 1              # прибавляем 1 к значению, если имя повторяется
                stats[name].append(message)  # добавляем сообщение к списку сообщений

    return stats


print(f"----message_stats----\n{message_stats(raw)}")


def longest_messages(raw: str) -> dict[str, str]:
    """Поиск самого длинного сообщения."""

    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    stats = {}

    for line in lines:
        parts = line.split(":", 1)

        if len(parts) == 2:
            name = parts[0].strip()
            message = parts[1].strip()

            if name not in stats:
                stats[name] = [message]

            else:
                stats[name].append(message)

    result = {}

    for name, messages in stats.items():
        longest_message = max(messages, key=len)
        result[name] = longest_message

    return result


print(f"----longest_messages----\n{longest_messages(raw)}")


def counter_messages(raw: str) -> dict[str, str]:
    """Поиск самого длинного сообщения."""

    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    stats = {}

    for line in lines:
        parts = line.split(":", 1)

        if len(parts) == 2:
            name = parts[0].strip()

            if name not in stats:
                stats[name] = 1

            else:
                stats[name] += 1

    # result = {}
    max_count = 0
    max_name = ""

    for name, count in stats.items():
        if count > max_count:
            max_count = count
            max_name = name

    # result[max_name] = max_count

    return {max_name: max_count}

    # max_count_message = len(messages)
    # max_count[name] = max_count_message

    # return max_count


print(f"----counter_messages----\n{counter_messages(raw)}")
