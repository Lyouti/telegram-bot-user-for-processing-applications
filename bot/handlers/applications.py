from aiogram import Router, F
from aiogram.types import Message
from language_model import llm
import logging
from handlers.templates_reply import templates

router = Router()

@router.message(F.text)
async def applications(message: Message):

    try:
        info_about_message = llm.llm_response(message.text)
        logging.info(str(info_about_message))
    except Exception:
        logging.error("Error receiving a response from the language model")
        info_about_message = None

    if info_about_message and info_about_message["classification"]:
        if None in info_about_message["extracted_info"].values():
            await message.reply(templates["warning_reply"])
        else: await message.reply(templates["success_reply"])
        