from typing import Any, Dict, List, Sequence, Literal
from langchain_core.messages import BaseMessage, ToolMessage, AIMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END


class ToolNode:
    tools: Dict[str, BaseTool]

    def __init__(self, tools: Sequence[BaseTool]):
        self.tools = {t.name: t for t in tools}

    def __call__(self, state: Dict[str, Any]) -> Dict[str, List[BaseMessage]]:
        messages = state["messages"]
        last_msg = messages[-1]

        if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
            return {"messages": []}

        results = []
        for tc in last_msg.tool_calls:
            tool_name = tc.get("name") if isinstance(tc, dict) else tc.name
            tool_args = tc.get("args") if isinstance(tc, dict) else tc.args
            tool_id = tc.get("id") if isinstance(tc, dict) else tc.id

            tool = self.tools.get(tool_name)
            if tool is None:
                output = f"错误：找不到工具 '{tool_name}'"
            else:
                try:
                    output = tool.invoke(tool_args)
                except Exception as e:
                    output = f"工具执行失败: {e}"

            results.append(ToolMessage(content=str(output), tool_call_id=tool_id))

        return {"messages": results}


def tools_condition(state: Dict[str, Any]) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    if messages and hasattr(messages[-1], "tool_calls") and messages[-1].tool_calls:
        return "tools"
    return "__end__"
