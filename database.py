import os
import sqlite3
from typing import Optional, Dict, List, Tuple

import aiosqlite

from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "users.db")

# Connection is created with check_same_thread=False to allow usage inside aiogram handlers
conn = sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db() -> None:
    """Create users table if it does not exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            language_code TEXT,
            message_count INTEGER DEFAULT 0,
            is_paid INTEGER DEFAULT 0,
            is_premium INTEGER DEFAULT 0
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            is_user INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS support_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            language_code TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            amount INTEGER,
            currency TEXT,
            stars_transaction_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def get_user(telegram_id: int) -> Optional[Dict]:
    """Return user dictionary or None."""
    cur = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cur.fetchone()
    if row:
        keys = [col[0] for col in cur.description]
        return dict(zip(keys, row))
    return None


def increment_messages(telegram_id: int) -> None:
    """Increase message count for user; create user row if needed."""
    user = get_user(telegram_id)
    if user:
        conn.execute(
            "UPDATE users SET message_count = message_count + 1 WHERE telegram_id = ?",
            (telegram_id,),
        )
    else:
        conn.execute(
            "INSERT INTO users (telegram_id, message_count) VALUES (?, 1)",
            (telegram_id,),
        )
    conn.commit()


def reset_messages(telegram_id: int) -> None:
    """Reset message counter for the given user."""
    conn.execute(
        "UPDATE users SET message_count = 0 WHERE telegram_id = ?",
        (telegram_id,),
    )
    conn.commit()


def set_paid(telegram_id: int, paid: bool = True) -> None:
    """Mark user as paid or unpaid."""
    conn.execute(
        "UPDATE users SET is_paid = ? WHERE telegram_id = ?",
        (1 if paid else 0, telegram_id),
    )
    conn.commit()


async def add_message(user_id: int, message: str, is_user: bool) -> None:
    """Store a single message for given user."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (user_id, message, is_user) VALUES (?, ?, ?)",
            (user_id, message, 1 if is_user else 0),
        )
        await db.commit()


async def get_last_messages(user_id: int, limit: int = 10) -> List[Tuple[str, bool]]:
    """Return last messages for user ordered by timestamp ascending."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT message, is_user FROM messages WHERE user_id = ? "
            "ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit),
        )
        rows = await cur.fetchall()
    return [ (row["message"], bool(row["is_user"])) for row in reversed(rows) ]


async def get_message_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT message_count FROM users WHERE telegram_id = ?",
            (user_id,),
        )
        row = await cur.fetchone()
    return row[0] if row else 0



async def increment_message_count(user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "UPDATE users SET message_count = COALESCE(message_count, 0) + 1 "
            "WHERE telegram_id = ?",
            (user_id,),
        )
        if cur.rowcount == 0:
            await db.execute(
                "INSERT INTO users (telegram_id, message_count) VALUES (?, 1)",
                (user_id,),
            )
        await db.commit()


async def mark_user_premium(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_premium = 1 WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()


def log_support_message(user_id: int, username: str, language_code: str, message: str) -> None:
    """Store user support message for later reference."""
    conn.execute(
        "INSERT INTO support_messages (user_id, username, language_code, message) VALUES (?, ?, ?, ?)",
        (user_id, username, language_code, message),
    )
    conn.commit()


def get_user_language(user_id: int) -> str:
    """Return last known language for the user."""
    cur = conn.execute(
        "SELECT language_code FROM support_messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1",
        (user_id,),
    )
    row = cur.fetchone()
    return row[0] if row else "en"


# Ensure tables are created when the module is imported
init_db()


