from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def applications(message: Message):
    await message.answer("Ваша завака принята")