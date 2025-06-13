from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_categories_kb(categories, language, parent_id=None, show_back=False):
    """Create categories keyboard"""
    keyboard = []

    # Categories list
    for category in categories:
        keyboard.append([
            InlineKeyboardButton(
                text=category.get_name(language),
                callback_data=f"category_{category.id}"
            )
        ])

    # Back button
    if parent_id or show_back:
        back_text = "🔙 Orqaga" if language == 'uz' else "🔙 Назад"
        if parent_id:
            keyboard.append([
                InlineKeyboardButton(
                    text=back_text,
                    callback_data=f"back_to_parent_{parent_id}"
                )
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(
                    text=back_text,
                    callback_data="back_to_categories"
                )
            ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)