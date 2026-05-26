from fastapi import APIRouter, HTTPException, Query
from langchain_core.messages import HumanMessage, AIMessage

from agents import chat_app, tool_app, memory_app, human_app, advanced_app

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/basic")
async def basic_chat(message: str = Query("你好", description="用户输入的消息")):
    response = chat_app.invoke({"messages": [HumanMessage(content=message)]})
    return {"response": response["messages"][-1].content}


@router.get("/tool")
async def tool_chat(message: str = Query("北京的天气怎么样", description="需要工具处理的消息")):
    response = tool_app.invoke({"messages": [HumanMessage(content=message)]})
    return {"response": response["messages"][-1].content}


@router.get("/memory")
async def memory_chat(
    message: str = Query("你好", description="用户输入的消息"),
    thread_id: str = Query("default", description="对话线程ID，用于保持上下文")
):
    config = {"configurable": {"thread_id": thread_id}}
    response = memory_app.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )
    return {"response": response["messages"][-1].content, "thread_id": thread_id}


@router.get("/human")
async def human_chat(
    message: str = Query("北京的天气怎么样", description="用户输入的消息"),
    thread_id: str = Query("human_default", description="对话线程ID"),
    approve: bool = Query(True, description="是否批准工具调用")
):
    config = {"configurable": {"thread_id": thread_id}}

    try:
        current_state = human_app.get_state(config)
        has_interrupt = bool(
            current_state.tasks
            and any(t.interrupts for t in current_state.tasks)
        )
    except Exception:
        has_interrupt = False

    if has_interrupt:
        human_app.update_state(config, {"approved": approve})
        result = human_app.invoke(None, config=config)
        return {
            "response": result["messages"][-1].content,
            "thread_id": thread_id,
            "approved": approve
        }

    result = human_app.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )

    if result.get("messages") and isinstance(result["messages"][-1], AIMessage):
        last_msg = result["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            human_app.update_state(config, {"approved": approve})
            result = human_app.invoke(None, config=config)

    return {"response": result["messages"][-1].content, "thread_id": thread_id}


@router.get("/advanced")
async def advanced_chat(message: str = Query("如何搭建一个微服务架构", description="需要多方面分析的问题")):
    response = advanced_app.invoke({"messages": [HumanMessage(content=message)]})
    return {"response": response["messages"][-1].content}
