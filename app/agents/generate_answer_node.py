from .state import State
from llm import generation_model
from utils.logger import logger

GENERATE_PROMPT = (
    "You are a data-based question answering assistant.\n"
    "You only base your answers on the data provided to you along with the question.\n"
    "You always refer to the specific origin of the information you need for each part of your answer.\n"
    "You are given a question and a set of snippets of texts to help you answer the question.\n"
    "The snippets are provided to you in the following format: 'Snippet <number> : <text>'. A '<end_of_snippet>' tag signals the end of a snippet.\n"
    "If you use information from a snippet to make a statement, your statement (the answer to question) should be followed by the snippet number in this format : **(<number>)**.\n"
    "For example, if your use 'Snippet 4' to answer a question, your answer should look like this : '<answer> **(4)**.\n"
    "If you combined multiple snippets (e.g 5 and 3) to answer a question, your answer should look like this : '<first statement> **(5)**, <second statement> **(3)**, ...'.\n"
    "If you don't have enough information to answer, just say only the following failure message in persian : 'اطلاعات کافی برای پاسخ وجود ندارد'.\n"
    "Critical: The answer should be written in persian (Farsi) only and not in english."
    "Question: {question} \n"
    "Context: {context}"
)

def augment_context(input_dict):

    docs = input_dict["docs"]
    context = ""
    sourcing = {}

    for i, doc in enumerate(docs):
        sourcing[i+1] = {"text" : doc.page_content, **doc.metadata}
        context += f"Snippet {i+1} : {doc.page_content} <end_of_snippet>\n"
    return (context, sourcing)

def generate_answer(state: State):
    """Generate an answer."""
    question = state["messages"][-2].content
    context, sourcing  = augment_context(state)
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = generation_model.llm.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response], "rewrite_count" : state["rewrite_count"], "docs" : state["docs"], "sourcing" : sourcing}