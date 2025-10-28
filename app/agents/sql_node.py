import re

from .state import SmartSQLPipelineState
from db import sql_manager
from llm import validation_llm
from utils.logger import logger

PERSIAN_SQL_PROMPT = (
    "You are a SQL expert. Given an input question in Persian, first understand the intent,"
    "then create a SQL query in T-SQL format that answers the question.\n"
    "Schema information:\n"
    "{schema}\n"
    "Question in Persian: {question}\n\n"
    "Note: Use proper T-SQL syntax and consider Persian text encoding in filters.\n"
    "The query should be executable and include only the necessary columns.\n"
    "Do not include any explanations, only return the SQL query.\n\n"
    "SQL Query:"
)

def clean_sql(sql: str) -> str:
    # Remove Markdown code fences like ```sql ... ```
    return re.sub(r"^```(?:sql)?|```$", "", sql.strip(), flags=re.MULTILINE).strip()

def generate_sql(question: str) -> str:
    """Generate SQL query from Persian question"""

    schema = sql_manager.get_combined_schema()
    prompt = PERSIAN_SQL_PROMPT.format(question=question, schema=schema)

    response = validation_llm.llm.invoke([{"role": "user", "content": prompt}])

    sql_query = response.content.strip()
    sql_query = clean_sql(sql_query)

    logger.info(f"================\n\n{sql_query}\n\n=================")
    
    return sql_query

def execute_sql(state: SmartSQLPipelineState) -> str:
    """Execute SQL to get information rows"""

    question = state["messages"][-1].content
    sql_query = generate_sql(question)
    extracted_data = sql_manager.execute_sql(sql_query)

    result = ""

    for row in extracted_data:
        for key in row.keys():
            result += f"{key}: {row[key]}"
        result += "\n"

    return {"messages": [{"role": "user", "content": result}]}