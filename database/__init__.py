"""
Пакет для работы с базой данных.

Содержит подключение к SQLite и SQL-запросы для работы с задачами.
"""

from .connection import init_db
from .queries import (
    add_task,
    cancel_task,
    create_task,
    delete_task,
    export_tasks,
    get_task_by_id,
    get_tasks_with_deadline,
    list_active_tasks,
    set_task_status,
    update_task_status,
    user_tasks,
)

__all__ = [
    "init_db",
    "add_task",
    "cancel_task",
    "create_task",
    "delete_task",
    "export_tasks",
    "get_task_by_id",
    "get_tasks_with_deadline",
    "list_active_tasks",
    "set_task_status",
    "update_task_status",
    "user_tasks",
]
