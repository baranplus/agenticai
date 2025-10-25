import os

from .client import get_weaviate_client, get_mongodb_client
from .collection import get_mongodb_db, get_mongodb_collection

WEAVIATE_HOST = os.environ.get("WEAVIATE_HOST")
WEAVIATE_PORT = os.environ.get("WEAVIATE_PORT")
WEAVIATE_USER_KEY = os.environ.get("WEAVIATE_USER_KEY")
MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME")
MONGODB_COLLECTION_SOURCE_FILES = os.environ.get("MONGODB_COLLECTION_SOURCE_FILES")
MONGO_INITDB_DEV_USERNAME = os.environ.get("MONGO_INITDB_DEV_USERNAME")
MONGO_INITDB_DEV_PASSWORD = os.environ.get("MONGO_INITDB_DEV_PASSWORD")

weaviate_client = get_weaviate_client(WEAVIATE_HOST, WEAVIATE_PORT, WEAVIATE_USER_KEY)
mongodb_client = get_mongodb_client(MONGODB_URI, MONGO_INITDB_DEV_USERNAME, MONGO_INITDB_DEV_PASSWORD, MONGODB_DB_NAME)
mongodb_db = get_mongodb_db(mongodb_client, MONGODB_DB_NAME)
mongodb_source_files_collection = get_mongodb_collection(mongodb_db, MONGODB_COLLECTION_SOURCE_FILES)