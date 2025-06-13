from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_categories_kb(categories, language, parent_id=None):
    """Create categories keyboard"""
    keyboard = []

    for category in categories:
        keyboard.append([
            InlineKeyboardButton(
                text=category.get_name(language),
                callback_data=f"category_{category.id}"
            )
        ])

    # Add back button if this is subcategory
    if parent_id:
        if language == 'uz':
            keyboard.append([
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data=f"category_{parent_id}"
                )
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=f"category_{parent_id}"
                )
            ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_category_back_kb(language):
    """Create back to categories keyboard"""
    if language == 'uz':
        text = "🔙 Kategoriyalarga qaytish"
    else:
        text = "🔙 Вернуться к категориям"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data="back_to_categories")]
    ])