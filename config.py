"""
Модуль конфигурации.

Загружает переменные окружения из файла `.env` и предоставляет
доступ к ним в виде удобных констант.
"""

import os

from dotenv import load_dotenv

# Загружаем переменные из .env файла (если он есть).
# Это позволяет не хранить секреты прямо в коде.
load_dotenv()


# Токен бота Telegram, полученный у @BotFather.
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# ID чата или группы для отправки уведомлений (необязательно).
# Может быть пустым, если массовые уведомления не нужны.
NOTIFY_CHAT_ID: str | None = os.getenv("NOTIFY_CHAT_ID")

# Имя файла базы данных SQLite. Хранится рядом с проектом.
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "taskbot.db")
