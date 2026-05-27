from fastapi import APIRouter, HTTPException, Query
from langchain_core.messages import HumanMessage, AIMessage

from agents.chat_agent import app

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/chat")
async def basic_chat(message: str = Query("你好", description="用户输入的消息")):
    message2 = "你是谁"
    config = {"configurable": {"thread_id": "my_thread_1"}}
    response = app.invoke({"messages": [HumanMessage(content=message2),
                                        HumanMessage(content=message)]},
                          config=config,
                          # stream_mode="updates"   会返回列表
                          )
    print(f"{response["messages"][-1].content}")
    response = app.invoke(
        {"messages": [HumanMessage(content="我刚才问了什么问题")]},
        config=config,
    )
    print("-------------------")
    print(f"{response["messages"][-1].content}")
    return {"response": response["messages"][-1].content}

