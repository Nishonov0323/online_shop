from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_cart_kb(cart_items_data, language, total_price):
    """Create cart keyboard"""
    keyboard = []

    # Cart items data dan iterate qilish (bu tayyor ma'lumotlar bo'lishi kerak)
    for item_data in cart_items_data:
        button_text = f"{item_data['product_name']} ({item_data['color_name']}) - {item_data['quantity']} x {item_data['price']:,.0f}"

        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"cartitem_{item_data['item_id']}"
            )
        ])

    # Total price and action buttons
    if language == 'uz':
        total_text = f"💰 Jami: {total_price:,.0f} so'm"
        checkout_text = "✅ Buyurtma berish"
        clear_text = "🗑 Tozalash"
    else:
        total_text = f"💰 Итого: {total_price:,.0f} сум"
        checkout_text = "✅ Оформить заказ"
        clear_text = "🗑 Очистить"

    keyboard.extend([
        [InlineKeyboardButton(text=total_text, callback_data="total")],
        [
            InlineKeyboardButton(text=checkout_text, callback_data="checkout"),
            InlineKeyboardButton(text=clear_text, callback_data="clearcart")
        ]
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cart_item_kb(item_id, language):
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
            InlineKeyboardButton(text=minus_text, callback_data=f"quantity_{item_id}_minus"),
            InlineKeyboardButton(text=plus_text, callback_data=f"quantity_{item_id}_plus")
        ],
        [InlineKeyboardButton(text=remove_text, callback_data=f"remove_{item_id}")],
        [InlineKeyboardButton(text=back_text, callback_data="show_cart")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)