from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from rag_bot.core.qdrant import qdrant_manager
from rag_bot.core.llm import generate_answer
import logging

logger = logging.getLogger(__name__)
router = Router(name="user_router")

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Задайте мне вопрос по базе знаний.")

@router.message(F.text & ~F.text.startswith("/"))
async def handle_rag_query(message: Message):
    query = message.text
    processing_msg = await message.answer("Ищу ответ...")

    try:
        # Search for context
        search_results = await qdrant_manager.search(query)

        if not search_results:
            context = ""
        else:
            context = "\n\n".join([res.get("text", "") for res in search_results if "text" in res])

        # Generate answer with LLM
        answer = await generate_answer(query, context)

        await processing_msg.edit_text(answer)

    except Exception as e:
        logger.error(f"Error handling query: {e}")
        await processing_msg.edit_text("Извините, произошла ошибка при формировании ответа.")
