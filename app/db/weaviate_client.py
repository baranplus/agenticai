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

    def create_collection(self, collection_name) -> Tuple[bool, str]:
        
        if self.check_collection_existence(collection_name):
            return (False, "Collection already exist in databse")
        try:
            self.client.collections.create(
                name=collection_name,
                description=f"A collection holding semantically similar documents about {collection_name}",
                vector_config=[
                    Configure.Vectors.text2vec_transformers(
                        name="content_vector",
                        source_properties=["content"]
                    ),
                    Configure.Vectors.text2vec_transformers(
                        name="keywords_vector",
                        source_properties=["keywords"]
                    )
                ],
                properties=[
                    Property(
                        name="content",
                        data_type=DataType.TEXT,
                        description="The textual content of the document"
                    ),
                    Property(
                        name="source",
                        data_type=DataType.TEXT,
                        description="The source file path or origin of the document"
                    ),
                    Property(
                        name="keywords",
                        data_type=DataType.TEXT_ARRAY,
                        description="Keywords extracted from textual content"
                    ),
                    Property(
                        name="chunk_index",
                        data_type=DataType.INT,
                        description="Relative position of the chunk"
                    ),
                    Property(
                        name="total_pages",
                        data_type=DataType.INT,
                        description="Total number of pages"
                    )
                ]
            )

            return (True, f"{collection_name} successfully created")
        except Exception as e:
            return (False, f"Can't create collection : {collection_name} due to {str(e)}")
        
    def fetch_all_records_in_collection(self, collection_name : str) -> List[Document]:
        collection = self.get_collection(collection_name)
        response = collection.query.fetch_objects()
        return self._processing_query_returns(response.objects)

    def fetch_records_by_source(self, collection_name : str, source_name : str) -> List[Document]:
        collection = self.get_collection(collection_name)
        response = collection.query.fetch_objects(filters=Filter.by_property("source").equal(source_name.strip()))
        return self._processing_query_returns(response.objects)
    
    async def index_chunks(self, collection_name : str, batch_size : int, chunks : List[Document]) -> None:

        collection = self.client.collections.get(collection_name)

        with collection.batch.fixed_size(batch_size=batch_size) as batch:
            
            for src_obj in tqdm(chunks):

                content = src_obj.page_content
                chunk_index = src_obj.metadata.get("chunk_index")
                source = src_obj.metadata.get("source")
                obj_uuid = deterministic_uuid(source, chunk_index, content)
                
                batch.add_object(
                    uuid=obj_uuid,
                    properties={
                        "content": content,
                        "source": source,
                        "keywords": src_obj.metadata.get("keywords", []),
                        "chunk_index": chunk_index,
                        "total_pages": src_obj.metadata.get("total_pages"),
                    },
                )
                if batch.number_errors > 10:
                    logger.error("Batch import stopped due to excessive errors.")
                    raise 
                
        failed_objects = collection.batch.failed_objects
        if failed_objects:
            logger.info(f"Number of failed imports: {len(failed_objects)}")
            logger.info(f"First failed object: {failed_objects[0]}")

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
        params["vector"] = openrouter_embedding_request(params["query"])
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


def deterministic_uuid(source, idx, text):
    hashval = hashlib.sha1(text.encode("utf-8")).hexdigest()
    key = f"{source}-{idx}-{hashval}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, key))

def openrouter_embedding_request(text: str):
    response = requests.post(
        url="https://openrouter.ai/api/v1/embeddings",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "openai/text-embedding-3-large",
            "input": text,
            "encoding_format": "float"
        })
    )

    response.raise_for_status()
    return response.json()["data"][0]["embedding"]

def avval_embedding_request(text: str):
    response = requests.post(
        url="https://api.avalai.ir/v1/embeddings",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "text-embedding-3-large",
            "input": text,
        })
    )

    response.raise_for_status()
    return response.json()["data"][0]["embedding"]