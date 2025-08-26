"""Debate commands for the DAIP-LIVE CLI."""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)
console = Console()


def export_debate_to_wiki(debate_id: str, wiki_title: str, format: str = "markdown") -> bool:
    """Export debate results to a wiki page.
    
    Args:
        debate_id (str): The ID or topic of the debate to export
        wiki_title (str): Title for the wiki page
        format (str): Export format (markdown, html)
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        # Import wiki service
        from src.cli.service_utils import get_wiki_service
        wiki_service = get_wiki_service()
        
        # Load debate results from saved files
        debate_results = _load_debate_results(debate_id)
        if not debate_results:
            logger.error(f"No debate results found for debate ID: {debate_id}")
            return False
        
        # Extract key insights and format content
        wiki_content = _format_debate_for_wiki(debate_results, format)
        
        # Create wiki entry
        wiki_version = wiki_service.create_entry(
            entry_name=wiki_title,
            content=wiki_content,
            author_role="debate_exporter",
            tags=["debate", "export", "ai-discussion"],
            category="debate_results"
        )
        
        if wiki_version:
            logger.info(f"Successfully exported debate '{debate_id}' to wiki page '{wiki_title}'")
            return True
        else:
            logger.error(f"Failed to create wiki entry for debate '{debate_id}'")
            return False
            
    except Exception as e:
        logger.error(f"Error exporting debate to wiki: {e}")
        return False


def _load_debate_results(debate_id: str) -> Optional[Dict[str, Any]]:
    """Load debate results from saved files.
    
    Args:
        debate_id (str): The debate ID or topic to search for
        
    Returns:
        Optional[Dict[str, Any]]: Debate results if found, None otherwise
    """
    try:
        # Search for debate result files
        possible_files = [
            f"{debate_id}.json",
            f"debate_results_{debate_id}.json",
            f"debate_results.txt",
            "debate_results.json"
        ]
        
        # Also check common output directories
        search_paths = [
            Path("."),
            Path("debate_results"),
            Path("data/debates"),
            Path("daip_mvp_project/memory_bank/tasks")
        ]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            for filename in possible_files:
                file_path = search_path / filename
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            if file_path.suffix == '.json':
                                return json.load(f)
                            else:
                                # Parse text format if needed
                                return _parse_debate_text_file(f.read(), debate_id)
                    except Exception as e:
                        logger.warning(f"Failed to read debate file {file_path}: {e}")
                        continue
        
        # Try to find by topic matching in existing files
        return _find_debate_by_topic(debate_id)
        
    except Exception as e:
        logger.error(f"Error loading debate results: {e}")
        return None


def _parse_debate_text_file(content: str, debate_id: str) -> Dict[str, Any]:
    """Parse debate results from text file format.
    
    Args:
        content (str): Content of the text file
        debate_id (str): Debate identifier
        
    Returns:
        Dict[str, Any]: Parsed debate results
    """
    # Simple parsing for text format - adjust based on actual format
    lines = content.split('\n')
    
    debate_data = {
        "topic": debate_id,
        "history": [],
        "consensus": None,
        "synthesis": None,
        "success": True
    }
    
    # Extract information from text format
    current_role = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for role indicators
        if line.startswith('[') and ']' in line:
            if current_role and current_content:
                debate_data["history"].append({
                    "role": current_role,
                    "opinion": '\n'.join(current_content).strip()
                })
            
            current_role = line.split(']')[0][1:]  # Extract role from [Role]
            current_content = []
        elif current_role:
            current_content.append(line)
        elif line.lower().startswith('consensus:'):
            debate_data["consensus"] = line.split(':', 1)[1].strip()
        elif line.lower().startswith('synthesis:'):
            debate_data["synthesis"] = line.split(':', 1)[1].strip()
    
    # Add the last role's content
    if current_role and current_content:
        debate_data["history"].append({
            "role": current_role,
            "opinion": '\n'.join(current_content).strip()
        })
    
    return debate_data


def _find_debate_by_topic(topic: str) -> Optional[Dict[str, Any]]:
    """Find debate results by topic matching.
    
    Args:
        topic (str): Topic to search for
        
    Returns:
        Optional[Dict[str, Any]]: Debate results if found
    """
    try:
        # Search in common directories for JSON files
        search_dirs = [
            Path("."),
            Path("debate_results"),
            Path("data/debates"),
            Path("daip_mvp_project/memory_bank/tasks")
        ]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
                
            for json_file in search_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Check if this file contains the debate we're looking for
                    if data.get("topic") == topic or data.get("title") == topic:
                        return data
                        
                except Exception as e:
                    logger.warning(f"Failed to read {json_file}: {e}")
                    continue
        
        return None
        
    except Exception as e:
        logger.error(f"Error finding debate by topic: {e}")
        return None


def _format_debate_for_wiki(debate_results: Dict[str, Any], format: str) -> str:
    """Format debate results for wiki display.
    
    Args:
        debate_results (Dict[str, Any]): Debate results data
        format (str): Output format (markdown, html)
        
    Returns:
        str: Formatted content for wiki
    """
    topic = debate_results.get("topic", "Unknown Debate")
    history = debate_results.get("history", [])
    consensus = debate_results.get("consensus")
    synthesis = debate_results.get("synthesis")
    
    if format.lower() == "html":
        return _format_debate_html(topic, history, consensus, synthesis)
    else:
        return _format_debate_markdown(topic, history, consensus, synthesis)


def _format_debate_markdown(topic: str, history: list, consensus: Optional[str], synthesis: Optional[str]) -> str:
    """Format debate results as Markdown.
    
    Args:
        topic (str): Debate topic
        history (list): List of debate turns
        consensus (Optional[str]): Consensus result
        synthesis (Optional[str]): Debate synthesis
        
    Returns:
        str: Markdown formatted content
    """
    content = f"# Debate: {topic}\n\n"
    
    # Add debate statistics
    content += "## Debate Statistics\n\n"
    content += f"- **Total Participants:** {len(set(turn.get('role', 'Unknown') for turn in history))}\n"
    content += f"- **Total Turns:** {len(history)}\n"
    
    # Add consensus if available
    if consensus:
        content += f"- **Consensus:** {consensus}\n"
    
    content += "\n---\n\n"
    
    # Add debate transcript
    content += "## Debate Transcript\n\n"
    
    for turn in history:
        role = turn.get('role', 'Unknown')
        opinion = turn.get('opinion', '')
        
        content += f"### {role}\n\n"
        content += f"{opinion}\n\n"
        content += "---\n\n"
    
    # Add synthesis if available
    if synthesis:
        content += "## Synthesis\n\n"
        content += f"{synthesis}\n\n"
    
    # Add key insights section
    content += "## Key Insights\n\n"
    content += _extract_key_insights(history, consensus, synthesis)
    
    return content


def _format_debate_html(topic: str, history: list, consensus: Optional[str], synthesis: Optional[str]) -> str:
    """Format debate results as HTML.
    
    Args:
        topic (str): Debate topic
        history (list): List of debate turns
        consensus (Optional[str]): Consensus result
        synthesis (Optional[str]): Debate synthesis
        
    Returns:
        str: HTML formatted content
    """
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Debate: {topic}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .statistics {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .transcript {{ margin: 20px 0; }}
        .turn {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #3498db; }}
        .role {{ font-weight: bold; color: #2980b9; }}
        .synthesis {{ background: #e8f6f3; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .insights {{ background: #fef9e7; padding: 20px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>Debate: {topic}</h1>
    
    <div class="statistics">
        <h2>Debate Statistics</h2>
        <ul>
            <li><strong>Total Participants:</strong> {len(set(turn.get('role', 'Unknown') for turn in history))}</li>
            <li><strong>Total Turns:</strong> {len(history)}</li>"""
    
    if consensus:
        content += f'\n            <li><strong>Consensus:</strong> {consensus}</li>'
    
    content += """
        </ul>
    </div>
    
    <div class="transcript">
        <h2>Debate Transcript</h2>"""
    
    for turn in history:
        role = turn.get('role', 'Unknown')
        opinion = turn.get('opinion', '')
        
        content += f"""
        <div class="turn">
            <h3 class="role">{role}</h3>
            <p>{opinion.replace(chr(10), '<br>')}</p>
        </div>"""
    
    if synthesis:
        content += f"""
    </div>
    
    <div class="synthesis">
        <h2>Synthesis</h2>
        <p>{synthesis.replace(chr(10), '<br>')}</p>
    </div>"""
    
    content += f"""
    <div class="insights">
        <h2>Key Insights</h2>
        <p>{_extract_key_insights(history, consensus, synthesis).replace(chr(10), '<br>')}</p>
    </div>
    
</body>
</html>"""
    
    return content


def _extract_key_insights(history: list, consensus: Optional[str], synthesis: Optional[str]) -> str:
    """Extract key insights from debate results.
    
    Args:
        history (list): List of debate turns
        consensus (Optional[str]): Consensus result
        synthesis (Optional[str]): Debate synthesis
        
    Returns:
        str: Key insights summary
    """
    insights = []
    
    # Analyze participant contributions
    role_contributions = {}
    for turn in history:
        role = turn.get('role', 'Unknown')
        opinion = turn.get('opinion', '')
        
        if role not in role_contributions:
            role_contributions[role] = []
        role_contributions[role].append(opinion)
    
    # Add participant insights
    if role_contributions:
        insights.append("### Participant Perspectives")
        for role, contributions in role_contributions.items():
            total_words = sum(len(cont.split()) for cont in contributions)
            insights.append(f"- **{role}**: Contributed {len(contributions)} turns, approximately {total_words} words")
    
    # Add consensus insights
    if consensus:
        insights.append("### Consensus Analysis")
        insights.append(f"- The debate reached a consensus: {consensus}")
    
    # Add synthesis insights if available
    if synthesis:
        insights.append("### Synthesis Highlights")
        # Extract key points from synthesis (simple approach)
        sentences = synthesis.split('.')
        key_points = [s.strip() for s in sentences if len(s.strip()) > 50][:3]  # Top 3 substantial sentences
        for point in key_points:
            insights.append(f"- {point}.")
    
    # Add general insights
    insights.append("### Discussion Dynamics")
    insights.append(f"- Total engagement: {len(history)} turns across {len(role_contributions)} participants")
    
    if len(history) > 0:
        avg_turn_length = sum(len(turn.get('opinion', '').split()) for turn in history) / len(history)
        insights.append(f"- Average contribution length: {avg_turn_length:.1f} words per turn")
    
    return '\n\n'.join(insights)


def view_debate_disagreements(debate_id: str) -> bool:
    """View key disagreement points in a debate.
    
    Args:
        debate_id (str): The ID or topic of the debate to analyze
        
    Returns:
        bool: True if analysis was successful, False otherwise
    """
    try:
        # Load debate results
        debate_results = _load_debate_results(debate_id)
        if not debate_results:
            console.print(f"[red]❌ Debate not found: {debate_id}[/red]")
            return False
        
        # Extract and analyze disagreements
        disagreements = _extract_disagreements(debate_results)
        
        if not disagreements:
            console.print(f"[green]✅ No significant disagreements found in debate: {debate_id}[/green]")
            console.print("[yellow]The debate appears to have reached broad consensus.[/yellow]")
            return True
        
        # Display disagreements
        console.print(f"[bold blue]🔍 Debate Disagreements Analysis: {debate_id}[/bold blue]")
        console.print()
        
        # Create disagreement table
        table = Table(title="Key Disagreement Points")
        table.add_column("Issue", style="cyan", no_wrap=True)
        table.add_column("Parties Involved", style="magenta")
        table.add_column("Intensity", style="red")
        table.add_column("Summary", style="yellow")
        
        for disagreement in disagreements:
            table.add_row(
                disagreement["issue"],
                ", ".join(disagreement["parties"]),
                disagreement["intensity"],
                disagreement["summary"][:100] + "..." if len(disagreement["summary"]) > 100 else disagreement["summary"]
            )
        
        console.print(table)
        
        # Show detailed analysis
        console.print("\n[bold]📊 Detailed Analysis:[/bold]")
        console.print(f"[dim]Total disagreements identified: {len(disagreements)}[/dim]")
        console.print(f"[dim]Most contentious issue: {disagreements[0]['issue'] if disagreements else 'N/A'}[/dim]")
        
        # Show consensus status
        consensus = debate_results.get("consensus")
        if consensus:
            console.print(f"\n[green]🎯 Despite disagreements, the debate reached consensus: {consensus}[/green]")
        else:
            console.print(f"\n[yellow]⚠️  No final consensus was reached due to these disagreements[/yellow]")
        
        return True
        
    except Exception as e:
        logger.error(f"Error viewing debate disagreements: {e}")
        console.print(f"[red]❌ Error analyzing disagreements: {e}[/red]")
        return False


def select_consensus_algorithm(debate_id: str, algorithm_name: str) -> bool:
    """Select or change the consensus algorithm for a debate.
    
    Args:
        debate_id (str): The ID or topic of the debate
        algorithm_name (str): Name of the consensus algorithm to use
        
    Returns:
        bool: True if selection was successful, False otherwise
    """
    try:
        # Validate algorithm name
        valid_algorithms = ["simple_majority_vote", "weighted_vote", "consensus_building", "expert_judgment"]
        if algorithm_name not in valid_algorithms:
            console.print(f"[red]❌ Invalid consensus algorithm: {algorithm_name}[/red]")
            console.print(f"[yellow]Valid options: {', '.join(valid_algorithms)}[/yellow]")
            return False
        
        # Load debate results
        debate_results = _load_debate_results(debate_id)
        if not debate_results:
            console.print(f"[red]❌ Debate not found: {debate_id}[/red]")
            return False
        
        # Update consensus algorithm
        old_algorithm = debate_results.get("consensus_algorithm", "simple_majority_vote")
        debate_results["consensus_algorithm"] = algorithm_name
        
        # Recalculate consensus if needed
        if old_algorithm != algorithm_name:
            console.print(f"[bold blue]🔄 Recalculating consensus with new algorithm: {algorithm_name}[/bold blue]")
            new_consensus = _recalculate_consensus(debate_results, algorithm_name)
            if new_consensus:
                debate_results["consensus"] = new_consensus
        
        # Save updated debate results
        if _save_debate_results(debate_id, debate_results):
            console.print(f"[green]✅ Consensus algorithm updated successfully[/green]")
            console.print(f"[dim]Previous: {old_algorithm} → New: {algorithm_name}[/dim]")
            
            if new_consensus:
                console.print(f"[green]🎯 New consensus: {new_consensus}[/green]")
            
            return True
        else:
            console.print(f"[red]❌ Failed to save updated debate results[/red]")
            return False
            
    except Exception as e:
        logger.error(f"Error selecting consensus algorithm: {e}")
        console.print(f"[red]❌ Error selecting consensus algorithm: {e}[/red]")
        return False


def _extract_disagreements(debate_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract key disagreement points from debate results.
    
    Args:
        debate_results (Dict[str, Any]): Debate results data
        
    Returns:
        List[Dict[str, Any]]: List of disagreement points
    """
    disagreements = []
    history = debate_results.get("history", [])
    
    if not history:
        return disagreements
    
    # Simple disagreement detection based on content analysis
    # In a real implementation, this would use more sophisticated NLP
    
    # Group contributions by role
    role_contributions = {}
    for turn in history:
        role = turn.get('role', 'Unknown')
        opinion = turn.get('opinion', '')
        
        if role not in role_contributions:
            role_contributions[role] = []
        role_contributions[role].append(opinion)
    
    # Look for conflicting viewpoints
    roles = list(role_contributions.keys())
    for i in range(len(roles)):
        for j in range(i + 1, len(roles)):
            role1, role2 = roles[i], roles[j]
            conflicts = _find_conflicts(role_contributions[role1], role_contributions[role2])
            
            for conflict in conflicts:
                disagreements.append({
                    "issue": conflict["issue"],
                    "parties": [role1, role2],
                    "intensity": conflict["intensity"],
                    "summary": conflict["summary"]
                })
    
    # Sort by intensity
    disagreements.sort(key=lambda x: x["intensity"], reverse=True)
    
    return disagreements


def _find_conflicts(contributions1: List[str], contributions2: List[str]) -> List[Dict[str, Any]]:
    """Find conflicts between two sets of contributions.
    
    Args:
        contributions1 (List[str]): Contributions from first role
        contributions2 (List[str]): Contributions from second role
        
    Returns:
        List[Dict[str, Any]]: List of conflicts
    """
    conflicts = []
    
    # Simple conflict detection based on keyword opposition
    # This is a basic implementation - real system would use more sophisticated NLP
    
    opposition_keywords = {
        "support": ["oppose", "against", "reject", "disagree"],
        "agree": ["disagree", "dispute", "challenge"],
        "beneficial": ["harmful", "negative", "detrimental"],
        "effective": ["ineffective", "useless", "failed"],
        "necessary": ["unnecessary", "optional", "redundant"]
    }
    
    text1 = " ".join(contributions1).lower()
    text2 = " ".join(contributions2).lower()
    
    for positive, negatives in opposition_keywords.items():
        if positive in text1:
            for negative in negatives:
                if negative in text2:
                    conflicts.append({
                        "issue": f"Stance on {positive} vs {negative}",
                        "intensity": "High",
                        "summary": f"One party supports {positive} while the other advocates {negative}"
                    })
    
    return conflicts


def _recalculate_consensus(debate_results: Dict[str, Any], algorithm: str) -> Optional[str]:
    """Recalculate consensus using the specified algorithm.
    
    Args:
        debate_results (Dict[str, Any]): Debate results data
        algorithm (str): Algorithm to use
        
    Returns:
        Optional[str]: New consensus result
    """
    try:
        history = debate_results.get("history", [])
        
        if algorithm == "simple_majority_vote":
            return _simple_majority_consensus(history)
        elif algorithm == "weighted_vote":
            return _weighted_consensus(history)
        elif algorithm == "consensus_building":
            return _consensus_building(history)
        elif algorithm == "expert_judgment":
            return _expert_judgment_consensus(history)
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error recalculating consensus: {e}")
        return None


def _simple_majority_consensus(history: list) -> str:
    """Simple majority vote consensus."""
    # This is a simplified implementation
    # In a real system, this would analyze the actual positions taken
    return "Consensus reached through simple majority vote"


def _weighted_consensus(history: list) -> str:
    """Weighted voting consensus."""
    # This is a simplified implementation
    # In a real system, this would consider role weights and expertise
    return "Consensus reached through weighted voting"


def _consensus_building(history: list) -> str:
    """Consensus building through discussion."""
    # This is a simplified implementation
    # In a real system, this would analyze the discussion process
    return "Consensus built through iterative discussion"


def _expert_judgment_consensus(history: list) -> str:
    """Expert judgment consensus."""
    # This is a simplified implementation
    # In a real system, this would prioritize expert opinions
    return "Consensus reached through expert judgment"


def _save_debate_results(debate_id: str, debate_results: Dict[str, Any]) -> bool:
    """Save updated debate results.
    
    Args:
        debate_id (str): Debate identifier
        debate_results (Dict[str, Any]): Updated debate data
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        # Try to save to the same location it was loaded from
        possible_paths = [
            Path(f"{debate_id}.json"),
            Path(f"debate_results_{debate_id}.json"),
            Path("debate_results") / f"{debate_id}.json",
            Path("data/debates") / f"{debate_id}.json"
        ]
        
        for file_path in possible_paths:
            if file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(debate_results, f, indent=4, ensure_ascii=False)
                logger.info(f"Saved updated debate results to {file_path}")
                return True
        
        # If no existing file found, create a new one
        save_path = Path("data/debates")
        save_path.mkdir(parents=True, exist_ok=True)
        
        with open(save_path / f"{debate_id}.json", 'w', encoding='utf-8') as f:
            json.dump(debate_results, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Created new debate results file: {save_path / f'{debate_id}.json'}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving debate results: {e}")
        return False