import logging
import traceback
from aiogram import Router
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)
router = Router(name="errors_router")

@router.errors()
async def global_error_handler(event: ErrorEvent):
    logger.error("Critical error in update %s: %s", event.update.update_id, event.exception)
    logger.error(traceback.format_exc())

    # Try to notify user if possible
    if event.update.message:
        try:
            await event.update.message.answer("Произошла техническая ошибка. Мы уже работаем над ее устранением.")
        except Exception as e:
            logger.error("Failed to notify user about error: %s", e)
    elif event.update.callback_query:
        try:
            await event.update.callback_query.answer("Произошла техническая ошибка.", show_alert=True)
        except Exception as e:
            logger.error("Failed to notify user about error: %s", e)

    return True
