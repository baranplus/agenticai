from weaviate.client import WeaviateClient
from pymongo import MongoClient
from pymongo.database import Database as MongoDBDatabase
from pymongo.collection import Collection as MongoDBCollection

def check_collection_existence(client : WeaviateClient, collection_name : str) -> bool:
    collection = client.collections.get(collection_name)
    return collection.exists()

def get_mongodb_db(client : MongoClient, db_name : str) -> MongoDBDatabase:

    db_list = client.list_database_names()

    if db_name not in db_list:
        raise LookupError("Can't find the specified database in mongodb instance")
    
    db = client[db_name]

    return db

def get_mongodb_collection(db : MongoDBDatabase, collection_name : str) -> MongoDBCollection:

    collection_list = db.list_collection_names()

    if collection_name not in collection_list:
        raise LookupError("Can't find the specified collection in the mongodb database")
    
    collection = db[collection_name]

    return collection