import os
from langchain_openai import ChatOpenAI

from utils.logger import logger

API_KEY = os.environ.get("API_KEY")
BASE_URL = os.environ.get("BASE_URL")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL")
GENERATION_MODEL = os.environ.get("GENERATION_MODEL")

class LLM:

    def __init__(self, temperature, model_name : str = GENERATION_MODEL):
        try:
            self.llm = ChatOpenAI(
                temperature=temperature,
                model_name=model_name,
                base_url=BASE_URL,
                api_key=API_KEY
            )
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise