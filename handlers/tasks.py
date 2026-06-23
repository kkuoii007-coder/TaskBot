"""
Обработчики команд работы с задачами: /add, /list, /my, /done, /cancel, /status, /delete.

Содержит FSM-диалог для добавления задач и обработчики для остальных команд.
"""

import logging
from datetime import datetime, timedelta

import aiosqlite
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from keyboards.inline import (
    get_priority_keyboard,
    get_skip_deadline_keyboard,
    get_skip_assignee_keyboard,
    get_status_keyboard,
)
from database.queries import (
    add_task,
    get_task_by_id,
    list_active_tasks,
    user_tasks,
    update_task_status,
    cancel_task,
    delete_task,
)
from utils.formatters import format_task_card

# Создаем роутер для группировки обработчиков задач.
tasks_router = Router()

# Логгер для этого модуля.
logger = logging.getLogger(__name__)


# Состояния FSM для пошагового диалога добавления задачи.
class AddTask(StatesGroup):
    """Группа состояний для диалога добавления задачи."""
    waiting_for_text = State()        # Ожидание текста задачи
    waiting_for_priority = State()    # Ожидание выбора приоритета
    waiting_for_deadline = State()    # Ожидание дедлайна
    waiting_for_assignee = State()    # Ожидание исполнителя


@tasks_router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик команды /add.

    Запускает FSM-диалог для создания новой задачи.
    Первый шаг — ввод текста задачи.

    Аргументы:
        message - входящее сообщение от пользователя.
        state   - контекст FSM для хранения состояния диалога.
        db      - подключение к базе данных (из middleware).
    """
    await state.clear()  # Очищаем предыдущие состояния, если были.
    await state.set_state(AddTask.waiting_for_text)
    await message.answer("📝 Введите текст задачи:")


@tasks_router.message(AddTask.waiting_for_text)
async def process_task_text(message: Message, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик первого шага FSM: ввод текста задачи.

    Сохраняет текст и переходит к выбору приоритета.

    Аргументы:
        message - входящее сообщение с текстом задачи.
        state   - контекст FSM.
        db      - подключение к базе данных (из middleware).
    """
    await state.update_data(text=message.text)
    await state.set_state(AddTask.waiting_for_priority)
    await message.answer(
        "🎯 Укажите приоритет:",
        reply_markup=get_priority_keyboard(),
    )


@tasks_router.callback_query(F.data.startswith("priority:"), StateFilter(AddTask.waiting_for_priority))
async def process_priority(callback: CallbackQuery, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик выбора приоритета.

    Сохраняет приоритет и переходит к вводу дедлайна.

    Аргументы:
        callback - вызов inline-кнопки.
        state    - контекст FSM.
        db       - подключение к базе данных (из middleware).
    """
    priority = callback.data.split(":")[1]  # Извлекаем 'high', 'medium' или 'low'.
    await state.update_data(priority=priority)
    await state.set_state(AddTask.waiting_for_deadline)
    await callback.message.answer(
        "📅 Укажите дедлайн (ГГГГ-ММ-ДД) или нажмите «Пропустить»:",
        reply_markup=get_skip_deadline_keyboard(),
    )
    await callback.answer()


@tasks_router.callback_query(F.data == "skip:deadline", StateFilter(AddTask.waiting_for_deadline))
async def process_skip_deadline(callback: CallbackQuery, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик пропуска дедлайна.

    Сохраняет None как дедлайн и переходит к вводу исполнителя.

    Аргументы:
        callback - вызов inline-кнопки.
        state    - контекст FSM.
        db       - подключение к базе данных (из middleware).
    """
    await state.update_data(deadline=None)
    await state.set_state(AddTask.waiting_for_assignee)
    await callback.message.answer(
        "👷 Укажите исполнителя (@username) или нажмите «Пропустить»:",
        reply_markup=get_skip_assignee_keyboard(),
    )
    await callback.answer()


@tasks_router.message(AddTask.waiting_for_deadline)
async def process_deadline(message: Message, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик ввода дедлайна.

    Проверяет формат даты (ГГГГ-ММ-ДД) и сохраняет её.
    Если формат неверен — запрашивает ввод повторно.

    Аргументы:
        message - входящее сообщение с датой.
        state   - контекст FSM.
        db      - подключение к базе данных (из middleware).
    """
    raw_date = message.text.strip()

    # Проверяем, что дата соответствует формату YYYY-MM-DD.
    try:
        parsed = datetime.strptime(raw_date, "%Y-%m-%d")
    except ValueError:
        await message.answer(
            "❌ Неверный формат даты. Введите дедлайн в формате ГГГГ-ММ-ДД "
            "(например, 2026-06-30) или нажмите «Пропустить»:",
            reply_markup=get_skip_deadline_keyboard(),
        )
        return

    # Сохраняем дату в едином формате YYYY-MM-DD.
    await state.update_data(deadline=parsed.strftime("%Y-%m-%d"))
    await state.set_state(AddTask.waiting_for_assignee)
    await message.answer(
        "👷 Укажите исполнителя (@username) или нажмите «Пропустить»:",
        reply_markup=get_skip_assignee_keyboard(),
    )


@tasks_router.callback_query(F.data == "skip:assignee", StateFilter(AddTask.waiting_for_assignee))
async def process_skip_assignee(callback: CallbackQuery, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик пропуска исполнителя.

    Сохраняет None как исполнителя и завершает диалог.

    Аргументы:
        callback - вызов inline-кнопки.
        state    - контекст FSM.
        db       - подключение к базе данных (из middleware).
    """
    await state.update_data(assignee=None)
    await finalize_add_task(callback.message, state, db)


@tasks_router.message(AddTask.waiting_for_assignee)
async def process_assignee(message: Message, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик ввода исполнителя.

    Сохраняет username исполнителя и завершает диалог.

    Аргументы:
        message - входящее сообщение с username.
        state   - контекст FSM.
        db      - подключение к базе данных (из middleware).
    """
    await state.update_data(assignee=message.text)
    await finalize_add_task(message, state, db)


async def finalize_add_task(message: Message, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Финализирует создание задачи: сохраняет в БД и показывает карточку.

    Аргументы:
        message - сообщение для отправки результата.
        state   - контекст FSM с данными задачи.
        db      - подключение к базе данных (из middleware).
    """
    data = await state.get_data()
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"

    try:
        task_id = await add_task(
            db=db,
            user_id=user_id,
            username=username,
            text=data["text"],
            priority=data["priority"],
            deadline=data.get("deadline"),
            assignee=data.get("assignee"),
        )

        # Получаем созданную задачу для отображения.
        task = await get_task_by_id(db, task_id)
        card = format_task_card(task)

        await message.answer(card, parse_mode="HTML")
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ Ошибка при создании задачи: {e}")


@tasks_router.message(Command("list"))
async def cmd_list(message: Message, db: aiosqlite.Connection) -> None:
    """
    Обработчик команды /list.

    Показывает все активные задачи команды.

    Аргументы:
        message - входящее сообщение от пользователя.
        db      - подключение к базе данных (из middleware).
    """
    try:
        tasks = await list_active_tasks(db)

        if not tasks:
            await message.answer("📭 Активных задач нет.")
            return

        response = "📋 <b>Активные задачи команды:</b>\n\n"
        for task in tasks:
            card = format_task_card(task)
            response += f"{card}\n\n"

        await message.answer(response, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"❌ Ошибка при получении задач: {e}")


@tasks_router.message(Command("my"))
async def cmd_my(message: Message, db: aiosqlite.Connection) -> None:
    """
    Обработчик команды /my.

    Показывает все задачи, созданные текущим пользователем.

    Аргументы:
        message - входящее сообщение от пользователя.
        db      - подключение к базе данных (из middleware).
    """
    user_id = message.from_user.id

    try:
        tasks = await user_tasks(db, user_id)

        if not tasks:
            await message.answer("📭 У вас пока нет задач.")
            return

        response = f"📋 <b>Ваши задачи:</b> ({len(tasks)})\n\n"
        for task in tasks:
            card = format_task_card(task)
            response += f"{card}\n\n"

        await message.answer(response, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"❌ Ошибка при получении ваших задач: {e}")


@tasks_router.message(Command("done"))
async def cmd_done(message: Message, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик команды /done <id>.

    Помечает задачу как выполненную.

    Аргументы:
        message - входящее сообщение с ID задачи.
        state   - контекст FSM (для очистки состояния).
        db      - подключение к базе данных (из middleware).
    """
    await state.clear()

    parts = message.text.split()
    if len(parts) < 2:
        logger.warning("Команда /done без ID от user_id=%s", message.from_user.id)
        await message.answer("⚠️ Укажите ID задачи: /done <id>")
        return

    try:
        task_id = int(parts[1])
    except ValueError:
        logger.warning("Неверный ID задачи в /done: %s", parts[1])
        await message.answer("❌ ID задачи должен быть числом.")
        return

    logger.info("Обработка /done для задачи #%s, user_id=%s", task_id, message.from_user.id)

    try:
        task = await get_task_by_id(db, task_id)

        if not task:
            await message.answer(f"❌ Задача #{task_id} не найдена.")
            return

        if task["status"] == "done":
            await message.answer(f"⚠️ Задача #{task_id} уже выполнена.")
            return

        success = await update_task_status(db, task_id, "done")

        if success:
            await message.answer(f"✅ Задача #{task_id} отмечена как выполненная.")
            logger.info("Задача #%s отмечена как выполненная", task_id)
        else:
            await message.answer("❌ Не удалось обновить статус задачи.")

    except Exception as e:
        logger.error("Ошибка в /done: %s", e)
        await message.answer(f"❌ Ошибка: {e}")


@tasks_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик команды /cancel <id>.

    Отменяет задачу (устанавливает статус 'cancelled').

    Аргументы:
        message - входящее сообщение с ID задачи.
        state   - контекст FSM.
        db      - подключение к базе данных (из middleware).
    """
    await state.clear()

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ Укажите ID задачи: /cancel <id>")
        return

    try:
        task_id = int(parts[1])
    except ValueError:
        await message.answer("❌ ID задачи должен быть числом.")
        return

    try:
        task = await get_task_by_id(db, task_id)

        if not task:
            await message.answer(f"❌ Задача #{task_id} не найдена.")
            return

        success = await cancel_task(db, task_id)

        if success:
            await message.answer(f"❌ Задача #{task_id} отменена.")
        else:
            await message.answer("❌ Не удалось отменить задачу.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@tasks_router.message(Command("status"))
async def cmd_status(message: Message, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик команды /status <id>.

    Показывает inline-кнопки для изменения статуса задачи.

    Аргументы:
        message - входящее сообщение с ID задачи.
        state   - контекст FSM.
        db      - подключение к базе данных (из middleware).
    """
    await state.clear()

    parts = message.text.split()
    if len(parts) < 2:
        logger.warning("Команда /status без ID от user_id=%s", message.from_user.id)
        await message.answer("⚠️ Укажите ID задачи: /status <id>")
        return

    try:
        task_id = int(parts[1])
    except ValueError:
        logger.warning("Неверный ID задачи в /status: %s", parts[1])
        await message.answer("❌ ID задачи должен быть числом.")
        return

    logger.info("Обработка /status для задачи #%s, user_id=%s", task_id, message.from_user.id)

    try:
        task = await get_task_by_id(db, task_id)

        if not task:
            await message.answer(f"❌ Задача #{task_id} не найдена.")
            return

        card = format_task_card(task)
        keyboard = get_status_keyboard(task["status"], task_id)

        await message.answer(
            f"🔄 Изменить статус задачи #{task_id}:\n\n{card}",
            parse_mode="HTML",
            reply_markup=keyboard,
        )
        logger.info("Показаны кнопки статуса для задачи #%s", task_id)

    except Exception as e:
        logger.error("Ошибка в /status: %s", e)
        await message.answer(f"❌ Ошибка: {e}")


@tasks_router.message(Command("delete"))
async def cmd_delete(message: Message, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик команды /delete <id>.

    Удаляет задачу. Правила:
    - Автор может удалить свою задачу в любое время.
    - Любой пользователь может удалить задачу в течение 1 часа после создания.

    Аргументы:
        message - входящее сообщение с ID задачи.
        state   - контекст FSM.
        db      - подключение к базе данных (из middleware).
    """
    await state.clear()

    parts = message.text.split()
    if len(parts) < 2:
        logger.warning("Команда /delete без ID от user_id=%s", message.from_user.id)
        await message.answer("⚠️ Укажите ID задачи: /delete <id>")
        return

    try:
        task_id = int(parts[1])
    except ValueError:
        logger.warning("Неверный ID задачи в /delete: %s", parts[1])
        await message.answer("❌ ID задачи должен быть числом.")
        return

    user_id = message.from_user.id

    logger.info("Обработка /delete для задачи #%s, user_id=%s", task_id, user_id)

    try:
        task = await get_task_by_id(db, task_id)

        if not task:
            await message.answer(f"❌ Задача #{task_id} не найдена.")
            return

        # Проверяем, является ли пользователь автором задачи.
        is_author = task["user_id"] == user_id

        # Если не автор — проверяем, не прошёл ли 1 час с момента создания.
        if not is_author:
            created_at = datetime.fromisoformat(task["created_at"])
            elapsed = datetime.now() - created_at

            if elapsed > timedelta(hours=1):
                await message.answer(
                    "❌ Удалить задачу может только её автор. "
                    "Срок удаления (1 час) уже истёк."
                )
                return

        # Выполняем удаление: автор может удалить всегда,
        # не-автор — только в течение 1 часа (проверено выше).
        success = await delete_task(db, task_id, user_id, is_admin=is_author)

        if success:
            await message.answer(f"🗑️ Задача #{task_id} удалена.")
            logger.info("Задача #%s удалена пользователем %s", task_id, user_id)
        else:
            await message.answer("❌ Не удалось удалить задачу.")

    except Exception as e:
        logger.error("Ошибка при удалении задачи #%s: %s", task_id, e)
        await message.answer(f"❌ Ошибка: {e}")


# Обработка callback-вызовов для изменения статуса задачи.
@tasks_router.callback_query(F.data.startswith("status:"), StateFilter("*"))
async def process_status_change(callback: CallbackQuery, state: FSMContext, db: aiosqlite.Connection) -> None:
    """
    Обработчик изменения статуса задачи через inline-кнопки.

    Аргументы:
        callback - вызов inline-кнопки.
        state    - контекст FSM.
        db       - подключение к базе данных (из middleware).
    """
    # Формат callback_data: status:<new_status>:<task_id>
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("❌ Неверный формат команды.")
        return

    new_status = parts[1]
    task_id = int(parts[2])

    try:
        task = await get_task_by_id(db, task_id)

        if not task:
            await callback.answer("❌ Задача не найдена.")
            return

        success = await update_task_status(db, task_id, new_status)

        if success:
            updated_task = await get_task_by_id(db, task_id)
            card = format_task_card(updated_task)

            await callback.answer("✅ Статус обновлен.")
            await callback.message.edit_text(
                f"🔄 Задача #{task_id}:\n\n{card}",
                parse_mode="HTML",
                reply_markup=get_status_keyboard(new_status, task_id),
            )
        else:
            await callback.answer("❌ Не удалось обновить статус.")

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}")
