import os
import requests
import json
import hashlib
import uuid
import weaviate
from weaviate.collections import Collection
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import Filter, MetadataQuery, BM25Operator
from weaviate.collections.classes.internal import Object as WeaviateObject
from langchain_core.documents import Document
from tqdm import tqdm
from typing import List, Tuple, Dict, Any

from utils.logger import logger

API_KEY = os.environ.get("API_KEY")
EMBEDDING_URL = os.environ.get("EMBEDDING_URL")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL")
class WeaviateClientManager:

    def __init__(self, host: str, port: str, grcp_port : str, user_key: str, alpha : float) -> None:

        self.client = weaviate.connect_to_local(
            host=host,
            port=port,
            grpc_port=grcp_port,
            auth_credentials=Auth.api_key(user_key),
        )
        self.alpha_hybrid_search = alpha

        if not self.client.is_live():
            raise ConnectionError("Can't connect to an instance of weaviate database")
        
    def check_collection_existence(self, collection_name : str) -> bool:
        collection = self.client.collections.get(collection_name)
        return collection.exists()
    
    def get_all_collections(self) -> List[str]:
        return self.client.collections.list_all()
    
    def get_collection(self, collection_name : str) -> Collection:
        return self.client.collections.get(collection_name)
    
    def delete_collection(self, collection_name : str) -> None:
        self.client.collections.delete(collection_name)
        
    def fetch_all_records_in_collection(self, collection_name : str) -> List[Document]:
        collection = self.get_collection(collection_name)
        response = collection.query.fetch_objects()
        return self._processing_query_returns(response.objects)

    def fetch_records_by_source(self, collection_name : str, source_name : str, filter_property : str = "filename") -> List[Document]:
        collection = self.get_collection(collection_name)
        response = collection.query.fetch_objects(filters=Filter.by_property(filter_property).equal(source_name.strip()))
        return self._processing_query_returns(response.objects)
    
    def query(self, collection_name : str, alpha : float, top_k : int, query : str) -> List[Document]:
        
        collection = self.get_collection(collection_name)

        response =  collection.query.hybrid(
            query=query, 
            limit=top_k,
            include_vector=False,
            alpha=alpha,
            return_metadata=MetadataQuery(score=True, explain_score=True),
            bm25_operator=BM25Operator.or_(minimum_match=2),
        )

        return self._processing_query_returns(response.objects)

    def query_params(self, collection_name : str, params : Dict[str, Any]) -> List[Document]:
        
        collection = self.get_collection(collection_name)

        params["return_metadata"] = MetadataQuery(score=True, explain_score=True)
        params["bm25_operator"] = BM25Operator.or_(minimum_match=2)
        response =  collection.query.hybrid(**params)

        return self._processing_query_returns(response.objects)
    
    def _processing_query_returns(self, query_objs : List[WeaviateObject]) -> List[Document]:
        """
        Converts a list of Weaviate Object instances into a list of LangChain Document objects.
        """
        langchain_docs = []

        for obj in query_objs:

            page_content = obj.properties.get("content", "")

            metadata = {}

            for key, value in obj.properties.items():
                if key != "content":
                    if key == "filename":
                        metadata["source"] = value
                    else:
                        metadata[key] = value

            metadata["weaviate_uuid"] = str(obj.uuid)

            if obj.metadata and obj.metadata.distance is not None:
                metadata["distance"] = obj.metadata.distance
            if obj.metadata and obj.metadata.score is not None:
                metadata["score"] = obj.metadata.score

            doc = Document(
                page_content=page_content,
                metadata=metadata
            )
            langchain_docs.append(doc)

        return langchain_docs

def embedding_request(text: str):
    response = requests.post(
        url=EMBEDDING_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": EMBEDDING_MODEL,
            "input": text,
        })
    )

    response.raise_for_status()
    return response.json()["data"][0]["embedding"]