# raw = """   Иван:   Привет!    Как дела?   \r\n
# Анна:   Всё хорошо!     \r\n\r\n
# Петр:    Отлично!    До встречи.
# \r\n
# Анна:   Спасибо!   \r\n
# Иван:   Ок.
# Анна:   Хорошо, увидимся завтра!
# Федор: Привет.
# Федор: Как у вас дела?
# """
import time


def input_data():
    raws = []

    while True:
        raw = input("Введите данные:\n")

        if raw.lower() == 'стоп':
            print("Выход из цикла.")
            break

        else:
            raws.append(raw)

    print(raws)
    time.sleep(0.2)
    return raws


def authors_with_long_messages(row: str, *, min_length: int = 1) -> dict[str, int]:
    """Функция определения сколько длинных сообщений написал каждый автор."""

    # text = row.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in row]

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

    # print(f"----- stats ----- \n{stats}")

    author_msg = {}

    for name, messages in stats.items():
        for message in messages:
            if len(message) > min_length:

                if name not in author_msg:
                    author_msg[name] = 1

                else:
                    author_msg[name] += 1

    # print(f"----- author_msg ----- \n{author_msg}")

    massages_info = {}

    for name, messages in stats.items():

        messages_list = []

        for message in messages:
            massages_i = {
                "Сообщение": message,
                "Длинна": len(message),
            }
            messages_list.append(massages_i)

        massages_info[name] = messages_list

    # print(f"----- massages_info ----- \n{massages_info}")

    table_rows = []

    for name, items in massages_info.items():

        for item in items:
            table_rows.append({
                'Автор': name,
                'Сообщение': item['Сообщение'],
                'Длинна': item['Длинна']
            })


    # Вывод таблицы через pandas
    import pandas as pd

    df = pd.DataFrame(table_rows)
    print(f"\nТаблица Pandas:\n", df)

    print("\nСохранение в файл:")

    # Сохранение в файл
    try:
        df.to_excel('data/messages_report.xlsx', index=False)
        print("Файл messages_report.xlsx успешно сохранен.")

        df.to_csv('data/messages_report.csv', index=False, sep=';', encoding='utf-8-sig')
        print("Файл messages_report.csv успешно сохранен.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    import csv

    with open('data/messages_report_python.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        # Задаем заголовки колонок и разделитель точку с запятой
        writer = csv.DictWriter(csvfile, fieldnames=['Автор', 'Сообщение', 'Длинна'], delimiter=';')

        writer.writeheader()  # Пишем шапку таблицы
        writer.writerows(table_rows)  # Пишем все строки данных

    print("Файл успешно сохранен без внешних библиотек!")

    # Вывод таблицы через tabulate
    from tabulate import tabulate

    print(f"\nТаблица tabulate:\n", tabulate(table_rows, headers="keys", tablefmt="psql"))

    # Чистый Python
    print(f"\nТаблица Python:")
    print(f"{'Автор':<10} | {'Сообщение':<26} | {'Длинна':<6}")
    print(f"=" * 50)

    for row in table_rows:
        print(f"{row['Автор']:<10} | {row['Сообщение']:<26} | {row['Длинна']:<6}")

    return massages_info


def record_data_in_xlsx_style(data_file: dict) -> None:
    """Запись данных в файл xlsx и стилизация таблицы."""

    import pandas as pd
    from openpyxl.styles import (PatternFill, Font, Alignment,
                                 Border, Side)
    from openpyxl.utils import get_column_letter

    # 2. Готовим список с данными из входящего словаря
    table_rows = []

    for name, items in data_file.items():

        for item in items:
            table_rows.append({
                'Автор': name,
                'Сообщение': item.get('Сообщение', None),
                'Длинна': item.get('Длинна', None)
            })

    df = pd.DataFrame(table_rows)

    # 2. Начинаем запись в Excel с красивым оформлением
    file_name = 'data/beautiful_messages_report.xlsx'

    # Используем ExcelWriter для тонкой настройки стилей
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Аналитика', index=False)

        # Получаем доступ к листу openpyxl для стилизации
        # workbook = writer.book
        worksheet = writer.sheets['Аналитика']

        # --- СТИЛИЗАЦИЯ ШАПКИ ---
        # Красивый темно-синий цвет для фона и белый жирный шрифт
        header_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
        header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
        center_alignment = Alignment(horizontal='center', vertical='center')

        #== Стили для «зебры» и границ
        # Светло-серый для четных строк
        gray_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        # Белый для нечетных
        white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

        thin_border = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )

        # Применяем стили к первой строке (заголовкам)
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_alignment

        # --- СТИЛИЗАЦИЯ СТРОК ДАННЫХ И «ЗЕБРА» ---
        for row_idx in range(2, worksheet.max_row + 1):
            # Если номер строки четный — красим в серый, если нечетный — оставляем белым
            current_fill = gray_fill if row_idx % 2 == 0 else white_fill

            for col_idx in range(1, worksheet.max_column + 1):
                cell = worksheet.cell(row=row_idx, column=col_idx)
                cell.fill = current_fill
                cell.border = thin_border

                # Дополнительно: выравниваем числа по центру
                if col_idx == 3:
                    cell.alignment = center_alignment

        # --- АВТОПОДБОР ШИРИНЫ КОЛОНОК ---
        # Проходим по всем колонкам и делаем ширину по самому длинному тексту + запас
        for col in worksheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)

            for cell in col:
                if cell.value is not None:
                    max_len = max(max_len, len(str(cell.value)))

            # Устанавливаем ширину с небольшим отступом
            worksheet.column_dimensions[col_letter].width = max(max_len + 5, 15)

    print(f"\nФайл '{file_name}' с отредактированными строками и подсветкой 'зебра' успешно создан!")


if __name__ == "__main__":
    raw = input_data()
    data_dict = authors_with_long_messages(raw)
    record_data_in_xlsx_style(data_dict)
# print(f"----authors_with_long_messages----\n{authors_with_long_messages(raw, min_length=1)}")
print(f":" * 60)

















#
# # =========================================================
# raw = """ Иван: Привет! Как дела? \r\n
# Анна: Всё хорошо! \r\n\r\n
# Петр: Отлично! До встречи.
# \r\n
# Анна: Спасибо! \r\n
# Иван: Ок.
# Анна: Хорошо, увидимся завтра!"""
#
#
# # ----authors_with_long_messages - ---
# # {'Иван': 1, 'Анна': 1, 'Петр': 1}
#
# def authors_with_long_messages(row: str, min_length: int = 15) -> dict[str, list[str]]:
#     raw_replace = row.replace("\r\n", "")
#     raw_split = raw_replace.strip().split("\n")
#
#     stats = {}
#
#     for i in raw_split:
#         parts = i.split(":", 1)
#
#         if len(parts) == 2:
#             name = parts[0].strip()
#             message = parts[1].strip()
#
#             if name not in stats:
#                 stats[name] = [message]
#
#             else:
#                 stats[name].append(message)
#
#     stats_5 = {}
#
#     for k, v in stats.items():
#         # stats_5[k] = {msg: len(msg) for msg in v}
#         inner = {}
#
#         for msg in v:
#             inner[msg] = len(msg)
#
#         stats_5[k] = inner
#
#     # print(f"DICT 5\n", stats_5)
#
#     stats_6 = {}
#
#     for k, v in stats.items():
#         # stats_6[k] = {i: {"Сообщение": msg, "длина": len(msg)} for i, msg in enumerate(v, 1)}
#
#         inner = {}
#
#         for i, msg in enumerate(v, 1):
#             inner[i] = {"Сообщение": msg, "длина": len(msg)}
#
#         stats_6[k] = inner
#
#     # print(f"DICT 6\n", stats_6)
#
#     stats_3 = {}
#
#     for k, v in stats.items():
#         new_list = []
#
#         for i in v:
#             stats_2 = {"Сообщение": i, "длина": len(i)}
#             new_list.append(stats_2)
#
#         stats_3[k] = new_list
#
#     # print(f"DICT 3\n", stats_3)
#
#     stats_2 = {}
#
#     for k, v in stats.items():
#         # print(v)
#         for s in v:
#             # print(s)
#             if len(s) >= min_length:
#                 if k not in stats_2:
#                     stats_2[k] = 1
#                 else:
#                     stats_2[k] += 1
#
#     # print(f"DICT 2\n", stats_2)
#
#     return stats_3
#
#
# # result = authors_with_long_messages(raw)
# # print(result)
