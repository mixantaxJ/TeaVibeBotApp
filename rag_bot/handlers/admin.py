from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from rag_bot.core.qdrant import qdrant_manager

router = Router(name="admin_router")

# Protect the whole router
router.message.filter(F.user_role == "admin")

class AdminStates(StatesGroup):
    waiting_for_knowledge = State()

@router.message(Command("add"))
async def add_to_knowledge_base_start(message: Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_knowledge)
    await message.answer("Отправьте текст для добавления в базу знаний. Для отмены используйте команду /cancel")

@router.message(Command("cancel"), StateFilter(AdminStates.waiting_for_knowledge))
async def cancel_add_knowledge(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добавление отменено.")

@router.message(F.text & ~F.text.startswith("/"), StateFilter(AdminStates.waiting_for_knowledge))
async def process_new_knowledge(message: Message, state: FSMContext):
    text = message.text
    try:
        await qdrant_manager.add_document(text, payload={"source": "telegram", "user_id": message.from_user.id})
        await message.answer("Успешно добавлено в базу знаний!")
        await state.clear()
    except Exception as e:
        await message.answer(f"Ошибка при добавлении: {str(e)}")
        await state.clear()
