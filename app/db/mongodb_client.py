import gridfs
import base64
from io import BytesIO
from pymongo import MongoClient
from pymongo.database import Database as MongoDBDatabase
from pymongo.collection import Collection as MongoDBCollection
from typing import List, Dict, Any, Tuple, Optional

class MongoDBManager:

    """
    MongoDB database manager
    - Connect, manage and search mongodb 
    - Download files from db
    """

    def __init__(self, host : str, user : str, password : str):

        self.client = MongoClient(
            host=host,
            username=user,
            password=password,
        )

        if not self.client.admin.command('ping').get("ok") == 1:
            raise ConnectionError("Can't connect to an instance of mongodb database")

    def get_mongodb_db(self, db_name : str) -> MongoDBDatabase:
        return self.client[db_name]

    def check_db_existence(self, db_name : str) -> bool:
        db_list = self.client.list_database_names()
        if db_name not in db_list:
            return False
        return True
        
    def get_mongodb_collection(self, db_name : str, collection_name : str) -> MongoDBCollection:
        db = self.get_mongodb_db(db_name)
        collection = db[collection_name]
        return collection
    
    def check_collection_existence(self, db_name : str, collection_name : str) -> bool:
        db = self.get_mongodb_db(db_name)
        collection_list = db.list_collection_names()
        if collection_name not in collection_list:
            return False
        return True
    
    def full_text_search(self, db_name : str, collection_name : str, query : str, source : Optional[str] = None, top_k : int = 100) -> List[Dict[str, Any]]:
        search_query = {"$text": {"$search": query}}
        if source:
            search_query["filename"] = source


        collection = self.get_mongodb_collection(db_name, collection_name)
        cursor = collection.find(
            search_query,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(top_k)

        found_docs = []
        for doc in cursor:
            found_docs.append(doc)

        return found_docs

    def full_text_search_new(self, db_name: str, collection_name: str, query: str, source: Optional[str] = None, top_k: int = 100) -> List[Dict[str, Any]]:
        
        search_query = {"$text": {"$search": query}}

        # NEW: match "source" instead of old "filename"
        if source:
            search_query["source"] = source

        collection = self.get_mongodb_collection(db_name, collection_name)

        cursor = collection.find(
            search_query,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(top_k)

        return list(cursor)
    
    def get_file_source(self, db_name: str, file_name: str, collection_name: str = "source_files") -> Tuple[str, BytesIO]:
        collection = self.get_mongodb_collection(db_name, collection_name)
        
        document = collection.find_one({"filename": file_name})
        if document is None:
            raise FileNotFoundError(f"File '{file_name}' not found.")

        file_id = document.get("gridfs_id")
        if not file_id:
            raise FileNotFoundError(f"GridFS ID missing for file '{file_name}'")

        # Open GridFS bucket
        db = self.get_mongodb_db(db_name)
        fs = gridfs.GridFS(db)

        try:
            grid_out = fs.get(file_id)
        except Exception:
            raise FileNotFoundError(f"File data not found in GridFS for '{file_name}'")

        file_bytes = grid_out.read()
        content_stream = BytesIO(file_bytes)

        # file_size = str(document.get("file_size", len(file_bytes)))
        file_size = str(len(file_bytes))

        return file_size, content_stream

    def get_file_source(self, db_name: str, filename: str, collection_name: str = "file_documents") -> Tuple[str, BytesIO]:

        collection = self.get_mongodb_collection(db_name, collection_name)

        # NEW SCHEMA: match file by its filename field
        document = collection.find_one({"filename": filename})
        if document is None:
            raise FileNotFoundError(f"File '{filename}' not found.")

        # NEW SCHEMA: originalBuffer contains BASE64 string
        base64_data = document.get("originalBuffer")
        if not base64_data:
            raise FileNotFoundError(f"No binary data found for '{filename}'")

        try:
            file_bytes = base64.b64decode(base64_data)
        except Exception:
            raise FileNotFoundError("originalBuffer is not valid base64")

        content_stream = BytesIO(file_bytes)

        file_size = str(len(file_bytes))

        return file_size, content_stream