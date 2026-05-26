from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage

from agents.common.models import get_model

SYSTEM_PROMPT = "你是一个有帮助的AI助手。请用中文回答用户的问题。"

model = get_model()

def call_model(state: MessagesState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
