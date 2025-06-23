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

    info_about_message = await llm.llm_response(text)
    logger.info(str(info_about_message))

    if info_about_message["classification"] and info_about_message["extracted_info"]:
        if None in info_about_message["extracted_info"].values():
            await message.reply(templates["warning_reply"])
        else: await message.reply(templates["success_reply"])
        