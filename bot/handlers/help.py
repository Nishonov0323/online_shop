from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

from store.models import User


def get_help_router():
    router = Router()

    # Register help command handler
    router.message.register(help_command, Command("help"))

    return router


async def help_command(message: Message, **kwargs):
    """Handle /help command - show bot information and available commands"""
    telegram_user = message.from_user

    try:
        # Get user to determine language
        user = await sync_to_async(User.objects.get)(telegram_id=telegram_user.id)
        language = user.language
    except User.DoesNotExist:
        # Default to Uzbek for unregistered users
        language = 'uz'

    # Prepare help text based on language
    if language == 'uz':
        help_text = """
🤖 **Online Do'kon Bot Haqida**

Salom! Men sizning online do'kon botingizman. Men orqali siz:

📋 **Asosiy funksiyalar:**
• 🛍️ Mahsulotlarni ko'rish va sotib olish
• 🗂️ Kategoriyalar bo'yicha qidirish
• 🛒 Savatga mahsulot qo'shish
• 📦 Buyurtmalarni boshqarish
• ⚙️ Sozlamalarni o'zgartirish
• 📞 Biz bilan bog'lanish

🎯 **Qanday foydalanish:**
1. /start - Ishni boshlash
2. Asosiy menyudan kerakli bo'limni tanlang
3. Mahsulotlarni ko'ring va savatga qo'shing
4. Buyurtma berish uchun savatga o'ting

💡 **Maslahatlar:**
• Mahsulotlarni kategoriyalar bo'yicha qidiring
• Savatdagi mahsulotlar sonini nazorat qiling
• Buyurtma tarixingizni ko'rib turing
• Sozlamalarda tilni o'zgartirishingiz mumkin

📞 **Yordam kerakmi?**
"📞 Bog'lanish" bo'limidan biz bilan bog'laning!

Xarid qilishingiz bilan! 🛒✨
        """
    else:
        help_text = """
🤖 **О боте интернет-магазина**

Привет! Я ваш бот интернет-магазина. Через меня вы можете:

📋 **Основные функции:**
• 🛍️ Просмотр и покупка товаров
• 🗂️ Поиск по категориям
• 🛒 Добавление товаров в корзину
• 📦 Управление заказами
• ⚙️ Изменение настроек
• 📞 Связь с нами

🎯 **Как пользоваться:**
1. /start - Начать работу
2. Выберите нужный раздел из главного меню
3. Просматривайте товары и добавляйте в корзину
4. Перейдите в корзину для оформления заказа

💡 **Советы:**
• Ищите товары по категориям
• Следите за количеством товаров в корзине
• Просматривайте историю своих заказов
• Можете изменить язык в настройках

📞 **Нужна помощь?**
Свяжитесь с нами через раздел "📞 Связаться"!

Приятных покупок! 🛒✨
        """

    await message.answer(help_text, parse_mode="Markdown")