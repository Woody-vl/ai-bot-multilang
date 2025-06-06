from typing import Dict


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

