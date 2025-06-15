from aiogram import Router, F
from aiogram.types import Message
from language_model import llm

router = Router()

@router.message(F.text)
async def applications(message: Message):
    info = llm.llm_response(message.text)
    text = "\n".join(f"{key}: {value}" for key, value in info.items())
    await message.answer(text)