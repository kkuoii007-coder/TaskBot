"""
Reply-клавиатура главного меню бота.

Содержит основные команды, доступные пользователю в любой момент.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает главное меню бота с основными командами.

    Возвращает:
        ReplyKeyboardMarkup с кнопками для навигации.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/add - Создать задачу"),
                KeyboardButton(text="/list - Список задач"),
            ],
            [
                KeyboardButton(text="/my - Мои задачи"),
                KeyboardButton(text="/list_csv - Экспорт CSV"),
            ],
            [
                KeyboardButton(text="/help - Помощь"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
