from .state import AgenticRAGState, SmartSQLPipelineState
from llm import final_response_llm, initial_response_llm

GENERATE_PROMPT_INITAL_RESPONSE = (
    "You are 'Baray', a smart intial response generator.\n"
    "\n"
    "CRITICAL LANGUAGE RULE: You MUST answer all user inquiries ONLY in Persian (Farsi).\n"
    "\n"
    "GREETING PROTOCOL:\n"
    "1. If the user starts the conversation with a greeting (e.g., 'سلام', 'درود', 'hi', 'hello'), you MUST respond with the EXACT Farsi phrase: 'به چت بات هوشمند حقوقی بارای خوش امدید.'\n"
    "2. If the user asks an irrelevant or non-legal question WITHOUT a prior greeting, respond with a polite and welcoming Farsi phrase that clearly redirects them to their main task. Use a variation of the welcome message, such as: 'سلام، من چت‌بات حقوقی هوشمند بارای هستم. لطفاً سؤال حقوقی خود را بپرسید تا راهنمایی‌تان کنم.' (This means: Hello, I am the Baray smart legal chatbot. Please ask your legal question so I can guide you.)\n"
    "\n"
    "MAIN TASK: ONLY GREETING AND REFUSING TO ANSWER BECAUSE THE USER QUERY ISN'T RELATE TO BARAY DOMAIN WHICH IS LEGAL MATTERS.\n"
    "Question: {question}"
)

GENERATE_PROMPT_AGENTIC_RAG = (
    "You are a data-based question answering assistant.\n"
    "You only base your answers on the data provided to you along with the question.\n"
    "You always refer to the specific origin of the information you need for each part of your answer.\n"
    "You are given a question and a set of snippets of texts to help you answer the question.\n"
    "The snippets are provided to you in the following format: 'Snippet <number> : <text>'. A '<end_of_snippet>' tag signals the end of a snippet.\n"
    "If you use information from a snippet to make a statement, your statement (the answer to question) should be followed by the snippet number in this format : **(<number>)**.\n"
    "For example, if your use 'Snippet 4' to answer a question, your answer should look like this : '<answer> **(4)**.\n"
    "If you combined multiple snippets (e.g 5 and 3) to answer a question, your answer should look like this : '<first statement> **(5)**, <second statement> **(3)**, ...'.\n"
    "If the information provided thorough Context isn't enough to answer, just say only the following failure message in persian : 'اطلاعات کافی برای پاسخ وجود ندارد'.\n"
    "Critical: The answer should be written in persian (Farsi) only and not in english."
    "Question: {question} \n"
    "Context: {context}"
)

GENERATE_PROMPT_SMART_SQL = (
    "You are a specialized question answering assistant that exclusively analyzes SQL query results.\n"
    "You only base your answers on the specific SQL data (rows and fields) provided to you along with the question.\n"
    "You are given a question and a set of data rows derived from SQL query results (rows or fields) to help you answer the question.\n"
    "If the information provided thorough Context isn't enough to answer, just say only the following failure message in persian : 'اطلاعات کافی برای پاسخ وجود ندارد'.\n"
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

def generate_answer_agentic_rag(state: AgenticRAGState):
    """Generate an answer."""
    question = state["messages"][0].content
    context, sourcing  = augment_context(state)
    prompt = GENERATE_PROMPT_AGENTIC_RAG.format(question=question, context=context)
    response = final_response_llm.llm.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response], "sourcing" : sourcing}

def generate_answer_smart_sql(state: SmartSQLPipelineState):
    """Generate an answer"""
    question = state["messages"][0].content
    context = state["messages"][-1].content
    prompt = GENERATE_PROMPT_SMART_SQL.format(question=question, context=context)
    respoonse = final_response_llm.llm.invoke([{"role": "user", "content": prompt}])
    return {"messages": [respoonse]}

def generate_intial_answer(state: AgenticRAGState):
    """Generate an initial answer."""
    question = state["messages"][0].content
    prompt = GENERATE_PROMPT_INITAL_RESPONSE.format(question=question)
    response = initial_response_llm.llm.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}

def generate_null_answer(state: AgenticRAGState):
    """Generate a null answer."""
    return {"messages": [{"role": "user", "content": ""}]}