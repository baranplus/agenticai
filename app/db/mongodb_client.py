import gridfs
import base64
from io import BytesIO
from pymongo import MongoClient
from pymongo.database import Database as MongoDBDatabase
from pymongo.collection import Collection as MongoDBCollection
from typing import List, Dict, Any, Tuple, Optional, Set

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
    
    def get_all_records(self, db_name : str, collection_name : str) -> List[Dict[str, any]]:
        collection = self.get_mongodb_collection(db_name, collection_name)
        cursor = collection.find()
        found_docs = [doc for doc in cursor]
        return found_docs

    def get_record(self, db_name : str, collection_name : str, search_record : Dict[str, Any]) -> Dict[str, any]:
        collection = self.get_mongodb_collection(db_name, collection_name)
        record = collection.find_one(search_record)
        return record
    
    def full_text_search(
            self, 
            db_name : str, 
            collection_name : str, 
            query : str, 
            source : Optional[str] = None, 
            top_k : int = 100
        ) -> List[Dict[str, Any]]:

        search_query = {"$text": {"$search": query}}

        if source:
            search_query["filename"] = source

        collection = self.get_mongodb_collection(db_name, collection_name)
        cursor = collection.find(
            search_query,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(top_k)

        return list(cursor)

    def get_file_from_gridfs_by_filename(self, db_name: str, collection : str, file_name: str, gridfs_collection : str = "files") -> Tuple[str, str, BytesIO]:

        db = self.get_mongodb_db(db_name)
        collection = self.get_mongodb_collection(db_name, collection)

        file_doc = collection.find_one({"filename" : file_name})

        if file_doc is None:
            raise FileNotFoundError(f"GridFS file '{file_name}' not found in fs.files")

        file_id = file_doc["_id"]
        filename = file_doc["filename"]

        fs = gridfs.GridFS(db, collection=gridfs_collection)

        try:
            grid_out = fs.get(file_id)
        except Exception:
            raise FileNotFoundError(f"Failed to read GridFS file '{file_name}'")

        file_bytes = grid_out.read()
        content_stream = BytesIO(file_bytes)

        file_size = str(file_doc.get("length", len(file_bytes)))

        return file_size, filename, content_stream

    def get_file_from_collection(
        self, 
        db_name: str,
        collection_name: str,
        search_record : Dict[str, Any],
        buffer_field: str = "originalBuffer"
    ) -> Tuple[str, BytesIO]:

        collection = self.get_mongodb_collection(db_name, collection_name)

        document = collection.find_one(search_record)
        if document is None:
            raise FileNotFoundError(f"File '{search_record}' not found.")

        base64_data = document.get(buffer_field)
        if not base64_data:
            raise FileNotFoundError(f"No binary data found for '{search_record}'")

        try:
            file_bytes = base64.b64decode(base64_data)
        except Exception:
            raise FileNotFoundError("originalBuffer is not valid base64")

        content_stream = BytesIO(file_bytes)

        file_size = str(len(file_bytes))

        return file_size, content_stream

    def get_unique_field_values(self, db_name: str, collection_name: str, field_name: str) -> Set[Any]:

        collection = self.get_mongodb_collection(db_name, collection_name)

        match_filter: Dict[str, Any] = {
            field_name: {"$exists": True, "$nin": [None, ""]}
        }

        pipeline = [
            {"$match": match_filter},
            {"$group": {
                "_id": None,
                "values": {"$addToSet": f"${field_name}"}
            }},
            {"$project": {"_id": 0, "values": 1}}
        ]

        result = list(collection.aggregate(pipeline))

        if not result:
            return set()

        return set(result[0].get("values", []))