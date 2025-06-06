import re
from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from translations import get_translation, SUPPORTED_LANGS
from utils import translate_text
from database import init_db, log_support_message, get_user_language

OWNER = "@VasiliiOz"

router = Router()


def menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧾 Проблема с оплатой")],
            [KeyboardButton(text="❓ Другое")],
            [KeyboardButton(text="📨 Связаться с человеком")],
        ],
        resize_keyboard=True,
    )


class Form(StatesGroup):
    payment = State()
    support = State()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    init_db()
    await state.clear()
    lang = message.from_user.language_code or "en"
    lang = lang if lang in SUPPORTED_LANGS else "en"
    await message.answer(get_translation(lang, "start"), reply_markup=menu_keyboard())


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    lang = message.from_user.language_code or "en"
    lang = lang if lang in SUPPORTED_LANGS else "en"
    await message.answer(get_translation(lang, "help"))


@router.message(Command("paysupport"))
async def paysupport_command(message: Message, state: FSMContext) -> None:
    lang = message.from_user.language_code or "en"
    lang = lang if lang in SUPPORTED_LANGS else "en"
    await message.answer(get_translation(lang, "ask_payment"))
    await state.set_state(Form.payment)


@router.message(Command("support"))
async def support_command(message: Message, state: FSMContext) -> None:
    lang = message.from_user.language_code or "en"
    lang = lang if lang in SUPPORTED_LANGS else "en"
    await message.answer(get_translation(lang, "ask_support"))
    await state.set_state(Form.support)


@router.message(lambda m: m.text == "🧾 Проблема с оплатой")
async def paysupport_button(message: Message, state: FSMContext) -> None:
    await paysupport_command(message, state)


@router.message(lambda m: m.text == "❓ Другое")
async def support_button(message: Message, state: FSMContext) -> None:
    await support_command(message, state)


@router.message(lambda m: m.text == "📨 Связаться с человеком")
async def contact_button(message: Message) -> None:
    await message.answer("https://t.me/VasiliiOz")


@router.message(Form.payment)
async def handle_payment(message: Message, state: FSMContext, bot: Bot) -> None:
    lang = message.from_user.language_code or "en"
    lang = lang if lang in SUPPORTED_LANGS else "en"
    log_support_message(message.from_user.id, message.from_user.username or "", lang, message.text)
    text_ru = await translate_text(message.text, "ru")
    await bot.send_message(OWNER, f"pay from {message.from_user.id}: {text_ru}")
    await state.clear()
    await message.answer("✅")


@router.message(Form.support)
async def handle_support(message: Message, state: FSMContext, bot: Bot) -> None:
    lang = message.from_user.language_code or "en"
    lang = lang if lang in SUPPORTED_LANGS else "en"
    log_support_message(message.from_user.id, message.from_user.username or "", lang, message.text)
    text_ru = await translate_text(message.text, "ru")
    await bot.send_message(OWNER, f"support from {message.from_user.id}: {text_ru}")
    await state.clear()
    await message.answer("✅")


@router.message()
async def default_handler(message: Message, bot: Bot) -> None:
    if message.from_user.username == OWNER.lstrip("@"):
        match = re.match(r"reply:(\d+)\s+(.*)", message.text or "", re.DOTALL)
        if match:
            user_id = int(match.group(1))
            text = match.group(2)
            lang = get_user_language(user_id)
            translated = await translate_text(text, lang)
            await bot.send_message(user_id, translated)
            return
    log_support_message(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.language_code or "en",
        message.text or "",
    )
