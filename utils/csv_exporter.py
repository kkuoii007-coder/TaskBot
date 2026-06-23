"""
Утилита для генерации CSV-файла из данных задач.

Импортируется из handlers/export.py для экспорта задач.
CSV генерируется с BOM для корректного открытия в Excel.
"""

import csv
import io

# BOM (Byte Order Mark) для корректного отображения UTF-8 в Excel.
CSV_BOM = "\ufeff"


def generate_csv(tasks: list[dict]) -> str:
    """
    Генерирует CSV-строку из списка задач.

    Добавляет BOM в начало файла для корректного открытия в Excel
    (Excel требует BOM для распознавания UTF-8 кодировки).

    Аргументы:
        tasks - список словарей с данными задач.

    Возвращает:
        CSV-строку в кодировке UTF-8 с BOM.
    """
    # Определяем колонки CSV.
    fieldnames = [
        "id",
        "text",
        "user",
        "user_id",
        "assignee",
        "status",
        "priority",
        "deadline",
        "created_at",
        "updated_at",
    ]

    # Создаем буфер для записи CSV.
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

    writer.writeheader()
    writer.writerows(tasks)

    # Добавляем BOM в начало для Excel.
    return CSV_BOM + output.getvalue()
