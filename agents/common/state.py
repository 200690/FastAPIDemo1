from typing import TypedDict, Annotated, List, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class ToolCallState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


class ApprovalState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    pending_action: str
    approved: bool


class MultiAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    next: str
    team_members: List[str]
