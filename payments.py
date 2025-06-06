import os

from aiogram import Bot, Dispatcher, types
from database import get_user, mark_user_premium


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


def setup_payment_handlers(dp: Dispatcher, bot: Bot) -> None:
    @dp.pre_checkout_query_handler(lambda query: True)
    async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
        await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

    @dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
    async def successful_payment(message: types.Message):
        await message.answer("✅ Оплата успешно завершена! Спасибо за покупку.")
        await mark_user_premium(message.from_user.id)

