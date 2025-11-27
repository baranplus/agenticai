from weaviate.client import WeaviateClient

def check_collection_existence(client : WeaviateClient, collection_name : str) -> bool:
    collection = client.collections.get(collection_name)
    return collection.exists()