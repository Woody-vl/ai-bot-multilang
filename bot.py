import asyncio
import logging
import os
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
from openai import AsyncOpenAI

# Configuration from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FREE_MESSAGES = int(os.getenv("FREE_MESSAGES", "10"))

BOTS = [
    {"token": os.getenv("TOKEN_TURKEY"), "lang": "tr"},
    {"token": os.getenv("TOKEN_INDONESIA"), "lang": "id"},
    {"token": os.getenv("TOKEN_ARABIC"), "lang": "ar"},
    {"token": os.getenv("TOKEN_VIETNAM"), "lang": "vi"},
    {"token": os.getenv("TOKEN_BRAZIL"), "lang": "pt"},
]

WELCOME_MESSAGES = {
    "tr": "🇹🇷 Merhaba! Ben senin Türkçe AI asistanınım. İlk 10 mesaj — ücretsiz.",
    "id": "🇮🇩 Hai! Saya asisten AI pertamamu dalam Bahasa Indonesia. 10 pesan pertama — gratis.",
    "ar": "🇦🇪 أهلاً! أنا مساعد الذكاء الاصطناعي الأول باللغة العربية. أول 10 رسائل مجاناً.",
    "vi": "🇻🇳 Xin chào! Tôi là trợ lý AI đầu tiên bằng tiếng Việt. 10 tin nhắn đầu tiên miễn phí.",
    "pt": "🇧🇷 Olá! Sou seu primeiro assistente de IA em português. Primeiras 10 mensagens grátis.",
}

# Database setup
DB_PATH = "users.db"
conn = sqlite3.connect(DB_PATH)
conn.execute(
    "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, message_count INTEGER DEFAULT 0)"
)
conn.commit()

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


def get_message_count(user_id: int) -> int:
    cur = conn.execute("SELECT message_count FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    return row[0] if row else 0


def increment_message_count(user_id: int) -> None:
    cur = conn.execute("SELECT message_count FROM users WHERE user_id = ?", (user_id,))
    if cur.fetchone():
        conn.execute(
            "UPDATE users SET message_count = message_count + 1 WHERE user_id = ?",
            (user_id,),
        )
    else:
        conn.execute(
            "INSERT INTO users (user_id, message_count) VALUES (?, 1)",
            (user_id,),
        )
    conn.commit()


def purchase_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Купить подписку 🔓",
                    url="https://t.me/your_bot?start=pay",
                )
            ]
        ]
    )


def reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Напиши сообщение")]],
        resize_keyboard=True,
    )


async def start_bot(token: str, lang: str) -> None:
    if not token:
        logging.warning("Token for language %s is not set", lang)
        return

    bot = Bot(token=token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_handler(message: Message) -> None:
        await message.answer(WELCOME_MESSAGES.get(lang, "Привет!"), reply_markup=reply_keyboard())

    @dp.message()
    async def handle_message(message: Message) -> None:
        user_id = message.from_user.id
        count = get_message_count(user_id)
        if count >= FREE_MESSAGES:
            await message.answer(
                "Лимит бесплатных сообщений исчерпан.",
                reply_markup=purchase_keyboard(),
            )
            return

        increment_message_count(user_id)

        try:
            completion = await openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant that speaks {lang}."},
                    {"role": "user", "content": message.text},
                ],
            )
            answer = completion.choices[0].message.content.strip()
            await message.answer(answer)
        except Exception:
            logging.exception("OpenAI error")
            await message.answer("Ошибка подключения. Попробуйте позже.")

async def main() -> None:
    print("Тест переменных окружения:")
    print(f"TOKEN_TURKEY: {os.getenv('TOKEN_TURKEY')}")
    print(f"TOKEN_INDONESIA: {os.getenv('TOKEN_INDONESIA')}")
    print(f"TOKEN_ARABIC: {os.getenv('TOKEN_ARABIC')}")
    print(f"TOKEN_VIETNAM: {os.getenv('TOKEN_VIETNAM')}")
    print(f"TOKEN_BRAZIL: {os.getenv('TOKEN_BRAZIL')}")
    print(f"ACTIVE_TOKEN: {os.getenv('ACTIVE_TOKEN')}")
    print("main() успешно вызвана")
    logging.basicConfig(level=logging.INFO)
    tasks = [start_bot(cfg["token"], cfg["lang"]) for cfg in BOTS if cfg["token"]]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("Запускаем main()...")  # Лог перед запуском
    asyncio.run(main())
