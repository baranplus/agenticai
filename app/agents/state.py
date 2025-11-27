from langchain.schema import Document
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict

class AgenticRAGState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    answers: list[BaseMessage]
    docs: list[Document]
    sourcing: dict
    rewrite_count: int
    collection_name: str
    top_k: int
    return_docs: bool
    mongodb_db : str
    mongodb_source_collection : str
    mongodb_text_collection : str

class SmartSQLPipelineState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]