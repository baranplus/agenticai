import os

from .client import get_weaviate_client

WEAVIATE_HOST = os.environ.get("WEAVIATE_HOST")
WEAVIATE_PORT = os.environ.get("WEAVIATE_PORT")
WEAVIATE_USER_KEY = os.environ.get("WEAVIATE_USER_KEY")

weaviate_client = get_weaviate_client(WEAVIATE_HOST, WEAVIATE_PORT, WEAVIATE_USER_KEY)