import weaviate
from weaviate.client import WeaviateClient
from weaviate.classes.init import Auth

def get_weaviate_client(host : str, port : int, user_key : str) -> WeaviateClient:

    client = weaviate.connect_to_local(
        host=host,
        port=port,
        auth_credentials=Auth.api_key(user_key)
    )

    if not client.is_live():
        raise ConnectionError("Can't connect to an instance of weaviate database")

    return client