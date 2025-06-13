from django.utils.translation import gettext as _


class TextManager:
    """
    Matnlarni boshqarish va formatlarni saqlash uchun klass
    """

    @staticmethod
    def get_product_info(product, color, language):
        """Get product information text"""
        product_name = product.get_name(language)
        color_name = color.get_name(language)
        price = color.price

        if language == 'uz':
            return f"<b>{product_name}</b>\n" \
                   f"<i>{color_name}</i>\n" \
                   f"Narxi: {price} so'm"
        else:
            return f"<b>{product_name}</b>\n" \
                   f"<i>{color_name}</i>\n" \
                   f"Цена: {price} сум"

    @staticmethod
    def get_cart_item_info(cart_item, language):
        """Get cart item information text"""
        product_name = cart_item.color.product.get_name(language)
        color_name = cart_item.color.get_name(language)
        price = cart_item.color.price
        quantity = cart_item.quantity
        total = price * quantity

        if language == 'uz':
            return f"<b>{product_name}</b>\n" \
                   f"<i>{color_name}</i>\n" \
                   f"Narxi: {price} so'm\n" \
                   f"Soni: {quantity}\n" \
                   f"Jami: {total} so'm"
        else:
            return f"<b>{product_name}</b>\n" \
                   f"<i>{color_name}</i>\n" \
                   f"Цена: {price} сум\n" \
                   f"Количество: {quantity}\n" \
                   f"Итого: {total} сум"

    @staticmethod
    def get_order_summary(cart, address, language):
        """Get order summary text"""
        cart_items = cart.items.all()
        items_text = ""
        total_price = cart.get_total_price()

        for item in cart_items:
            product_name = item.color.product.get_name(language)
            color_name = item.color.get_name(language)
            price = item.color.price
            quantity = item.quantity
            item_total = price * quantity

            if language == 'uz':
                items_text += f"- {product_name} ({color_name}) x {quantity} = {item_total} so'm\n"
            else:
                items_text += f"- {product_name} ({color_name}) x {quantity} = {item_total} сум\n"

        if language == 'uz':
            return f"Buyurtmangiz:\n\n" \
                   f"{items_text}\n" \
                   f"Yetkazib berish manzili: {address}\n\n" \
                   f"Jami summa: {total_price} so'm\n\n" \
                   f"Buyurtmani tasdiqlaysizmi?"
        else:
            return f"Ваш заказ:\n\n" \
                   f"{items_text}\n" \
                   f"Адрес доставки: {address}\n\n" \
                   f"Итоговая сумма: {total_price} сум\n\n" \
                   f"Подтверждаете заказ?"