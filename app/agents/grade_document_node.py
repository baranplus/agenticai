import os
from pydantic import BaseModel, Field, ValidationError
from typing import Literal

from .state import AgenticRAGState
from llm import grader_model

MAX_RETRY_NUMBER_FOR_AGENTS = int(os.environ.get("MAX_RETRY_NUMBER_FOR_AGENTS", 3 ))

GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question. \n "
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Answer only with one word: 'yes' or 'no', to indicate whether the document is relevant to the question."
)

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )

def safe_parse_grade(response_text: str) -> GradeDocuments:
    try:
        
        return GradeDocuments.model_validate_json(response_text)
    except Exception:
        
        if "yes" in response_text.lower():
            return GradeDocuments(binary_score="yes")
        return GradeDocuments(binary_score="no")

def grade_documents(state: AgenticRAGState) -> Literal["generate_answer_agentic_rag", "rewrite_question"]:

    """Determine whether the retrieved documents are relevant to the question."""

    if state["rewrite_count"] < MAX_RETRY_NUMBER_FOR_AGENTS:
        question = state["messages"][0].content
        context = state["messages"][-1].content

        prompt = GRADE_PROMPT.format(question=question, context=context)
        response = grader_model.llm.invoke([{"role": "user", "content": prompt}])
        parsed_response = safe_parse_grade(response.content)
        score = parsed_response.binary_score
        if score == "yes":
            return "generate_answer_agentic_rag"
        else:
            return "rewrite_question"
    else:
        return "generate_answer_agentic_rag"