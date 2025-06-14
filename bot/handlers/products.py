from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

from store.models import Category, Product, Color, Cart, CartItem
from bot.keyboards.products import get_product_colors_kb, get_product_actions_kb, get_add_to_cart_kb
from bot.keyboards.categories import get_categories_kb
from bot.keyboards.common import get_back_btn


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


async def process_product(callback: CallbackQuery, **kwargs):
    """Process product selection"""
    print(f"DEBUG: process_product called with data: {callback.data}")

    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        print("DEBUG: User not found in kwargs")
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    print(f"DEBUG: User found: {user.telegram_id}")

    try:
        product_id = int(callback.data.split('_')[1])
        category_id = int(callback.data.split('_')[2]) if len(callback.data.split('_')) > 2 else None

        print(f"DEBUG: Parsed IDs - product: {product_id}, category: {category_id}")

        # Get product using sync_to_async
        product = await sync_to_async(Product.objects.get)(id=product_id)

        # Get product colors using sync_to_async
        colors = await sync_to_async(lambda: list(product.colors.filter(is_active=True)))()

        print(f"DEBUG: Found {len(colors)} colors for product")

        # Get product details
        name = product.get_name(user.language)
        description = product.get_description(user.language) or _("Tavsif mavjud emas.")

        # Prepare product info
        if product.main_image:
            # ImageFieldFile'ni URL'ga aylantirish
            image_url = product.main_image.url
            print(f"DEBUG: Using product image: {image_url}")
            # Send photo with caption
            await callback.message.delete()  # Delete previous message
            await callback.message.answer_photo(
                photo=image_url,
                caption=f"<b>{name}</b>\n\n{description}",
                reply_markup=get_product_colors_kb(colors, user.language, product.id, category_id)
            )
        else:
            print("DEBUG: No product image, sending text")
            # Send text message
            await callback.message.edit_text(
                f"<b>{name}</b>\n\n{description}",
                reply_markup=get_product_colors_kb(colors, user.language, product.id, category_id)
            )

    except Product.DoesNotExist:
        print("DEBUG: Product not found")
        await callback.answer(_("Mahsulot topilmadi."))
    except Exception as e:
        print(f"DEBUG: Error in process_product: {e}")
        await callback.answer(_("Xatolik yuz berdi."))

    await callback.answer()


async def process_color(callback: CallbackQuery, **kwargs):
    """Process color selection"""
    print(f"DEBUG: process_color called with data: {callback.data}")

    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        print("DEBUG: User not found in kwargs")
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    print(f"DEBUG: User found: {user.telegram_id}")

    try:
        parts = callback.data.split('_')
        if len(parts) < 3:
            print(f"DEBUG: Invalid callback data format: {callback.data}")
            await callback.message.answer(f"Noto'g'ri callback data: {callback.data}")
            return

        color_id = int(parts[1])
        product_id = int(parts[2])
        category_id = int(parts[3]) if len(parts) > 3 else None

        print(f"DEBUG: Parsed IDs - color: {color_id}, product: {product_id}, category: {category_id}")

        # Get color and product using sync_to_async
        color = await sync_to_async(Color.objects.get)(id=color_id)
        product = await sync_to_async(Product.objects.get)(id=product_id)

        # Get color details
        color_name = color.get_name(user.language)
        price = color.price

        # Show color images if exist - using sync_to_async
        has_images = await sync_to_async(lambda: color.images.exists())()

        print(f"DEBUG: Color has images: {has_images}")

        # Caption for the image/message
        caption = f"<b>{product.get_name(user.language)}</b>\n" \
                  f"<i>{color_name}</i>\n" \
                  f"{_('Narxi')}: {price:,.0f} {_('so\'m')}"

        # Always delete previous message and send new one to avoid caption/text conflicts
        await callback.message.delete()

        if has_images:
            # Get images using sync_to_async
            color_images = await sync_to_async(lambda: list(color.images.all()))()
            first_image = color_images[0]

            # Send photo with caption
            await callback.message.answer_photo(
                photo=first_image.image.url,
                caption=caption,
                reply_markup=get_add_to_cart_kb(color.id, product.id, category_id, user.language)
            )

            # Send other images if available
            for img in color_images[1:]:
                await callback.message.answer_photo(photo=img.image.url)
        else:
            # If no images, use product main image
            if product.main_image:
                await callback.message.answer_photo(
                    photo=product.main_image.url,
                    caption=caption,
                    reply_markup=get_add_to_cart_kb(color.id, product.id, category_id, user.language)
                )
            else:
                # Send text message if no images at all
                await callback.message.answer(
                    caption,
                    reply_markup=get_add_to_cart_kb(color.id, product.id, category_id, user.language)
                )

    except (Color.DoesNotExist, Product.DoesNotExist) as e:
        print(f"DEBUG: Object not found: {e}")
        await callback.answer(_("Mahsulot yoki rang topilmadi."))
    except Exception as e:
        print(f"DEBUG: Error in process_color: {e}")
        await callback.message.answer(f"Xato: {str(e)}")

    await callback.answer()


async def process_add_to_cart(callback: CallbackQuery, **kwargs):
    """Add product to cart"""
    print(f"DEBUG: process_add_to_cart called with data: {callback.data}")

    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        print("DEBUG: User not found in kwargs")
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    print(f"DEBUG: User found: {user.telegram_id}")

    try:
        # Callback data parse qilish
        parts = callback.data.split('_')
        print(f"DEBUG: Callback data parts: {parts}")

        if len(parts) < 4:
            print(f"DEBUG: Invalid callback data format: {callback.data}")
            await callback.answer("Noto'g'ri ma'lumot formati")
            return

        color_id = int(parts[3])  # add_to_cart_COLOR_ID
        quantity = 1

        print(f"DEBUG: Parsing - color_id: {color_id}, quantity: {quantity}")

        # Test: Avval color mavjudligini tekshirish
        try:
            color = await sync_to_async(Color.objects.get)(id=color_id)
            print(f"DEBUG: Color found: {color.name_uz} - {color.price}")
        except Color.DoesNotExist:
            print(f"DEBUG: Color not found with id: {color_id}")
            await callback.answer(_("Mahsulot topilmadi."))
            return

        # Test: Cart yaratish yoki olish
        @sync_to_async
        def add_to_cart():
            print(f"DEBUG: Creating/getting cart for user: {user.telegram_id}")

            # Get or create active cart for user
            cart, created = Cart.objects.get_or_create(
                user=user,
                is_active=True
            )
            print(f"DEBUG: Cart {'created' if created else 'found'}: {cart.id}")

            # Check if item already in cart
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                color=color,
                defaults={'quantity': quantity}
            )
            print(f"DEBUG: Cart item {'created' if item_created else 'found'}: {cart_item.id}")

            # If item already exists, increase quantity
            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()
                print(f"DEBUG: Updated quantity to: {cart_item.quantity}")

            return cart_item

        cart_item = await add_to_cart()
        print(f"DEBUG: Successfully added to cart - item_id: {cart_item.id}")

        # Success message
        await callback.answer(_("Mahsulot savatchaga qo'shildi!"), show_alert=True)

        # Optional: Show updated cart info
        product_name = color.product.get_name(user.language)
        color_name = color.get_name(user.language)
        await callback.message.answer(
            f"✅ {product_name} ({color_name}) savatchaga qo'shildi!\n"
            f"Miqdor: {cart_item.quantity}\n"
            f"Narxi: {color.price:,.0f} so'm"
        )

    except Exception as e:
        print(f"DEBUG: Error in process_add_to_cart: {str(e)}")
        import traceback
        traceback.print_exc()
        await callback.answer(f"Xatolik: {str(e)}")


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

        # Process product without changing callback data
        await process_product_direct(callback, user, product, category_id)

    except Product.DoesNotExist:
        await callback.answer(_("Mahsulot topilmadi."))


async def process_product_direct(callback: CallbackQuery, user, product, category_id):
    """Process product directly without callback data manipulation"""
    try:
        # Get product colors using sync_to_async
        colors = await sync_to_async(lambda: list(product.colors.filter(is_active=True)))()

        # Get product details
        name = product.get_name(user.language)
        description = product.get_description(user.language) or _("Tavsif mavjud emas.")

        # Prepare product info
        if product.main_image:
            # Send photo with caption
            await callback.message.delete()  # Delete previous message
            await callback.message.answer_photo(
                photo=product.main_image.url,
                caption=f"<b>{name}</b>\n\n{description}",
                reply_markup=get_product_colors_kb(colors, user.language, product.id, category_id)
            )
        else:
            # Send text message
            await callback.message.edit_text(
                f"<b>{name}</b>\n\n{description}",
                reply_markup=get_product_colors_kb(colors, user.language, product.id, category_id)
            )

    except Exception as e:
        print(f"DEBUG: Error in process_product_direct: {e}")
        await callback.answer(_("Xatolik yuz berdi."))

    await callback.answer()