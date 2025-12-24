import re
import urllib.parse
import os

from .states import AgenticRAGState
from utils.logger import logger

SOURCE_DOWNLOAD_API_PATH_BASE = os.environ.get('SOURCE_DOWNLOAD_API_PATH_BASE')

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

    # First remove invalid references
    replaced_text = text
    for match in matches:
        idx = int(match)
        if idx not in sourcing:
            replaced_text = replaced_text.replace(f" **({match})**", "", 1)
    
    filename_to_indices = {}
    for idx in valid_integers:
        source_name = sourcing[idx]["source"]
        if source_name not in filename_to_indices:
            filename_to_indices[source_name] = []
        filename_to_indices[source_name].append(idx)
    
    superscript_map = {}
    i = 0
    for source_name, indices in filename_to_indices.items():
        superscript = int_to_superscript(i + 1)
        for idx in indices:
            superscript_map[idx] = superscript
        i += 1
    
    for i, old_value in enumerate(valid_integers):
        new_value = superscript_map[int(old_value)]
        replaced_text = replaced_text.replace(f" **({old_value})**", new_value, 1)
    
    superscript_to_old = {}
    for source_name, indices in filename_to_indices.items():
        first_idx = indices[0]
        superscript = superscript_map[first_idx]
        superscript_to_old[superscript] = first_idx
    
    return replaced_text, superscript_to_old

def prettify_sources_new(text, sourcing):
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

    for superscript, integer in source_matching.items():
        src_meta = sourcing[integer]
        filename = src_meta["source"]
        file_id = src_meta.get("fileId")
        chunk_index = src_meta.get("chunk_index")
        encoded_filename = urllib.parse.quote(filename)
        download_url = f"{SOURCE_DOWNLOAD_API_PATH_BASE}/{mongodb_db}/{mongodb_collection}/{encoded_filename}/{file_id}/{chunk_index}"
        download_link = f"[{filename}]({download_url})"
        new_answer += f"{superscript} {download_link}\n"

    if has_sources:
        result = new_answer.strip()
    else:
        result = ""
    return result

def concatenate_answer_new(answer, sourcing, mongodb_db, mongodb_collection):
    new_answer, source_matching = prettify_sources_new(answer, sourcing)
    has_sources = bool(source_matching)
    new_answer += "\n\nSources:\n"

    # Sort by superscript order (¹, ², ³...) for clean output
    sorted_items = sorted(source_matching.items(), key=lambda x: superscript_to_int(x[0]))

    for superscript, idx in sorted_items:
        src_meta = sourcing[idx]
        filename = src_meta["source"]
        file_id = src_meta.get("fileId")
        chunk_index = src_meta.get("chunk_index", 0)
        encoded_filename = urllib.parse.quote(filename)
        download_url = f"{SOURCE_DOWNLOAD_API_PATH_BASE}/{mongodb_db}/{mongodb_collection}/{encoded_filename}/{file_id}/{chunk_index}"
        download_link = f"[{filename}]({download_url})"
        new_answer += f"{superscript} {download_link}\n"

    return new_answer.strip() if has_sources else ""

def show_source(state : AgenticRAGState):
    answer_vector = state["answers"][0].content
    sourcing_vector = state["sourcing"][0]

    answer_text = state["answers"][1].content
    sourcing_text = state["sourcing"][1]

    # source_collection = state["mongodb_source_collection"]
    source_collection = "pdf_pages"

    result_vector = concatenate_answer_new(answer_vector, sourcing_vector, state["mongodb_db"], source_collection)
    result_text = concatenate_answer_new(answer_text, sourcing_text, state["mongodb_db"], source_collection)

    return {"messages": [{"role" : "user", "content" : f"{result_vector}\n\n{result_text}"}]}