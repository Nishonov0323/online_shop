from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from django.utils.translation import gettext as _
from decimal import Decimal
from asgiref.sync import sync_to_async

from store.models import Cart, Order, OrderItem
from bot.handlers.cart import OrderStates
from bot.keyboards.common import get_main_menu_kb


def get_orders_router():
    router = Router()

    # Register handlers
    router.message.register(process_address, OrderStates.waiting_for_address)
    router.message.register(process_order_confirm, OrderStates.confirm_order)

    return router


async def process_address(message: Message, state: FSMContext, **kwargs):
    """Process delivery address input"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await message.answer(
            _("Iltimos, botni qaytadan ishga tushirish uchun /start buyrug'ini yuboring")
        )
        await state.clear()
        return

    # Save address to state
    await state.update_data(address=message.text)

    try:
        # Get cart using sync_to_async
        cart = await sync_to_async(Cart.objects.get)(user=user, is_active=True)

        # Get total price using sync_to_async
        total_price = await sync_to_async(cart.get_total_price)()

        # Get cart items using sync_to_async
        cart_items = await sync_to_async(lambda: list(cart.items.all()))()

        items_text = ""

        for item in cart_items:
            product_name = item.color.product.get_name(user.language)
            color_name = item.color.get_name(user.language)
            price = item.color.price
            quantity = item.quantity
            item_total = price * quantity

            items_text += f"- {product_name} ({color_name}) x {quantity} = {item_total} {_('so\'m')}\n"

        confirmation_text = (
            f"{_('Buyurtmangiz:')}\n\n"
            f"{items_text}\n"
            f"{_('Yetkazib berish manzili')}: {message.text}\n\n"
            f"{_('Jami summa')}: {total_price} {_('so\'m')}\n\n"
            f"{_('Buyurtmani tasdiqlaysizmi?')}"
        )

        # Ask for confirmation
        builder = ReplyKeyboardBuilder()
        if user.language == 'uz':
            builder.row(
                KeyboardButton(text="✅ Tasdiqlash"),
                KeyboardButton(text="❌ Bekor qilish")
            )
        else:
            builder.row(
                KeyboardButton(text="✅ Подтвердить"),
                KeyboardButton(text="❌ Отменить")
            )

        await message.answer(
            confirmation_text,
            reply_markup=builder.as_markup(resize_keyboard=True)
        )

        # Set state to confirm order
        await state.set_state(OrderStates.confirm_order)

    except Cart.DoesNotExist:
        await message.answer(
            _("Sizning savatchagiz bo'sh."),
            reply_markup=get_main_menu_kb(user.language)
        )
        await state.clear()


async def process_order_confirm(message: Message, state: FSMContext, **kwargs):
    """Process order confirmation"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await message.answer(
            _("Iltimos, botni qaytadan ishga tushirish uchun /start buyrug'ini yuboring")
        )
        await state.clear()
        return

    # Get user response
    confirm = False
    cancel = False

    if user.language == 'uz':
        if message.text == "✅ Tasdiqlash":
            confirm = True
        elif message.text == "❌ Bekor qilish":
            cancel = True
    else:
        if message.text == "✅ Подтвердить":
            confirm = True
        elif message.text == "❌ Отменить":
            cancel = True

    if cancel:
        await message.answer(
            _("Buyurtma bekor qilindi."),
            reply_markup=get_main_menu_kb(user.language)
        )
        await state.clear()
        return

    if not confirm:
        # Invalid response
        builder = ReplyKeyboardBuilder()
        if user.language == 'uz':
            builder.row(
                KeyboardButton(text="✅ Tasdiqlash"),
                KeyboardButton(text="❌ Bekor qilish")
            )
        else:
            builder.row(
                KeyboardButton(text="✅ Подтвердить"),
                KeyboardButton(text="❌ Отменить")
            )

        await message.answer(
            _("Iltimos, tugmalardan birini tanlang."),
            reply_markup=builder.as_markup(resize_keyboard=True)
        )
        return

    # Confirm order
    try:
        state_data = await state.get_data()
        address = state_data.get('address', '')

        # Get cart using sync_to_async
        cart = await sync_to_async(Cart.objects.get)(user=user, is_active=True)

        # Get total price using sync_to_async
        total_price = await sync_to_async(cart.get_total_price)()

        # Buyurtma yaratish va Cart items ni O'chirish - Django ORM'ni sync_to_async bilan o'rash
        @sync_to_async
        def create_order_and_process_cart():
            # Create order
            order = Order.objects.create(
                user=user,
                address=address,
                total_price=Decimal(str(total_price))
            )

            # Create order items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product_name=item.color.product.name_uz,  # Store current names
                    color_name=item.color.name_uz,
                    price=item.color.price,
                    quantity=item.quantity
                )

            # Mark cart as inactive
            cart.is_active = False
            cart.save()

            return order

        # Buyurtmani yaratish
        order = await create_order_and_process_cart()

        # Send confirmation
        await message.answer(
            _("Buyurtma muvaffaqiyatli yaratildi!\n"
              "Buyurtma raqami: {order_id}\n\n"
              "Tez orada operatorlarimiz siz bilan bog'lanishadi.").format(order_id=order.id),
            reply_markup=get_main_menu_kb(user.language)
        )

        await state.clear()

    except Cart.DoesNotExist:
        await message.answer(
            _("Afsuski, buyurtmani yaratishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."),
            reply_markup=get_main_menu_kb(user.language)
        )
        await state.clear()