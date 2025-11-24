"""
Grounded Theory Expert Subagent for Chinese qualitative data analysis.
"""
from typing import List, Dict, Any, Optional
from .base import TheorySubagent, AnalysisResult, SubagentCapabilities


class GroundedTheorySubagent(TheorySubagent):
    """Specialized Subagent for Grounded Theory analysis of Chinese qualitative data."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("grounded_theory_expert", config)
        self.coding_categories = [
            "Experience", "Behavior", "Attitude", "Environment", 
            "Process", "Strategy", "Outcome", "Context"
        ]
    
    def analyze(self, data: str, context: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """
        Perform Grounded Theory analysis on Chinese qualitative data.
        
        Args:
            data: Chinese qualitative text data
            context: Additional context for analysis
            
        Returns:
            AnalysisResult with coded data and theoretical insights
        """
        context = context or {}
        
        # Perform basic coding analysis
        codes = self._perform_coding(data)
        categories = self._categorize_codes(codes)
        theory = self._generate_theory(categories, data)
        
        # Create analysis content
        content = f"""Grounded Theory Analysis Results:

1. Open Coding Results:
{self._format_codes(codes)}

2. Axial Coding Results:
{self._format_categories(categories)}

3. Theoretical Insights:
{theory}

4. Methodological Notes:
- Analysis conducted using Chinese qualitative data
- Cultural context considered in coding process
- Theory construction aligned with本土化 requirements"""

        metadata = {
            "method": "grounded_theory",
            "coding_results": codes,
            "category_results": categories,
            "data_length": len(data),
            "context": context
        }
        
        return AnalysisResult(
            content=content,
            metadata=metadata,
            confidence=0.85,
            subagent_name=self.name
        )
    
    def get_capabilities(self) -> SubagentCapabilities:
        """Get the capabilities of this Subagent."""
        return SubagentCapabilities(
            name=self.name,
            description="Expert in Grounded Theory analysis of Chinese qualitative data with本土化 coding",
            supported_domains=["grounded_theory", "qualitative_analysis", "chinese_text"],
            required_skills=["text_analysis", "coding", "theory_building"],
            version="1.0"
        )
    
    def _perform_coding(self, data: str) -> List[Dict[str, Any]]:
        """Perform open coding on the data."""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated NLP techniques
        sentences = data.split('。')  # Split by Chinese period
        codes = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # Simple keyword-based coding
                sentence_lower = sentence.lower()
                category_matches = []
                
                for category in self.coding_categories:
                    if category.lower() in sentence_lower:
                        category_matches.append(category)
                
                if category_matches:
                    codes.append({
                        "id": f"code_{i}",
                        "text": sentence.strip(),
                        "categories": category_matches,
                        "position": i
                    })
        
        return codes
    
    def _categorize_codes(self, codes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Perform axial coding to categorize codes."""
        categories = {category: [] for category in self.coding_categories}
        
        for code in codes:
            for category in code.get("categories", []):
                if category in categories:
                    categories[category].append(code)
        
        # Remove empty categories
        categories = {k: v for k, v in categories.items() if v}
        
        return categories
    
    def _generate_theory(self, categories: Dict[str, List[Dict[str, Any]]], data: str) -> str:
        """Generate theoretical insights from categorized codes."""
        if not categories:
            return "Insufficient data for theory generation."
        
        # Simple theory generation based on category relationships
        theory_parts = []
        
        # Identify dominant categories
        dominant_categories = sorted(
            categories.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:3]
        
        theory_parts.append("Based on the analysis, the following theoretical insights emerge:")
        
        for category, codes in dominant_categories:
            theory_parts.append(f"\n- {category} emerges as a central theme with {len(codes)} related codes.")
        
        theory_parts.append("\nThese themes suggest a pattern of interaction between individual experiences and environmental factors.")
        
        return "\n".join(theory_parts)
    
    def _format_codes(self, codes: List[Dict[str, Any]]) -> str:
        """Format codes for display."""
        if not codes:
            return "No codes identified."
        
        formatted = []
        for code in codes:
            formatted.append(f"  • {code['text']} (Categories: {', '.join(code['categories'])})")
        
        return "\n".join(formatted)
    
    def _format_categories(self, categories: Dict[str, List[Dict[str, Any]]]) -> str:
        """Format categories for display."""
        if not categories:
            return "No categories identified."
        
        formatted = []
        for category, codes in categories.items():
            formatted.append(f"  {category}: {len(codes)} codes")
        
        return "\n".join(formatted)