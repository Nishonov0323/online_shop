from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

from store.models import Category
from bot.keyboards.categories import get_categories_kb, get_category_back_kb
from bot.keyboards.common import get_main_menu_kb


def get_categories_router():
    router = Router()

    # Text o'rniga F.text.in_ ishlatamiz
    router.message.register(show_categories, F.text.in_(["🛍 Mahsulotlar katalogi", "🛍 Каталог товаров"]))
    router.callback_query.register(process_category, F.data.startswith("category_"))

    return router


async def show_categories(message: Message, **kwargs):
    """Show main categories"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        # Agar user mavjud bo'lmasa, login qilish kerakligini aytish
        await message.answer(
            _("Iltimos, botni qaytadan ishga tushirish uchun /start buyrug'ini yuboring")
        )
        return

    # Get all root categories using sync_to_async
    categories = await sync_to_async(lambda: list(Category.objects.filter(parent=None, is_active=True)))()

    if categories:
        await message.answer(
            _("Kategoriyani tanlang:"),
            reply_markup=get_categories_kb(categories, user.language)
        )
    else:
        await message.answer(
            _("Hozircha kategoriyalar mavjud emas."),
            reply_markup=get_main_menu_kb(user.language)
        )


async def process_category(callback: CallbackQuery, **kwargs):
    """Process category selection"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    category_id = int(callback.data.split('_')[1])

    try:
        # sync_to_async bilan o'rash
        category = await sync_to_async(Category.objects.get)(id=category_id)

        # Check if category has subcategories
        subcategories = await sync_to_async(lambda: list(category.children.filter(is_active=True)))()

        if subcategories:
            # Show subcategories
            await callback.message.edit_text(
                _("{category} bo'limidagi kategoriyalar:").format(category=category.get_name(user.language)),
                reply_markup=get_categories_kb(subcategories, user.language, parent_id=category.id)
            )
        else:
            # Show products in this category
            from bot.handlers.products import show_category_products
            await callback.message.delete()  # Delete the categories message
            await show_category_products(callback.message, user, category)

    except Category.DoesNotExist:
        await callback.answer(_("Kategoriya topilmadi."))

    await callback.answer()