import os

from database import get_user


BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot")


def get_payment_url(user_id: int) -> str:
    """Return Telegram Stars payment URL for given user."""
    return f"https://t.me/{BOT_USERNAME}?start=pay_{user_id}"


def check_payment(user_id: int) -> bool:
    """Stub payment check. Returns True when user.is_paid flag set."""
    user = get_user(user_id)
    return bool(user and user.get("is_paid"))
