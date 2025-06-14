from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async
from django.conf import settings
import os
import requests
from PIL import Image
import io

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


def get_image_file_path(image_field):
    """Get file path for image field"""
    if not image_field:
        return None

    try:
        # Get full file path
        file_path = os.path.join(settings.MEDIA_ROOT, str(image_field))
        if os.path.exists(file_path):
            return file_path
        return None
    except Exception as e:
        print(f"DEBUG: Error getting image file path: {e}")
        return None


def validate_image_for_telegram(file_path):
    """Validate image for Telegram compatibility"""
    if not file_path or not os.path.exists(file_path):
        return False

    try:
        # Check file size (max 10MB for photos)
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            print(f"DEBUG: File too large: {file_size} bytes")
            return False

        # Check if it's a valid image
        with Image.open(file_path) as img:
            # Check format
            if img.format not in ['JPEG', 'PNG', 'GIF', 'WEBP']:
                print(f"DEBUG: Unsupported format: {img.format}")
                return False

            # Check dimensions (max 10000x10000)
            if img.width > 10000 or img.height > 10000:
                print(f"DEBUG: Image too large: {img.width}x{img.height}")
                return False

        return True
    except Exception as e:
        print(f"DEBUG: Error validating image: {e}")
        return False


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
        text_content = f"<b>{name}</b>\n\n{description}"
        keyboard = get_product_colors_kb(colors, user.language, product.id, category_id)

        # Try to send with image first
        if product.main_image:
            file_path = get_image_file_path(product.main_image)
            print(f"DEBUG: Product image file path: {file_path}")

            if file_path and validate_image_for_telegram(file_path):
                try:
                    await callback.message.delete()
                    await callback.message.answer_photo(
                        photo=FSInputFile(file_path),
                        caption=text_content,
                        reply_markup=keyboard
                    )
                    print("DEBUG: Successfully sent product photo")
                    await callback.answer()
                    return
                except Exception as e:
                    print(f"DEBUG: Error sending photo with FSInputFile: {e}")

        # Fallback to text message
        print("DEBUG: Sending text message instead of photo")
        await callback.message.edit_text(
            text_content,
            reply_markup=keyboard
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

        # Caption for the image/message
        caption = f"<b>{product.get_name(user.language)}</b>\n" \
                  f"<i>{color_name}</i>\n" \
                  f"{_('Narxi')}: {price:,.0f} {_('so\'m')}"

        keyboard = get_add_to_cart_kb(color.id, product.id, category_id, user.language)

        # Always delete previous message
        await callback.message.delete()

        # Check for color images
        has_images = await sync_to_async(lambda: color.images.exists())()
        print(f"DEBUG: Color has images: {has_images}")

        if has_images:
            # Get images using sync_to_async
            color_images = await sync_to_async(lambda: list(color.images.all()))()

            # Try to send first image
            for color_image in color_images:
                file_path = get_image_file_path(color_image.image)
                print(f"DEBUG: Color image file path: {file_path}")

                if file_path and validate_image_for_telegram(file_path):
                    try:
                        await callback.message.answer_photo(
                            photo=FSInputFile(file_path),
                            caption=caption,
                            reply_markup=keyboard
                        )
                        print("DEBUG: Successfully sent color photo")

                        # Send additional images without caption
                        for additional_image in color_images[1:]:
                            additional_path = get_image_file_path(additional_image.image)
                            if additional_path and validate_image_for_telegram(additional_path):
                                try:
                                    await callback.message.answer_photo(
                                        photo=FSInputFile(additional_path)
                                    )
                                except Exception as e:
                                    print(f"DEBUG: Error sending additional image: {e}")

                        await callback.answer()
                        return
                    except Exception as e:
                        print(f"DEBUG: Error sending color photo: {e}")
                        continue

        # If no valid color images, try product main image
        if product.main_image:
            file_path = get_image_file_path(product.main_image)
            if file_path and validate_image_for_telegram(file_path):
                try:
                    await callback.message.answer_photo(
                        photo=FSInputFile(file_path),
                        caption=caption,
                        reply_markup=keyboard
                    )
                    print("DEBUG: Successfully sent product main image")
                    await callback.answer()
                    return
                except Exception as e:
                    print(f"DEBUG: Error sending product main image: {e}")

        # Fallback to text message
        print("DEBUG: Sending text message instead of photo")
        await callback.message.answer(
            caption,
            reply_markup=keyboard
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
    print(f"DEBUG: add_to_cart called with data: {callback.data}")

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

        print(f"DEBUG: Adding color_id: {color_id} to cart")

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
    print(f"DEBUG: back_to_category called with data: {callback.data}")

    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    try:
        category_id = int(callback.data.split('_')[3])

        # Get category using sync_to_async
        category = await sync_to_async(Category.objects.get)(id=category_id)
        await callback.message.delete()  # Delete current message

        # Import qilishda xatolik bo'lmasligi uchun to'g'ridan-to'g'ri chaqirish
        await show_category_products(callback.message, user, category)

    except Category.DoesNotExist:
        await callback.answer(_("Kategoriya topilmadi."))
    except Exception as e:
        print(f"DEBUG: Error in back_to_category: {e}")
        await callback.answer(_("Xatolik yuz berdi."))

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

        text_content = f"<b>{name}</b>\n\n{description}"
        keyboard = get_product_colors_kb(colors, user.language, product.id, category_id)

        # Try to send with image first
        if product.main_image:
            file_path = get_image_file_path(product.main_image)
            if file_path and validate_image_for_telegram(file_path):
                try:
                    await callback.message.delete()
                    await callback.message.answer_photo(
                        photo=FSInputFile(file_path),
                        caption=text_content,
                        reply_markup=keyboard
                    )
                    await callback.answer()
                    return
                except Exception as e:
                    print(f"DEBUG: Error sending photo in direct: {e}")

        # Fallback to text message
        await callback.message.edit_text(
            text_content,
            reply_markup=keyboard
        )

    except Exception as e:
        print(f"DEBUG: Error in process_product_direct: {e}")
        await callback.answer(_("Xatolik yuz berdi."))

    await callback.answer()