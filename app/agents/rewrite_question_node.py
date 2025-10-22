from .state import State
from llm import generation_model

from utils.logger import logger

REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
    "Try to change the query into a series of related keyword. \n"
    "Important : Don't answer in english and don't translate from persian to english first. \n"
    "Critical: The improved question should be written in persian (Farsi).\n"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Formulate an improved question:"
)

def rewrite_question(state: State):
    """Rewrite the original user question."""
    question = state["messages"][-2].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = generation_model.llm.invoke([{"role": "user", "content": prompt}])
    logger.info(response.content)
    return {"messages": [{"role": "user", "content": response.content}], "rewrite_count": state["rewrite_count"] + 1, "docs" : state["docs"], "sourcing" : state["sourcing"]}