from typing import TypedDict, Literal

from langchain_core.messages import BaseMessage, trim_messages, RemoveMessage
from langgraph.types import RetryPolicy
from pydantic import BaseModel,field_validator

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, END, add_messages, START

from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from typing_extensions import Annotated

load_dotenv()

# 状态,BaseModel数据验证模型，TypedDict类型提示字典
class PydanticState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_input: str
    agent_response: str
    tool_output: str
    tool_call: str
    mood: str

    # @field_validator("mood")
    # @classmethod
    # def validate_mood(cls, value):
    #     if value not in ["happy", "sad"]:
    #         raise ValueError("情绪状态异常")
    #     return value

# 私有状态
class ToolState(TypedDict):
    user_input: str
    agent_response: str
    tool_output: str

@tool
def search(content: str):
    """这是搜索工具"""
    return "搜索成功"

@tool
def buy(goods: str):
    """这是购买商品的工具"""
    return "购买成功"

tools = [search, buy]
tool_nodes = ToolNode(tools)

# 节点
# 对话节点
def chat_model(state):
    model = ChatOpenAI(model="deepseek-v4-flash", temperature=0).bind_tools(tools)
    message_history = state["messages"]
    if not model:
        raise Exception("模型初始化失败")
    trimmed_messages = trim_messages(
        message_history,
        max_tokens = 1000,
        strategy = "last",
        token_counter=len,
        allow_partial = False
    )
    llm_response = model.invoke(trimmed_messages)
    return {"messages": [llm_response]}

# 判断条件边
def should_turn(state) -> Literal["chat_model", "END"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "chat_model"
    return END

# 删除问候
def filter_message(state):
    message_history = state["messages"]
    message_remove = []
    for message in message_history:
        if message.content == "你好" or message.content == "hello":
            print(f"删除{message.content}")
            message_remove.append(RemoveMessage(id = message.id))
    return {"messages": message_remove}

# 工具解析节点（待）
def tool_node(state: ToolState) -> PydanticState:
    if state:
        return {"tool_call": '工具节点调用成功'}
    else:
        raise Exception("state为空")

workflow = StateGraph(PydanticState)

workflow.add_node(chat_model)
# workflow.add_node(tool_nodes)
workflow.add_node(filter_message)

workflow.add_edge(START, "filter_message")
workflow.add_edge("filter_message", "chat_model")
workflow.add_conditional_edges("chat_model", should_turn,
                               {
                                   "chat_model": "chat_model",  # 返回 "chat_model" 时去的节点
                                   END: END  # 返回 "END" 时结束
                               }
                               )


app = workflow.compile()
