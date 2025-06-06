import os

from aiogram import Bot, Router, F
from aiogram.types import PreCheckoutQuery, Message
from database import get_user, mark_user_premium, conn


BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot")


def get_payment_url(user_id: int) -> str:
    """Return Telegram Stars payment URL for given user."""
    return f"https://t.me/{BOT_USERNAME}?start=pay_{user_id}"


def check_payment(user_id: int) -> bool:
    """Stub payment check. Returns True when user.is_paid flag set."""
    user = get_user(user_id)
    return bool(user and user.get("is_paid"))


async def generate_purchase_button(user_id: int):
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    url = get_payment_url(user_id)
    button = InlineKeyboardButton(text='Buy', url=url)
    return InlineKeyboardMarkup(inline_keyboard=[[button]])


def log_payment(user_id: int, username: str, amount: int, currency: str, transaction_id: str) -> None:
    """Store payment information in the database."""
    conn.execute(
        "INSERT INTO payments (user_id, username, amount, currency, stars_transaction_id) VALUES (?, ?, ?, ?, ?)",
        (user_id, username, amount, currency, transaction_id),
    )
    conn.commit()


def setup_payment_handlers() -> Router:
    """Configure payment handlers and return a router."""
    router = Router()

    @router.pre_checkout_query()
    async def pre_checkout_query(
        pre_checkout_q: PreCheckoutQuery, bot: Bot
    ) -> None:
        await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

    @router.message(F.successful_payment)
    async def successful_payment(message: Message, bot: Bot) -> None:
        await message.answer("✅ Оплата успешно завершена! Спасибо за покупку.")
        await mark_user_premium(message.from_user.id)
        payment = message.successful_payment
        log_payment(
            message.from_user.id,
            message.from_user.username or "",
            payment.total_amount,
            payment.currency,
            payment.telegram_payment_charge_id,
        )

    return router

