import os
import sqlite3
from typing import Optional, Dict

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
            is_paid INTEGER DEFAULT 0
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


async def get_message_count(user_id: int) -> int:
    user = get_user(user_id)
    return user.get('message_count', 0) if user else 0



async def increment_message_count(user_id: int) -> None:
    increment_messages(user_id)

