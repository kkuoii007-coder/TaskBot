"""
Обработчики команд экспорта: /list_csv.

Позволяет экспортировать все задачи в CSV-файл.
"""

import logging

import aiosqlite
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from database.queries import export_tasks
from utils.csv_exporter import generate_csv

# Создаем роутер для экспорта.
export_router = Router()

# Логгер для этого модуля.
logger = logging.getLogger(__name__)


@export_router.message(Command("list_csv"))
async def cmd_list_csv(message: Message, db: aiosqlite.Connection) -> None:
    """
    Обработчик команды /list_csv.

    Экспортирует все задачи в CSV-файл и отправляет его пользователю.

    Аргументы:
        message - входящее сообщение от пользователя.
        db      - подключение к базе данных (из middleware).
    """
    try:
        tasks = await export_tasks(db)

        if not tasks:
            await message.answer("📭 Нет задач для экспорта.")
            return

        # Генерируем CSV-файл с BOM для корректного открытия в Excel.
        csv_content = generate_csv(tasks)

        # Отправляем файл пользователю (кодируем в UTF-8 байты).
        await message.answer_document(
            BufferedInputFile(
                csv_content.encode("utf-8"),
                filename="tasks_export.csv",
            ),
            caption="📊 Экспорт всех задач в CSV.",
        )
        logger.info("CSV-экспорт выполнен для user_id=%s", message.from_user.id)

    except Exception as e:
        logger.error("Ошибка при экспорте CSV: %s", e)
        await message.answer(f"❌ Ошибка при экспорте: {e}")
