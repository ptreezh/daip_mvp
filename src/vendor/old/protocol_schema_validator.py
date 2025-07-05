from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError, root_validator


class ProtocolNode(BaseModel):
    id: str
    name: str
    type: str
    role: Optional[str]
    next: Optional[list[str]] = []


class ProtocolEdge(BaseModel):
    from_: str = Field(..., alias="from")
    to: str


class ProtocolDAG(BaseModel):
    nodes: list[ProtocolNode]
    edges: list[ProtocolEdge]

    @root_validator(pre=True)
    def check_dag_acyclic(cls, values):
        # 检查DAG无环
        nodes = values.get("nodes", [])
        edges = values.get("edges", [])
        node_ids = {n["id"] if isinstance(n, dict) else n.id for n in nodes}
        graph = {nid: [] for nid in node_ids}
        for e in edges:
            from_id = e["from"] if isinstance(e, dict) else e.from_
            to_id = e["to"] if isinstance(e, dict) else e.to
            graph[from_id].append(to_id)
        visited = set()
        stack = set()

        def visit(nid):
            if nid in stack:
                raise ValueError(f"DAG contains a cycle at node {nid}")
            if nid in visited:
                return
            stack.add(nid)
            for succ in graph.get(nid, []):
                visit(succ)
            stack.remove(nid)
            visited.add(nid)

        for nid in node_ids:
            visit(nid)
        return values


def validate_protocol_dag(dag: dict[str, Any]):
    try:
        ProtocolDAG(**dag)
        return True, ""
    except ValidationError as e:
        return False, str(e)
    except ValueError as e:
        return False, str(e)
