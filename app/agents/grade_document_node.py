import os
from pydantic import BaseModel, Field
from typing import Literal

from .state import State
from llm import grader_model

from utils.logger import logger

MAX_RETRY_NUMBER_FOR_AGENTS = int(os.environ.get("MAX_RETRY_NUMBER_FOR_AGENTS", 3 ))

GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question. \n "
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
)

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )

def grade_documents(state: State) -> Literal["generate_answer", "rewrite_question"]:

    """Determine whether the retrieved documents are relevant to the question."""

    if state["rewrite_count"] < MAX_RETRY_NUMBER_FOR_AGENTS:
        question = state["messages"][0].content
        context = state["messages"][-1].content

        prompt = GRADE_PROMPT.format(question=question, context=context)
        response = (
            grader_model.llm
            .with_structured_output(GradeDocuments).invoke(
                [{"role": "user", "content": prompt}]
            )
        )
        score = response.binary_score

        if score == "yes":
            return "generate_answer"
        else:
            return "rewrite_question"
    else:
        return "generate_answer"