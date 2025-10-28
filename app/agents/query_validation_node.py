import os
from typing import Literal

from .state import AgenticRAGState
from .helper_classes import safe_parse_grade
from llm import validation_llm

GRADE_PROMPT = (
    "You are a grador assessing relevance of a user question to following domains. \n "
    "Domains:\n\n"
    "شهرداری, شهرسازی ,  قوانین کشوری و شهری, قوانین شهرداری, ماده صد, ماده هشتاد, قوانین حقوقی, حقوق, قانون\n"
    "به طور کلی تمام موضوعات مربوط به قوانین و حقوقی کشور جمهوری اسلامی ایران و مخصوصا قوانین مرتبط با شهرداری و ایین نامه های مربوط به آن در خصوص شهرسازی پهنه های مجاز و .... رای گیری شکایات و ... موضوعات درست هستند\n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Answer only with one word: 'yes' or 'no', to indicate whether the document is relevant to the question."
)

def grade_query(state: AgenticRAGState) -> Literal["extract_keywords_initial", "generate_intial_answer"]:

    """Determine whether initial user query is releated to domain."""

    question = state["messages"][0].content

    prompt = GRADE_PROMPT.format(question=question)

    response = validation_llm.llm.invoke([{"role": "user", "content": prompt}])

    parsed_response = safe_parse_grade(response.content)

    score = parsed_response.binary_score
    if score == "yes":
        return "extract_keywords_initial"
    else:
        return "generate_intial_answer"