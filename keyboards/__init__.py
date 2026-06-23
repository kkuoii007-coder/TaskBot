"""
Пакет с клавиатурами бота.

Содержит reply- и inline-клавиатуры для взаимодействия с пользователем.
"""

from .inline import (
    get_priority_keyboard,
    get_skip_assignee_keyboard,
    get_skip_deadline_keyboard,
    get_status_keyboard,
)
from .reply import get_main_menu_keyboard

__all__ = [
    "get_main_menu_keyboard",
    "get_priority_keyboard",
    "get_skip_deadline_keyboard",
    "get_skip_assignee_keyboard",
    "get_status_keyboard",
]
