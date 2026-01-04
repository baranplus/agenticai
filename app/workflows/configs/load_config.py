import yaml
from pathlib import Path
from langgraph.graph import START, END
from workflows.graph import WorkflowConfig, ConditionalEdgeConfig

from langgraph.graph import START, END

def load_workflow_config(
    config_path: str,
    node_functions: dict[str, callable],
    condition_functions: dict[str, callable],
) -> WorkflowConfig:
    config_data = yaml.safe_load(Path(config_path).read_text())

    nodes = {key: node_functions[value] for key, value in config_data["nodes"].items()}

    edges = []
    for edge in config_data["edges"]:
        src, dst = edge 
        src = START if src == "START" else src
        dst = END if dst == "END" else dst
        edges.append((src, dst))

    conditional_edges_data = config_data.get("conditional_edges", [])

    conditional_edges = []
    for edge in conditional_edges_data:
        condition_fn = condition_functions[edge["condition_fn"]]
        source = START if edge["source"] == "START" else edge["source"]
        conditional_edges.append(
            ConditionalEdgeConfig(
                source=source,
                condition_fn=condition_fn,
                mapping=edge["mapping"],
            )
        )

    return WorkflowConfig(
        nodes=nodes,
        edges=edges,
        conditional_edges=conditional_edges,
    )