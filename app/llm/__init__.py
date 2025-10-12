from .model import LLM, Embeddings

embedding_func = Embeddings()
grader_model = LLM(temperature=0)
generation_model = LLM(temperature=0.3)