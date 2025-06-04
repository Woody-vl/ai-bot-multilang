import os
import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.context import FSMContext

import openai

# Load environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
FREE_MESSAGES = int(os.getenv('FREE_MESSAGES', '10'))

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Database setup
DB_PATH = 'users.db'
conn = sqlite3.connect(DB_PATH)
conn.execute(
    'CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, message_count INTEGER DEFAULT 0)'
)
conn.commit()


def get_message_count(user_id: int) -> int:
    cur = conn.execute('SELECT message_count FROM users WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    return row[0] if row else 0


def increment_message_count(user_id: int) -> None:
    cur = conn.execute('SELECT message_count FROM users WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    if row:
        conn.execute(
            'UPDATE users SET message_count = message_count + 1 WHERE user_id = ?',
            (user_id,)
        )
    else:
        conn.execute('INSERT INTO users (user_id, message_count) VALUES (?, ?)', (user_id, 1))
    conn.commit()


router = Dispatcher()


def get_greeting(lang: str) -> str:
    greetings = {
        'tr': 'Merhaba! Ben senin yapay zeka asistanınım.',
        'id': 'Halo! Saya asisten AI Anda.',
        'ar': 'مرحبًا! أنا مساعد الذكاء الاصطناعي الخاص بك.',
        'vi': 'Xin chào! Tôi là trợ lý AI của bạn.',
        'pt': 'Olá! Sou seu assistente de IA.',
    }
    return greetings.get(lang, 'Привет! Я твой помощник ИИ.')


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    greeting = get_greeting(message.from_user.language_code or '')
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Напиши сообщение')]],
        resize_keyboard=True,
    )
    await state.clear()
    await message.answer(greeting, reply_markup=kb)


@router.message()
async def message_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    count = get_message_count(user_id)
    if count >= FREE_MESSAGES:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Купить подписку 🔓', url='https://t.me/your_bot?start=pay')]
            ]
        )
        await message.answer('Лимит бесплатных сообщений исчерпан.', reply_markup=kb)
        return

    increment_message_count(user_id)

    try:
        response = await openai.ChatCompletion.acreate(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': message.text}],
        )
        answer = response.choices[0].message.content
        await message.answer(answer)
    except Exception as e:
        logging.exception('OpenAI error')
        await message.answer('Ошибка подключения. Попробуйте позже.')


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(TELEGRAM_BOT_TOKEN)
    await router.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
