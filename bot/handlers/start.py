from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

from store.models import User
from bot.keyboards.common import get_main_menu_kb, get_language_kb


class RegistrationStates(StatesGroup):
    waiting_for_contact = State()
    waiting_for_name = State()


def get_start_router():
    router = Router()

    # Register handlers
    router.message.register(start_command, CommandStart())
    router.callback_query.register(process_language, F.data.startswith("lang_"))
    router.message.register(process_contact, RegistrationStates.waiting_for_contact)
    router.message.register(process_name, RegistrationStates.waiting_for_name)

    return router


async def start_command(message: Message, state: FSMContext, **kwargs):
    """Handle /start command"""
    telegram_user = message.from_user

    try:
        # Check if user exists using sync_to_async
        user = await sync_to_async(User.objects.get)(telegram_id=telegram_user.id)

        # User exists, show main menu
        welcome_text = _("Xush kelibsiz!") if user.language == 'uz' else "Добро пожаловать!"
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_kb(user.language)
        )

    except User.DoesNotExist:
        # New user, ask for language
        await state.clear()  # Clear any existing state
        await message.answer(
            "Tilni tanlang / Выберите язык:",
            reply_markup=get_language_kb()
        )


async def process_language(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Process language selection"""
    language = callback.data.split('_')[1]  # 'uz' or 'ru'
    telegram_user = callback.from_user

    # Store language in state for later use
    await state.update_data(language=language)

    # Ask for contact
    if language == 'uz':
        text = "📱 Telefon raqamingizni yuboring:"
        button_text = "📱 Telefon raqamini yuborish"
    else:
        text = "📱 Отправьте ваш номер телефона:"
        button_text = "📱 Отправить номер телефона"

    contact_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button_text, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await callback.message.edit_text(text, reply_markup=None)
    await callback.message.answer(
        "👇 Tugmani bosing / Нажмите кнопку:",
        reply_markup=contact_kb
    )

    await state.set_state(RegistrationStates.waiting_for_contact)
    await callback.answer()


async def process_contact(message: Message, state: FSMContext, **kwargs):
    """Process contact information"""
    state_data = await state.get_data()
    language = state_data.get('language', 'uz')

    phone_number = None
    if message.contact:
        phone_number = message.contact.phone_number
    elif message.text and message.text.startswith('+'):
        phone_number = message.text

    if phone_number:
        # Store phone in state
        await state.update_data(phone_number=phone_number)

        # Ask for name
        if language == 'uz':
            text = "👤 Ismingizni kiriting:"
        else:
            text = "👤 Введите ваше имя:"

        await message.answer(
            text,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="❌ Bekor qilish" if language == 'uz' else "❌ Отмена")]],
                resize_keyboard=True
            )
        )

        await state.set_state(RegistrationStates.waiting_for_name)
    else:
        if language == 'uz':
            error_text = "❌ Iltimos, telefon raqamingizni yuboring!"
        else:
            error_text = "❌ Пожалуйста, отправьте ваш номер телефона!"

        await message.answer(error_text)


async def process_name(message: Message, state: FSMContext, **kwargs):
    """Process name and complete registration"""
    state_data = await state.get_data()
    language = state_data.get('language', 'uz')
    phone_number = state_data.get('phone_number')

    # Check for cancel
    if message.text in ["❌ Bekor qilish", "❌ Отмена"]:
        await message.answer(
            "Ro'yxatdan o'tish bekor qilindi." if language == 'uz' else "Регистрация отменена.",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start")]], resize_keyboard=True)
        )
        await state.clear()
        return

    name = message.text.strip()

    if name and len(name) > 0:
        telegram_user = message.from_user

        # Create user using sync_to_async
        @sync_to_async
        def create_user():
            user, created = User.objects.get_or_create(
                telegram_id=telegram_user.id,
                defaults={
                    'username': telegram_user.username or f"user_{telegram_user.id}",
                    'first_name': name,
                    'last_name': telegram_user.last_name or '',
                    'language': language,
                    'phone_number': phone_number
                }
            )

            if not created:
                # Update existing user
                user.first_name = name
                user.language = language
                user.phone_number = phone_number
                user.save()

            return user

        user = await create_user()

        # Registration complete
        if language == 'uz':
            welcome_text = f"✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!\n\nXush kelibsiz, {name}!"
        else:
            welcome_text = f"✅ Регистрация успешно завершена!\n\nДобро пожаловать, {name}!"

        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_kb(language)
        )

        await state.clear()
    else:
        if language == 'uz':
            error_text = "❌ Iltimos, haqiqiy ismingizni kiriting!"
        else:
            error_text = "❌ Пожалуйста, введите ваше настоящее имя!"

        await message.answer(error_text)