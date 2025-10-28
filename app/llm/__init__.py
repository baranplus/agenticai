from .model import LLM, Embeddings

embedding_func = Embeddings()

validation_llm = LLM(temperature=0)
final_response_llm = LLM(temperature=0)
initial_response_llm = LLM(temperature=0.4)