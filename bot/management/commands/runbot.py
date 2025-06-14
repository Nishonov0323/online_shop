import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings
from django.core.management.base import BaseCommand
from bot.handlers import (
    get_start_router,
    get_categories_router,
    get_products_router,
    get_cart_router,
    get_orders_router,
    get_contact_router,
    get_settings_router
)
from bot.middlewares.authentication import AuthenticationMiddleware


class Command(BaseCommand):
    help = 'Run Telegram bot'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Starting bot...')
            asyncio.run(self.start_bot())
        except (KeyboardInterrupt, SystemExit):
            self.stdout.write('Bot stopped!')

    async def start_bot(self):
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        )

        # Initialize bot and dispatcher
        bot = Bot(token=settings.TELEGRAM_TOKEN, parse_mode="HTML")
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        # Register middlewares
        dp.update.outer_middleware(AuthenticationMiddleware())

        # Register routers
        dp.include_router(get_start_router())
        dp.include_router(get_categories_router())
        dp.include_router(get_products_router())
        dp.include_router(get_cart_router())
        dp.include_router(get_orders_router())
        dp.include_router(get_contact_router())
        dp.include_router(get_settings_router())


        # Start polling
        self.stdout.write('Bot started!')
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())