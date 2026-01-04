from .llm import LLM
from .embedding import Embedding
from .prompts import PromptRegistry
from configs.env_configs import env_config

llm = LLM(
    base_url=env_config.base_url,
    api_key=env_config.api_key
)

embedding_model = Embedding(
    url=env_config.embedding_url,
    api_key=env_config.api_key,
    model_name=env_config.embedding_model
)

prompt_registry = PromptRegistry(source=env_config.prompts_path)

def get_llm() -> LLM:
    """Dependency provider for FastAPI."""
    return llm

def get_embedding() -> Embedding:
    """Dependency provider for FastAPI."""
    return embedding_model

def get_prompt_registry() -> PromptRegistry:
    """Dependency provider for FastAPI."""
    return prompt_registry