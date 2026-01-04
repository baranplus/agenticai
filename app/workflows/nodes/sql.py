import re
from langchain_core.messages import SystemMessage
from langgraph.runtime import Runtime

from workflows.states import SmartSQLPipelineState, SmartSQLPipelineContextSchema
from utils.logger import logger
from configs.env_configs import env_config

from typing import Any

SQL_GENERATION_MAX_RETRIES = 2

def clean_sql(sql: str) -> str:
    # Remove Markdown code fences like ```sql ... ```
    return re.sub(r"^```(?:sql)?|```$", "", sql.strip(), flags=re.MULTILINE).strip()

def generate_sql(question: str, llm : Any, sql_manager : Any, prompt_registry : Any) -> str:
    """Generate SQL query from Persian question"""

    schema = sql_manager.get_combined_schema()
    prompt = prompt_registry.get("sql", "sql_query_generation", "v1").format(question=question, schema=schema)

    response = llm.invoke(
        model_name=env_config.sql_generation_model,
        temperature=0.0,
        message=[{"role": "user", "content": prompt}]
    )

    sql_query = response.content.strip()
    sql_query = clean_sql(sql_query)

    logger.info(f"================\n\n{sql_query}\n\n=================")
    
    return sql_query

def execute_sql(state: SmartSQLPipelineState, runtime : Runtime[SmartSQLPipelineContextSchema]) -> str:
    """Execute SQL to get information rows"""

    question = state["messages"][-1].content

    for _ in range(SQL_GENERATION_MAX_RETRIES):
        result = ""
        try:
            sql_query = generate_sql(question, runtime.context.llm, runtime.context.sql_manager, runtime.context.prompt_registry)
            extracted_data = runtime.context.sql_manager.execute_sql(sql_query)

            for row in extracted_data:
                for key in row.keys():
                    result += f"{key}: {row[key]}"
                result += "\n"
            break
        except Exception as e:
            logger.info(f"Sql error : {str(e)}")

    return {"messages": [SystemMessage(content=result)]}