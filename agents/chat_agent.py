from langgraph.graph import StateGraph, MessagesState, START, END
from agents.common.models import get_model

model = get_model()

def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

app = workflow.compile()
