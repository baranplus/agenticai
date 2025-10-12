import os

from .client import get_weaviate_client
from .vector_store import get_weaviate_vector_store
from llm import embedding_func

WEAVIATE_HOST = os.environ.get("WEAVIATE_HOST")
WEAVIATE_PORT = os.environ.get("WEAVIATE_PORT")
WEAVIATE_USER_KEY = os.environ.get("WEAVIATE_USER_KEY")
WEAVIATE_COLLECTION = os.environ.get("WEAVIATE_COLLECTION")

weaviate_client = get_weaviate_client(WEAVIATE_HOST, WEAVIATE_PORT, WEAVIATE_USER_KEY)
weaviate_vector_store = get_weaviate_vector_store(weaviate_client, WEAVIATE_COLLECTION, embedding_func.embeddings_model)