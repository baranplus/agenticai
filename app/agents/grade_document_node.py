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
    context_vector = state["messages"][-1].content[0]
    context_text = state["messages"][-1].content[1]

    prompt = GRADE_PROMPT.format(question=question, context=context_vector)
    response_vector = validation_llm.llm.invoke([{"role": "user", "content": prompt}])

    prompt = GRADE_PROMPT.format(question=question, context=context_text)
    response_text = validation_llm.llm.invoke([{"role": "user", "content": prompt}])

    parsed_response_vector = safe_parse_grade(response_vector.content)
    parsed_response_text = safe_parse_grade(response_text.content)

    score_vector = parsed_response_vector.binary_score
    score_text = parsed_response_text.binary_score

    from utils.logger import logger
    logger.info(f"Score Vetor : {score_vector} -------- Score Text : {score_text}")

    if (score_vector == "yes" or score_text == "yes") and state["return_docs"]:
        return "return_docs"
    if (score_vector == "yes" or score_text == "yes") and not state["return_docs"]:
        return "generate_answer_agentic_rag"
    return "generate_null_answer"