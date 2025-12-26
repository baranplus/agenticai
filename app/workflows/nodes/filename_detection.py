from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage

from workflows.states import AgenticRAGState, AgenticRAGContextSchema
from ai.prompt_templates import FILENAME_DETECTION_PROMPT
from configs.env_configs import env_config
from utils.logger import logger

def detect_filename(state : AgenticRAGState, runtime : Runtime[AgenticRAGContextSchema]):

    if not runtime.context.use_file_filtering:
        logger.info("File filtering is disabled. Skipping filename detection.")
        return state

    question = state["messages"][-1].content
    available_filenames = runtime.context.mongodb_manager.get_unique_field_values(
        db_name=state["mongodb_dbname"],
        collection_name=state["mongodb_files_collection"],
        field_name="filename"
    )
    prompt = FILENAME_DETECTION_PROMPT.format(
        question=question,
        available_files="\n".join(f"{fid}: {fn}" for fid, fn in available_filenames.items())
    )

    response = runtime.context.llm.get_completions(
        model_name=env_config.generation_model,
        temperature=0.0,
        message=[{"role": "user", "content": prompt}]
    )

    file_ids = [fid.strip() for fid in response.content.split(",") if fid.strip() in available_filenames]
    selected_filenames = [available_filenames[fid] for fid in file_ids]
    logger.info(f"Filenames chosen by model: {selected_filenames}")
    return {"filtered_filenames" : selected_filenames}