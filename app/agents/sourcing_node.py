import re
import urllib.parse
import os

from .state import AgenticRAGState

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
    
    filename_to_indices = {}
    for idx in integers:
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
    
    replaced_text = text
    for i, old_value in enumerate(matches):
        new_value = superscript_map[int(old_value)]
        replaced_text = replaced_text.replace(f" **({old_value})**", new_value, 1)
    
    superscript_to_old = {}
    for source_name, indices in filename_to_indices.items():
        first_idx = indices[0]
        superscript = superscript_map[first_idx]
        superscript_to_old[superscript] = first_idx
    
    return replaced_text, superscript_to_old

def show_source(state : AgenticRAGState):
    answer = state["messages"][-1].content
    sourcing = state["sourcing"]

    new_answer, source_matching = prettify_sources(answer, sourcing)
    has_sources = bool(source_matching)
    new_answer += "\n\nSources:\n"

    for superscript, integer in source_matching.items():
        src_meta = sourcing[integer]
        filename = src_meta["source"]
        encoded_filename = urllib.parse.quote(filename)
        download_url = f"{SOURCE_DOWNLOAD_API_PATH_BASE}/{encoded_filename}"
        download_link = f"[{filename}]({download_url})"
        new_answer += f"{superscript} {download_link}\n"

    return {
        "messages": [{"role" : "user", "content" : new_answer.strip()}], 
        "has_sources": has_sources
    }