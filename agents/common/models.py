from typing import Any, Dict, List, Optional, Sequence, Union, Type, Callable
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.tools import BaseTool
from langchain_core.runnables import Runnable
from pydantic import Field


class MockChatModel(BaseChatModel):
    model_name: str = Field(default="mock-model")
    bound_tools: List[Dict] = Field(default_factory=list)

    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], Type, Callable, BaseTool]],
        **kwargs: Any,
    ) -> Runnable:
        tool_defs = []
        for t in tools:
            if isinstance(t, BaseTool):
                tool_defs.append({"name": t.name, "description": t.description})
            elif isinstance(t, dict):
                tool_defs.append(t)
        self.bound_tools = tool_defs
        return self

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> ChatResult:
        last_msg = messages[-1] if messages else AIMessage(content="")
        last_content = last_msg.content if hasattr(last_msg, "content") else ""
        has_tools = bool(self.bound_tools) or bool(kwargs.get("tools", kwargs.get("functions", [])))

        if has_tools and not isinstance(last_msg, ToolMessage):
            if "天气" in last_content:
                return ChatResult(generations=[
                    ChatGeneration(message=AIMessage(
                        content="让我查询天气",
                        tool_calls=[{
                            "name": "get_weather",
                            "args": {"city": "北京"},
                            "id": "call_mock_001",
                            "type": "tool_call"
                        }]
                    ))
                ])
            if "计算" in last_content:
                expr = "2 + 3 * 4"
                return ChatResult(generations=[
                    ChatGeneration(message=AIMessage(
                        content="让我计算",
                        tool_calls=[{
                            "name": "calculator",
                            "args": {"expression": expr},
                            "id": "call_mock_002",
                            "type": "tool_call"
                        }]
                    ))
                ])
            if "搜索" in last_content:
                return ChatResult(generations=[
                    ChatGeneration(message=AIMessage(
                        content="让我搜索",
                        tool_calls=[{
                            "name": "search",
                            "args": {"query": last_content},
                            "id": "call_mock_003",
                            "type": "tool_call"
                        }]
                    ))
                ])

        if "技术" in last_content and "业务" in last_content:
            return ChatResult(generations=[
                ChatGeneration(message=AIMessage(
                    content="[综合分析] 从技术和业务两个维度来看：\n1. 技术方面需要选择合适的架构\n2. 业务方面需要明确需求边界\n---\n以上是对问题的综合分析。"
                ))
            ])

        return ChatResult(generations=[
            ChatGeneration(message=AIMessage(content=f"[模拟回复] 已收到：{last_content[:80]}"))
        ])

    @property
    def _llm_type(self) -> str:
        return "mock-chat-model"


def get_model(temperature: float = 0):
    return MockChatModel(model_name="mock-model")
