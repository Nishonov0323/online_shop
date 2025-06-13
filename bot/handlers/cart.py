from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

from store.models import Cart, CartItem
from bot.keyboards.cart import get_cart_kb, get_cart_item_kb
from bot.keyboards.common import get_main_menu_kb


class OrderStates(StatesGroup):
    waiting_for_address = State()
    confirm_order = State()


def get_cart_router():
    router = Router()

    # Register handlers with F filter
    router.message.register(show_cart, F.text.in_(["🛒 Savatcha", "🛒 Корзина"]))
    router.callback_query.register(show_cart_callback, F.data == "show_cart")
    router.callback_query.register(process_cart_item, F.data.startswith("cartitem_"))
    router.callback_query.register(remove_from_cart, F.data.startswith("remove_"))
    router.callback_query.register(change_quantity, F.data.startswith("quantity_"))
    router.callback_query.register(clear_cart, F.data.startswith("clearcart"))
    router.callback_query.register(start_checkout, F.data.startswith("checkout"))

    return router


async def show_cart(message: Message, **kwargs):
    """Show cart items"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await message.answer(
            _("Iltimos, botni qaytadan ishga tushirish uchun /start buyrug'ini yuboring")
        )
        return

    try:
        # Get cart using sync_to_async
        cart = await sync_to_async(Cart.objects.get)(user=user, is_active=True)

        # Get cart items and total price using sync_to_async
        cart_items = await sync_to_async(lambda: list(cart.items.all()))()
        total_price = await sync_to_async(cart.get_total_price)()

        if cart_items:
            await message.answer(
                _("Sizning savatchangiz:"),
                reply_markup=get_cart_kb(cart_items, user.language, total_price)
            )
        else:
            await message.answer(
                _("Sizning savatchagiz bo'sh."),
                reply_markup=get_main_menu_kb(user.language)
            )
    except Cart.DoesNotExist:
        await message.answer(
            _("Sizning savatchagiz bo'sh."),
            reply_markup=get_main_menu_kb(user.language)
        )


async def show_cart_callback(callback: CallbackQuery, **kwargs):
    """Show cart items from callback"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    try:
        # Get cart using sync_to_async
        cart = await sync_to_async(Cart.objects.get)(user=user, is_active=True)

        # Get cart items and total price using sync_to_async
        cart_items = await sync_to_async(lambda: list(cart.items.all()))()
        total_price = await sync_to_async(cart.get_total_price)()

        if cart_items:
            await callback.message.edit_text(
                _("Sizning savatchangiz:"),
                reply_markup=get_cart_kb(cart_items, user.language, total_price)
            )
        else:
            await callback.message.edit_text(
                _("Sizning savatchagiz bo'sh."),
                reply_markup=get_main_menu_kb(user.language)
            )
    except Cart.DoesNotExist:
        await callback.message.edit_text(
            _("Sizning savatchagiz bo'sh."),
            reply_markup=get_main_menu_kb(user.language)
        )

    await callback.answer()


async def process_cart_item(callback: CallbackQuery, **kwargs):
    """Process cart item selection"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    item_id = int(callback.data.split('_')[1])

    try:
        # Get cart item using sync_to_async
        cart_item = await sync_to_async(CartItem.objects.get)(id=item_id)

        # Get product name and color
        product_name = cart_item.color.product.get_name(user.language)
        color_name = cart_item.color.get_name(user.language)
        price = cart_item.color.price
        quantity = cart_item.quantity
        total = price * quantity

        # Prepare info message
        message_text = (
            f"<b>{product_name}</b>\n"
            f"<i>{color_name}</i>\n"
            f"{_('Narxi')}: {price:,.0f} {_('so\'m')}\n"
            f"{_('Soni')}: {quantity}\n"
            f"{_('Jami')}: {total:,.0f} {_('so\'m')}"
        )

        # Get first product image using sync_to_async
        has_images = await sync_to_async(lambda: cart_item.color.images.exists())()

        if has_images:
            first_image = await sync_to_async(lambda: cart_item.color.images.first())()
            # ImageFieldFile'ni URL'ga aylantirish
            image_url = first_image.image.url
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=image_url,
                caption=message_text,
                reply_markup=get_cart_item_kb(cart_item.id, user.language)
            )
        else:
            await callback.message.edit_text(
                message_text,
                reply_markup=get_cart_item_kb(cart_item.id, user.language)
            )

    except CartItem.DoesNotExist:
        await callback.answer(_("Mahsulot topilmadi."))

    await callback.answer()


async def remove_from_cart(callback: CallbackQuery, **kwargs):
    """Remove item from cart"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    item_id = int(callback.data.split('_')[1])

    try:
        # Get and delete cart item using sync_to_async
        @sync_to_async
        def delete_cart_item():
            cart_item = CartItem.objects.get(id=item_id)
            cart_item.delete()

        await delete_cart_item()

        await callback.answer(_("Mahsulot savatchadan o'chirildi."))

        # Show updated cart
        await show_cart_callback(callback, **kwargs)

    except CartItem.DoesNotExist:
        await callback.answer(_("Mahsulot topilmadi."))


async def change_quantity(callback: CallbackQuery, **kwargs):
    """Change item quantity"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    data_parts = callback.data.split('_')
    item_id = int(data_parts[1])
    action = data_parts[2]  # "plus" or "minus"

    try:
        # Update quantity using sync_to_async wrapper functions
        @sync_to_async
        def update_quantity():
            cart_item = CartItem.objects.get(id=item_id)

            if action == "plus":
                cart_item.quantity += 1
                cart_item.save()
                return cart_item, True, "increased"
            elif action == "minus":
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                    return cart_item, True, "decreased"
                else:
                    return cart_item, False, "minimum"

            return cart_item, False, "unknown"

        cart_item, success, action_result = await update_quantity()

        if success:
            if action_result == "increased":
                await callback.answer(_("Miqdor oshirildi."))
            elif action_result == "decreased":
                await callback.answer(_("Miqdor kamaytirildi."))

            # Update current message
            product_name = cart_item.color.product.get_name(user.language)
            color_name = cart_item.color.get_name(user.language)
            price = cart_item.color.price
            quantity = cart_item.quantity
            total = price * quantity

            message_text = (
                f"<b>{product_name}</b>\n"
                f"<i>{color_name}</i>\n"
                f"{_('Narxi')}: {price:,.0f} {_('so\'m')}\n"
                f"{_('Soni')}: {quantity}\n"
                f"{_('Jami')}: {total:,.0f} {_('so\'m')}"
            )

            await callback.message.edit_caption(
                caption=message_text,
                reply_markup=get_cart_item_kb(cart_item.id, user.language)
            )
        else:
            if action_result == "minimum":
                await callback.answer(_("Miqdor kamida 1 bo'lishi kerak."))

    except CartItem.DoesNotExist:
        await callback.answer(_("Mahsulot topilmadi."))


async def clear_cart(callback: CallbackQuery, **kwargs):
    """Clear the entire cart"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    try:
        # Get cart and delete all items using sync_to_async
        @sync_to_async
        def clear_cart_items():
            cart = Cart.objects.get(user=user, is_active=True)
            cart.items.all().delete()

        await clear_cart_items()

        await callback.answer(_("Savatcha tozalandi."))
        await callback.message.edit_text(
            _("Sizning savatchagiz bo'sh."),
            reply_markup=get_main_menu_kb(user.language)
        )

    except Cart.DoesNotExist:
        await callback.answer(_("Savatcha allaqachon bo'sh."))


async def start_checkout(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Start checkout process"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    try:
        # Get cart and check if it has items using sync_to_async
        cart = await sync_to_async(Cart.objects.get)(user=user, is_active=True)
        has_items = await sync_to_async(lambda: cart.items.exists())()

        if has_items:
            # Set state to waiting for address
            await state.set_state(OrderStates.waiting_for_address)

            await callback.message.delete()
            await callback.message.answer(
                _("Buyurtma berish uchun yetkazib berish manzilini kiriting:"),
                reply_markup=types.ReplyKeyboardRemove()
            )
        else:
            await callback.answer(_("Savatchagiz bo'sh."))

    except Cart.DoesNotExist:
        await callback.answer(_("Savatchagiz bo'sh."))