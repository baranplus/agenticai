from .weaviate_client import WeaviateClientManager
from .sql_client import SQLDatabaseManager
from .mongodb_client import MongoDBManager
from .redis_client import RedisManager
from configs.env_configs import env_config

from utils.logger import logger

SQL_CONNECTION_URI = f"mssql+pyodbc://{env_config.sql_user}:{env_config.sql_pass}@{env_config.sql_host}:{env_config.sql_port}/{env_config.sql_db}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=no"

weaviate_client_manager = WeaviateClientManager(
    host=env_config.weaviate_host, 
    port=env_config.weaviate_port,
    grpc_port=env_config.weaviate_grpc_port, 
    user_key=env_config.weaviate_user_key,
    alpha=env_config.hybrid_search_alpha
)

mongodb_manager = MongoDBManager(
    host=env_config.mongodb_uri,
    user=env_config.mongodb_initdb_dev_username,
    password=env_config.mongodb_initdb_dev_password
)

if env_config.sql_endpoint_enabled:
    sql_manager = SQLDatabaseManager(
        connection_uri=SQL_CONNECTION_URI,
        required_tables=env_config.sql_required_tables,
        cache_path=env_config.sql_metadata_cache_path
    )

if env_config.redis_cache_enabled:
    redis_manager = RedisManager(
        host=env_config.redis_host,
        port=env_config.redis_port,
        db=env_config.redis_db,
        password=env_config.redis_password,
    )
else:
    redis_manager = None

logger.info(redis_manager.get_cache_stats())

def get_weaviate_client_manager() -> WeaviateClientManager:
    """Dependency provider for FastAPI."""
    return weaviate_client_manager

def get_mongodb_manager() -> MongoDBManager:
    """Dependency provider for FastAPI."""
    return mongodb_manager

def get_sql_manager() -> SQLDatabaseManager:
    """Dependency provider for FastAPI."""
    return sql_manager

def get_redis_manager() -> RedisManager:
    """Dependency provider for FastAPI."""
    if redis_manager is None:
        raise RuntimeError("Redis cache is not enabled. Set REDIS_CACHE_ENABLED=true to use it.")
    return redis_manager