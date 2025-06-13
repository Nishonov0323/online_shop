from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async

from django.utils.translation import gettext as _
from store.models import User
from bot.keyboards.common import get_main_menu_kb


class RegistrationStates(StatesGroup):
    language = State()
    name = State()
    phone = State()


def get_start_router():
    router = Router()

    router.message.register(start_cmd, CommandStart())
    router.message.register(language_selection, RegistrationStates.language)
    router.message.register(name_input, RegistrationStates.name)
    router.message.register(phone_handler_contact, RegistrationStates.phone, F.content_type == "contact")
    router.message.register(phone_handler_text, RegistrationStates.phone)

    return router


async def start_cmd(message: Message, state: FSMContext):
    """
    Start command handler
    """
    await state.clear()

    try:
        # Use sync_to_async to get user from database
        user = await sync_to_async(User.objects.get)(telegram_id=message.from_user.id)

        # User already exists, show welcome message
        await message.answer(
            _("Xush kelibsiz, {name}!").format(name=user.first_name),
            reply_markup=get_main_menu_kb(user.language)
        )
    except User.DoesNotExist:
        # User doesn't exist, start registration process
        # Set state to language selection
        await state.set_state(RegistrationStates.language)

        # Show language selection keyboard
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🇺🇿 O'zbekcha"),
                    KeyboardButton(text="🇷🇺 Русский")
                ]
            ],
            resize_keyboard=True
        )

        await message.answer(
            "Tilni tanlang / Выберите язык",
            reply_markup=markup
        )


async def language_selection(message: Message, state: FSMContext):
    """
    Language selection handler
    """
    language = None

    if message.text == "🇺🇿 O'zbekcha":
        language = "uz"
    elif message.text == "🇷🇺 Русский":
        language = "ru"

    if language:
        # Save language to state
        await state.update_data(language=language)

        # Set state to name input
        await state.set_state(RegistrationStates.name)

        # Show name input message (with translation based on selected language)
        if language == "uz":
            await message.answer(
                "Ismingizni kiriting:",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await message.answer(
                "Введите ваше имя:",
                reply_markup=ReplyKeyboardRemove()
            )
    else:
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🇺🇿 O'zbekcha"),
                    KeyboardButton(text="🇷🇺 Русский")
                ]
            ],
            resize_keyboard=True
        )

        await message.answer(
            "Iltimos, tilni tanlang / Пожалуйста, выберите язык",
            reply_markup=markup
        )


async def name_input(message: Message, state: FSMContext):
    """
    Name input handler
    """
    name = message.text.strip()

    if len(name) < 2:
        # Name is too short
        state_data = await state.get_data()
        language = state_data.get("language", "uz")

        if language == "uz":
            await message.answer("Ism kamida 2 ta belgidan iborat bo'lishi kerak. Qaytadan kiriting:")
        else:
            await message.answer("Имя должно содержать минимум 2 символа. Введите снова:")
        return

    # Save name to state
    await state.update_data(first_name=name)

    # Set state to phone input
    await state.set_state(RegistrationStates.phone)

    # Show phone input message
    state_data = await state.get_data()
    language = state_data.get("language", "uz")

    # Create keyboard with contact sharing button
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 Raqamni yuborish" if language == "uz" else "📱 Отправить номер",
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True
    )

    if language == "uz":
        await message.answer(
            "Telefon raqamingizni yuboring yoki kiriting (+998XXXXXXXXX formatida):",
            reply_markup=markup
        )
    else:
        await message.answer(
            "Отправьте или введите ваш номер телефона (в формате +998XXXXXXXXX):",
            reply_markup=markup
        )


async def phone_handler_contact(message: Message, state: FSMContext):
    """
    Phone handler for contact sharing
    """
    phone_number = message.contact.phone_number

    # Save phone to state
    await state.update_data(phone_number=phone_number)

    # Get all data from state
    state_data = await state.get_data()
    language = state_data.get("language", "uz")
    first_name = state_data.get("first_name", "")

    # Create user
    user = await sync_to_async(User.objects.create)(
        telegram_id=message.from_user.id,
        first_name=first_name,
        phone_number=phone_number,
        language=language
    )

    # Clear state
    await state.clear()

    # Show welcome message
    await message.answer(
        _("Xush kelibsiz, {name}!").format(name=user.first_name),
        reply_markup=get_main_menu_kb(user.language)
    )


async def phone_handler_text(message: Message, state: FSMContext):
    """
    Phone handler for manual input
    """
    phone_number = message.text.strip()

    # Validate phone number
    if not (phone_number.startswith("+") and len(phone_number) >= 12 and phone_number[1:].isdigit()):
        # Invalid phone number
        state_data = await state.get_data()
        language = state_data.get("language", "uz")

        if language == "uz":
            await message.answer("Noto'g'ri telefon raqami formati. Qaytadan kiriting (+998XXXXXXXXX formatida):")
        else:
            await message.answer("Неверный формат номера телефона. Введите снова (в формате +998XXXXXXXXX):")
        return

    # Save phone to state
    await state.update_data(phone_number=phone_number)

    # Get all data from state
    state_data = await state.get_data()
    language = state_data.get("language", "uz")
    first_name = state_data.get("first_name", "")

    # Create user
    user = await sync_to_async(User.objects.create)(
        telegram_id=message.from_user.id,
        first_name=first_name,
        phone_number=phone_number,
        language=language
    )

    # Clear state
    await state.clear()

    # Show welcome message
    await message.answer(
        _("Xush kelibsiz, {name}!").format(name=user.first_name),
        reply_markup=get_main_menu_kb(user.language)
    )