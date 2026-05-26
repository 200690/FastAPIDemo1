from fastapi import APIRouter, HTTPException, Query
from langchain_core.messages import HumanMessage, AIMessage

from agents import chat_app

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/basic")
async def basic_chat(message: str = Query("你好", description="用户输入的消息")):
    response = chat_app.invoke({"messages": [HumanMessage(content=message)]})
    return {"response": response["messages"][-1].content}
