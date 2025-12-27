import requests
import json
from typing import List

from utils.logger import logger

MAX_TIMEOUT_SECONDS = 120

class Embedding:

    def __init__(self, url : str, api_key : str, model_name : str):
        self.url = url
        self.api_key = api_key
        self.model_name = model_name
    
    def get_embeddings(self, text : str) -> List[float]:

        headers = {
            "Authorization" : f"Bearer {self.api_key}",
            "Content-Type" : "application/json"
        }

        payload = {
            "model" : self.model_name,
            "input" : text,
        }

        try:
            response = requests.post(url=self.url, headers=headers, data=json.dumps(payload), timeout=MAX_TIMEOUT_SECONDS)
            response.raise_for_status()

            if "error" in response.json():
                logger.info(response.json())

            return response.json()["data"][0]["embedding"]
        except Exception as e:
            raise e