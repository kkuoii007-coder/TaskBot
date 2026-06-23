"""
Модуль подключения к базе данных SQLite.

Отвечает за инициализацию подключения и создание таблиц/индексов.
В проекте используется асинхронная обертка aiosqlite,
чтобы не блокировать основной event loop бота.
"""

import logging

import aiosqlite

from config import DATABASE_NAME

# SQL-запрос для создания основной таблицы задач.
CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    text        TEXT NOT NULL,
    "user"      TEXT NOT NULL,
    user_id     INTEGER NOT NULL,
    assignee    TEXT,
    status      TEXT NOT NULL DEFAULT 'new',
    priority    TEXT NOT NULL DEFAULT 'medium',
    deadline    TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
"""

# Индексы для ускорения фильтрации по часто используемым полям.
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);",
    "CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline);",
]


async def init_db() -> aiosqlite.Connection:
    """
    Инициализирует подключение к SQLite и создает таблицы с индексами.

    Возвращает:
        Объект асинхронного подключения aiosqlite.Connection.
    """
    # Открываем соединение с базой данных.
    db = await aiosqlite.connect(DATABASE_NAME)

    # Включаем поддержку внешних ключей (хорошая практика для SQLite).
    await db.execute("PRAGMA foreign_keys = ON;")

    # Создаем таблицу задач.
    await db.execute(CREATE_TASKS_TABLE)

    # Создаем индексы для производительности.
    for index_query in CREATE_INDEXES:
        await db.execute(index_query)

    # Сохраняем изменения.
    await db.commit()

    logging.info("База данных инициализирована: %s", DATABASE_NAME)
    return db
