import os
from langchain_openai import ChatOpenAI

class LLM:

    def __init__(self, base_url : str, api_key : str):
        self.base_url = base_url
        self.api_key = api_key

    def _get_client(self, model_name : str, temperature : float) -> ChatOpenAI:
        client = ChatOpenAI(
            temperature=temperature,
            model_name=model_name,
            base_url=self.base_url,
            api_key=self.api_key
        )
        return client

    def get_completions(self, model_name: str, temperature : float):
        client = self._get_client(model_name, temperature)
        return None