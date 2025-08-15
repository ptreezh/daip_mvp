"""@Time    : 2025-07-24 18:00:00
@Author  : DAIP-LIVE Team
@File    : result_formatter.py
@Description:
    Result formatting for different output formats.
"""
import csv
import io
import json
import xml.etree.ElementTree as ET
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree


class ResultFormatter:
    """Format workflow results for different output types."""

    def __init__(self):
        """Initialize the result formatter."""
        self.supported_formats = [
            "json", "markdown", "html", "xml", "csv", "yaml", "text"
        ]
<<<<<<< HEAD

    def format_as_json(self, result: Dict[str, Any], indent: int = 2) -> str:
        """Format result as JSON string."""
        return json.dumps(result, indent=indent, ensure_ascii=False, default=str)

    def format_as_markdown(self, result: Dict[str, Any]) -> str:
=======
    
    def format_as_json(self, result: dict[str, Any], indent: int = 2) -> str:
        """Format result as JSON string."""
        return json.dumps(result, indent=indent, ensure_ascii=False, default=str)
    
    def format_as_markdown(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
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
<<<<<<< HEAD

    def display_critical_review_result(self, result: Dict[str, Any], console: Console) -> None:
=======
    
    def display_critical_review_result(self, result: dict[str, Any], console: Console) -> None:
>>>>>>> feature/core-services-refactor
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
            "[green]Critical Review Completed Successfully[/green]",
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
<<<<<<< HEAD

    def display_multi_perspective_result(self, result: Dict[str, Any], console: Console) -> None:
=======
    
    def display_multi_perspective_result(self, result: dict[str, Any], console: Console) -> None:
>>>>>>> feature/core-services-refactor
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
            "[green]Multi-perspective Analysis Completed Successfully[/green]",
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
            console.print("\n[blue]Viewpoint Analysis:[/blue]")
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
<<<<<<< HEAD

    def _format_critical_review_markdown(self, result: Dict[str, Any]) -> str:
=======
    
    def _format_critical_review_markdown(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
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
<<<<<<< HEAD

    def _format_multi_perspective_markdown(self, result: Dict[str, Any]) -> str:
=======
    
    def _format_multi_perspective_markdown(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
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
<<<<<<< HEAD

    def format_as_html(self, result: Dict[str, Any]) -> str:
=======
    
    def format_as_html(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """Format result as HTML string."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Workflow Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }
        .success { color: green; }
        .error { color: red; }
        .warning { color: orange; }
        .section { margin: 20px 0; }
        .fact-table { border-collapse: collapse; width: 100%; }
        .fact-table th, .fact-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .fact-table th { background-color: #f2f2f2; }
        .high-score { background-color: #d4edda; }
        .medium-score { background-color: #fff3cd; }
        .low-score { background-color: #f8d7da; }
        .trace-item { margin: 10px 0; padding: 10px; border-left: 3px solid #007bff; background-color: #f8f9fa; }
    </style>
</head>
<body>
"""

        # Header
        status_class = "success" if result.get("success") else "error"
        status_text = "✅ Success" if result.get("success") else "❌ Failed"

        html += f"""
    <div class="header">
        <h1>Workflow Results</h1>
        <p><strong>Status:</strong> <span class="{status_class}">{status_text}</span></p>
        <p><strong>Execution ID:</strong> {result.get('execution_id', 'Unknown')}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""

        if not result.get("success"):
            html += f"""
    <div class="section">
        <h2>Error</h2>
        <p class="error">{result.get('error', 'Unknown error')}</p>
    </div>
"""
        else:
            # Add workflow-specific content
            if "synthesis" in result and "perspectives" in result:
                html += self._format_multi_perspective_html(result)
            elif "revised_content" in result or "original_content" in result:
                html += self._format_critical_review_html(result)
            else:
                html += self._format_generic_html(result)

        # Add execution trace if available
        if "execution_trace" in result:
            html += self._format_execution_trace_html(result["execution_trace"])

        html += """
</body>
</html>
"""
        return html
<<<<<<< HEAD

    def format_as_xml(self, result: Dict[str, Any]) -> str:
=======
    
    def format_as_xml(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """Format result as XML string."""
        root = ET.Element("workflow_result")

        # Basic info
        ET.SubElement(root, "execution_id").text = str(result.get("execution_id", ""))
        ET.SubElement(root, "success").text = str(result.get("success", False))
        ET.SubElement(root, "timestamp").text = datetime.now().isoformat()

        if not result.get("success"):
            ET.SubElement(root, "error").text = str(result.get("error", ""))

        # Add workflow-specific data
        for key, value in result.items():
            if key not in ["execution_id", "success", "error", "execution_trace"]:
                self._add_xml_element(root, key, value)

        # Add execution trace
        if "execution_trace" in result:
            trace_elem = ET.SubElement(root, "execution_trace")
            for step in result["execution_trace"]:
                step_elem = ET.SubElement(trace_elem, "step")
                self._add_xml_element(step_elem, "step_data", step)

        return ET.tostring(root, encoding='unicode', method='xml')
<<<<<<< HEAD

    def format_as_csv(self, result: Dict[str, Any]) -> str:
=======
    
    def format_as_csv(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """Format result as CSV string (for tabular data)."""
        output = io.StringIO()

        # Basic info
        writer = csv.writer(output)
        writer.writerow(["Field", "Value"])
        writer.writerow(["Execution ID", result.get("execution_id", "")])
        writer.writerow(["Success", result.get("success", False)])
        writer.writerow(["Timestamp", datetime.now().isoformat()])

        if not result.get("success"):
            writer.writerow(["Error", result.get("error", "")])

        # Add credibility scores if available
        if "credibility_scores" in result and result["credibility_scores"]:
            writer.writerow([])  # Empty row
            writer.writerow(["Fact ID", "Credibility Score"])
            for fact_id, score in result["credibility_scores"].items():
                writer.writerow([fact_id, f"{score:.3f}"])

        # Add perspectives if available
        if "perspectives" in result and result["perspectives"]:
            writer.writerow([])  # Empty row
            writer.writerow(["Perspectives"])
            for perspective in result["perspectives"]:
                writer.writerow([perspective])

        return output.getvalue()
<<<<<<< HEAD

    def format_as_yaml(self, result: Dict[str, Any]) -> str:
=======
    
    def format_as_yaml(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """Format result as YAML string."""
        try:
            import yaml
            return yaml.dump(result, default_flow_style=False, allow_unicode=True)
        except ImportError:
            # Fallback to simple YAML-like format
            return self._simple_yaml_format(result)
<<<<<<< HEAD

    def format_as_text(self, result: Dict[str, Any]) -> str:
=======
    
    def format_as_text(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """Format result as plain text."""
        lines = []
        lines.append("WORKFLOW RESULTS")
        lines.append("=" * 50)
        lines.append("")

        # Basic info
        lines.append(f"Execution ID: {result.get('execution_id', 'Unknown')}")
        lines.append(f"Status: {'SUCCESS' if result.get('success') else 'FAILED'}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        if not result.get("success"):
            lines.append("ERROR:")
            lines.append(f"  {result.get('error', 'Unknown error')}")
            lines.append("")
        else:
            # Add workflow-specific content
            if "synthesis" in result:
                lines.append("SYNTHESIS:")
                lines.append(f"  {result['synthesis']}")
                lines.append("")

            if "original_content" in result:
                lines.append("ORIGINAL CONTENT:")
                lines.append(f"  {result['original_content']}")
                lines.append("")

            if "revised_content" in result:
                lines.append("REVISED CONTENT:")
                lines.append(f"  {result['revised_content']}")
                lines.append("")

            if "credibility_scores" in result and result["credibility_scores"]:
                lines.append("CREDIBILITY SCORES:")
                for fact_id, score in result["credibility_scores"].items():
                    lines.append(f"  {fact_id}: {score:.3f}")
                lines.append("")

        # Add execution trace summary
        if "execution_trace" in result:
            lines.append("EXECUTION TRACE:")
            for i, step in enumerate(result["execution_trace"], 1):
                step_name = step.get("step_name", f"Step {i}")
                status = step.get("status", "unknown")
                lines.append(f"  {i}. {step_name} - {status.upper()}")
            lines.append("")

        return "\n".join(lines)

    def format_with_traceability(
<<<<<<< HEAD
        self,
        result: Dict[str, Any],
=======
        self, 
        result: dict[str, Any], 
>>>>>>> feature/core-services-refactor
        format_type: str = "json",
        include_reasoning: bool = True,
        include_confidence: bool = True,
        include_sources: bool = True
    ) -> str:
        """Format result with enhanced traceability information."""
        # Enhance result with traceability data
        enhanced_result = result.copy()

        if include_reasoning:
            enhanced_result["reasoning_trace"] = self._extract_reasoning_trace(result)

        if include_confidence:
            enhanced_result["confidence_analysis"] = self._extract_confidence_analysis(result)

        if include_sources:
            enhanced_result["source_attribution"] = self._extract_source_attribution(result)

        # Add metadata
        enhanced_result["traceability_metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "format": format_type,
            "includes_reasoning": include_reasoning,
            "includes_confidence": include_confidence,
            "includes_sources": include_sources
        }

        # Format according to requested type
        if format_type == "json":
            return self.format_as_json(enhanced_result)
        elif format_type == "markdown":
            return self._format_traceable_markdown(enhanced_result)
        elif format_type == "html":
            return self._format_traceable_html(enhanced_result)
        else:
            return self.format_as_json(enhanced_result)

    def display_with_transparency(
<<<<<<< HEAD
        self,
        result: Dict[str, Any],
=======
        self, 
        result: dict[str, Any], 
>>>>>>> feature/core-services-refactor
        console: Console,
        transparency_level: str = "detailed"
    ) -> None:
        """Display result with configurable transparency levels."""
        if transparency_level == "minimal":
            self._display_minimal_transparency(result, console)
        elif transparency_level == "moderate":
            self._display_moderate_transparency(result, console)
        elif transparency_level == "detailed":
            self._display_detailed_transparency(result, console)
        else:
            # Default to moderate
            self._display_moderate_transparency(result, console)
<<<<<<< HEAD

    def _format_generic_markdown(self, result: Dict[str, Any]) -> str:
=======
    
    def _format_generic_markdown(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
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
<<<<<<< HEAD

        return md

    def _format_critical_review_html(self, result: Dict[str, Any]) -> str:
=======
        
        return md  
  
    def _format_critical_review_html(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """Format Critical Review result as HTML."""
        html = """
    <div class="section">
        <h2>Critical Review Results</h2>
"""

        if "original_content" in result:
            html += f"""
        <h3>Original Content</h3>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
            {result['original_content']}
        </div>
"""

        # Statistics
        html += """
        <h3>Review Statistics</h3>
        <ul>
"""
        html += f"<li><strong>Facts Extracted:</strong> {result.get('facts_extracted', 0)}</li>"
        html += f"<li><strong>Facts Reviewed:</strong> {result.get('facts_reviewed', 0)}</li>"
        html += f"<li><strong>Facts Needing Revision:</strong> {result.get('facts_needing_revision', 0)}</li>"
        html += """
        </ul>
"""

        # Credibility scores table
        if "credibility_scores" in result and result["credibility_scores"]:
            html += """
        <h3>Credibility Scores</h3>
        <table class="fact-table">
            <tr><th>Fact ID</th><th>Score</th><th>Status</th></tr>
"""
            for fact_id, score in result["credibility_scores"].items():
                score_class = "high-score" if score >= 0.7 else "medium-score" if score >= 0.5 else "low-score"
                status = "High" if score >= 0.7 else "Medium" if score >= 0.5 else "Low"
                html += f'<tr class="{score_class}"><td>{fact_id}</td><td>{score:.3f}</td><td>{status}</td></tr>'

            html += """
        </table>
"""

        if result.get("revision_needed", False) and "final_content" in result:
            html += f"""
        <h3>Revised Content</h3>
        <div style="background-color: #d4edda; padding: 15px; border-radius: 5px;">
            {result['final_content']}
        </div>
"""

        html += """
    </div>
"""
        return html
<<<<<<< HEAD

    def _format_multi_perspective_html(self, result: Dict[str, Any]) -> str:
=======
    
    def _format_multi_perspective_html(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """Format Multi-perspective result as HTML."""
        html = """
    <div class="section">
        <h2>Multi-perspective Analysis Results</h2>
"""

        html += f"""
        <p><strong>Topic:</strong> {result.get('topic', 'Unknown')}</p>
        <p><strong>Perspectives:</strong> {', '.join(result.get('perspectives', []))}</p>
"""

        # Quality metrics
        if "quality_score" in result or "confidence" in result:
            html += "<h3>Quality Metrics</h3><ul>"
            if "quality_score" in result:
                html += f"<li><strong>Quality Score:</strong> {result['quality_score']:.3f}</li>"
            if "confidence" in result:
                html += f"<li><strong>Confidence:</strong> {result['confidence']:.3f}</li>"
            html += "</ul>"

        if "synthesis" in result:
            html += f"""
        <h3>Synthesis</h3>
        <div style="background-color: #d4edda; padding: 15px; border-radius: 5px;">
            {result['synthesis']}
        </div>
"""

        html += """
    </div>
"""
        return html
<<<<<<< HEAD

    def _format_generic_html(self, result: Dict[str, Any]) -> str:
=======
    
    def _format_generic_html(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """Format generic result as HTML."""
        html = """
    <div class="section">
        <h2>Results</h2>
        <ul>
"""

        for key, value in result.items():
            if key not in ["success", "execution_id", "error", "execution_trace"]:
                html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"

        html += """
        </ul>
    </div>
"""
        return html
<<<<<<< HEAD

    def _format_execution_trace_html(self, trace: List[Dict[str, Any]]) -> str:
=======
    
    def _format_execution_trace_html(self, trace: list[dict[str, Any]]) -> str:
>>>>>>> feature/core-services-refactor
        """Format execution trace as HTML."""
        html = """
    <div class="section">
        <h2>Execution Trace</h2>
"""

        for i, step in enumerate(trace, 1):
            step_name = step.get("step_name", f"Step {i}")
            status = step.get("status", "unknown")
            duration = step.get("duration", 0)

            html += f"""
        <div class="trace-item">
            <h4>{i}. {step_name}</h4>
            <p><strong>Status:</strong> {status}</p>
            <p><strong>Duration:</strong> {duration:.2f}s</p>
"""

            if step.get("inputs"):
                html += f"<p><strong>Inputs:</strong> {step['inputs']}</p>"

            if step.get("outputs"):
                html += f"<p><strong>Outputs:</strong> {step['outputs']}</p>"

            if step.get("error"):
                html += f'<p><strong>Error:</strong> <span class="error">{step["error"]}</span></p>'

            html += """
        </div>
"""

        html += """
    </div>
"""
        return html

    def _add_xml_element(self, parent: ET.Element, key: str, value: Any) -> None:
        """Add an XML element for a key-value pair."""
        if isinstance(value, dict):
            elem = ET.SubElement(parent, key)
            for k, v in value.items():
                self._add_xml_element(elem, k, v)
        elif isinstance(value, list):
            elem = ET.SubElement(parent, key)
            for i, item in enumerate(value):
                self._add_xml_element(elem, f"item_{i}", item)
        else:
            elem = ET.SubElement(parent, key)
            elem.text = str(value)
<<<<<<< HEAD

    def _simple_yaml_format(self, data: Dict[str, Any], indent: int = 0) -> str:
=======
    
    def _simple_yaml_format(self, data: dict[str, Any], indent: int = 0) -> str:
>>>>>>> feature/core-services-refactor
        """Simple YAML-like formatting without external dependencies."""
        lines = []
        prefix = "  " * indent

        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._simple_yaml_format(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{prefix}  -")
                        lines.append(self._simple_yaml_format(item, indent + 2))
                    else:
                        lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}{key}: {value}")

        return "\n".join(lines)
<<<<<<< HEAD

    def _extract_reasoning_trace(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
=======
    
    def _extract_reasoning_trace(self, result: dict[str, Any]) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Extract reasoning trace from result."""
        reasoning_trace = []

        # Extract from execution trace if available
        if "execution_trace" in result:
            for step in result["execution_trace"]:
                if "reasoning" in step:
                    reasoning_trace.append({
                        "step": step.get("step_name", "Unknown"),
                        "reasoning": step["reasoning"],
                        "confidence": step.get("confidence", 0.0)
                    })

        # Extract from credibility scores
        if "credibility_scores" in result:
            reasoning_trace.append({
                "step": "Credibility Assessment",
                "reasoning": f"Evaluated {len(result['credibility_scores'])} facts for credibility",
                "confidence": sum(result["credibility_scores"].values()) / len(result["credibility_scores"])
            })

        return reasoning_trace
<<<<<<< HEAD

    def _extract_confidence_analysis(self, result: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def _extract_confidence_analysis(self, result: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Extract confidence analysis from result."""
        analysis = {
            "overall_confidence": 0.0,
            "confidence_distribution": {},
            "low_confidence_items": []
        }

        # Analyze credibility scores
        if "credibility_scores" in result and result["credibility_scores"]:
            scores = list(result["credibility_scores"].values())
            analysis["overall_confidence"] = sum(scores) / len(scores)

            # Distribution
            high_count = sum(1 for s in scores if s >= 0.7)
            medium_count = sum(1 for s in scores if 0.5 <= s < 0.7)
            low_count = sum(1 for s in scores if s < 0.5)

            analysis["confidence_distribution"] = {
                "high": high_count,
                "medium": medium_count,
                "low": low_count
            }

            # Low confidence items
            analysis["low_confidence_items"] = [
                {"fact_id": fact_id, "score": score}
                for fact_id, score in result["credibility_scores"].items()
                if score < 0.5
            ]

        return analysis
<<<<<<< HEAD

    def _extract_source_attribution(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
=======
    
    def _extract_source_attribution(self, result: dict[str, Any]) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Extract source attribution from result."""
        sources = []

        # Extract from evidence reports if available
        if "evidence_reports" in result:
            for report in result["evidence_reports"]:
                if isinstance(report, dict) and "supporting_evidence" in report:
                    for evidence in report["supporting_evidence"]:
                        if isinstance(evidence, dict) and "source" in evidence:
                            sources.append({
                                "source": evidence["source"],
                                "type": "supporting",
                                "credibility": evidence.get("credibility", 0.0),
                                "fact_id": report.get("fact_id", "unknown")
                            })

        return sources
<<<<<<< HEAD

    def _format_traceable_markdown(self, result: Dict[str, Any]) -> str:
=======
    
    def _format_traceable_markdown(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """Format result with traceability as Markdown."""
        md = self.format_as_markdown(result)

        # Add traceability sections
        if "reasoning_trace" in result:
            md += "\n## Reasoning Trace\n\n"
            for i, trace in enumerate(result["reasoning_trace"], 1):
                md += f"### {i}. {trace['step']}\n\n"
                md += f"**Reasoning:** {trace['reasoning']}\n\n"
                md += f"**Confidence:** {trace['confidence']:.3f}\n\n"

        if "confidence_analysis" in result:
            analysis = result["confidence_analysis"]
            md += "\n## Confidence Analysis\n\n"
            md += f"**Overall Confidence:** {analysis['overall_confidence']:.3f}\n\n"

            if analysis.get("confidence_distribution"):
                dist = analysis["confidence_distribution"]
                md += "**Confidence Distribution:**\n"
                md += f"- High (≥0.7): {dist.get('high', 0)}\n"
                md += f"- Medium (0.5-0.7): {dist.get('medium', 0)}\n"
                md += f"- Low (<0.5): {dist.get('low', 0)}\n\n"

        if "source_attribution" in result and result["source_attribution"]:
            md += "\n## Source Attribution\n\n"
            md += "| Source | Type | Credibility | Fact ID |\n"
            md += "|--------|------|-------------|----------|\n"
            for source in result["source_attribution"]:
                md += f"| {source['source']} | {source['type']} | {source['credibility']:.3f} | {source['fact_id']} |\n"
            md += "\n"

        return md
<<<<<<< HEAD

    def _format_traceable_html(self, result: Dict[str, Any]) -> str:
=======
    
    def _format_traceable_html(self, result: dict[str, Any]) -> str:
>>>>>>> feature/core-services-refactor
        """Format result with traceability as HTML."""
        html = self.format_as_html(result)

        # Insert traceability sections before closing body tag
        traceability_html = ""

        if "reasoning_trace" in result:
            traceability_html += """
    <div class="section">
        <h2>Reasoning Trace</h2>
"""
            for i, trace in enumerate(result["reasoning_trace"], 1):
                traceability_html += f"""
        <div class="trace-item">
            <h3>{i}. {trace['step']}</h3>
            <p><strong>Reasoning:</strong> {trace['reasoning']}</p>
            <p><strong>Confidence:</strong> {trace['confidence']:.3f}</p>
        </div>
"""
            traceability_html += """
    </div>
"""

        if "confidence_analysis" in result:
            analysis = result["confidence_analysis"]
            traceability_html += f"""
    <div class="section">
        <h2>Confidence Analysis</h2>
        <p><strong>Overall Confidence:</strong> {analysis['overall_confidence']:.3f}</p>
"""

            if analysis.get("confidence_distribution"):
                dist = analysis["confidence_distribution"]
                traceability_html += """
        <h3>Confidence Distribution</h3>
        <ul>
"""
                traceability_html += f"<li>High (≥0.7): {dist.get('high', 0)}</li>"
                traceability_html += f"<li>Medium (0.5-0.7): {dist.get('medium', 0)}</li>"
                traceability_html += f"<li>Low (<0.5): {dist.get('low', 0)}</li>"
                traceability_html += """
        </ul>
"""

            traceability_html += """
    </div>
"""

        # Insert before closing body tag
        html = html.replace("</body>", traceability_html + "</body>")
        return html
<<<<<<< HEAD

    def _display_minimal_transparency(self, result: Dict[str, Any], console: Console) -> None:
=======
    
    def _display_minimal_transparency(self, result: dict[str, Any], console: Console) -> None:
>>>>>>> feature/core-services-refactor
        """Display result with minimal transparency."""
        if not result.get("success", False):
            console.print(Panel(
                "[red]Workflow Failed[/red]",
                title="Error",
                border_style="red"
            ))
            return

        # Show only final results
        if "synthesis" in result:
            console.print(Panel(
                result["synthesis"],
                title="Synthesis",
                border_style="green"
            ))
        elif "final_content" in result:
            console.print(Panel(
                result["final_content"],
                title="Final Content",
                border_style="green"
            ))
        elif "revised_content" in result:
            console.print(Panel(
                result["revised_content"],
                title="Revised Content",
                border_style="green"
            ))
<<<<<<< HEAD

    def _display_moderate_transparency(self, result: Dict[str, Any], console: Console) -> None:
=======
    
    def _display_moderate_transparency(self, result: dict[str, Any], console: Console) -> None:
>>>>>>> feature/core-services-refactor
        """Display result with moderate transparency."""
        # Show key reasoning steps and confidence scores
        if "synthesis" in result and "perspectives" in result:
            self.display_multi_perspective_result(result, console)
        elif "revised_content" in result or "original_content" in result:
            self.display_critical_review_result(result, console)
        else:
            console.print(Panel(
                json.dumps(result, indent=2, ensure_ascii=False, default=str),
                title="Results",
                border_style="blue"
            ))
<<<<<<< HEAD

    def _display_detailed_transparency(self, result: Dict[str, Any], console: Console) -> None:
=======
    
    def _display_detailed_transparency(self, result: dict[str, Any], console: Console) -> None:
>>>>>>> feature/core-services-refactor
        """Display result with detailed transparency."""
        # Show complete processing chains and detailed metrics
        self._display_moderate_transparency(result, console)

        # Add execution trace
        if "execution_trace" in result:
            console.print("\n[blue]Execution Trace:[/blue]")

            tree = Tree("[blue]Workflow Steps[/blue]")
            for i, step in enumerate(result["execution_trace"], 1):
                step_name = step.get("step_name", f"Step {i}")
                status = step.get("status", "unknown")
                duration = step.get("duration", 0)

                step_node = tree.add(f"[cyan]{step_name}[/cyan] - {status} ({duration:.2f}s)")

                if step.get("inputs"):
                    step_node.add(f"[yellow]Inputs:[/yellow] {step['inputs']}")

                if step.get("outputs"):
                    step_node.add(f"[green]Outputs:[/green] {step['outputs']}")

                if step.get("error"):
                    step_node.add(f"[red]Error:[/red] {step['error']}")

            console.print(tree)

        # Add reasoning trace if available
        reasoning_trace = self._extract_reasoning_trace(result)
        if reasoning_trace:
            console.print("\n[blue]Reasoning Trace:[/blue]")
            for i, trace in enumerate(reasoning_trace, 1):
                console.print(f"  {i}. [cyan]{trace['step']}[/cyan]")
                console.print(f"     Reasoning: {trace['reasoning']}")
                console.print(f"     Confidence: {trace['confidence']:.3f}")

        # Add confidence analysis
        confidence_analysis = self._extract_confidence_analysis(result)
        if confidence_analysis.get("overall_confidence", 0) > 0:
            console.print(f"\n[blue]Overall Confidence:[/blue] {confidence_analysis['overall_confidence']:.3f}")

            if confidence_analysis.get("low_confidence_items"):
                console.print("[yellow]Low Confidence Items:[/yellow]")
                for item in confidence_analysis["low_confidence_items"]:
                    console.print(f"  - {item['fact_id']}: {item['score']:.3f}")
<<<<<<< HEAD

    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats."""
        return self.supported_formats.copy()

    def format_result(self, result: Dict[str, Any], format_type: str = "json") -> str:
=======
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported output formats."""
        return self.supported_formats.copy()
    
    def format_result(self, result: dict[str, Any], format_type: str = "json") -> str:
>>>>>>> feature/core-services-refactor
        """Format result in the specified format."""
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}. Supported formats: {self.supported_formats}")

        if format_type == "json":
            return self.format_as_json(result)
        elif format_type == "markdown":
            return self.format_as_markdown(result)
        elif format_type == "html":
            return self.format_as_html(result)
        elif format_type == "xml":
            return self.format_as_xml(result)
        elif format_type == "csv":
            return self.format_as_csv(result)
        elif format_type == "yaml":
            return self.format_as_yaml(result)
        elif format_type == "text":
            return self.format_as_text(result)
        else:
            return self.format_as_json(result)
