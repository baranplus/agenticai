import re
import urllib
from langchain_core.messages import SystemMessage
from workflows.states import AgenticRAGState, AgenticRAGContextSchema
from configs.env_configs import env_config

superscripts = "⁰¹²³⁴⁵⁶⁷⁸⁹"

def int_to_superscript(integer):
    return ''.join(superscripts[int(d)] for d in str(integer))

def superscript_to_int(superscript):
    return ''.join(str([c for c in superscripts].index(d)) for d in superscript)

def prettify_sources(text, sourcing):
    pattern = r"\*\*\((\d+)\)\*\*"
    matches = re.findall(pattern, text)
    integers = list(map(int, matches))
    valid_integers = [idx for idx in integers if idx in sourcing]

    # Remove invalid references
    replaced_text = text
    for match in matches:
        idx = int(match)
        if idx not in sourcing:
            replaced_text = replaced_text.replace(f" **({match})**", "", 1)

    # DO NOT deduplicate — keep original indices
    # Replace **(1)** with ¹, **(2)** with ², etc., one by one
    for idx in valid_integers:
        superscript = int_to_superscript(idx)  # idx starts from ? usually 1
        replaced_text = replaced_text.replace(f" **({idx})**", superscript, 1)

    # Return mapping: superscript → original index (for sourcing list)
    superscript_to_idx = {}
    for idx in valid_integers:
        superscript = int_to_superscript(idx)
        superscript_to_idx[superscript] = idx

    return replaced_text, superscript_to_idx

def concatenate_answer(answer, sourcing, mongodb_db, mongodb_collection):
    new_answer, source_matching = prettify_sources(answer, sourcing)
    has_sources = bool(source_matching)
    new_answer += "\n\nSources:\n"

    # Sort by superscript order (¹, ², ³...) for clean output
    sorted_items = sorted(source_matching.items(), key=lambda x: superscript_to_int(x[0]))

    for superscript, idx in sorted_items:
        src_meta = sourcing[idx]
        filename = src_meta["filename"]
        file_id = src_meta.get("fileId")
        chunk_index = src_meta.get("chunk_index", 0)
        encoded_filename = urllib.parse.quote(filename)
        download_url = f"{env_config.source_download_api_path_base}/{mongodb_db}/{mongodb_collection}/{encoded_filename}/{file_id}/{chunk_index}"
        download_link = f"[{filename}]({download_url})"
        new_answer += f"{superscript} {download_link}\n"

    return new_answer.strip() if has_sources else ""

def show_source(state : AgenticRAGState):

    for message in state["messages"]:
        if message.additional_kwargs.get("path") == "vector_search":
            answer_vector_search = message.content
        elif message.additional_kwargs.get("path") == "fulltext_search":
            answer_fulltext_search = message.content

    if answer_vector_search == None or answer_fulltext_search == None:
        raise ValueError("Answers Can't be of None value")

    sourcing_vector_search = state["sourcing_vector_search"]
    sourcing_fulltext_search = state["sourcing_full_text_search"]

    pdf_page_collection = state["mongodb_page_collection"]

    answer_string_vector_search = concatenate_answer(
        answer_vector_search, 
        sourcing_vector_search, 
        state["mongodb_dbname"], 
        pdf_page_collection
    )

    answer_string_fulltext_search = concatenate_answer(
        answer_fulltext_search, 
        sourcing_fulltext_search, 
        state["mongodb_dbname"], 
        pdf_page_collection
    )

    final_answer = f"{answer_string_vector_search}\n\n{answer_string_fulltext_search}"

    return {"messages": [SystemMessage(content=final_answer)]}