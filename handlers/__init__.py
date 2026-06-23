"""
Пакет обработчиков бота.

Экспортирует роутеры для подключения в main.py.
"""

from .common import common_router
from .tasks import tasks_router
from .export import export_router

__all__ = [
    "common_router",
    "tasks_router",
    "export_router",
]
