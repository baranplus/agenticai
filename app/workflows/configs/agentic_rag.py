from langgraph.graph import START, END

from workflows.graph import WorkflowConfig, ConditionalEdgeConfig
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

AGENTIC_RAG_WORKFLOW = WorkflowConfig(
    nodes={
        "extract_keywords": extract_keywords_initial,
        "detect_filename": detect_filename,
        "retrieve_documents_by_vector_search": retrieve_documents_by_vector_search,
        "retrieve_documents_by_fulltext_search": retrieve_documents_by_fulltext_search,
        "merge_after_retrieve": merge_after_retrieve,
        "return_docs": return_docs,
        "generate_answer_branching": generate_answer_branching,
        "generate_answer_agentic_rag_for_vector_search": generate_answer_agentic_rag_for_vector_search,
        "generate_answer_agentic_rag_for_fulltext_search": generate_answer_agentic_rag_for_fulltext_search,
        "show_source": show_source,
    },
    edges=[
        (START, "extract_keywords"),

        ("extract_keywords", "detect_filename"),
        ("detect_filename", "retrieve_documents_by_vector_search"),
        ("detect_filename", "retrieve_documents_by_fulltext_search"),

        ("retrieve_documents_by_vector_search", "merge_after_retrieve"),
        ("retrieve_documents_by_fulltext_search", "merge_after_retrieve"),

        ("return_docs", END),

        ("generate_answer_branching", "generate_answer_agentic_rag_for_vector_search"),
        ("generate_answer_branching", "generate_answer_agentic_rag_for_fulltext_search"),

        ("generate_answer_agentic_rag_for_vector_search", "show_source"),
        ("generate_answer_agentic_rag_for_fulltext_search", "show_source"),

        ("show_source", END),
    ],
    conditional_edges=[
        ConditionalEdgeConfig(
            source="merge_after_retrieve",
            condition_fn=return_docs_or_generate_answer,
            mapping={
                "return_docs": "return_docs",
                "generate_answer": "generate_answer_branching",
            },
        )
    ],
)
