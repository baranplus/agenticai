from langgraph.runtime import Runtime
from langchain.schema import Document
from langchain_core.messages import AIMessage
from typing import List, Tuple, Dict, Any

from workflows.states import (
    AgenticRAGState,
    AgenticRAGContextSchema, 
    SmartSQLPipelineState,
    SmartSQLPipelineContextSchema
)

from configs.env_configs import env_config
from utils.logger import logger

def augment_context(docs : List[Document]) -> Tuple[str, Dict[str, Any]]:

    context = ""
    sourcing = {}
    for i, doc in enumerate(docs):
        sourcing[i+1] = {"text" : doc.page_content, **doc.metadata}
        context += f"Snippet {i+1} : {doc.page_content} <end_of_snippet>\n"
    return (context, sourcing)

def generate_answer_agentic_rag_for_vector_search(
        state: AgenticRAGState, 
        runtime : Runtime[AgenticRAGContextSchema]
    ):
    """Generate an answer."""

    question = state["messages"][0].content
    docs =  state["vector_docs"]
    context, sourcing  = augment_context(docs)

    prompt = runtime.context.prompt_registry.get("generate_answer", "agentic_rag", "v1").format(question=question, context=context)

    response = runtime.context.llm.get_completions(
        model_name=env_config.generation_model,
        temperature=0.0,
        message=[{"role": "user", "content": prompt}]
    )

    answer = AIMessage(content=response.content, additional_kwargs={ "path" : "vector_search"})

    return {"messages": [answer], "sourcing_vector_search" : sourcing}

def generate_answer_agentic_rag_for_fulltext_search(
        state: AgenticRAGState, 
        runtime : Runtime[AgenticRAGContextSchema]
    ):
    """Generate an answer."""

    question = state["messages"][0].content
    docs =  state["full_text_docs"]
    context, sourcing  = augment_context(docs)

    prompt = runtime.context.prompt_registry.get("generate_answer", "agentic_rag", "v1").format(question=question, context=context)

    response = runtime.context.llm.get_completions(
        model_name=env_config.generation_model,
        temperature=0.0,
        message=[{"role": "user", "content": prompt}]
    )

    answer = AIMessage(content=response.content, additional_kwargs={ "path" : "fulltext_search"})

    return {"messages": [answer], "sourcing_full_text_search" : sourcing}

def generate_answer_smart_sql(
        state: SmartSQLPipelineState,
        runtime : Runtime[SmartSQLPipelineContextSchema]
    ):
    """Generate an answer"""
    question = state["messages"][0].content
    context = state["messages"][-1].content
    logger.info(f"------\n\n{context}\n\n------------")
    prompt = runtime.context.prompt_registry.get("generate_answer", "smart_sql", "v1").format(question=question, context=context)
    response = runtime.context.llm.get_completions(
        model_name=env_config.generation_model,
        temperature=0.0,
        message=[{"role": "user", "content": prompt}]
    )

    answer = AIMessage(content=response.content)

    return {"messages": [answer]}

def generate_answer_branching(state : AgenticRAGState, runtime : Runtime[AgenticRAGContextSchema]):
    return state