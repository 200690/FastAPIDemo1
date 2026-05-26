from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

from agents.common.models import get_model
from agents.common.state import MultiAgentState

model = get_model()

def agent_1(state: MultiAgentState):
    last_content = state["messages"][-1].content if state["messages"] else ""
    response = model.invoke([
        HumanMessage(content=f"请分析用户问题的技术方面：{last_content}")
    ])
    return {"messages": [response]}

def agent_2(state: MultiAgentState):
    last_content = state["messages"][-1].content if state["messages"] else ""
    response = model.invoke([
        HumanMessage(content=f"请分析用户问题的业务方面：{last_content}")
    ])
    return {"messages": [response]}

def supervisor(state: MultiAgentState):
    tech_content = state["messages"][-2].content if len(state["messages"]) >= 2 else ""
    biz_content = state["messages"][-1].content if len(state["messages"]) >= 1 else ""
    response = model.invoke([
        HumanMessage(content=f"综合以下分析结果，给出最终回答：\n技术分析：{tech_content}\n业务分析：{biz_content}")
    ])
    return {"messages": [response]}

workflow = StateGraph(MultiAgentState)
workflow.add_node("agent_1", agent_1)
workflow.add_node("agent_2", agent_2)
workflow.add_node("supervisor", supervisor)

workflow.add_edge(START, "agent_1")
workflow.add_edge(START, "agent_2")
workflow.add_edge("agent_1", "supervisor")
workflow.add_edge("agent_2", "supervisor")
workflow.add_edge("supervisor", END)

app = workflow.compile()
