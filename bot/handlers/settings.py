from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

from store.models import User
from bot.keyboards.common import get_main_menu_kb, get_language_kb


class SettingsStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_name = State()


def get_settings_router():
    router = Router()

    # Register handlers
    router.message.register(show_settings, F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки"]))
    router.callback_query.register(change_language, F.data.startswith("change_lang"))
    router.callback_query.register(change_phone, F.data == "change_phone")
    router.callback_query.register(change_name, F.data == "change_name")
    router.callback_query.register(process_language_change, F.data.startswith("new_lang_"))
    router.message.register(process_phone_change, SettingsStates.waiting_for_phone)
    router.message.register(process_name_change, SettingsStates.waiting_for_name)

    return router


def get_settings_kb(user_language):
    """Create settings keyboard"""
    if user_language == 'uz':
        keyboard = [
            [InlineKeyboardButton(text="🌐 Tilni o'zgartirish", callback_data="change_lang")],
            [InlineKeyboardButton(text="📱 Telefon raqamini o'zgartirish", callback_data="change_phone")],
            [InlineKeyboardButton(text="👤 Ismni o'zgartirish", callback_data="change_name")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton(text="🌐 Изменить язык", callback_data="change_lang")],
            [InlineKeyboardButton(text="📱 Изменить номер телефона", callback_data="change_phone")],
            [InlineKeyboardButton(text="👤 Изменить имя", callback_data="change_name")]
        ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def show_settings(message: Message, **kwargs):
    """Show user settings"""
    # User ni kwargs dan olish
    user = kwargs.get('user')
    if not user:
        await message.answer(
            _("Iltimos, botni qaytadan ishga tushirish uchun /start buyrug'ini yuboring")
        )
        return

    if user.language == 'uz':
        settings_text = (
            f"⚙️ <b>Sozlamalar</b>\n\n"
            f"👤 <b>Ism:</b> {user.first_name or 'Kiritilmagan'}\n"
            f"📱 <b>Telefon:</b> {user.phone_number or 'Kiritilmagan'}\n"
            f"🌐 <b>Til:</b> O'zbek\n"
            f"🆔 <b>ID:</b> {user.telegram_id}"
        )
    else:
        settings_text = (
            f"⚙️ <b>Настройки</b>\n\n"
            f"👤 <b>Имя:</b> {user.first_name or 'Не указано'}\n"
            f"📱 <b>Телефон:</b> {user.phone_number or 'Не указан'}\n"
            f"🌐 <b>Язык:</b> Русский\n"
            f"🆔 <b>ID:</b> {user.telegram_id}"
        )

    await message.answer(
        settings_text,
        parse_mode="HTML",
        reply_markup=get_settings_kb(user.language)
    )


async def change_language(callback: CallbackQuery, **kwargs):
    """Show language selection"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    if user.language == 'uz':
        text = "Yangi tilni tanlang:"
    else:
        text = "Выберите новый язык:"

    # Create new language keyboard with different callback data
    keyboard = [
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="new_lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="new_lang_ru")
        ]
    ]

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


async def process_language_change(callback: CallbackQuery, **kwargs):
    """Process language change"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    new_language = callback.data.split('_')[2]  # 'uz' or 'ru'

    # Update user language using sync_to_async
    @sync_to_async
    def update_language():
        user.language = new_language
        user.save()
        return user

    updated_user = await update_language()

    if new_language == 'uz':
        success_text = "✅ Til muvaffaqiyatli o'zgartirildi!"
    else:
        success_text = "✅ Язык успешно изменен!"

    await callback.message.edit_text(success_text)

    # Show main menu with new language
    await callback.message.answer(
        "👇 Asosiy menyu:" if new_language == 'uz' else "👇 Главное меню:",
        reply_markup=get_main_menu_kb(new_language)
    )

    await callback.answer()


async def change_phone(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Request new phone number"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    # Create contact button
    if user.language == 'uz':
        text = "📱 Yangi telefon raqamingizni yuboring:"
        button_text = "📱 Telefon raqamini yuborish"
    else:
        text = "📱 Отправьте ваш новый номер телефона:"
        button_text = "📱 Отправить номер телефона"

    contact_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button_text, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await callback.message.delete()
    await callback.message.answer(text, reply_markup=contact_kb)
    await state.set_state(SettingsStates.waiting_for_phone)

    await callback.answer()


async def process_phone_change(message: Message, state: FSMContext, **kwargs):
    """Process phone number change"""
    user = kwargs.get('user')
    if not user:
        await message.answer(
            _("Iltimos, botni qaytadan ishga tushirish uchun /start buyrug'ini yuboring")
        )
        await state.clear()
        return

    phone_number = None

    if message.contact:
        phone_number = message.contact.phone_number
    elif message.text and message.text.startswith('+'):
        phone_number = message.text

    if phone_number:
        # Update user phone using sync_to_async
        @sync_to_async
        def update_phone():
            user.phone_number = phone_number
            user.save()
            return user

        await update_phone()

        if user.language == 'uz':
            success_text = f"✅ Telefon raqam muvaffaqiyatli o'zgartirildi!\n📱 Yangi raqam: {phone_number}"
        else:
            success_text = f"✅ Номер телефона успешно изменен!\n📱 Новый номер: {phone_number}"

        await message.answer(
            success_text,
            reply_markup=get_main_menu_kb(user.language)
        )
    else:
        if user.language == 'uz':
            error_text = "❌ Telefon raqam noto'g'ri formatda. Iltimos, qaytadan urinib ko'ring."
        else:
            error_text = "❌ Неверный формат номера телефона. Пожалуйста, попробуйте снова."

        await message.answer(
            error_text,
            reply_markup=get_main_menu_kb(user.language)
        )

    await state.clear()


async def change_name(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Request new name"""
    user = kwargs.get('user')
    if not user:
        await callback.answer(_("Iltimos, botni qaytadan ishga tushiring"))
        return

    if user.language == 'uz':
        text = "👤 Yangi ismingizni kiriting:"
    else:
        text = "👤 Введите ваше новое имя:"

    await callback.message.edit_text(text)
    await state.set_state(SettingsStates.waiting_for_name)

    await callback.answer()


async def process_name_change(message: Message, state: FSMContext, **kwargs):
    """Process name change"""
    user = kwargs.get('user')
    if not user:
        await message.answer(
            _("Iltimos, botni qaytadan ishga tushirish uchun /start buyrug'ini yuboring")
        )
        await state.clear()
        return

    new_name = message.text.strip()

    if new_name and len(new_name) > 0:
        # Update user name using sync_to_async
        @sync_to_async
        def update_name():
            user.first_name = new_name
            user.save()
            return user

        await update_name()

        if user.language == 'uz':
            success_text = f"✅ Ism muvaffaqiyatli o'zgartirildi!\n👤 Yangi ism: {new_name}"
        else:
            success_text = f"✅ Имя успешно изменено!\n👤 Новое имя: {new_name}"

        await message.answer(
            success_text,
            reply_markup=get_main_menu_kb(user.language)
        )
    else:
        if user.language == 'uz':
            error_text = "❌ Ism bo'sh bo'lishi mumkin emas. Iltimos, haqiqiy ism kiriting."
        else:
            error_text = "❌ Имя не может быть пустым. Пожалуйста, введите настоящее имя."

        await message.answer(
            error_text,
            reply_markup=get_main_menu_kb(user.language)
        )

    await state.clear()