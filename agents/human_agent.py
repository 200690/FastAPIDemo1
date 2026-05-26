from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from agents.common.models import get_model
from agents.common.tools import tools, tool_node
from agents.common.state import ApprovalState

model = get_model().bind_tools(tools)

def call_model(state: ApprovalState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def need_approval(state: ApprovalState):
    last_msg = state["messages"][-1]
    if getattr(last_msg, "tool_calls", None):
        action = f"调用工具: {last_msg.tool_calls[0]['name']}"
        return {"pending_action": action, "approved": False}
    return {"pending_action": "", "approved": True}

def after_approval(state: ApprovalState):
    if not state["approved"]:
        return {"messages": [HumanMessage(content=f"[已拒绝] {state['pending_action']} 已被用户取消。")]}
    return state

def should_continue(state: ApprovalState) -> Literal["human_approval", "tools", "__end__"]:
    if state["pending_action"] and not state["approved"]:
        return "human_approval"
    if state["pending_action"] and state["approved"]:
        return "tools"
    return "__end__"

def after_approval_route(state: ApprovalState) -> Literal["tools", "__end__"]:
    if state["approved"]:
        return "tools"
    return "__end__"

workflow = StateGraph(ApprovalState)
workflow.add_node("agent", call_model)
workflow.add_node("check_approval", need_approval)
workflow.add_node("human_approval", after_approval)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_edge("agent", "check_approval")
workflow.add_conditional_edges(
    "check_approval",
    should_continue,
    {"human_approval": "human_approval", "tools": "tools", "__end__": END}
)
workflow.add_conditional_edges(
    "human_approval",
    after_approval_route,
    {"tools": "tools", "__end__": END}
)
workflow.add_edge("tools", "agent")

memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["human_approval"])
