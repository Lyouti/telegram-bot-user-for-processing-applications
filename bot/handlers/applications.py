from aiogram import Router, F
from aiogram.types import Message
from language_model import llm
import logging

router = Router()

@router.message(F.text)
async def applications(message: Message):
    info_about_message = llm.llm_response(message.text)

    try:
        info_about_message = llm.llm_response(message.text)
        logging.info(str(info_about_message))
    except Exception:
        logging.error("Error receiving a response from the language model")
        info_about_message = None

    if info_about_message is not None:
        if info_about_message["classification"] == True:
            if None in info_about_message["extracted_info"].values():
                await message.reply(
                    '''Ваша заявка откланена.Все заявки, направляемые в данный чат, обязаны соответствовать установленному регламенту. Несоблюдение требований приведёт к игнорированию обращения до момента корректного оформления.

                        Регламент оформления заявки:
                        1. Кабинет / отдел – точное местоположение инцидента.
                        2. ФИО сотрудника – полностью: фамилия, имя, отчество.
                        3. Контактный номер телефона – мобильный или внутренний.
                        4. Подробное описание проблемы – укажите:
                            – что именно не работает;
                            – когда и при каких условиях появилась проблема;
                            – что уже было предпринято для её устранения.''')
            else: await message.reply("Ваша заявка принята!")
        