from langgraph.graph import StateGraph, START, END

from .state import State
from .retriever_node import retrieve_documents, retrieve_documents_use_weaviate_embedding
from .grade_document_node import grade_documents
from .rewrite_question_node import rewrite_question
from .generate_answer_node import generate_answer
from .sourcing_node import show_source


def build_graph():
    
    graph_builder = StateGraph(State)

    graph_builder.add_node(retrieve_documents)
    graph_builder.add_node(generate_answer)
    graph_builder.add_node(rewrite_question)
    graph_builder.add_node(show_source)

    graph_builder.add_edge(START, "retrieve_documents")
    graph_builder.add_conditional_edges("retrieve_documents", grade_documents)
    graph_builder.add_edge("rewrite_question", "retrieve_documents")
    graph_builder.add_edge("generate_answer", "show_source")
    graph_builder.add_edge("show_source", END)
    graph = graph_builder.compile()

    return graph

def build_graph_local_embedding():
    
    graph_builder = StateGraph(State)

    graph_builder.add_node(retrieve_documents_use_weaviate_embedding)
    graph_builder.add_node(generate_answer)
    graph_builder.add_node(rewrite_question)
    graph_builder.add_node(show_source)

    graph_builder.add_edge(START, "retrieve_documents_use_weaviate_embedding")
    graph_builder.add_conditional_edges("retrieve_documents_use_weaviate_embedding", grade_documents)
    graph_builder.add_edge("rewrite_question", "retrieve_documents_use_weaviate_embedding")
    graph_builder.add_edge("generate_answer", "show_source")
    graph_builder.add_edge("show_source", END)
    graph = graph_builder.compile()

    return graph