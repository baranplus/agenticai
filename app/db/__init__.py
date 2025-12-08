import os

from .weaviate_client import WeaviateClientManager
from .sql_client import SQLDatabaseManager
from .mongodb_client import MongoDBManager

WEAVIATE_HOST = os.environ.get("WEAVIATE_HOST")
WEAVIATE_PORT = os.environ.get("WEAVIATE_PORT")
WEAVIATE_USER_KEY = os.environ.get("WEAVIATE_USER_KEY")
HYBRID_SEARCH_ALPHA = os.environ.get("HYBRID_SEARCH_ALPHA")
MONGODB_URI = os.environ.get("MONGODB_URI")
MONGO_INITDB_DEV_USERNAME = os.environ.get("MONGO_INITDB_DEV_USERNAME")
MONGO_INITDB_DEV_PASSWORD = os.environ.get("MONGO_INITDB_DEV_PASSWORD")
SQL_HOST = os.environ.get("SQL_HOST")
SQL_PORT = os.environ.get("SQL_PORT")
SQL_USER = os.environ.get("SQL_USER")
SQL_PASS = os.environ.get("SQL_PASS")
SQL_DB = os.environ.get("SQL_DB")
SQL_METADATA_CACHE_PATH = os.environ.get("SQL_METADATA_CACHE_PATH")
SQL_REQUIRED_TABLE = os.environ.get("SQL_REQUIRED_TABLE")

API_KEY = os.environ.get("API_KEY")
BASE_URL = os.environ.get("BASE_URL")

SQL_CONNECTION_URI = f"mssql+pyodbc://{SQL_USER}:{SQL_PASS}@{SQL_HOST}:{SQL_PORT}/{SQL_DB}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=no"

sql_required_tables = [table.strip() for table in SQL_REQUIRED_TABLE.split(",") if table.strip()]

headers = {"X-OpenAI-Api-Key": API_KEY, "X-OpenRouter-Api-Key": API_KEY, "X-OpenAI-Baseurl" : BASE_URL}
weaviate_client = WeaviateClientManager(WEAVIATE_HOST, WEAVIATE_PORT, WEAVIATE_USER_KEY, headers, HYBRID_SEARCH_ALPHA)
sql_manager = SQLDatabaseManager(SQL_CONNECTION_URI, sql_required_tables, SQL_METADATA_CACHE_PATH)
mongodb_manager = MongoDBManager(MONGODB_URI, MONGO_INITDB_DEV_USERNAME, MONGO_INITDB_DEV_PASSWORD)