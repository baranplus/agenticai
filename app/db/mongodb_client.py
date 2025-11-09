from io import BytesIO
from pymongo import MongoClient
from pymongo.database import Database as MongoDBDatabase
from pymongo.collection import Collection as MongoDBCollection
from typing import List, Dict, Any, Tuple

class MongoDBManager:

    """
    MongoDB database manager
    - Connect, manage and search mongodb 
    - Download files from db
    """

    def __init__(self, host : str, user : str, password : str, auth_db : str):

        self.client = MongoClient(
            host=host,
            username=user,
            password=password,
            authSource=auth_db
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
    
    def full_text_search(self, db_name : str, collection_name : str, query : str, top_k : int = 100) -> List[Dict[str, Any]]:
        collection = self.get_mongodb_collection(db_name, collection_name)
        cursor = collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(top_k)

        found_docs = []
        for doc in cursor:
            found_docs.append(doc)

        return found_docs
    
    def get_file_source(self, db_name : str, file_name : str, collection_name : str = "source_files") -> Tuple[str, BytesIO]:
        collection = self.get_mongodb_collection(db_name, collection_name)
        document = collection.find_one({"filename": file_name})
        if document is None:
            raise FileNotFoundError(f"File '{file_name}' not found.")

        content = document.get('content')

        if not content:
            raise FileNotFoundError(f"Content not found for file '{file_name}'")

        content_stream = BytesIO(content)
        file_size = str(document.get('file_size', 0))

        return (file_size, content_stream)