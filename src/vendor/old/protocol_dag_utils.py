import json
from typing import Optional

import ollama

from src.protocol_function_schema import protocol_step_extraction_schema
from src.tool_config import tool_config


def extract_protocol_steps_with_ollama(
    nl_input: str,
    model: Optional[str] = None,
    base_url: str = "http://localhost:11434",
):
    if model is None:
        model = tool_config.model.function_calling_model

    client = ollama.Client(host=base_url)
    messages = [
        {"role": "system", "content": "你是一个协议流程结构化助手。"},
        {"role": "user", "content": nl_input},
    ]
    response = client.chat(
        model=model,
        messages=messages,
        tools=[protocol_step_extraction_schema],
        stream=False,
    )
    tool_calls = response.get("message", {}).get("tool_calls", [])
    for call in tool_calls:
        if call.get("name") == "extract_protocol_steps":
            args = call.get("arguments", {})
            if isinstance(args, str):
                args = json.loads(args)
            return args.get("steps", [])
    return []


def build_protocol_dag(steps: list) -> dict:
    nodes = []
    edges = []
    name_to_id = {}
    for i, step in enumerate(steps):
        node_id = f"n{i+1}"
        name_to_id[step["name"]] = node_id
        nodes.append(
            {
                "id": node_id,
                "name": step["name"],
                "type": step.get("type", "auto"),
                "role": step.get("role", ""),
            },
        )
    for step in steps:
        from_id = name_to_id[step["name"]]
        for next_name in step.get("next", []):
            to_id = name_to_id.get(next_name)
            if to_id:
                edges.append({"from": from_id, "to": to_id})
    return {"nodes": nodes, "edges": edges}
