import re
import urllib.parse
import os

from .state import State

SOURCE_DOWNLOAD_API_PATH_BASE = os.environ.get('SOURCE_DOWNLOAD_API_PATH_BASE')

superscripts = "⁰¹²³⁴⁵⁶⁷⁸⁹"

def int_to_superscript(integer):
    return ''.join(superscripts[int(d)] for d in str(integer))

def superscript_to_int(superscript):
    return ''.join(str([c for c in superscripts].index(d)) for d in superscript)

def prettify_sources(text):
    pattern = r"\*\*\((\d+)\)\*\*"
    matches = re.findall(pattern, text)
    integers = list(map(int, matches))
    superscript_map = {}
    seen = set()
    i = 0
    for integer in integers:
        if integer not in seen:
            superscript_map[integer] = int_to_superscript(i + 1)
            i += 1
            seen.add(integer)
    replaced_text = text
    for i, old_value in enumerate(matches):
        new_value = superscript_map[int(old_value)]
        replaced_text = replaced_text.replace(f" **({old_value})**", new_value, 1)
    
    superscript_to_old = {v: k for k, v in superscript_map.items()}
    
    return replaced_text, superscript_to_old

def show_source(state : State):
    answer = state["messages"][-1].content
    sourcing = state["sourcing"]

    new_answer, source_matching = prettify_sources(answer)
    new_answer += "\n\nSources:\n"

    for superscript, integer in source_matching.items():
        src_meta = sourcing[integer]
        filename = src_meta["source"]
        # Create a markdown link that opens in a new tab with full URL
        encoded_filename = urllib.parse.quote(filename)
        download_url = f"{SOURCE_DOWNLOAD_API_PATH_BASE}/{encoded_filename}"
        download_link = f"[{filename}]({download_url})"
        new_answer += f"{superscript} {download_link}\n"

    return {"messages": [{"role" : "user", "content" : new_answer.strip()}], "rewrite_count" : state["rewrite_count"], "docs" : state["docs"], "sourcing" : state["sourcing"]}