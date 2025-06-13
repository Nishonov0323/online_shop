from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_product_actions_kb(products, language, category_id):
    """Create products list keyboard"""
    keyboard = []

    # Products list dan iterate qilish (bu allaqachon list bo'lishi kerak)
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=product.get_name(language),
                callback_data=f"product_{product.id}_{category_id}"
            )
        ])

    # Back to categories button
    if language == 'uz':
        back_text = "🔙 Kategoriyalarga qaytish"
    else:
        back_text = "🔙 Вернуться к категориям"

    keyboard.append([
        InlineKeyboardButton(
            text=back_text,
            callback_data="back_to_categories"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_product_colors_kb(colors_list, language, product_id, category_id=None):
    """Create product colors keyboard"""
    keyboard = []

    # Colors list dan iterate qilish (bu allaqachon list bo'lishi kerak)
    for color in colors_list:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{color.get_name(language)} - {color.price:,.0f} so'm",
                callback_data=f"color_{color.id}_{product_id}_{category_id or 0}"
            )
        ])

    # Back button
    if language == 'uz':
        back_text = "🔙 Orqaga"
    else:
        back_text = "🔙 Назад"

    if category_id:
        keyboard.append([
            InlineKeyboardButton(
                text=back_text,
                callback_data=f"back_to_category_{category_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_add_to_cart_kb(color_id, product_id, category_id, language):
    """Create add to cart keyboard"""
    if language == 'uz':
        add_text = "🛒 Savatchaga qo'shish"
        back_text = "🔙 Mahsulotga qaytish"
    else:
        add_text = "🛒 Добавить в корзину"
        back_text = "🔙 Вернуться к товару"

    keyboard = [
        [InlineKeyboardButton(
            text=add_text,
            callback_data=f"add_to_cart_{color_id}"
        )],
        [InlineKeyboardButton(
            text=back_text,
            callback_data=f"back_to_product_{product_id}_{category_id or 0}"
        )]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)