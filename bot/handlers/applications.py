from aiogram import Router, F
from aiogram.types import Message
from language_model import llm
import logging
from handlers.templates_reply import templates

logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text | F.photo)
async def applications(message: Message):
    if message.content_type == "photo":
        text = message.caption
    else: text = message.text

    try:
        info_about_message = await llm.llm_response(text)
        logger.info(str(info_about_message))
    except Exception:
        logger.error("Error receiving a response from the language model")
        info_about_message = None

    if info_about_message and info_about_message["classification"]:
        if None in info_about_message["extracted_info"].values():
            await message.reply(templates["warning_reply"])
        else: await message.reply(templates["success_reply"])
        