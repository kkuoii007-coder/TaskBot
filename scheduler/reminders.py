"""
Планировщик напоминаний о задачах.

Использу APScheduler для ежедневной проверки задач с дедлайном
сегодня или завтра и отправки уведомлений создателям.
"""

import logging
from datetime import datetime, timedelta

from aiogram import Bot
import aiosqlite

from database.queries import get_tasks_with_deadline

# Создаем логгер для планировщика.
logger = logging.getLogger(__name__)

# Запускаем планировщик один раз при старте бота.
# Уведомления отправляются каждый день в 09:00.


def start_scheduler(bot: Bot, db: aiosqlite.Connection) -> None:
    """
    Запускает планировщик напоминаний.

    Настраивает APScheduler для ежедневной проверки задач
    с дедлайном сегодня или завтра.

    Аргументы:
        bot - экземпляр бота для отправки уведомлений.
        db  - подключение к базе данных.
    """
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    # Создаем асинхронный планировщик.
    scheduler = AsyncIOScheduler()

    # Добавляем задачу на ежедневное выполнение в 09:00.
    scheduler.add_job(
        _send_reminders,
        "cron",
        hour=9,
        minute=0,
        args=[bot, db],
        id="send_deadline_reminders",
        name="Напоминания о дедлайнах",
        replace_existing=True,
    )

    # Запускаем планировщик.
    scheduler.start()
    logger.info("Планировщик напоминаний запущен.")


async def _send_reminders(bot: Bot, db: aiosqlite.Connection) -> None:
    """
    Отправляет напоминания о задачах с дедлайном сегодня или завтра.

    Проверяет задачи, у которых дедлайн совпадает с сегодняшней
    или завтрашней датой, и статус не 'done'/'cancelled'.

    Аргументы:
        bot - экземпляр бота для отправки уведомлений.
        db  - подключение к базе данных.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Получаем задачи с дедлайном сегодня.
    today_tasks = await get_tasks_with_deadline(db, today)

    # Получаем задачи с дедлайном завтра.
    tomorrow_tasks = await get_tasks_with_deadline(db, tomorrow)

    all_tasks = today_tasks + tomorrow_tasks

    if not all_tasks:
        logger.info("Нет задач с дедлайном сегодня или завтра.")
        return

    # Отправляем напоминания каждому создателю.
    for task in all_tasks:
        user_id = task["user_id"]
        task_id = task["id"]
        text = task["text"]
        deadline = task["deadline"]

        # Форматируем дату дедлайна в формат ДД.ММ.ГГГГ.
        deadline_formatted = datetime.strptime(deadline, "%Y-%m-%d").strftime("%d.%m.%Y")

        # Определяем текст напоминания.
        if deadline == today:
            reminder = (
                f"⏰ *Напоминание!*\n"
                f"Задача #{task_id} «{text}» истекает сегодня ({deadline_formatted})"
            )
        else:
            reminder = (
                f"⏰ *Напоминание!*\n"
                f"Задача #{task_id} «{text}» истекает завтра ({deadline_formatted})"
            )

        try:
            await bot.send_message(
                user_id,
                reminder,
                parse_mode="Markdown",
            )
            logger.info("Напоминание отправлено пользователю %s", user_id)
        except Exception as e:
            logger.error("Не удалось отправить напоминание пользователю %s: %s", user_id, e)
