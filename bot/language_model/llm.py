from langchain_community.chat_models import ChatOllama
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, START, END
from typing import Optional, Any

llm = ChatOllama(model="herenickname/t-tech_T-lite-it-1.0:q4_k_m", temperature=0)

class Information_about_application(BaseModel):
    name: Optional[str] = Field(description="ФИО заявителя")
    number_phone: Optional[int] = Field(description="Номер телефона заявителя")
    number_office: Optional[int] = Field(description="Номер кабинета")
    description_application: Optional[str] = Field(description="Описание заявки на помощь системного администратора")

class Classification_application(BaseModel):
    classification: bool = Field(description="логическое значение является ли сообщение заявкой. True - если сообщение заявка и False - если не заявка.")

class State(BaseModel):
    user_input: str
    classification: Optional[bool] = None
    extracted_info: Optional[dict] = None
    missing_info: Optional[list[str]] = None

def classification_node(state: State):
    parser = PydanticOutputParser(pydantic_object=Classification_application)

    prompt = PromptTemplate(
        template="Ты администратор в группе, где пишут заявки на помощь от системных администраторов. Ты должен распознать, является ли сообщение заявкой.  {format_instructions}.\nСообщение: {user_input}",
        input_variables=["user_input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    classification_input = chain.invoke(state.user_input)
    return {"classification": classification_input.classification}

def collecting_information_node(state: State):

    parser = PydanticOutputParser(pydantic_object=Information_about_application)

    prompt = PromptTemplate(
        template="Выдели информацию из сообщения. {format_instructions}.\n Сообщение: {user_input}\n",
        input_variables=["user_input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    info = chain.invoke(state.user_input)
    return {"extracted_info": info.dict()}

def route_classifcation_edge(state: State):
    if state.classification == False:
        return END
    else: return "collecting_information_node"

def llm_response(message):
    workflow = StateGraph(State) 

    workflow.add_node("classification_node", classification_node)
    workflow.add_node("collecting_information_node", collecting_information_node)

    workflow.add_edge(START, "classification_node")
    workflow.add_conditional_edges("classification_node", route_classifcation_edge)
    workflow.add_edge("collecting_information_node", END)

    app = workflow.compile()

    state_input = {"user_input": message}
    result = app.invoke(state_input)
    return result