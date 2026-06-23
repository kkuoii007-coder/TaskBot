"""
Пакет планировщика бота.

Содержит логику для отправки напоминаний о задачах.
"""

from .reminders import start_scheduler

__all__ = [
    "start_scheduler",
]
