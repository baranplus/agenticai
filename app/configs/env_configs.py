import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '../..', '.env')

load_dotenv(env_path)

@dataclass
class Environment_Config:

    api_key : str
    base_url : str
    generation_model : str
    sql_generation_model : str
    embedding_url : str
    embedding_model : str
    weaviate_host : str
    weaviate_port : int
    weaviate_grpc_port : int
    weaviate_user_key : str
    hybrid_search_alpha : float
    mongodb_uri : str
    mongodb_initdb_dev_username : str
    mongodb_initdb_dev_password : str
    source_download_api_path_base : str
    sql_host : str
    sql_port : int
    sql_user : str
    sql_pass : str
    sql_db : str
    sql_metadata_cache_path : str
    sql_required_tables : List[str]
    sql_endpoint_enabled : bool

    @classmethod
    def initialize(cls) -> "Environment_Config":

        api_key = os.environ.get("API_KEY")
        base_url = os.environ.get("BASE_URL")
        generation_model = os.environ.get("GENERATION_MODEL")
        sql_generation_model = os.environ.get("SQL_GENERATION_MODEL")
        embedding_url = os.environ.get("EMBEDDING_URL")
        embedding_model = os.environ.get("EMBEDDING_MODEL")
        weaviate_host = os.environ.get("WEAVIATE_HOST")
        weaviate_port = int(os.environ.get("WEAVIATE_PORT"))
        weaviate_grpc_port = int(os.environ.get("WEAVIATE_GRPC_PORT"))
        weaviate_user_key = os.environ.get("WEAVIATE_USER_KEY")
        hybrid_search_alpha = float(os.environ.get("HYBRID_SEARCH_ALPHA"))
        mongodb_uri = os.environ.get("MONGODB_URI")
        mongodb_initdb_dev_username = os.environ.get("MONGODB_INITDB_DEV_USERNAME")
        mongodb_initdb_dev_password = os.environ.get("MONGODB_INITDB_DEV_PASSWORD")
        source_download_api_path_base = os.environ.get("SOURCE_DOWNLOAD_API_PATH_BASE")
        sql_host = os.environ.get("SQL_HOST")
        sql_port = int(os.environ.get("SQL_PORT"))
        sql_user = os.environ.get("SQL_USER")
        sql_pass = os.environ.get("SQL_PASS")
        sql_db = os.environ.get("SQL_DB")
        sql_metadata_cache_path = os.environ.get("SQL_METADATA_CACHE_PATH")
        sql_required_tables = [table.strip() for table in os.environ.get("SQL_REQUIRED_TABLES").split(",") if table.strip()]
        sql_endpoint_enabled = os.environ.get("SQL_ENDPOINT_ENABLED").lower() == "true"
        return cls(
            api_key = api_key,
            base_url = base_url,
            generation_model = generation_model,
            sql_generation_model = sql_generation_model,
            embedding_url = embedding_url,
            embedding_model = embedding_model,
            weaviate_host = weaviate_host,
            weaviate_port = weaviate_port,
            weaviate_grpc_port = weaviate_grpc_port,
            weaviate_user_key = weaviate_user_key,
            hybrid_search_alpha = hybrid_search_alpha,
            mongodb_uri = mongodb_uri,
            mongodb_initdb_dev_username = mongodb_initdb_dev_username,
            mongodb_initdb_dev_password = mongodb_initdb_dev_password,
            source_download_api_path_base = source_download_api_path_base,
            sql_host = sql_host,
            sql_port = sql_port,
            sql_user = sql_user,
            sql_pass = sql_pass,
            sql_db = sql_db,
            sql_metadata_cache_path = sql_metadata_cache_path,
            sql_required_tables = sql_required_tables,
            sql_endpoint_enabled = sql_endpoint_enabled
        )

env_config = Environment_Config.initialize()

