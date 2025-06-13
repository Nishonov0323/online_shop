from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from asgiref.sync import sync_to_async

from django.conf import settings
from store.models import User


class AuthenticationMiddleware(BaseMiddleware):
    """
    Authentication middleware for Telegram bot
    """

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        # Update obyektidan to'g'ri event turini aniqlash
        user_id = None

        # Message event
        if event.message:
            user_id = event.message.from_user.id
        # CallbackQuery event
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
        # Inline query
        elif event.inline_query:
            user_id = event.inline_query.from_user.id
        # Pre-checkout query
        elif event.pre_checkout_query:
            user_id = event.pre_checkout_query.from_user.id
        # Shipping query
        elif event.shipping_query:
            user_id = event.shipping_query.from_user.id
        # Chat member update
        elif event.chat_member:
            user_id = event.chat_member.from_user.id
        elif event.my_chat_member:
            user_id = event.my_chat_member.from_user.id

        # Agar user_id topilmasa, handlerga o'tkizib yuborish
        if not user_id:
            return await handler(event, data)

        try:
            # Get user from database using sync_to_async
            user = await sync_to_async(User.objects.get)(telegram_id=user_id)

            # Add user to data dict to make it accessible in handlers
            data["user"] = user

        except User.DoesNotExist:
            # If user doesn't exist, we don't add anything to data dict
            # Registration will be handled by start handler
            pass

        # Call next handler
        return await handler(event, data)