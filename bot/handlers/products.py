from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _
from aiogram.types import InputFile
import os

from bot.keyboards.categories import get_categories_kb
from bot.keyboards.common import get_back_btn
from bot.keyboards.products import get_product_colors_kb, get_product_actions_kb, get_add_to_cart_kb
from store.models import Category, Product, Color, Cart, CartItem


def get_products_router():
    router = Router()

    # Register handlers with F filter
    router.callback_query.register(process_product, F.data.startswith("product_"))
    router.callback_query.register(process_color, F.data.startswith("color_"))
    router.callback_query.register(process_add_to_cart, F.data.startswith("add_to_cart_"))
    router.callback_query.register(back_to_category, F.data.startswith("back_to_category_"))
    router.callback_query.register(back_to_product, F.data.startswith("back_to_product_"))

    return router


async def show_category_products(message: Message, user, category):
    """Show products in a category"""
    # Get products using sync_to_async
    products = await sync_to_async(lambda: list(Product.objects.filter(categories=category, is_active=True)))()

    if products:
        await message.answer(
            _("{category} kategoriyasidagi mahsulotlar:").format(
                category=category.get_name(user.language)
            ),
            reply_markup=get_product_actions_kb(products, user.language, category.id)
        )
    else:
        # Get parent categories using sync_to_async
        parent_categories = await sync_to_async(
            lambda: list(Category.objects.filter(children=category, is_active=True)))()

        if parent_categories:
            parent = parent_categories[0]
            await message.answer(
                _("Bu kategoriyada hech qanday mahsulot yo'q."),
                reply_markup=get_categories_kb([parent], user.language,
                                               parent_id=parent.parent_id if parent.parent else None)
            )
        else:
            await message.answer(
                _("Bu kategoriyada hech qanday mahsulot yo'q."),
                reply_markup=get_back_btn(user.language)
            )


# process_product funksiyasida:
async def process_product(callback: CallbackQuery, **kwargs):
    """Process product selection"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    product_id = int(callback.data.split('_')[1])

    try:
        # Get product using sync_to_async
        product = await sync_to_async(Product.objects.get)(id=product_id)
        category_id = int(callback.data.split('_')[2]) if len(callback.data.split('_')) > 2 else None

        # Get product colors using sync_to_async
        colors = await sync_to_async(lambda: list(product.colors.filter(is_active=True)))()

        # Get product details
        name = product.get_name(user.language)
        description = product.get_description(user.language) or _("Tavsif mavjud emas.")

        # Prepare product info
        if product.main_image:
            # ImageFieldFile'ni URL'ga aylantirish
            image_url = product.main_image.url
            # Send photo with caption
            await callback.message.delete()  # Delete previous message
            await callback.message.answer_photo(
                photo=image_url,
                caption=f"<b>{name}</b>\n\n{description}",
                reply_markup=get_product_colors_kb(colors, user.language, product.id, category_id)
            )
        else:
            # Send text message
            await callback.message.edit_text(
                f"<b>{name}</b>\n\n{description}",
                reply_markup=get_product_colors_kb(colors, user.language, product.id, category_id)
            )

    except Product.DoesNotExist:
        await callback.answer(_("Mahsulot topilmadi."))

    await callback.answer()


# back_to_product funksiyasini to'g'rilash (callback.data ni o'zgartirmaslik):
async def back_to_product(callback: CallbackQuery, **kwargs):
    """Return to product details"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    product_id = int(callback.data.split('_')[3])
    category_id = int(callback.data.split('_')[4]) if len(callback.data.split('_')) > 4 else None

    try:
        # Get product using sync_to_async
        product = await sync_to_async(Product.objects.get)(id=product_id)

        # Yangi callback yaratish (callback.data ni o'zgartirmaslik)
        from aiogram.types import CallbackQuery as NewCallbackQuery

        # process_product funksiyasini to'g'ridan-to'g'ri chaqirish
        # Ammo avval yangi callback data yaratish kerak
        new_data = f"product_{product_id}_{category_id}" if category_id else f"product_{product_id}"

        # Temporary callback data for processing
        original_data = callback.data
        callback.data = new_data

        await process_product(callback, **kwargs)

        # Restore original data
        callback.data = original_data

    except Product.DoesNotExist:
        await callback.answer(_("Mahsulot topilmadi."))


async def process_color(callback: CallbackQuery, **kwargs):
    """Process color selection"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    color_id = int(callback.data.split('_')[1])
    product_id = int(callback.data.split('_')[2])
    category_id = int(callback.data.split('_')[3]) if len(callback.data.split('_')) > 3 else None

    try:
        # Get color and product using sync_to_async
        color = await sync_to_async(Color.objects.get)(id=color_id)
        product = await sync_to_async(Product.objects.get)(id=product_id)

        # Get color details
        color_name = color.get_name(user.language)
        price = color.price

        # Show color images if exist - using sync_to_async
        has_images = await sync_to_async(lambda: color.images.exists())()

        if has_images:
            # Get images using sync_to_async
            color_images = await sync_to_async(lambda: list(color.images.all()))()
            first_image = color_images[0]

            # Caption for the image
            caption = f"<b>{product.get_name(user.language)}</b>\n" \
                      f"<i>{color_name}</i>\n" \
                      f"{_('Narxi')}: {price:,.0f} {_('so\'m')}"

            # Send with add to cart button
            await callback.message.delete()  # Delete previous message

            # Rasm URL'ini tekshirish va InputFile ishlatish
            if first_image.image and first_image.image.name:
                try:
                    # Rasm fayli mavjudligini tekshirish
                    image_path = first_image.image.path
                    if os.path.exists(image_path):
                        # InputFile ishlatish
                        photo = InputFile(image_path)
                        await callback.message.answer_photo(
                            photo=photo,
                            caption=caption,
                            reply_markup=get_add_to_cart_kb(color.id, product.id, category_id, user.language)
                        )
                    else:
                        # Rasm mavjud bo'lmasa, faqat matn yuborish
                        await callback.message.answer(
                            caption,
                            reply_markup=get_add_to_cart_kb(color.id, product.id, category_id, user.language)
                        )
                except Exception as e:
                    # Xatolik bo'lsa, faqat matn yuborish
                    await callback.message.answer(
                        caption,
                        reply_markup=get_add_to_cart_kb(color.id, product.id, category_id, user.language)
                    )
            else:
                # Rasm mavjud bo'lmasa, faqat matn yuborish
                await callback.message.answer(
                    caption,
                    reply_markup=get_add_to_cart_kb(color.id, product.id, category_id, user.language)
                )

            # Send other images if available
            for img in color_images[1:]:
                if img.image and img.image.name and os.path.exists(img.image.path):
                    try:
                        photo = InputFile(img.image.path)
                        await callback.message.answer_photo(photo=photo)
                    except Exception:
                        pass  # Skip if error
        else:
            # If no images, use product main image
            caption = f"<b>{product.get_name(user.language)}</b>\n" \
                      f"<i>{color_name}</i>\n" \
                      f"{_('Narxi')}: {price:,.0f} {_('so\'m')}"

            if product.main_image and product.main_image.name and os.path.exists(product.main_image.path):
                try:
                    photo = InputFile(product.main_image.path)
                    await callback.message.answer_photo(
                        photo=photo,
                        caption=caption,
                        reply_markup=get_add_to_cart_kb(color.id, product.id, category_id, user.language)
                    )
                except Exception:
                    await callback.message.answer(
                        caption,
                        reply_markup=get_add_to_cart_kb(color.id, product.id, category_id, user.language)
                    )
            else:
                await callback.message.edit_caption(
                    caption=caption,
                    reply_markup=get_add_to_cart_kb(color.id, product.id, category_id, user.language)
                )

    except (Color.DoesNotExist, Product.DoesNotExist):
        await callback.answer(_("Mahsulot yoki rang topilmadi."))

    await callback.answer()


async def process_add_to_cart(callback: CallbackQuery, **kwargs):
    """Add product to cart"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    color_id = int(callback.data.split('_')[3])
    global quantity
    quantity = int(callback.data.split('_')[4]) if len(callback.data.split('_')) > 4 else 1

    try:
        # Get color using sync_to_async
        color = await sync_to_async(Color.objects.get)(id=color_id)

        # Get or create cart and add item using sync_to_async
        @sync_to_async
        def add_to_cart():
            # Get or create active cart for user
            cart, created = Cart.objects.get_or_create(
                user=user,
                is_active=True
            )

            # Check if item already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                color=color,
                defaults={'quantity': quantity}
            )

            # If item already exists, increase quantity
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        await add_to_cart()
        await callback.answer(_("Mahsulot savatchaga qo'shildi!"), show_alert=True)

    except Color.DoesNotExist:
        await callback.answer(_("Mahsulot topilmadi."))


async def back_to_category(callback: CallbackQuery, **kwargs):
    """Return to category products"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    category_id = int(callback.data.split('_')[3])

    try:
        # Get category using sync_to_async
        category = await sync_to_async(Category.objects.get)(id=category_id)
        await callback.message.delete()  # Delete current message
        await show_category_products(callback.message, user, category)

    except Category.DoesNotExist:
        await callback.answer(_("Kategoriya topilmadi."))

    await callback.answer()


async def back_to_product(callback: CallbackQuery, **kwargs):
    """Return to product details"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    product_id = int(callback.data.split('_')[3])
    category_id = int(callback.data.split('_')[4]) if len(callback.data.split('_')) > 4 else None

    try:
        # Get product using sync_to_async
        product = await sync_to_async(Product.objects.get)(id=product_id)
        # Create new callback data for product processing
        callback.data = f"product_{product_id}_{category_id}" if category_id else f"product_{product_id}"
        await process_product(callback, **kwargs)

    except Product.DoesNotExist:
        await callback.answer(_("Mahsulot topilmadi."))