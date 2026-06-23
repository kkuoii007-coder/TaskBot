"""
Middleware для передачи подключения к базе данных в обработчики.

В aiogram 3.x нельзя напрямую получить доступ к dispatcher из handler,
поэтому используем middleware для передачи db через data контекста.
"""

from typing import Any, Awaitable, Callable

import aiosqlite

from aiogram import BaseMiddleware


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware для передачи подключения к БД во все обработчики.

    Добавляет ключ 'db' в data контекста, который доступен
    в обработчиках через аргумент функции.
    """

    def __init__(self, db: aiosqlite.Connection) -> None:
        """
        Инициализирует middleware с подключением к БД.

        Аргументы:
            db - подключение к SQLite через aiosqlite.
        """
        self.db = db

    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        """
        Добавляет db в data и вызывает следующий обработчик.

        Аргументы:
            handler - следующий обработчик в цепочке.
            event   - входящее событие.
            data    - контекст данных события.

        Возвращает:
            Результат вызова следующего обработчика.
        """
        # Добавляем подключение к БД в контекст.
        data["db"] = self.db
        return await handler(event, data)
