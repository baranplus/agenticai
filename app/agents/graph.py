from langgraph.graph import StateGraph, START, END

from .state import AgenticRAGState, SmartSQLPipelineState
from .query_validation_node import grade_query
from .generate_answer_node import generate_intial_answer, generate_null_answer, generate_answer_agentic_rag, generate_answer_smart_sql
from .extract_keywords_node import extract_keywords_initial
from .retriever_node import retrieve_documents
from .grade_document_node import grade_documents
from .return_docs_node import return_docs
from .sourcing_node import show_source
from .sql_node import execute_sql

def build_graph_agentic_rag_local_embedding():
    
    graph_builder = StateGraph(AgenticRAGState)

    graph_builder.add_node(grade_query)
    graph_builder.add_node(generate_intial_answer)
    graph_builder.add_node(generate_null_answer)
    graph_builder.add_node(generate_answer_agentic_rag)
    graph_builder.add_node(generate_answer_smart_sql)
    graph_builder.add_node(extract_keywords_initial)
    graph_builder.add_node(retrieve_documents)
    graph_builder.add_node(grade_documents)
    graph_builder.add_node(return_docs)
    graph_builder.add_node(show_source)

    # Either generate_intial_answer, extract_keywords_initial
    graph_builder.add_conditional_edges(START, grade_query)
    graph_builder.add_edge("generate_intial_answer", END)
    graph_builder.add_edge("extract_keywords_initial", "retrieve_documents")
    # Either extract_keywords, generate_null_answer, return_docs, generate_answer_agentic_rag
    graph_builder.add_conditional_edges("retrieve_documents", grade_documents)
    graph_builder.add_edge("generate_null_answer", END)
    graph_builder.add_edge("return_docs", END)
    graph_builder.add_edge("generate_answer_agentic_rag", "show_source")
    graph_builder.add_edge("show_source", END)

    graph = graph_builder.compile()
    
    return graph

def build_graph_smart_sql():

    graph_builder = StateGraph(SmartSQLPipelineState)

    graph_builder.add_node(execute_sql)
    graph_builder.add_node(generate_answer_smart_sql)

    graph_builder.add_edge(START, "execute_sql")
    graph_builder.add_edge("execute_sql", "generate_answer_smart_sql")
    graph_builder.add_edge("generate_answer_smart_sql", END)
    graph = graph_builder.compile()

    return graph
    