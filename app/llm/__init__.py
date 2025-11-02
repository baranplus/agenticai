import os
from .model import LLM, Embeddings

embedding_func = Embeddings()

SQL_GENERATION_MODEL = os.environ.get("SQL_GENERATION_MODEL")

validation_llm = LLM(temperature=0)
final_response_llm = LLM(temperature=0)
initial_response_llm = LLM(temperature=0.4)
sql_generation_llm = LLM(temperature=0, model_name=SQL_GENERATION_MODEL)