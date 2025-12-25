from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage

from workflows.states import AgenticRAGState, AgenticRAGContextSchema
from ai.prompt_templates import EXTRACT_KEYWORDS_INITIAL_PROMPT, EXTRACT_KEYWORDS_PROMPT
from utils.logger import logger
from configs.env_configs import env_config

def extract_keywords_initial(state: AgenticRAGState, runtime : Runtime[AgenticRAGContextSchema]):
    """Rewrite the original user question."""
    question = state["messages"][0].content
    prompt = EXTRACT_KEYWORDS_INITIAL_PROMPT.format(question=question)
    response = runtime.context.llm.get_completions(
        model_name=env_config.generation_model,
        temperature=0.0,
        message=[{"role": "user", "content": prompt}]
    )
    return {"messages": [AIMessage(content=response.content)]}

def extract_keywords(state: AgenticRAGState, runtime : Runtime[AgenticRAGContextSchema]):
    """Rewrite the original user question."""
    question = state["messages"][0].content
    previous_keywords = state["messages"][-2].content
    prompt = EXTRACT_KEYWORDS_PROMPT.format(question=question, previous_keywords=previous_keywords)
    response = runtime.context.llm.get_completions(
        model_name=env_config.generation_model,
        temperature=0.0,
        message=[{"role": "user", "content": prompt}]
    )
    logger.info(response.content)
    return {
        "messages": [{"role": "user", "content": response.content}],
        "rewrite_count": state["rewrite_count"] + 1
    }