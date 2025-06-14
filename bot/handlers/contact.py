from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

from store.models import User
from bot.keyboards.common import get_main_menu_kb


def get_contact_router():
    router = Router()

    # Register handlers
    router.message.register(show_contact, F.text.in_(["📞 Bog'lanish", "📞 Связаться"]))

    return router


async def show_contact(message: Message, **kwargs):
    """Show contact information"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await message.answer(
            _("Iltimos, botni qaytadan ishga tushirish uchun /start buyrug'ini yuboring")
        )
        return

    if user.language == 'uz':
        contact_text = (
            "📞 <b>Bog'lanish</b>\n\n"
            "📧 <b>Email:</b> info@onlineshop.uz\n"
            "📱 <b>Telefon:</b> +998 90 123 45 67\n"
            "📲 <b>Telegram:</b> @onlineshop_admin\n\n"
            "🕒 <b>Ish vaqti:</b>\n"
            "Dushanba - Yakshanba: 09:00 - 21:00\n\n"
            "📍 <b>Manzil:</b>\n"
            "Toshkent sh., Yunusobod tumani,\n"
            "Amir Temur ko'chasi, 1-uy"
        )
    else:
        contact_text = (
            "📞 <b>Связаться</b>\n\n"
            "📧 <b>Email:</b> info@onlineshop.uz\n"
            "📱 <b>Телефон:</b> +998 90 123 45 67\n"
            "📲 <b>Telegram:</b> @onlineshop_admin\n\n"
            "🕒 <b>Время работы:</b>\n"
            "Понедельник - Воскресенье: 09:00 - 21:00\n\n"
            "📍 <b>Адрес:</b>\n"
            "г. Ташкент, Юнусабадский район,\n"
            "ул. Амир Темур, дом 1"
        )

    await message.answer(
        contact_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_kb(user.language)
    )