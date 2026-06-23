"""
Middleware для логирования входящих сообщений.

Записывает в лог все входящие сообщения и callback-вызовы.
Помогает отслеживать работу бота и отлаживать проблемы.
"""

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

# Создаем логгер для middleware.
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для логирования всех входящих обновлений.

    Записывает информацию о сообщении или callback-вызове
    в лог-файл бота.
    """

    async def __call__(
        self,
        handler: Callable[[Any, dict], Awaitable[Any]],
        event: Any,
        data: dict,
    ) -> Any:
        """
        Вызывается перед обработчиком события.

        Аргументы:
            handler - следующий обработчик в цепочке.
            event   - входящее событие (Message или CallbackQuery).
            data    - данные события, переданные в обработчик.

        Возвращает:
            Результат вызова следующего обработчика.
        """
        # Логируем входящее сообщение.
        if isinstance(event, Message):
            logger.info(
                "Входящее сообщение: user_id=%s, text=%s",
                event.from_user.id,
                event.text or "No text",
            )

        # Логируем callback-вызов.
        elif isinstance(event, CallbackQuery):
            logger.info(
                "Callback: user_id=%s, data=%s",
                event.from_user.id,
                event.data,
            )

        # Вызываем следующий обработчик.
        return await handler(event, data)
