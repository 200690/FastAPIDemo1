from typing import Literal
from langgraph.graph import StateGraph, START, END

from agents.common.models import get_model
from agents.common.tools import tools, tool_node
from agents.common.state import ToolCallState

model = get_model().bind_tools(tools)

def call_model(state: ToolCallState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: ToolCallState) -> Literal["tools", "__end__"]:
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return "__end__"

workflow = StateGraph(ToolCallState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", "__end__": END}
)
workflow.add_edge("tools", "agent")
workflow.add_edge(START, "agent")

app = workflow.compile()
