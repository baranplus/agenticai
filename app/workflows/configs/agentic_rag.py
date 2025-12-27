from langgraph.graph import START, END

from workflows.nodes.extract_keywords import extract_keywords_initial
from workflows.nodes.filename_detection import detect_filename
from workflows.nodes.retriever import retrieve_documents_by_vector_search, retrieve_documents_by_fulltext_search
from workflows.nodes.merge import merge_after_retrieve
from workflows.nodes.decision_point import return_docs_or_generate_answer
from workflows.nodes.return_docs import return_docs
from workflows.nodes.generate_answer import (
    generate_answer_branching,
    generate_answer_agentic_rag_for_vector_search,
    generate_answer_agentic_rag_for_fulltext_search
)
from workflows.nodes.sourcing import show_source

from workflows.configs.load_config import load_workflow_config
from configs.env_configs import env_config

NODE_FUNCTIONS = {
    "extract_keywords_initial": extract_keywords_initial,
    "detect_filename": detect_filename,
    "retrieve_documents_by_vector_search": retrieve_documents_by_vector_search,
    "retrieve_documents_by_fulltext_search": retrieve_documents_by_fulltext_search,
    "merge_after_retrieve": merge_after_retrieve,
    "return_docs": return_docs,
    "generate_answer_branching": generate_answer_branching,
    "generate_answer_agentic_rag_for_vector_search": generate_answer_agentic_rag_for_vector_search,
    "generate_answer_agentic_rag_for_fulltext_search": generate_answer_agentic_rag_for_fulltext_search,
    "show_source": show_source,
}

CONDITION_FUNCTIONS = {
    "return_docs_or_generate_answer": return_docs_or_generate_answer,
}

AGENTIC_RAG_WORKFLOW = load_workflow_config(
    config_path=env_config.agentic_rag_workflow_config_path,
    node_functions=NODE_FUNCTIONS,
    condition_functions=CONDITION_FUNCTIONS,
)
