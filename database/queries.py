"""
РњРѕРґСѓР»СЊ SQL-Р·Р°РїСЂРѕСЃРѕРІ РґР»СЏ СЂР°Р±РѕС‚С‹ СЃ Р·Р°РґР°С‡Р°РјРё.

Р—РґРµСЃСЊ СЃРѕР±СЂР°РЅС‹ РІСЃРµ РѕРїРµСЂР°С†РёРё CRUD (СЃРѕР·РґР°РЅРёРµ, С‡С‚РµРЅРёРµ, РѕР±РЅРѕРІР»РµРЅРёРµ, СѓРґР°Р»РµРЅРёРµ)
РґР»СЏ С‚Р°Р±Р»РёС†С‹ tasks. Р’СЃСЏ СЂР°Р±РѕС‚Р° СЃ SQL РёР·РѕР»РёСЂРѕРІР°РЅР° РёРјРµРЅРЅРѕ РІ СЌС‚РѕРј С„Р°Р№Р»Рµ.
"""

from datetime import datetime

import aiosqlite


async def add_task(
    db: aiosqlite.Connection,
    user_id: int,
    username: str,
    text: str,
    priority: str,
    deadline: str | None,
    assignee: str | None,
) -> int:
    """
    РЎРѕР·РґР°РµС‚ РЅРѕРІСѓСЋ Р·Р°РґР°С‡Сѓ РІ Р±Р°Р·Рµ РґР°РЅРЅС‹С….

    РђСЂРіСѓРјРµРЅС‚С‹:
        db       - РїРѕРґРєР»СЋС‡РµРЅРёРµ Рє Р±Р°Р·Рµ РґР°РЅРЅС‹С…
        user_id  - Telegram ID Р°РІС‚РѕСЂР° Р·Р°РґР°С‡Рё
        username - @username Р°РІС‚РѕСЂР° Р·Р°РґР°С‡Рё
        text     - С‚РµРєСЃС‚ Р·Р°РґР°С‡Рё
        priority - РїСЂРёРѕСЂРёС‚РµС‚ ('low', 'medium', 'high')
        deadline - РґРµРґР»Р°Р№РЅ РІ С„РѕСЂРјР°С‚Рµ YYYY-MM-DD РёР»Рё None
        assignee - @username РёСЃРїРѕР»РЅРёС‚РµР»СЏ РёР»Рё None

    Р’РѕР·РІСЂР°С‰Р°РµС‚:
        ID СЃРѕР·РґР°РЅРЅРѕР№ Р·Р°РґР°С‡Рё.
    """
    now = datetime.now().isoformat()

    cursor = await db.execute(
        """
        INSERT INTO tasks (text, "user", user_id, assignee, status, priority, deadline, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'new', ?, ?, ?, ?);
        """,
        (text, username, user_id, assignee, priority, deadline, now, now),
    )
    await db.commit()

    return cursor.lastrowid


async def get_task_by_id(db: aiosqlite.Connection, task_id: int) -> dict | None:
    """
    Р’РѕР·РІСЂР°С‰Р°РµС‚ Р·Р°РґР°С‡Сѓ РїРѕ РµС‘ ID.

    РђСЂРіСѓРјРµРЅС‚С‹:
        db      - РїРѕРґРєР»СЋС‡РµРЅРёРµ Рє Р±Р°Р·Рµ РґР°РЅРЅС‹С…
        task_id - ID Р·Р°РґР°С‡Рё

    Р’РѕР·РІСЂР°С‰Р°РµС‚:
        РЎР»РѕРІР°СЂСЊ СЃ РґР°РЅРЅС‹РјРё Р·Р°РґР°С‡Рё РёР»Рё None, РµСЃР»Рё Р·Р°РґР°С‡Р° РЅРµ РЅР°Р№РґРµРЅР°.
    """
    # row_factory СѓРєР°Р·С‹РІР°РµС‚ SQLite РІРѕР·РІСЂР°С‰Р°С‚СЊ СЃС‚СЂРѕРєРё РєР°Рє РѕР±СЉРµРєС‚С‹
    # СЃ РґРѕСЃС‚СѓРїРѕРј РїРѕ РёРјРµРЅРё РєРѕР»РѕРЅРєРё (РєР°Рє СЃР»РѕРІР°СЂСЊ). await Р·РґРµСЃСЊ РЅРµ РЅСѓР¶РµРЅ.
    db.row_factory = aiosqlite.Row
    async with db.execute(
        "SELECT * FROM tasks WHERE id = ?;", (task_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return dict(row) if row else None


async def list_active_tasks(db: aiosqlite.Connection) -> list[dict]:
    """
    Р’РѕР·РІСЂР°С‰Р°РµС‚ СЃРїРёСЃРѕРє Р°РєС‚РёРІРЅС‹С… Р·Р°РґР°С‡ РєРѕРјР°РЅРґС‹.

    РђРєС‚РёРІРЅС‹РјРё СЃС‡РёС‚Р°СЋС‚СЃСЏ Р·Р°РґР°С‡Рё СЃРѕ СЃС‚Р°С‚СѓСЃРѕРј, РѕС‚Р»РёС‡РЅС‹Рј РѕС‚ 'done' Рё 'cancelled'.

    РђСЂРіСѓРјРµРЅС‚С‹:
        db - РїРѕРґРєР»СЋС‡РµРЅРёРµ Рє Р±Р°Р·Рµ РґР°РЅРЅС‹С…

    Р’РѕР·РІСЂР°С‰Р°РµС‚:
        РЎРїРёСЃРѕРє СЃР»РѕРІР°СЂРµР№ СЃ РґР°РЅРЅС‹РјРё Р·Р°РґР°С‡.
    """
    db.row_factory = aiosqlite.Row
    async with db.execute(
        """
        SELECT * FROM tasks
        WHERE status NOT IN ('done', 'cancelled')
        ORDER BY
            CASE priority
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
            END,
            deadline ASC,
            created_at DESC;
        """
    ) as cursor:
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def user_tasks(db: aiosqlite.Connection, user_id: int) -> list[dict]:
    """
    Р’РѕР·РІСЂР°С‰Р°РµС‚ РІСЃРµ Р·Р°РґР°С‡Рё, СЃРѕР·РґР°РЅРЅС‹Рµ СѓРєР°Р·Р°РЅРЅС‹Рј РїРѕР»СЊР·РѕРІР°С‚РµР»РµРј.

    РђСЂРіСѓРјРµРЅС‚С‹:
        db      - РїРѕРґРєР»СЋС‡РµРЅРёРµ Рє Р±Р°Р·Рµ РґР°РЅРЅС‹С…
        user_id - Telegram ID РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ

    Р’РѕР·РІСЂР°С‰Р°РµС‚:
        РЎРїРёСЃРѕРє СЃР»РѕРІР°СЂРµР№ СЃ РґР°РЅРЅС‹РјРё Р·Р°РґР°С‡, РѕС‚СЃРѕСЂС‚РёСЂРѕРІР°РЅРЅС‹С… РїРѕ РґР°С‚Рµ СЃРѕР·РґР°РЅРёСЏ.
    """
    db.row_factory = aiosqlite.Row
    async with db.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC;",
        (user_id,),
    ) as cursor:
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def update_task_status(
    db: aiosqlite.Connection, task_id: int, new_status: str
) -> bool:
    """
    РћР±РЅРѕРІР»СЏРµС‚ СЃС‚Р°С‚СѓСЃ Р·Р°РґР°С‡Рё.

    РђСЂРіСѓРјРµРЅС‚С‹:
        db         - РїРѕРґРєР»СЋС‡РµРЅРёРµ Рє Р±Р°Р·Рµ РґР°РЅРЅС‹С…
        task_id    - ID Р·Р°РґР°С‡Рё
        new_status - РЅРѕРІС‹Р№ СЃС‚Р°С‚СѓСЃ ('new', 'in_progress', 'done', 'cancelled')

    Р’РѕР·РІСЂР°С‰Р°РµС‚:
        True, РµСЃР»Рё Р·Р°РїРёСЃСЊ Р±С‹Р»Р° РѕР±РЅРѕРІР»РµРЅР°, РёРЅР°С‡Рµ False.
    """
    now = datetime.now().isoformat()
    cursor = await db.execute(
        "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?;",
        (new_status, now, task_id),
    )
    await db.commit()
    return cursor.rowcount > 0


async def cancel_task(db: aiosqlite.Connection, task_id: int) -> bool:
    """
    РћС‚РјРµРЅСЏРµС‚ Р·Р°РґР°С‡Сѓ (СѓСЃС‚Р°РЅР°РІР»РёРІР°РµС‚ СЃС‚Р°С‚СѓСЃ 'cancelled').

    РђСЂРіСѓРјРµРЅС‚С‹:
        db      - РїРѕРґРєР»СЋС‡РµРЅРёРµ Рє Р±Р°Р·Рµ РґР°РЅРЅС‹С…
        task_id - ID Р·Р°РґР°С‡Рё

    Р’РѕР·РІСЂР°С‰Р°РµС‚:
        True, РµСЃР»Рё Р·Р°РґР°С‡Р° Р±С‹Р»Р° РѕС‚РјРµРЅРµРЅР°, РёРЅР°С‡Рµ False.
    """
    return await update_task_status(db, task_id, "cancelled")


async def delete_task(
    db: aiosqlite.Connection, task_id: int, user_id: int, is_admin: bool = False
) -> bool:
    """
    РЈРґР°Р»СЏРµС‚ Р·Р°РґР°С‡Сѓ РёР· Р±Р°Р·С‹ РґР°РЅРЅС‹С….

    РЈРґР°Р»РёС‚СЊ РјРѕР¶РµС‚ С‚РѕР»СЊРєРѕ Р°РІС‚РѕСЂ Р·Р°РґР°С‡Рё. РћРіСЂР°РЅРёС‡РµРЅРёРµ РїРѕ РІСЂРµРјРµРЅРё (1 С‡Р°СЃ)
    РЅР°РєР»Р°РґС‹РІР°РµС‚СЃСЏ РІ РѕР±СЂР°Р±РѕС‚С‡РёРєРµ, С‡С‚РѕР±С‹ РЅРµ СЃРјРµС€РёРІР°С‚СЊ Р±РёР·РЅРµСЃ-Р»РѕРіРёРєСѓ Рё SQL.

    РђСЂРіСѓРјРµРЅС‚С‹:
        db       - РїРѕРґРєР»СЋС‡РµРЅРёРµ Рє Р±Р°Р·Рµ РґР°РЅРЅС‹С…
        task_id  - ID Р·Р°РґР°С‡Рё
        user_id  - Telegram ID РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ, Р·Р°РїСЂР°С€РёРІР°СЋС‰РµРіРѕ СѓРґР°Р»РµРЅРёРµ
        is_admin - С„Р»Р°Рі Р°РґРјРёРЅРёСЃС‚СЂР°С‚РѕСЂР° (РµСЃР»Рё True, Р°РІС‚РѕСЂСЃС‚РІРѕ РЅРµ РїСЂРѕРІРµСЂСЏРµС‚СЃСЏ)

    Р’РѕР·РІСЂР°С‰Р°РµС‚:
        True, РµСЃР»Рё Р·Р°РґР°С‡Р° Р±С‹Р»Р° СѓРґР°Р»РµРЅР°, РёРЅР°С‡Рµ False.
    """
    if is_admin:
        cursor = await db.execute(
            "DELETE FROM tasks WHERE id = ?;", (task_id,)
        )
    else:
        cursor = await db.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?;",
            (task_id, user_id),
        )
    await db.commit()
    return cursor.rowcount > 0


async def export_tasks(db: aiosqlite.Connection) -> list[dict]:
    """
    Р’РѕР·РІСЂР°С‰Р°РµС‚ РІСЃРµ Р·Р°РґР°С‡Рё РёР· Р±Р°Р·С‹ РґР°РЅРЅС‹С… РґР»СЏ СЌРєСЃРїРѕСЂС‚Р° РІ CSV.

    РђСЂРіСѓРјРµРЅС‚С‹:
        db - РїРѕРґРєР»СЋС‡РµРЅРёРµ Рє Р±Р°Р·Рµ РґР°РЅРЅС‹С…

    Р’РѕР·РІСЂР°С‰Р°РµС‚:
        РЎРїРёСЃРѕРє СЃР»РѕРІР°СЂРµР№ СЃ РґР°РЅРЅС‹РјРё РІСЃРµС… Р·Р°РґР°С‡.
    """
    db.row_factory = aiosqlite.Row
    async with db.execute(
        "SELECT * FROM tasks ORDER BY id;"
    ) as cursor:
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_tasks_with_deadline(
    db: aiosqlite.Connection, date: str
) -> list[dict]:
    """
    Р’РѕР·РІСЂР°С‰Р°РµС‚ Р°РєС‚РёРІРЅС‹Рµ Р·Р°РґР°С‡Рё СЃ СѓРєР°Р·Р°РЅРЅС‹Рј РґРµРґР»Р°Р№РЅРѕРј.

    РђСЂРіСѓРјРµРЅС‚С‹:
        db   - РїРѕРґРєР»СЋС‡РµРЅРёРµ Рє Р±Р°Р·Рµ РґР°РЅРЅС‹С…
        date - РґР°С‚Р° РІ С„РѕСЂРјР°С‚Рµ YYYY-MM-DD

    Р’РѕР·РІСЂР°С‰Р°РµС‚:
        РЎРїРёСЃРѕРє СЃР»РѕРІР°СЂРµР№ СЃ РґР°РЅРЅС‹РјРё Р·Р°РґР°С‡.
    """
    db.row_factory = aiosqlite.Row
    async with db.execute(
        """
        SELECT * FROM tasks
        WHERE deadline = ? AND status NOT IN ('done', 'cancelled');
        """,
        (date,),
    ) as cursor:
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


# РџСЃРµРІРґРѕРЅРёРјС‹ РґР»СЏ СѓРґРѕР±СЃС‚РІР° РёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЏ РІ СЂР°Р·РЅС‹С… С‡Р°СЃС‚СЏС… РїСЂРѕРµРєС‚Р°.
create_task = add_task
set_task_status = update_task_status

