from langchain.schema import Document
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict

class AgenticRAGState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    docs: list[Document]
    sourcing: dict
    rewrite_count: int
    collection_name: str
    top_k: int
    return_docs: bool

class SmartSQLPipelineState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]