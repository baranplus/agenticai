from fastapi import Depends
from typing import Annotated
from db import (
    get_mongodb_manager,
    get_weaviate_client_manager,
    get_sql_manager,
    WeaviateClientManager,
    MongoDBManager,
    SQLDatabaseManager
)

from ai import get_llm, get_embedding, LLM, Embedding

WeaviateClientDependency = Annotated[WeaviateClientManager, Depends(get_weaviate_client_manager)]
MongoDBManagerDependency = Annotated[MongoDBManager, Depends(get_mongodb_manager)]
SQLDatabaseManagerDependency = Annotated[SQLDatabaseManager, Depends(get_sql_manager)]
LLMDependency = Annotated[LLM, Depends(get_llm)]
EmbeddingDependency = Annotated[Embedding, Depends(get_embedding)]
