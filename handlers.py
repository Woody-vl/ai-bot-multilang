import os
import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
import openai

from database import get_user, increment_messages, init_db, set_paid
from payments import get_payment_url, check_payment
from utils import get_locale_strings

openai.api_key = os.getenv("OPENAI_API_KEY")
FREE_MESSAGES = int(os.getenv("FREE_MESSAGES", "10"))

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    """Handle /start command and save user in DB."""
    init_db()
    lang = message.from_user.language_code or "en"
    user = get_user(message.from_user.id)
    if not user:
        # Insert new user with detected language
        from database import conn
        conn.execute(
            "INSERT INTO users (telegram_id, language_code) VALUES (?, ?)",
            (message.from_user.id, lang),
        )
        conn.commit()
    texts = get_locale_strings(lang)
    await state.clear()
    await message.answer(texts["greeting"])


@router.message()
async def handle_message(message: Message) -> None:
    """Process user messages and interact with OpenAI."""
    user = get_user(message.from_user.id)
    lang = (user.get("language_code") if user else message.from_user.language_code) or "en"
    texts = get_locale_strings(lang)

    if user and not user.get("is_paid") and user.get("message_count", 0) >= FREE_MESSAGES:
        url = get_payment_url(message.from_user.id)
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=texts["buy_button"], url=url)]]
        )
        await message.answer(texts["limit_exceeded"], reply_markup=kb)
        return

    increment_messages(message.from_user.id)

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}],
        )
        answer = response.choices[0].message.content
        await message.answer(answer)
    except Exception as e:
        logging.exception("OpenAI error")
        await message.answer("Error while contacting OpenAI.")
