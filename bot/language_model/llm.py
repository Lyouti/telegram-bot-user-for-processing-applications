from langchain_community.chat_models import ChatOllama
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, START, END
from typing import Optional, Any
import logging
import re

llm = ChatOllama(model="herenickname/t-tech_T-lite-it-1.0:q4_k_m", temperature=0)


class Classification_application(BaseModel):
    classification: bool = Field(description="логическое значение является ли сообщение заявкой. True - если сообщение заявка и False - если не заявка.")

class Name(BaseModel):
    name: Optional[str] = Field(description="ФИО заявителя")

class Number_office(BaseModel):
    number_office: Optional[str] = Field(description="Трёхзначный номер кабинета")

class State(BaseModel):
    user_input: str 
    classification: Optional[bool]
    extracted_info: Optional[dict[str, Any]]


def classification_node(state: State):
    parser = PydanticOutputParser(pydantic_object=Classification_application)

    prompt = PromptTemplate(
        template="Ты администратор в группе, где пишут заявки на помощь от системных администраторов. Ты должен распознать, является ли сообщение заявкой.  {format_instructions}.\nСообщение: {user_input}",
        input_variables=["user_input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    try: 
        classification_input = chain.invoke(state.user_input).classification
    except Exception:
        logging.error("Error in classificattion the user's message")
        classification_input = None

    return {"classification": classification_input}

def collecting_name_node(state: State):

    parser = PydanticOutputParser(pydantic_object=Name)

    prompt = PromptTemplate(
        template="Ты администратор в группе, где пишут заявки на помощь от системных администраторов. Выдели имя заказчика из сообщения и выведи в таком формате: {format_instructions}.\n Сообщение: {user_input}\n",
        input_variables=["user_input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    try: 
        name = chain.invoke(state.user_input).name
    except Exception:
        logging.error("Error in extracting information from the user's message")
        name = None

    result = {"name": name}
    return {"extracted_info": result}


def collecting_number_office_node(state: State):
    parser = PydanticOutputParser(pydantic_object=Number_office)

    prompt = PromptTemplate(
        template="Ты администратор в группе, где пишут заявки на помощь от системных администраторов. Выдели номер кабинета (например 220к - это кабинет 220) и ответь в таком формате: {format_instructions}.\n Сообщение: {user_input}\n",
        input_variables=["user_input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    try: 
        number_office = chain.invoke(state.user_input).number_office
    except Exception:
        logging.error("Error in extracting information from the user's message")
        number_office = None

    result = state.extracted_info
    result.update({"number_office": number_office})
    return {"extracted_info": result}

def collecting_numbers_phone_node(state: State):
    # Извлекает номера телефонов (четырехзначные и десятизначные) из текста.
    text = state.user_input
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
    
    result = state.extracted_info
    result.update({"numbers_phone": matches})
    return {"extracted_info": result}


def llm_response(message):
    workflow = StateGraph(State) 

    workflow.add_node("classification_node", classification_node)
    workflow.add_node("collecting_name_node", collecting_name_node)
    workflow.add_node("collecting_number_office_node", collecting_number_office_node)
    workflow.add_node("collecting_numbers_phone_node", collecting_numbers_phone_node)
    
    def route_classifcation_edge(state: State):
        if state.classification == False:
            return END
        else: return "collecting_name_node"

    workflow.add_edge(START, "classification_node")
    workflow.add_conditional_edges("classification_node", route_classifcation_edge)
    workflow.add_edge("collecting_name_node", "collecting_number_office_node")
    workflow.add_edge("collecting_number_office_node", "collecting_numbers_phone_node")
    workflow.add_edge("collecting_numbers_phone_node", END)

    app = workflow.compile()

    state_input = {"user_input": message, "classification": None, "extracted_info": None}
    result = app.invoke(state_input)
    return dict(result)



