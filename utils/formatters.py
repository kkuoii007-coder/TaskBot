"""
Утилита для форматирования карточки задачи.

Содержит функции для красивого отображения задач в Telegram.
Использует HTML-разметку для безопасного отображения пользовательского текста.
"""

from datetime import datetime
from html import escape


def _format_date(iso_string: str | None) -> str:
    """
    Форматирует дату из ISO-строки в формат ДД.ММ.ГГГГ ЧЧ:ММ.

    Аргументы:
        iso_string - дата в формате ISO 8601.

    Возвращает:
        Отформатированную дату или 'Не указано'.
    """
    if not iso_string:
        return "Не указано"

    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%d.%m.%Y в %H:%M")
    except (ValueError, TypeError):
        return iso_string


def _format_deadline(iso_string: str | None) -> str:
    """
    Форматирует дату дедлайна в формат ДД.ММ.ГГГГ.

    Аргументы:
        iso_string - дата в формате ISO 8601.

    Возвращает:
        Отформатированную дату или 'Не указано'.
    """
    if not iso_string:
        return "Не указано"

    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        return iso_string


def _get_priority_emoji(priority: str) -> str:
    """
    Возвращает эмодзи для приоритета.

    Аргументы:
        priority - строка приоритета ('low', 'medium', 'high').

    Возвращает:
        Эмодзи соответствующего приоритета.
    """
    emojis = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
    }
    return emojis.get(priority, "⚪")


def _get_priority_name(priority: str) -> str:
    """
    Возвращает название приоритета на русском.

    Аргументы:
        priority - строка приоритета.

    Возвращает:
        Название приоритета.
    """
    names = {
        "high": "Высокий",
        "medium": "Средний",
        "low": "Низкий",
    }
    return names.get(priority, "Не указан")


def _get_status_name(status: str) -> str:
    """
    Возвращает название статуса на русском.

    Аргументы:
        status - строка статуса.

    Возвращает:
        Название статуса.
    """
    names = {
        "new": "Новая",
        "in_progress": "В работе",
        "done": "Выполнена",
        "cancelled": "Отменена",
    }
    return names.get(status, "Неизвестно")


def format_task_card(task: dict) -> str:
    """
    Форматирует задачу в красивую карточку для отображения в Telegram.

    Использует HTML-разметку. Пользовательский текст экранируется
    функцией html.escape для предотвращения поломки разметки.

    Аргументы:
        task - словарь с данными задачи из БД.

    Возвращает:
        Отформатированную HTML-строку карточки задачи.
    """
    # Получаем данные задачи и экранируем пользовательский ввод.
    task_id = task["id"]
    text = escape(str(task["text"]))
    user = escape(str(task["user"]))
    assignee = escape(str(task.get("assignee") or "Не назначен"))
    priority_emoji = _get_priority_emoji(task["priority"])
    priority_name = _get_priority_name(task["priority"])
    deadline = _format_deadline(task.get("deadline"))
    status = _get_status_name(task["status"])
    created_at = _format_date(task["created_at"])

    # Формируем карточку в HTML-разметке.
    card = (
        f"📋 <b>Задача #{task_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 {text}\n"
        f"👤 Автор: @{user}\n"
        f"👷 Исполнитель: {assignee}\n"
        f"{priority_emoji} Приоритет: {priority_name}\n"
        f"📅 Дедлайн: {deadline}\n"
        f"🔄 Статус: {status}\n"
        f"🕐 Создана: {created_at}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    return card
