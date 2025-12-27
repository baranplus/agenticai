from fastapi import Depends
from typing import Annotated
from langgraph.graph.state import CompiledStateGraph

from db import (
    get_mongodb_manager,
    get_weaviate_client_manager,
    get_sql_manager,
    WeaviateClientManager,
    MongoDBManager,
    SQLDatabaseManager
)

from ai import get_llm, get_embedding, LLM, Embedding
from workflows import get_agentic_rag_graph, get_smart_sql_graph

WeaviateClientDependency = Annotated[WeaviateClientManager, Depends(get_weaviate_client_manager)]
MongoDBManagerDependency = Annotated[MongoDBManager, Depends(get_mongodb_manager)]
SQLDatabaseManagerDependency = Annotated[SQLDatabaseManager, Depends(get_sql_manager)]
LLMDependency = Annotated[LLM, Depends(get_llm)]
EmbeddingDependency = Annotated[Embedding, Depends(get_embedding)]
AgenticRagDependency = Annotated[CompiledStateGraph, Depends(get_agentic_rag_graph)]
SmartRAGDependency = Annotated[CompiledStateGraph, Depends(get_smart_sql_graph)]
