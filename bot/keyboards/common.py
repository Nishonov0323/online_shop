from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_kb(language):
    """Create main menu keyboard"""
    if language == 'uz':
        keyboard = [
            [KeyboardButton(text="🛍 Mahsulotlar katalogi")],
            [KeyboardButton(text="🛒 Savatcha")],
            [
                KeyboardButton(text="📞 Bog'lanish"),
                KeyboardButton(text="⚙️ Sozlamalar")
            ]
        ]
    else:
        keyboard = [
            [KeyboardButton(text="🛍 Каталог товаров")],
            [KeyboardButton(text="🛒 Корзина")],
            [
                KeyboardButton(text="📞 Связаться"),
                KeyboardButton(text="⚙️ Настройки")
            ]
        ]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_language_kb():
    """Create language selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_btn(language):
    """Create back button"""
    if language == 'uz':
        text = "🔙 Orqaga"
    else:
        text = "🔙 Назад"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data="back")]
    ])