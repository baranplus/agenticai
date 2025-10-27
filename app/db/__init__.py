import os

from .client import get_weaviate_client, get_mongodb_client
from .collection import get_mongodb_db, get_mongodb_collection
from .sql_client import SQLDatabaseManager

WEAVIATE_HOST = os.environ.get("WEAVIATE_HOST")
WEAVIATE_PORT = os.environ.get("WEAVIATE_PORT")
WEAVIATE_USER_KEY = os.environ.get("WEAVIATE_USER_KEY")
MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME")
MONGODB_COLLECTION_SOURCE_FILES = os.environ.get("MONGODB_COLLECTION_SOURCE_FILES")
MONGO_INITDB_DEV_USERNAME = os.environ.get("MONGO_INITDB_DEV_USERNAME")
MONGO_INITDB_DEV_PASSWORD = os.environ.get("MONGO_INITDB_DEV_PASSWORD")
SQL_HOST = os.environ.get("SQL_HOST")
SQL_PORT = os.environ.get("SQL_PORT")
SQL_USER = os.environ.get("SQL_USER")
SQL_PASS = os.environ.get("SQL_PASS")
SQL_DB = os.environ.get("SQL_DB")
SQL_METADATA_CACHE_PATH = os.environ.get("SQL_METADATA_CACHE_PATH")
SQL_REQUIRED_TABLE = os.environ.get("SQL_REQUIRED_TABLE")

SQL_CONNECTION_URI = f"mssql+pyodbc://{SQL_USER}:{SQL_PASS}@{SQL_HOST}:{SQL_PORT}/{SQL_DB}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=no"

sql_required_tables = [table.strip() for table in SQL_REQUIRED_TABLE.split(",") if table.strip()]

weaviate_client = get_weaviate_client(WEAVIATE_HOST, WEAVIATE_PORT, WEAVIATE_USER_KEY)
mongodb_client = get_mongodb_client(MONGODB_URI, MONGO_INITDB_DEV_USERNAME, MONGO_INITDB_DEV_PASSWORD, MONGODB_DB_NAME)
mongodb_db = get_mongodb_db(mongodb_client, MONGODB_DB_NAME)
mongodb_source_files_collection = get_mongodb_collection(mongodb_db, MONGODB_COLLECTION_SOURCE_FILES)
sql_manager = SQLDatabaseManager(SQL_CONNECTION_URI, sql_required_tables, SQL_METADATA_CACHE_PATH)