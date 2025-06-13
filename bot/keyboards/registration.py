from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton


def get_language_kb():
    """Language selection keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🇺🇿 O'zbekcha"),
        KeyboardButton(text="🇷🇺 Русский")
    )
    return builder.as_markup(resize_keyboard=True)


def get_contact_kb(language):
    """Contact keyboard with phone number request button"""
    builder = ReplyKeyboardBuilder()

    if language == "uz":
        builder.row(KeyboardButton(
            text="📱 Telefon raqamni yuborish",
            request_contact=True
        ))
    else:
        builder.row(KeyboardButton(
            text="📱 Отправить номер телефона",
            request_contact=True
        ))

    return builder.as_markup(resize_keyboard=True)