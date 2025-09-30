from pydantic import BaseModel
from typing_extensions import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Literal
from langgraph.graph import StateGraph , START , END
from langchain_core.messages import SystemMessage , HumanMessage
from dotenv import load_dotenv
load_dotenv()

class State(TypedDict):
    user_message: str
    is_coding_question: bool
    ai_message: str


def detect_query(state: State):

    user_message = state.get("user_message")

    system_prompt = '''
        You are an AI assistant. Your job is to detect if the user's query is related
        to coding question or not.
        Return the response in specified JSON boolean only.
        '''
    
    model = ChatGoogleGenerativeAI(
        model = "gemini-2.5-flash",
        temperature = 1.3
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    response = model.invoke(messages)

    state["is_coding_question"] = response.content

    return state

def routing(state: State) -> Literal["solve_coding_question" , "solve_general_question"]:
    is_coding_question = state.get("is_coding_question")

    if(is_coding_question):
        return "solve_coding_question"
    else:
        return "solve_general_question"
    
def solve_coding_question(state: State):
    user_message = state.get("user_message")

    system_prompt = '''
    You are an AI assistant. Your job is to resolve the user query based on coding 
    problem he is facing

    '''

    model = ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            temperature = 1.3
        )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    response = model.invoke(messages)

    state["ai_message"] = response.content
    return state

def solve_general_question(state: State):

    user_message = state.get("user_message")

    system_prompt = '''
    You are an AI assistant. Your job is to chat with the user and anwer
    any kind of general queries he/she is having.

    '''

    model = ChatGoogleGenerativeAI(
        model = "gemini-2.5-flash",
        temperature = 1.3
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    response = model.invoke(messages)

    state["ai_message"] = response.content

    return state


graph_builder = StateGraph(State)

graph_builder.add_node("detect_query" , detect_query)
graph_builder.add_node("routing" , routing)
graph_builder.add_node("solve_coding_question" , solve_coding_question)
graph_builder.add_node("solve_general_question" , solve_general_question)


graph_builder.add_edge(START , "detect_query")
graph_builder.add_conditional_edges("detect_query" , routing)
graph_builder.add_edge("solve_coding_question" , END)
graph_builder.add_edge("solve_general_question" , END)

graph = graph_builder.compile()

def call_graph():
    user_message = input(">> ")
    state = {
        "user_message": user_message,
        "ai_message": "",
        "is_coding_question": False
    }
    
    result = graph.invoke(state)

    print("Final Result", result['ai_message'])

call_graph()


