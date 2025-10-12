import os
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate.vectorstores import WeaviateVectorStore
from weaviate.client import WeaviateClient

from utils.logger import logger

def get_weaviate_vector_store(client : WeaviateClient, collection_name: str, embedding_function : OpenAIEmbeddings):

    try:
        vector_store =  WeaviateVectorStore(
            client=client,
            index_name=collection_name,
            text_key="content",
            embedding=embedding_function
        )
    except Exception as e:
        logger.error(f"An error occurred while initializing the vector store: {e}")
        raise
    
    return vector_store
