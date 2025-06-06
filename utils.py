from typing import Dict, List, Dict as DictType
import aiosqlite
from database import DB_PATH


def get_locale_strings(lang_code: str) -> Dict[str, str]:
    """Return localized strings for supported languages."""
    data = {
        "en": {
            "greeting": "Hello! I'm your AI assistant.",
            "limit_exceeded": "Free message limit exceeded.",
            "buy_button": "Buy access",
        },
        "ru": {
            "greeting": "Привет! Я твой ИИ помощник.",
            "limit_exceeded": "Лимит бесплатных сообщений исчерпан.",
            "buy_button": "Купить доступ",
        },
    }
    return data.get(lang_code, data["en"])


async def get_localized_strings(lang_code: str):
    return get_locale_strings(lang_code)


async def get_user_payments(user_id: int) -> List[DictType]:
    """Return a list of payment records for the given user."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM payments WHERE user_id = ? ORDER BY timestamp DESC",
            (user_id,),
        )
        rows = await cur.fetchall()
    return [dict(row) for row in rows]


from openai_client import chat

LANG_NAMES = {
    "tr": "Turkish",
    "id": "Indonesian",
    "ar": "Arabic",
    "vi": "Vietnamese",
    "pt": "Portuguese",
    "ru": "Russian",
    "en": "English",
}


async def translate_text(text: str, target_lang: str) -> str:
    """Translate text to the target language using OpenAI."""
    lang = LANG_NAMES.get(target_lang, "English")
    messages = [
        {"role": "system", "content": f"Translate the following text to {lang}. Only the translated text."},
        {"role": "user", "content": text},
    ]
    return await chat(messages)

