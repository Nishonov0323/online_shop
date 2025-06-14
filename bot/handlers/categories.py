from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

from store.models import Category
from bot.keyboards.categories import get_categories_kb
from bot.keyboards.common import get_main_menu_kb


def get_categories_router():
    router = Router()

    # Main menu buttons
    router.message.register(show_categories, F.text.in_(["🛍 Mahsulotlar katalogi", "🛍 Каталог товаров"]))
    router.callback_query.register(show_categories_callback, F.data == "show_categories")
    router.callback_query.register(show_category_products, F.data.startswith("category_"))
    router.callback_query.register(back_to_categories, F.data == "back_to_categories")

    return router


async def show_categories(message: Message, **kwargs):
    """Show main categories"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await message.answer(_("Iltimos, botni qaytadan ishga tushirish uchun /start buyrug'ini yuboring"))
        return

    try:
        # Get main categories (parent=None)
        categories = await sync_to_async(lambda: list(Category.objects.filter(parent=None, is_active=True)))()

        if categories:
            text = _("Kategoriyani tanlang:") if user.language == 'uz' else "Выберите категорию:"
            from bot.keyboards.categories import get_categories_kb
            await message.answer(
                text,
                reply_markup=get_categories_kb(categories, user.language)
            )
        else:
            await message.answer(
                _("Hozircha kategoriyalar mavjud emas."),
                reply_markup=get_main_menu_kb(user.language)
            )
    except Exception as e:
        await message.answer(
            _("Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring."),
            reply_markup=get_main_menu_kb(user.language)
        )


async def show_categories_callback(callback: CallbackQuery, **kwargs):
    """Show categories from callback"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    try:
        categories = await sync_to_async(lambda: list(Category.objects.filter(parent=None, is_active=True)))()

        if categories:
            text = _("Kategoriyani tanlang:") if user.language == 'uz' else "Выберите категорию:"
            from bot.keyboards.categories import get_categories_kb
            await callback.message.edit_text(
                text,
                reply_markup=get_categories_kb(categories, user.language)
            )
        else:
            await callback.message.edit_text(
                _("Hozircha kategoriyalar mavjud emas."),
                reply_markup=get_main_menu_kb(user.language)
            )
    except Exception as e:
        await callback.answer(_("Xatolik yuz berdi"))


async def show_category_products(callback: CallbackQuery, **kwargs):
    """Show products in selected category"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    try:
        category_id = int(callback.data.split('_')[1])

        # Get category
        category = await sync_to_async(Category.objects.get)(id=category_id, is_active=True)

        # Check if category has children
        children = await sync_to_async(lambda: list(category.children.filter(is_active=True)))()

        if children:
            # Show subcategories
            text = f"{category.get_name(user.language)}"
            from bot.keyboards.categories import get_categories_kb
            await callback.message.edit_text(
                text,
                reply_markup=get_categories_kb(children, user.language, parent_id=category_id)
            )
        else:
            # Show products in this category
            products = await sync_to_async(lambda: list(category.products.filter(is_active=True)))()

            if products:
                text = f"{category.get_name(user.language)} → {_('Mahsulotlar:')}"
                from bot.keyboards.products import get_product_actions_kb
                await callback.message.edit_text(
                    text,
                    reply_markup=get_product_actions_kb(products, user.language, category_id)
                )
            else:
                await callback.message.edit_text(
                    f"{category.get_name(user.language)} → {_('Bu kategoriyada mahsulotlar mavjud emas.')}",
                    reply_markup=get_categories_kb([category], user.language, show_back=True)
                )

    except Category.DoesNotExist:
        await callback.answer(_("Kategoriya topilmadi"))
    except ValueError:
        await callback.answer(_("Noto'g'ri kategoriya ID"))
    except Exception as e:
        await callback.answer(_("Xatolik yuz berdi"))


async def back_to_categories(callback: CallbackQuery, **kwargs):
    """Go back to main categories"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    await show_categories_callback(callback, **kwargs)