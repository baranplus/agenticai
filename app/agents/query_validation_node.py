import os
from typing import Literal

from .state import AgenticRAGState
from .helper_classes import safe_parse_grade
from llm import validation_llm

GRADE_PROMPT = (
    "You are a grader responsible for evaluating whether a user question is relevant to the specified domains.\n\n"
    "Domains:\n"
    "شهرداری، شهرسازی، قوانین کشوری و شهری، قوانین شهرداری، ماده صد، ماده هشتاد، "
    "قوانین حقوقی، حقوق، قانون، کمیسیون‌های شهرداری، کمیسیون‌های مجلس، "
    "شوراهای اسلامی، مجلس، شکایت، وکالت، قضاوت، سازمان‌های جمهوری اسلامی، "
    "قوانین جمهوری اسلامی ایران و آیین‌نامه‌های مرتبط با آنها، "
    "قوانین شهرسازی شامل ضوابط مربوط به پارکینگ مغازه‌ها و ساختمان‌ها، "
    "پهنه‌بندی شهری، کاربری زمین و مقررات ساخت‌وساز.\n\n"
    "به طور کلی هر موضوعی که به قوانین و مقررات جمهوری اسلامی ایران مربوط باشد، "
    "به‌ویژه در زمینه‌های حقوقی، شهری، شهرداری، شهرسازی، ضوابط ساخت‌وساز، "
    "پهنه‌بندی، پارکینگ، آیین‌نامه‌ها، رأی‌گیری، شکایات، تعرفه‌های وکالت و قضاوت، "
    "پروانه‌های کسب و سایر موضوعات قانونی، مرتبط محسوب می‌شود.\n\n"
    "User question:\n"
    "{question}\n\n"
    "If the question contains keywords or conveys semantic meaning related to any of the above domains, "
    "respond with a single word:\n"
    "- 'yes' → if it is relevant\n"
    "- 'no' → if it is not relevant."
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