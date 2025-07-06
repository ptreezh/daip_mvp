# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-04 10:00:00
@Author  : DAIP-LIVE Team
@File    : sskg_manager.py
@Description:
    Manages the Semantic Structured Knowledge Graph (SSKG) with persistence.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import networkx as nx

logger = logging.getLogger(__name__)


class SSKGManager:
    """
    Manages the storage, retrieval, and querying of structured knowledge
    in a semantic graph, with persistence to a file.
    """

    def __init__(self, graph_path: Optional[Path] = None):
        """
        Initializes the SSKGManager.

        Args:
            graph_path (Optional[Path]): Path to the graph file for persistence.
                                         If the file exists, it will be loaded.
        """
        self.graph_path = graph_path
        self.graph = self._load_graph()
        logger.info(
            "SSKGManager initialized with %d nodes and %d edges.",
            self.graph.number_of_nodes(),
            self.graph.number_of_edges(),
        )

    def _load_graph(self) -> nx.MultiDiGraph:
        """Loads the graph from the specified path, or creates a new one."""
        if self.graph_path and self.graph_path.exists():
            try:
                logger.info(f"Loading knowledge graph from {self.graph_path}")
                # Load the graph from file. It might be loaded as a DiGraph if no
                # parallel edges were present. We must convert it to a MultiDiGraph
                # to ensure consistency with the query logic that expects edge keys.
                loaded_graph = nx.read_graphml(self.graph_path)
                return nx.MultiDiGraph(loaded_graph)
            except Exception as e:
                logger.error(f"Failed to load graph from {self.graph_path}: {e}. Creating new graph.")
        return nx.MultiDiGraph()

    def save_graph(self):
        """Saves the current graph to the specified path."""
        if self.graph_path:
            try:
                logger.info(f"Saving knowledge graph to {self.graph_path}")
                nx.write_graphml(self.graph, self.graph_path)
            except Exception as e:
                logger.error(f"Failed to save graph to {self.graph_path}: {e}")

    def add_fact(self, subject: str, predicate: str, obj: str, metadata: Optional[Dict[str, Any]] = None):
        """Adds a structured fact (a triple) to the knowledge graph."""
        self.graph.add_edge(subject, obj, key=predicate, **(metadata or {}))
        logger.debug("Added fact: (%s, %s, %s)", subject, predicate, obj)

    def query(self, subject: str, predicate: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries the graph for facts related to a subject."""
        results = []
        if self.graph.has_node(subject):
            for u, v, key, data in self.graph.out_edges(subject, data=True, keys=True):
                if predicate is None or key == predicate:
                    results.append({"subject": u, "predicate": key, "object": v, "metadata": data})
        return results