from workflows.nodes.sql import execute_sql
from workflows.nodes.generate_answer import (
    generate_answer_smart_sql
)

from workflows.configs.load_config import load_workflow_config
from configs.env_configs import env_config

NODE_FUNCTIONS = {
    "execute_sql": execute_sql,
    "generate_answer_smart_sql": generate_answer_smart_sql,
}

CONDITION_FUNCTIONS = {}

SMART_SQL_WORKFLOW = load_workflow_config(
    config_path=env_config.smart_sql_workflow_config_path,
    node_functions=NODE_FUNCTIONS,
    condition_functions=CONDITION_FUNCTIONS,
)
