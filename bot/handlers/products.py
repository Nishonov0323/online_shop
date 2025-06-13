from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

from store.models import Product, Color, Cart, CartItem
from bot.keyboards.products import get_product_colors_kb, get_add_to_cart_kb
from bot.keyboards.categories import get_categories_kb
from bot.keyboards.common import get_main_menu_kb


def get_products_router():
    router = Router()

    router.callback_query.register(show_product_detail, F.data.startswith("product_"))
    router.callback_query.register(show_color_detail, F.data.startswith("color_"))
    router.callback_query.register(add_to_cart, F.data.startswith("add_to_cart_"))
    router.callback_query.register(back_to_product, F.data.startswith("back_to_product_"))
    router.callback_query.register(back_to_category, F.data.startswith("back_to_category_"))

    return router


async def show_product_detail(callback: CallbackQuery, **kwargs):
    """Show product details with colors"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    try:
        # Parse callback data: product_ID_categoryID
        parts = callback.data.split('_')
        product_id = int(parts[1])
        category_id = int(parts[2]) if parts[2] != '0' else None

        # Get product
        product = await sync_to_async(Product.objects.get)(id=product_id, is_active=True)

        # Get product colors
        colors = await sync_to_async(lambda: list(product.colors.filter(is_active=True)))()

        if colors:
            # Product info text
            product_name = product.get_name(user.language)
            description = product.get_description(user.language)

            text = f"<b>{product_name}</b>\n\n"
            if description:
                text += f"{description}\n\n"
            text += _("Rangni tanlang:")

            # Send product image if exists
            if product.main_image:
                await callback.message.delete()
                await callback.message.answer_photo(
                    photo=product.main_image,
                    caption=text,
                    reply_markup=get_product_colors_kb(colors, user.language, product_id, category_id)
                )
            else:
                await callback.message.edit_text(
                    text,
                    reply_markup=get_product_colors_kb(colors, user.language, product_id, category_id)
                )
        else:
            await callback.answer(_("Bu mahsulot uchun ranglar mavjud emas"))

    except Product.DoesNotExist:
        await callback.answer(_("Mahsulot topilmadi"))
    except Exception as e:
        await callback.answer(_("Xatolik yuz berdi"))


async def show_color_detail(callback: CallbackQuery, **kwargs):
    """Show color details with images and add to cart button"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    try:
        # Parse callback data: color_colorID_productID_categoryID
        parts = callback.data.split('_')
        color_id = int(parts[1])
        product_id = int(parts[2])
        category_id = int(parts[3]) if parts[3] != '0' else None

        # Get color with product
        color = await sync_to_async(Color.objects.select_related('product').get)(id=color_id, is_active=True)

        # Get color images
        images = await sync_to_async(lambda: list(color.images.all().order_by('order')))()

        # Product and color info
        product_name = color.product.get_name(user.language)
        color_name = color.get_name(user.language)
        price = color.price

        text = f"<b>{product_name}</b>\n"
        text += f"<i>{color_name}</i>\n\n"
        text += f"💰 {_('Narxi')}: {price:,.0f} {_("so\\'m")}"

        if images:
            # Send first image with text
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=
        images[0].image,
        caption = text,
        reply_markup = get_add_to_cart_kb(color_id, product_id, category_id, user.language)
        )

        # Send additional images if exists
        if len(images) > 1:
            media_group = []
        for img in images[1:4]:  # Max 3 additional images
            media_group.append(InputMediaPhoto(media=img.image))

        if media_group:
            await callback.message.answer_media_group(media_group)
        else:
            await callback.message.edit_text(
                text,
                reply_markup=get_add_to_cart_kb(color_id, product_id, category_id, user.language)
            )

    except Color.DoesNotExist:
        await callback.answer(_("Rang topilmadi"))
    except Exception as e:
        await callback.answer(_("Xatolik yuz berdi"))


async def add_to_cart(callback: CallbackQuery, **kwargs):
    """Add product color to cart"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    try:
        color_id = int(callback.data.split('_')[3])

        # Get color
        color = await sync_to_async(Color.objects.select_related('product').get)(id=color_id, is_active=True)

        # Get or create cart
        cart, created = await sync_to_async(Cart.objects.get_or_create)(
            user=user,
            is_active=True,
            defaults={'user': user}
        )

        # Check if item already in cart
        cart_item, item_created = await sync_to_async(CartItem.objects.get_or_create)(
            cart=cart,
            color=color,
            defaults={'quantity': 1}
        )

        if not item_created:
            # Increase quantity
            cart_item.quantity += 1
            await sync_to_async(cart_item.save)()

        product_name = color.product.get_name(user.language)
        color_name = color.get_name(user.language)

        success_text = _("✅ Savatchaga qo'shildi!\n\n{} ({})\nSoni: {}").format(
            product_name, color_name, cart_item.quantity
        )

        await callback.answer(success_text, show_alert=True)

    except Color.DoesNotExist:
        await callback.answer(_("Rang topilmadi"))
    except Exception as e:
        await callback.answer(_("Xatolik yuz berdi"))


async def back_to_product(callback: CallbackQuery, **kwargs):
    """Go back to product colors"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    # Parse callback data and show product detail
    parts = callback.data.split('_')
    product_id = parts[3]
    category_id = parts[4]

    # Reconstruct product callback data
    new_callback_data = f"product_{product_id}_{category_id}"
    callback.data = new_callback_data

    await show_product_detail(callback, **kwargs)


async def back_to_category(callback: CallbackQuery, **kwargs):
    """Go back to category products"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    # Parse callback data and show category
    category_id = callback.data.split('_')[3]

    # Reconstruct category callback data
    new_callback_data = f"category_{category_id}"
    callback.data = new_callback_data

    from bot.handlers.categories import show_category_products
    await show_category_products(callback, **kwargs)