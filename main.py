"""
Главный модуль бота TaskBot.

Отвечает за:
- инициализацию бота и диспетчера aiogram;
- подключение роутеров (handlers);
- регистрацию middleware;
- запуск планировщика напоминаний;
- запуск процесса polling для получения обновлений от Telegram.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import common_router, export_router, tasks_router
from middlewares.database_middleware import DatabaseMiddleware
from middlewares.logging_middleware import LoggingMiddleware
from scheduler.reminders import start_scheduler

# Настройка логирования: время, уровень, сообщение.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """
    Основная асинхронная функция запуска бота.

    Создает экземпляр бота, подключает обработчики,
    инициализирует БД и планировщик, запускает polling.
    """
    # Проверяем наличие токена перед запуском.
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не задан. Проверьте файл .env")
        return

    # Создаем объект бота с настройками по умолчанию.
    bot = Bot(token=BOT_TOKEN)

    # Storage для хранения состояний FSM в памяти (для небольших команд).
    storage = MemoryStorage()

    # Dispatcher отвечает за маршрутизацию входящих обновлений.
    dp = Dispatcher(storage=storage)

    # Инициализируем базу данных (создаем таблицы, если их нет).
    db = await init_db()

    # Регистрируем middleware для логирования всех входящих сообщений.
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Регистрируем middleware для передачи подключения к БД.
    # Это позволяет хендлерам получать db через аргумент функции.
    dp.message.middleware(DatabaseMiddleware(db))
    dp.callback_query.middleware(DatabaseMiddleware(db))

    # Подключаем роутеры с обработчиками команд.
    dp.include_router(common_router)
    dp.include_router(tasks_router)
    dp.include_router(export_router)

    # Запускаем планировщик ежедневных напоминаний.
    start_scheduler(bot, db)

    logger.info("Бот запущен. Ожидание сообщений...")

    try:
        # Запускаем основной цикл получения обновлений.
        await dp.start_polling(bot)
    finally:
        # При завершении работы закрываем подключение к БД и сессию бота.
        await db.close()
        await bot.session.close()
        logger.info("Бот остановлен.")


if __name__ == "__main__":
    # Точка входа: запускаем асинхронную функцию main.
    asyncio.run(main())
