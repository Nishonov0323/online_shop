from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from django.utils import translation


class LanguageMiddleware(BaseMiddleware):
    """Middleware for language selection"""

    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        user = data.get('user')

        if user:
            # Set language for this request
            translation.activate(user.language)

        result = await handler(event, data)

        # Reset language to default
        translation.deactivate()

        return result