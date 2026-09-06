from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from rag_bot.config import settings

class AuthorizationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")

        if user:
            if user.id in settings.admin_ids:
                data["user_role"] = "admin"
            else:
                data["user_role"] = "user"
        else:
            data["user_role"] = "user"

        return await handler(event, data)
