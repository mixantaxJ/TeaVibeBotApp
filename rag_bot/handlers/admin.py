from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from rag_bot.core.qdrant import qdrant_manager

router = Router(name="admin_router")

# Protect the whole router
router.message.filter(F.user_role == "admin")

@router.message(Command("add"))
async def add_to_knowledge_base_start(message: Message):
    await message.answer("Отправьте текст для добавления в базу знаний.")

@router.message(F.text & ~F.text.startswith("/"))
async def process_new_knowledge(message: Message):
    text = message.text
    try:
        await qdrant_manager.add_document(text, payload={"source": "telegram", "user_id": message.from_user.id})
        await message.answer("Успешно добавлено в базу знаний!")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении: {str(e)}")
