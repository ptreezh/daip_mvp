# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 18:00:00
@Author  : DAIP-LIVE Team
@File    : result_formatter.py
@Description:
    Result formatting for different output formats.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree


class ResultFormatter:
    """Format workflow results for different output types."""
    
    def __init__(self):
        """Initialize the result formatter."""
        pass
    
    def format_as_json(self, result: Dict[str, Any], indent: int = 2) -> str:
        """Format result as JSON string."""
        return json.dumps(result, indent=indent, ensure_ascii=False, default=str)
    
    def format_as_markdown(self, result: Dict[str, Any]) -> str:
        """Format result as Markdown string."""
        if not result.get("success", False):
            return f"# Workflow Failed\n\n**Error:** {result.get('error', 'Unknown error')}\n"
        
        # Determine workflow type
        if "synthesis" in result and "perspectives" in result:
            return self._format_multi_perspective_markdown(result)
        elif "revised_content" in result or "original_content" in result:
            return self._format_critical_review_markdown(result)
        else:
            return self._format_generic_markdown(result)
    
    def display_critical_review_result(self, result: Dict[str, Any], console: Console) -> None:
        """Display Critical Review Workflow result using Rich."""
        if not result.get("success", False):
            console.print(Panel(
                f"[red]Workflow Failed[/red]\n\n{result.get('error', 'Unknown error')}",
                title="Error",
                border_style="red"
            ))
            return
        
        # Main result panel
        console.print(Panel(
            f"[green]Critical Review Completed Successfully[/green]",
            title="Critical Review Workflow",
            border_style="green"
        ))
        
        # Original content
        if "original_content" in result:
            console.print(Panel(
                result["original_content"],
                title="Original Content",
                border_style="blue"
            ))
        
        # Facts extracted
        if "facts_extracted" in result:
            console.print(f"\n[blue]Facts Extracted:[/blue] {result['facts_extracted']}")
        
        # Facts reviewed
        if "facts_reviewed" in result:
            console.print(f"[blue]Facts Reviewed:[/blue] {result['facts_reviewed']}")
        
        # Facts needing revision
        if "facts_needing_revision" in result:
            console.print(f"[yellow]Facts Needing Revision:[/yellow] {result['facts_needing_revision']}")
        
        # Credibility scores
        if "credibility_scores" in result and result["credibility_scores"]:
            table = Table(title="Credibility Scores")
            table.add_column("Fact ID", style="cyan")
            table.add_column("Score", style="magenta")
            
            for fact_id, score in result["credibility_scores"].items():
                color = "green" if score >= 0.7 else "yellow" if score >= 0.5 else "red"
                table.add_row(fact_id, f"[{color}]{score:.2f}[/{color}]")
            
            console.print(table)
        
        # Revised content
        if result.get("revision_needed", False) and "final_content" in result:
            console.print(Panel(
                result["final_content"],
                title="Revised Content",
                border_style="green"
            ))
        
        # Revision summary
        if "revision_summary" in result:
            console.print(f"\n[blue]Revision Summary:[/blue] {result['revision_summary']}")
    
    def display_multi_perspective_result(self, result: Dict[str, Any], console: Console) -> None:
        """Display Multi-perspective Synthesis Workflow result using Rich."""
        if not result.get("success", False):
            console.print(Panel(
                f"[red]Workflow Failed[/red]\n\n{result.get('error', 'Unknown error')}",
                title="Error",
                border_style="red"
            ))
            return
        
        # Main result panel
        console.print(Panel(
            f"[green]Multi-perspective Analysis Completed Successfully[/green]",
            title="Multi-perspective Synthesis Workflow",
            border_style="green"
        ))
        
        # Topic and perspectives
        console.print(f"\n[blue]Topic:[/blue] {result.get('topic', 'Unknown')}")
        console.print(f"[blue]Perspectives:[/blue] {', '.join(result.get('perspectives', []))}")
        
        # Quality metrics
        if "quality_score" in result:
            quality_score = result["quality_score"]
            color = "green" if quality_score >= 0.8 else "yellow" if quality_score >= 0.6 else "red"
            console.print(f"[blue]Quality Score:[/blue] [{color}]{quality_score:.2f}[/{color}]")
        
        if "confidence" in result:
            confidence = result["confidence"]
            color = "green" if confidence >= 0.8 else "yellow" if confidence >= 0.6 else "red"
            console.print(f"[blue]Confidence:[/blue] [{color}]{confidence:.2f}[/{color}]")
        
        # Refinement info
        if result.get("refinement_applied", False):
            console.print(f"[blue]Refinement Applied:[/blue] {result.get('refinement_iterations', 0)} iterations")
        
        # Synthesis
        if "synthesis" in result:
            console.print(Panel(
                result["synthesis"],
                title="Synthesis",
                border_style="green"
            ))
        
        # Key insights
        if "key_insights" in result and result["key_insights"]:
            console.print("\n[blue]Key Insights:[/blue]")
            for i, insight in enumerate(result["key_insights"], 1):
                console.print(f"  {i}. {insight}")
        
        # Expert contributions
        if "expert_contributions" in result and result["expert_contributions"]:
            table = Table(title="Expert Contributions")
            table.add_column("Expert", style="cyan")
            table.add_column("Contributions", style="magenta")
            
            for expert, contributions in result["expert_contributions"].items():
                contributions_text = "\n".join(f"• {contrib}" for contrib in contributions)
                table.add_row(expert, contributions_text)
            
            console.print(table)
        
        # Viewpoint analysis
        if "viewpoint_analysis" in result:
            analysis = result["viewpoint_analysis"]
            console.print(f"\n[blue]Viewpoint Analysis:[/blue]")
            console.print(f"  Conflicts: {len(analysis.get('conflicts', []))}")
            console.print(f"  Consensus Areas: {len(analysis.get('consensus_areas', []))}")
            console.print(f"  Collection Quality: {analysis.get('quality_score', 0.0):.2f}")
        
        # Sub-problems
        if "sub_problems" in result and result["sub_problems"]:
            tree = Tree("[blue]Sub-problems[/blue]")
            for sub_problem in result["sub_problems"]:
                perspective = sub_problem.get("perspective", "Unknown")
                description = sub_problem.get("description", "")
                tree.add(f"[cyan]{perspective}:[/cyan] {description}")
            
            console.print(tree)
    
    def _format_critical_review_markdown(self, result: Dict[str, Any]) -> str:
        """Format Critical Review result as Markdown."""
        md = "# Critical Review Workflow Results\n\n"
        
        # Execution info
        md += f"**Execution ID:** {result.get('execution_id', 'Unknown')}\n"
        md += f"**Status:** {'✅ Success' if result.get('success') else '❌ Failed'}\n\n"
        
        # Original content
        if "original_content" in result:
            md += "## Original Content\n\n"
            md += f"{result['original_content']}\n\n"
        
        # Statistics
        md += "## Review Statistics\n\n"
        md += f"- **Facts Extracted:** {result.get('facts_extracted', 0)}\n"
        md += f"- **Facts Reviewed:** {result.get('facts_reviewed', 0)}\n"
        md += f"- **Facts Needing Revision:** {result.get('facts_needing_revision', 0)}\n\n"
        
        # Credibility scores
        if "credibility_scores" in result and result["credibility_scores"]:
            md += "## Credibility Scores\n\n"
            md += "| Fact ID | Score | Status |\n"
            md += "|---------|-------|--------|\n"
            
            for fact_id, score in result["credibility_scores"].items():
                status = "✅ High" if score >= 0.7 else "⚠️ Medium" if score >= 0.5 else "❌ Low"
                md += f"| {fact_id} | {score:.2f} | {status} |\n"
            
            md += "\n"
        
        # Revised content
        if result.get("revision_needed", False) and "final_content" in result:
            md += "## Revised Content\n\n"
            md += f"{result['final_content']}\n\n"
        
        # Revision summary
        if "revision_summary" in result:
            md += "## Revision Summary\n\n"
            md += f"{result['revision_summary']}\n\n"
        
        return md
    
    def _format_multi_perspective_markdown(self, result: Dict[str, Any]) -> str:
        """Format Multi-perspective Synthesis result as Markdown."""
        md = "# Multi-perspective Synthesis Workflow Results\n\n"
        
        # Execution info
        md += f"**Execution ID:** {result.get('execution_id', 'Unknown')}\n"
        md += f"**Status:** {'✅ Success' if result.get('success') else '❌ Failed'}\n"
        md += f"**Topic:** {result.get('topic', 'Unknown')}\n"
        md += f"**Perspectives:** {', '.join(result.get('perspectives', []))}\n\n"
        
        # Quality metrics
        md += "## Quality Metrics\n\n"
        md += f"- **Quality Score:** {result.get('quality_score', 0.0):.2f}\n"
        md += f"- **Confidence:** {result.get('confidence', 0.0):.2f}\n"
        
        if result.get("refinement_applied", False):
            md += f"- **Refinement Applied:** {result.get('refinement_iterations', 0)} iterations\n"
        
        md += "\n"
        
        # Synthesis
        if "synthesis" in result:
            md += "## Synthesis\n\n"
            md += f"{result['synthesis']}\n\n"
        
        # Key insights
        if "key_insights" in result and result["key_insights"]:
            md += "## Key Insights\n\n"
            for i, insight in enumerate(result["key_insights"], 1):
                md += f"{i}. {insight}\n"
            md += "\n"
        
        # Expert contributions
        if "expert_contributions" in result and result["expert_contributions"]:
            md += "## Expert Contributions\n\n"
            for expert, contributions in result["expert_contributions"].items():
                md += f"### {expert}\n\n"
                for contrib in contributions:
                    md += f"- {contrib}\n"
                md += "\n"
        
        # Viewpoint analysis
        if "viewpoint_analysis" in result:
            analysis = result["viewpoint_analysis"]
            md += "## Viewpoint Analysis\n\n"
            md += f"- **Conflicts Identified:** {len(analysis.get('conflicts', []))}\n"
            md += f"- **Consensus Areas:** {len(analysis.get('consensus_areas', []))}\n"
            md += f"- **Collection Quality:** {analysis.get('quality_score', 0.0):.2f}\n\n"
            
            # Consensus areas
            if analysis.get('consensus_areas'):
                md += "### Consensus Areas\n\n"
                for area in analysis['consensus_areas']:
                    md += f"- {area}\n"
                md += "\n"
        
        # Sub-problems
        if "sub_problems" in result and result["sub_problems"]:
            md += "## Sub-problems Analyzed\n\n"
            for sub_problem in result["sub_problems"]:
                perspective = sub_problem.get("perspective", "Unknown")
                description = sub_problem.get("description", "")
                md += f"### {perspective}\n\n"
                md += f"{description}\n\n"
                
                if sub_problem.get("questions"):
                    md += "**Key Questions:**\n"
                    for question in sub_problem["questions"]:
                        md += f"- {question}\n"
                    md += "\n"
        
        return md
    
    def _format_generic_markdown(self, result: Dict[str, Any]) -> str:
        """Format generic result as Markdown."""
        md = "# Workflow Results\n\n"
        
        # Basic info
        md += f"**Status:** {'✅ Success' if result.get('success') else '❌ Failed'}\n"
        md += f"**Execution ID:** {result.get('execution_id', 'Unknown')}\n\n"
        
        # Error if failed
        if not result.get("success"):
            md += f"**Error:** {result.get('error', 'Unknown error')}\n\n"
        
        # Other fields
        for key, value in result.items():
            if key not in ["success", "execution_id", "error"]:
                md += f"**{key.replace('_', ' ').title()}:** {value}\n"
        
        return md