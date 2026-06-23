"""
Inline-клавиатуры для бота.

Используются в пошаговых диалогах и для изменения статусов задач.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_priority_keyboard() -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для выбора приоритета задачи.

    Возвращает:
        InlineKeyboardMarkup с кнопками приоритетов.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔴 Высокий", callback_data="priority:high"),
                InlineKeyboardButton(text="🟡 Средний", callback_data="priority:medium"),
                InlineKeyboardButton(text="🟢 Низкий", callback_data="priority:low"),
            ],
        ],
    )


def get_skip_deadline_keyboard() -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру с кнопкой пропуска дедлайна.

    Возвращает:
        InlineKeyboardMarkup с кнопкой пропуски.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Пропустить", callback_data="skip:deadline"),
            ],
        ],
    )


def get_skip_assignee_keyboard() -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру с кнопкой пропуска исполнителя.

    Возвращает:
        InlineKeyboardMarkup с кнопкой пропуски.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Пропустить", callback_data="skip:assignee"),
            ],
        ],
    )


def get_status_keyboard(status: str, task_id: int | None = None) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру для изменения статуса задачи.

    Аргументы:
        status   - текущий статус задачи (для определения доступных кнопок)
        task_id  - ID задачи (для передачи в callback_data)

    Возвращает:
        InlineKeyboardMarkup с кнопками статусов.
    """
    buttons = []

    if status in ("new", "in_progress"):
        cb_data = f"status:in_progress:{task_id}" if task_id else "status:in_progress"
        buttons.append(InlineKeyboardButton(text="▶️ В работу", callback_data=cb_data))

    if status in ("new", "in_progress"):
        cb_data = f"status:done:{task_id}" if task_id else "status:done"
        buttons.append(InlineKeyboardButton(text="✅ Выполнено", callback_data=cb_data))

    if status in ("new", "in_progress"):
        cb_data = f"status:cancelled:{task_id}" if task_id else "status:cancelled"
        buttons.append(InlineKeyboardButton(text="❌ Отменено", callback_data=cb_data))

    return InlineKeyboardMarkup(
        inline_keyboard=[buttons],
    )
