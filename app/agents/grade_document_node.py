import os
from typing import Literal

from .state import AgenticRAGState
from .helper_classes import safe_parse_grade
from llm import validation_llm

GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question. \n "
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Answer only with one word: 'yes' or 'no', to indicate whether the document is relevant to the question."
)

def grade_documents(state: AgenticRAGState) -> Literal["generate_answer_agentic_rag","generate_null_answer", "return_docs"]:

    """Determine whether the retrieved documents are relevant to the question."""

    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context)
    response = validation_llm.llm.invoke([{"role": "user", "content": prompt}])
    parsed_response = safe_parse_grade(response.content)
    score = parsed_response.binary_score

    if score == "yes" and state["return_docs"]:
        return "return_docs"
    if score == "yes" and not state["return_docs"]:
        return "generate_answer_agentic_rag"
    return "generate_null_answer"