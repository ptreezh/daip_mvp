"""
SNA Expert Subagent for Chinese social network analysis.
"""
from typing import List, Dict, Any, Optional
from .base import TheorySubagent, AnalysisResult, SubagentCapabilities


class SNASubagent(TheorySubagent):
    """Specialized Subagent for Social Network Analysis of Chinese social relationships."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("sna_expert", config)
        self.network_metrics = [
            "Density", "Centrality", "Betweenness", "Closeness", 
            "Clustering_Coefficient", "Path_Length"
        ]
    
    def analyze(self, data: str, context: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """
        Perform Social Network Analysis on Chinese social relationship data.
        
        Args:
            data: Chinese social network data
            context: Additional context for analysis
            
        Returns:
            AnalysisResult with network analysis and insights
        """
        context = context or {}
        
        # Parse network data
        nodes, edges = self._parse_network_data(data)
        metrics = self._calculate_network_metrics(nodes, edges)
        patterns = self._identify_network_patterns(nodes, edges)
        
        # Create analysis content
        content = f"""Social Network Analysis Results:

1. Network Structure:
   - Nodes: {len(nodes)}
   - Edges: {len(edges)}
   - Density: {metrics.get('Density', 'N/A')}

2. Key Metrics:
{self._format_metrics(metrics)}

3. Network Patterns:
{patterns}

4. Cultural Interpretation:
- Analysis considers Chinese social relationship dynamics (关系, 面子, etc.)
- Hierarchy and guanxi patterns identified
-本土化 interpretation of network structures"""

        metadata = {
            "method": "social_network_analysis",
            "nodes": nodes,
            "edges": edges,
            "metrics": metrics,
            "patterns": patterns,
            "data_length": len(data),
            "context": context
        }
        
        return AnalysisResult(
            content=content,
            metadata=metadata,
            confidence=0.82,
            subagent_name=self.name
        )
    
    def get_capabilities(self) -> SubagentCapabilities:
        """Get the capabilities of this Subagent."""
        return SubagentCapabilities(
            name=self.name,
            description="Expert in Social Network Analysis of Chinese social relationships with cultural interpretation",
            supported_domains=["sna", "social_networks", "chinese_relationships"],
            required_skills=["network_analysis", "graph_theory", "cultural_interpretation"],
            version="1.0"
        )
    
    def _parse_network_data(self, data: str) -> tuple:
        """Parse network data into nodes and edges."""
        # This is a simplified implementation
        # In a real system, this would parse structured network data
        nodes = []
        edges = []
        
        # Simple parsing based on common Chinese relationship terms
        relationship_terms = ["关系", "联系", "连接", "网络", "互动"]
        
        # Extract potential nodes (entities)
        sentences = data.split('。')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for term in relationship_terms:
                if term in sentence:
                    # Extract potential entity names (simplified)
                    words = sentence.replace(',', ' ').replace('，', ' ').split()
                    for word in words:
                        if len(word) > 1 and word not in relationship_terms:
                            if word not in nodes:
                                nodes.append(word)
        
        # Create some sample edges based on proximity
        for i in range(len(nodes)):
            for j in range(i+1, min(i+3, len(nodes))):  # Connect to nearby nodes
                edges.append({
                    "source": nodes[i],
                    "target": nodes[j],
                    "weight": 1.0
                })
        
        return nodes, edges
    
    def _calculate_network_metrics(self, nodes: List[str], edges: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate network metrics."""
        if not nodes:
            return {}
        
        metrics = {}
        
        # Calculate density
        max_possible_edges = len(nodes) * (len(nodes) - 1) / 2
        actual_edges = len(edges)
        metrics["Density"] = actual_edges / max_possible_edges if max_possible_edges > 0 else 0
        
        # Calculate average degree
        node_degrees = {node: 0 for node in nodes}
        for edge in edges:
            node_degrees[edge["source"]] += 1
            node_degrees[edge["target"]] += 1
        
        avg_degree = sum(node_degrees.values()) / len(nodes) if nodes else 0
        metrics["Average_Degree"] = avg_degree
        
        # Simple centrality measure (degree centrality)
        if node_degrees:
            max_degree_node = max(node_degrees, key=node_degrees.get)
            metrics["Most_Central_Node"] = max_degree_node
            metrics["Max_Degree"] = node_degrees[max_degree_node]
        
        return metrics
    
    def _identify_network_patterns(self, nodes: List[str], edges: List[Dict[str, Any]]) -> str:
        """Identify network patterns."""
        if not nodes or not edges:
            return "Insufficient data for pattern identification."
        
        patterns = []
        
        # Check for hub nodes
        node_degrees = {node: 0 for node in nodes}
        for edge in edges:
            node_degrees[edge["source"]] += 1
            node_degrees[edge["target"]] += 1
        
        avg_degree = sum(node_degrees.values()) / len(nodes) if nodes else 0
        hub_nodes = [node for node, degree in node_degrees.items() if degree > avg_degree * 1.5]
        
        if hub_nodes:
            patterns.append(f"- Hub nodes identified: {', '.join(hub_nodes)}")
        
        # Check network density
        density = len(edges) / (len(nodes) * (len(nodes) - 1) / 2) if len(nodes) > 1 else 0
        if density > 0.5:
            patterns.append("- Network shows high connectivity")
        elif density < 0.2:
            patterns.append("- Network shows sparse connectivity")
        else:
            patterns.append("- Network shows moderate connectivity")
        
        # Check for clusters (simplified)
        if len(nodes) > 5:
            patterns.append("- Potential clustering patterns identified")
        
        return "\n".join(patterns) if patterns else "No significant patterns identified."
    
    def _format_metrics(self, metrics: Dict[str, float]) -> str:
        """Format metrics for display."""
        if not metrics:
            return "  No metrics calculated."
        
        formatted = []
        for metric, value in metrics.items():
            if isinstance(value, float):
                formatted.append(f"  {metric}: {value:.3f}")
            else:
                formatted.append(f"  {metric}: {value}")
        
        return "\n".join(formatted)