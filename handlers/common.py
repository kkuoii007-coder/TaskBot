"""
Обработчики общих команд: /start и /help.

Эти команды доступны всегда и не требуют FSM-состояний.
"""

import aiosqlite
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards.reply import get_main_menu_keyboard

# Создаем роутер для группировки обработчиков.
common_router = Router()


@common_router.message(Command("start"))
async def cmd_start(message: Message, db: aiosqlite.Connection) -> None:
    """
    Обработчик команды /start.

    Приветствует пользователя, показывает главное меню
    и регистрирует его в системе.

    Аргументы:
        message - входящее сообщение от пользователя.
        db      - подключение к базе данных (из middleware).
    """
    # Формируем приветственное сообщение.
    welcome_text = (
        "👋 Привет! Я TaskBot — помощник для управления задачами вашей команды.\n\n"
        "Вы можете создавать задачи, отслеживать их статус, "
        "назначать исполнителей и получать напоминания о дедлайнах.\n\n"
        "Используйте меню ниже для навигации или /help для списка всех команд."
    )

    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


@common_router.message(Command("help"))
async def cmd_help(message: Message, db: aiosqlite.Connection) -> None:
    """
    Обработчик команды /help.

    Выводит список всех доступных команд с описанием.

    Аргументы:
        message - входящее сообщение от пользователя.
        db      - подключение к базе данных (из middleware).
    """
    help_text = (
        "<b>📋 Список команд:</b>\n\n"
        "• /add — Создать новую задачу (пошаговый диалог)\n"
        "• /list — Показать все активные задачи команды\n"
        "• /my — Показать задачи, созданные вами\n"
        "• /done &lt;id&gt; — Отметить задачу как выполненную\n"
        "• /cancel &lt;id&gt; — Отменить задачу\n"
        "• /status &lt;id&gt; — Изменить статус через кнопки\n"
        "• /delete &lt;id&gt; — Удалить задачу (только автор)\n"
        "• /list_csv — Экспорт всех задач в CSV-файл\n"
        "• /help — Показать этот список команд"
    )

    await message.answer(help_text, parse_mode="HTML")
