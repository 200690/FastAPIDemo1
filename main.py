from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routers import chat

app = FastAPI(title="LangGraph实战 - 综合演示项目")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "message": "LangGraph实战 API",
        "endpoints": {
            "基础聊天": "/api/chat/basic?message=你好",
            "工具调用": "/api/chat/tool?message=北京的天气怎么样",
            "持久化记忆": "/api/chat/memory?message=我叫小明&thread_id=session_1",
            "人机审批": "/api/chat/human?message=计算2+3&approve=true",
            "多Agent协作": "/api/chat/advanced?message=如何搭建微服务",
        }
    }
