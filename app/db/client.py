import weaviate
from weaviate.client import WeaviateClient
from weaviate.classes.init import Auth
from pymongo import MongoClient

def get_weaviate_client(host : str, port : int, user_key : str) -> WeaviateClient:

    client = weaviate.connect_to_local(
        host=host,
        port=port,
        auth_credentials=Auth.api_key(user_key)
    )

    if not client.is_live():
        raise ConnectionError("Can't connect to an instance of weaviate database")

    return client

def get_mongodb_client(host : str, user : str, password : str, auth_db : str) -> MongoClient:

    client = MongoClient(
        host=host,
        username=user,
        password=password,
        authSource=auth_db
    )

    if not client.admin.command('ping').get("ok") == 1:
        raise ConnectionError("Can't connect to an instance of mongodb database")

    return client

