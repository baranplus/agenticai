from .states import AgenticRAGState
from llm import final_response_llm

from utils.logger import logger

EXTRACT_KEYWORDS_INITIAL_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning. using examples\n"
    "Try to change and expand the query into a series of related keyword. \n"
    "Keywords must be in singular form (not plural) and written only in Persian (Farsi).\n"
    "Each keyword should be at most have ten syllabus. \n"
    "Important : Don't answer in english and don't translate from persian to english first. \n"
    "The output must be a single string where keywords are separated by commas — no punctuation or extra text.\n"
    "Critical: The improved keywords should be written in persian (Farsi).\n"
    "----------------------"
    "Examples:\n"
    "Question : در پهنای R121 حداکثر تراکم مجاز چقدر است؟\n"
    "Keywords: پهنا R121, پهنا ار ۱۲۱, پهنا ار صد و بیست و یک, حداکثر تراکم\n"
    "Question: متن کامل ماده 13 قوانین آیین نامه شهرداری تهران را بگو\n"
    "Keywords: آیین نامه ماده 13, آیین نامه ماده ۱۳, ماده سیزده, ماده 13 شهرداری تهران,\n"
    "-----------------------"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Final output (only keywords):"
)


EXTRACT_KEYWORDS_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning using examples.\n"
    "Try to change and expand the query into a series of related keyword. With the knowldge that the previous set of keywords didn't worked \n"
    "Keywords must be in singular form (not plural) and written only in Persian (Farsi).\n"
    "Each keyword should be at most have ten syllabus. \n"
    "Important : Don't answer in english and don't translate from persian to english first. \n"
    "The output must be a single string where keywords are separated by commas — no punctuation or extra text.\n"
    "Critical: The improved keywords should be written in persian (Farsi).\n"
    "----------------------"
    "Examples:\n"
    "Question : در پهنای R121 حداکثر تراکم مجاز چقدر است؟\n"
    "Keywords: پهنا R121, پهنا ار ۱۲۱, پهنا ار صد و بیست و یک, حداکثر تراکم\n"
    "Question: متن کامل ماده 13 قوانین آیین نامه شهرداری تهران را بگو\n"
    "Keywords: آیین نامه ماده 13, آیین نامه ماده ۱۳, ماده سیزده, ماده 13 شهرداری تهران,\n"
    "-----------------------"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Here is the previously extracted keywords:"
    "\n ------- \n"
    "{previous_keywords}"
    "\n ------- \n"
    "Final output (only keywords):"
)

def extract_keywords_initial(state: AgenticRAGState):
    """Rewrite the original user question."""
    question = state["messages"][0].content
    prompt = EXTRACT_KEYWORDS_INITIAL_PROMPT.format(question=question)
    response = final_response_llm.llm.invoke([{"role": "user", "content": prompt}])
    logger.info(response.content)
    return {
        "messages": [{"role": "user", "content": response.content}],
    }


def extract_keywords(state: AgenticRAGState):
    """Rewrite the original user question."""
    question = state["messages"][0].content
    previous_keywords = state["messages"][-2].content
    prompt = EXTRACT_KEYWORDS_PROMPT.format(question=question, previous_keywords=previous_keywords)
    response = final_response_llm.llm.invoke([{"role": "user", "content": prompt}])
    logger.info(response.content)
    return {
        "messages": [{"role": "user", "content": response.content}],
        "rewrite_count": state["rewrite_count"] + 1
    }