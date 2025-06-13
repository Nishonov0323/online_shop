from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_cart_kb(cart_items, language, total_price):
    """Create cart keyboard"""
    keyboard = []

    # Cart items
    for item in cart_items:
        product_name = item.color.product.get_name(language)
        color_name = item.color.get_name(language)
        price = item.color.price
        quantity = item.quantity

        item_text = f"{product_name} ({color_name}) x {quantity} - {price * quantity:,.0f}"

        keyboard.append([
            InlineKeyboardButton(
                text=item_text,
                callback_data=f"cartitem_{item.id}"
            )
        ])

    # Action buttons
    if language == 'uz':
        clear_text = "🗑 Savatchani tozalash"
        checkout_text = f"🛒 Buyurtma berish ({total_price:,.0f} so'm)"
    else:
        clear_text = "🗑 Очистить корзину"
        checkout_text = f"🛒 Оформить заказ ({total_price:,.0f} сум)"

    keyboard.append([
        InlineKeyboardButton(text=clear_text, callback_data="clearcart")
    ])

    keyboard.append([
        InlineKeyboardButton(text=checkout_text, callback_data="checkout")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cart_item_kb(cart_item, language):
    """Create cart item management keyboard"""
    if language == 'uz':
        minus_text = "➖"
        plus_text = "➕"
        remove_text = "🗑 O'chirish"
        back_text = "🔙 Savatchaga qaytish"
    else:
        minus_text = "➖"
        plus_text = "➕"
        remove_text = "🗑 Удалить"
        back_text = "🔙 Вернуться в корзину"

    keyboard = [
        [
            InlineKeyboardButton(text=minus_text, callback_data=f"quantity_minus_{cart_item.id}"),
            InlineKeyboardButton(text=str(cart_item.quantity), callback_data="quantity_info"),
            InlineKeyboardButton(text=plus_text, callback_data=f"quantity_plus_{cart_item.id}")
        ],
        [
            InlineKeyboardButton(text=remove_text, callback_data=f"remove_{cart_item.id}")
        ],
        [
            InlineKeyboardButton(text=back_text, callback_data="show_cart")
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)