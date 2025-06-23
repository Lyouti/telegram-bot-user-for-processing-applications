from langchain_community.chat_models import ChatOllama
from decouple import config
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel
from typing import Optional, Any
import logging
import re

logger = logging.getLogger(__name__)

llm = ChatOllama(base_url=config("OLLAMA_HOST"), 
                model="herenickname/t-tech_T-lite-it-1.0:q4_k_m",
                temperature=0)

def parser_pydantic(obj):
    # костыль для преобразования модели pydantic в значение его поля
    return list(obj.dict().values())[0]
    
    
class Classification_application(BaseModel):
    classification: bool = Field(description="логическое значение является ли сообщение заявкой. True - если сообщение заявка и False - если не заявка.")

class Name(BaseModel):
    name: Optional[str] = Field(description="ФИО заявителя")

class Number_office(BaseModel):
    number_office: Optional[str] = Field(description="Трёхзначный номер кабинета")


def classification():
    parser = PydanticOutputParser(pydantic_object=Classification_application)

    prompt = PromptTemplate(
        template="Ты администратор в группе, где пишут заявки на помощь от системных администраторов. Ты должен распознать, является ли сообщение заявкой.  {format_instructions}.\nСообщение: {user_input}",
        input_variables=["user_input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser | parser_pydantic
    return chain

def collecting_name():

    parser = PydanticOutputParser(pydantic_object=Name)

    prompt = PromptTemplate(
        template="Ты администратор в группе, где пишут заявки на помощь от системных администраторов. Выдели имя заказчика из сообщения и выведи в таком формате: {format_instructions}.\n Сообщение: {user_input}\n",
        input_variables=["user_input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser | parser_pydantic
    return chain


def collecting_number_office():
    parser = PydanticOutputParser(pydantic_object=Number_office)

    prompt = PromptTemplate(
        template="Ты администратор в группе, где пишут заявки на помощь от системных администраторов. Выдели номер кабинета (например 220к - это кабинет 220) и ответь в таком формате: {format_instructions}.\n Сообщение: {user_input}\n",
        input_variables=["user_input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser | parser_pydantic
    return chain

def get_runnable_extraction_numbers():
    def extraction_numbers(text):
        # Извлекает номера телефонов (четырехзначные и десятизначные) из текста.

        # Паттерн для 4-значных номеров
        pattern_local_phone = r"\b\d{4}\b"

        # Паттерн для 10-значных номеров
        pattern_personal_phone = r"(?:\+7)?[\s\(]?\d{3}[\s\)]?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b"

        # Ищем все совпадения для обоих паттернов
        matches_local_phone = re.findall(pattern_local_phone, text)
        matches_personal_phone = re.findall(pattern_personal_phone, text)

        # Объединяем результаты
        matches = matches_local_phone + matches_personal_phone

        if not matches:
            matches = None
        return matches

    return RunnableLambda(extraction_numbers)

async def llm_response(message):
    
    result = {
        "user_input": message,
        "classification": None,
        "extracted_info": None
    }

    if not result["user_input"]:
        return result

    chain = RunnableParallel({
        "name": collecting_name(),
        "number_office": collecting_number_office(),
        "numbers_phone": get_runnable_extraction_numbers()
    })

    try:
        result["classification"] = await classification().ainvoke(message)
        if result["classification"]:
            result["extracted_info"] = await chain.ainvoke(message)
    except Exception: 
        logger.error("Error receiving a response from the language model 1")
    return result



