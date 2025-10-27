from .state import AgenticRAGState
from llm import generation_model

from utils.logger import logger

REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
    "Try to change and expand the query into a series of related keyword. \n"
    "Keywords must be in singular form (not plural) and written only in Persian (Farsi).\n"
    "Each keyword should be at most have ten syllabus. \n"
    "Important : Don't answer in english and don't translate from persian to english first. \n"
    "The output must be a single string where keywords are separated by spaces — no punctuation or extra text.\n"
    "Critical: The improved question should be written in persian (Farsi).\n"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Final output (only keywords):"
)

def rewrite_question(state: AgenticRAGState):
    """Rewrite the original user question."""
    question = state["messages"][-2].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = generation_model.llm.invoke([{"role": "user", "content": prompt}])
    logger.info(response.content)
    return {"messages": [{"role": "user", "content": response.content}], "rewrite_count": state["rewrite_count"] + 1, "docs" : state["docs"], "sourcing" : state["sourcing"]}