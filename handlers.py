import os
import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from openai import AsyncOpenAI

from database import (
    get_user,
    init_db,
    set_paid,
    add_message,
    get_last_messages,
    increment_message_count,
    get_message_count,
)
from payments import get_payment_url, check_payment
from aiogram import Bot, types
from utils import get_locale_strings

openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
FREE_MESSAGES = int(os.getenv("FREE_MESSAGES", "10"))

router = Router()


@router.message(Command('buy'))
async def buy_command(message: Message):
    prices = [types.LabeledPrice(label='Премиум подписка', amount=500)]
    bot = Bot.get_current()
    await bot.send_invoice(
        chat_id=message.chat.id,
        title='Премиум подписка',
        description='Доступ к премиум возможностям',
        payload='premium_subscription',
        provider_token='',
        currency='XTR',
        prices=prices,
        start_parameter='buy-premium'
    )


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

    if user:
        current_count = user.get("message_count", 0)
    else:
        current_count = await get_message_count(message.from_user.id)
    if user and not user.get("is_paid") and current_count >= FREE_MESSAGES:
        url = get_payment_url(message.from_user.id)
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=texts["buy_button"], url=url)]]
        )
        await message.answer(texts["limit_exceeded"], reply_markup=kb)
        return

    await increment_message_count(message.from_user.id)

    history = await get_last_messages(message.from_user.id, 10)
    chat_messages = [
        {"role": "user" if is_user else "assistant", "content": text}
        for text, is_user in history
    ]
    chat_messages.append({"role": "user", "content": message.text})

    await add_message(message.from_user.id, message.text, True)

    try:
        response = await openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_messages,
        )
        answer = response.choices[0].message.content
        await add_message(message.from_user.id, answer, False)
        await message.answer(answer)
    except Exception as e:
        logging.exception("OpenAI error")
        await message.answer("Error while contacting OpenAI.")
