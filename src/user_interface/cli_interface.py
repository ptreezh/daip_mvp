# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 18:00:00
@Author  : DAIP-LIVE Team
@File    : cli_interface.py
@Description:
    Command-line interface for the Virtual Role Chat System workflows.
"""
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from ..workflows.critical_review_workflow import CriticalReviewWorkflow
from ..workflows.multi_perspective_workflow import MultiPerspectiveSynthesisWorkflow
from .progress_monitor import ProgressMonitor
from .result_formatter import ResultFormatter

logger = logging.getLogger(__name__)
console = Console()


class CLIInterface:
    """Command-line interface for workflow execution."""
    
    def __init__(self):
        """Initialize the CLI interface."""
        self.progress_monitor = ProgressMonitor()
        self.result_formatter = ResultFormatter()
        self.console = Console()
    
    async def setup_services(self) -> Dict[str, Any]:
        """Set up required services for workflow execution."""
        try:
            from ..core_services.llm_interface import EnhancedLLMInterface
            from ..core_services.role_manager import RoleManager
            from ..kernel.tool_executor import ToolExecutor
            from ..core_services.synthesis_engine import SynthesisEngine
            from ..core_services.fact_extraction_service import FactExtractionService
            from ..core_services.wiki_service import WikiService
            
            # Initialize services
            llm_interface = EnhancedLLMInterface()
            role_manager = RoleManager()
            tool_executor = ToolExecutor()
            synthesis_engine = SynthesisEngine(llm_interface)
            fact_extraction_service = FactExtractionService()
            wiki_service = WikiService()
            
            return {
                "llm_interface": llm_interface,
                "role_manager": role_manager,
                "tool_executor": tool_executor,
                "synthesis_engine": synthesis_engine,
                "fact_extraction_service": fact_extraction_service,
                "wiki_service": wiki_service
            }
        except ImportError as e:
            console.print(f"[red]Error importing services: {e}[/red]")
            console.print("[yellow]Some services may not be available. Continuing with available services.[/yellow]")
            return {}
    
    async def execute_critical_review(
        self,
        content: str = None,
        content_file: str = None,
        config_file: str = None,
        output_file: str = None,
        format_type: str = "rich",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Execute Critical Review Workflow."""
        try:
            # Get content
            if content_file:
                with open(content_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif not content:
                content = click.prompt("Please enter the content to review")
            
            # Load configuration
            config = {}
            if config_file and Path(config_file).exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # Set up services
            console.print("[blue]Setting up services...[/blue]")
            services = await self.setup_services()
            
            # Create and execute workflow
            console.print("[blue]Starting Critical Review Workflow...[/blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Executing workflow...", total=None)
                
                workflow = CriticalReviewWorkflow("cli_critical_review", config)
                result = await workflow.execute(
                    prompt=f"Please review the following content: {content}",
                    services=services
                )
                
                progress.update(task, completed=True)
            
            # Format and display results
            if format_type == "rich":
                self.result_formatter.display_critical_review_result(result, console)
            elif format_type == "json":
                formatted_result = self.result_formatter.format_as_json(result)
                console.print(formatted_result)
            elif format_type == "markdown":
                formatted_result = self.result_formatter.format_as_markdown(result)
                console.print(formatted_result)
            
            # Save to file if requested
            if output_file:
                self._save_result_to_file(result, output_file, format_type)
                console.print(f"[green]Results saved to {output_file}[/green]")
            
            return result
            
        except Exception as e:
            console.print(f"[red]Error executing Critical Review Workflow: {e}[/red]")
            if verbose:
                console.print_exception()
            return {"success": False, "error": str(e)}
    
    async def execute_multi_perspective(
        self,
        topic: str = None,
        perspectives: List[str] = None,
        config_file: str = None,
        output_file: str = None,
        format_type: str = "rich",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Execute Multi-perspective Synthesis Workflow."""
        try:
            # Get topic
            if not topic:
                topic = click.prompt("Please enter the topic to analyze")
            
            # Get perspectives
            if not perspectives:
                perspectives_input = click.prompt(
                    "Enter perspectives (comma-separated, or press Enter for default)",
                    default="",
                    show_default=False
                )
                if perspectives_input:
                    perspectives = [p.strip() for p in perspectives_input.split(",")]
                else:
                    perspectives = ["经济", "社会", "技术", "伦理"]
            
            # Load configuration
            config = {}
            if config_file and Path(config_file).exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # Set up services
            console.print("[blue]Setting up services...[/blue]")
            services = await self.setup_services()
            
            # Create and execute workflow
            console.print(f"[blue]Starting Multi-perspective Analysis of: {topic}[/blue]")
            console.print(f"[blue]Perspectives: {', '.join(perspectives)}[/blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Executing workflow...", total=None)
                
                workflow = MultiPerspectiveSynthesisWorkflow("cli_multi_perspective", config)
                result = await workflow.execute(
                    topic=topic,
                    perspectives=perspectives,
                    services=services
                )
                
                progress.update(task, completed=True)
            
            # Format and display results
            if format_type == "rich":
                self.result_formatter.display_multi_perspective_result(result, console)
            elif format_type == "json":
                formatted_result = self.result_formatter.format_as_json(result)
                console.print(formatted_result)
            elif format_type == "markdown":
                formatted_result = self.result_formatter.format_as_markdown(result)
                console.print(formatted_result)
            
            # Save to file if requested
            if output_file:
                self._save_result_to_file(result, output_file, format_type)
                console.print(f"[green]Results saved to {output_file}[/green]")
            
            return result
            
        except Exception as e:
            console.print(f"[red]Error executing Multi-perspective Synthesis Workflow: {e}[/red]")
            if verbose:
                console.print_exception()
            return {"success": False, "error": str(e)}
    
    def list_workflows(self) -> None:
        """List available workflows."""
        table = Table(title="Available Workflows")
        table.add_column("Workflow", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")
        table.add_column("Command", style="green")
        
        table.add_row(
            "Critical Review",
            "Systematic fact validation through multi-role review",
            "critical-review"
        )
        table.add_row(
            "Multi-perspective Synthesis",
            "Comprehensive analysis from multiple expert perspectives",
            "multi-perspective"
        )
        
        console.print(table)
    
    def show_workflow_help(self, workflow_name: str) -> None:
        """Show help for a specific workflow."""
        if workflow_name == "critical-review":
            help_text = """
# Critical Review Workflow

This workflow systematically validates content through multi-role fact checking.

## Usage:
```bash
python -m src.user_interface.cli critical-review --content "Your content here"
```

## Options:
- `--content TEXT`: Content to review (or use --content-file)
- `--content-file PATH`: File containing content to review
- `--config-file PATH`: JSON configuration file
- `--output-file PATH`: Save results to file
- `--format [rich|json|markdown]`: Output format
- `--verbose`: Show detailed error information

## Configuration:
Create a JSON file with workflow configuration:
```json
{
  "generation": {
    "role_name": "创作者"
  },
  "consensus": {
    "credibility_threshold": 0.7
  }
}
```
            """
        elif workflow_name == "multi-perspective":
            help_text = """
# Multi-perspective Synthesis Workflow

This workflow analyzes topics from multiple expert perspectives.

## Usage:
```bash
python -m src.user_interface.cli multi-perspective --topic "AI impact on jobs"
```

## Options:
- `--topic TEXT`: Topic to analyze
- `--perspectives TEXT`: Comma-separated list of perspectives
- `--config-file PATH`: JSON configuration file
- `--output-file PATH`: Save results to file
- `--format [rich|json|markdown]`: Output format
- `--verbose`: Show detailed error information

## Configuration:
Create a JSON file with workflow configuration:
```json
{
  "task_decomposition": {
    "max_sub_problems": 4
  },
  "enhanced_synthesis": {
    "quality_threshold": 0.8
  }
}
```
            """
        else:
            help_text = "Unknown workflow. Use 'list' to see available workflows."
        
        console.print(Panel(help_text, title=f"Help: {workflow_name}", expand=False))
    
    def _save_result_to_file(self, result: Dict[str, Any], output_file: str, format_type: str) -> None:
        """Save result to file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format_type == "json":
            content = self.result_formatter.format_as_json(result)
        elif format_type == "markdown":
            content = self.result_formatter.format_as_markdown(result)
        else:
            # Default to JSON for file output
            content = json.dumps(result, indent=2, ensure_ascii=False)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


# CLI Commands using Click
@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """Virtual Role Chat System - Institutional Primitives CLI"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    # Configure logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@cli.command()
@click.option('--content', '-c', help='Content to review')
@click.option('--content-file', '-f', type=click.Path(exists=True), help='File containing content to review')
@click.option('--config-file', type=click.Path(), help='JSON configuration file')
@click.option('--output-file', '-o', help='Save results to file')
@click.option('--format', 'format_type', type=click.Choice(['rich', 'json', 'markdown']), default='rich', help='Output format')
@click.pass_context
def critical_review(ctx, content, content_file, config_file, output_file, format_type):
    """Execute Critical Review Workflow for systematic fact validation."""
    cli_interface = CLIInterface()
    
    async def run():
        return await cli_interface.execute_critical_review(
            content=content,
            content_file=content_file,
            config_file=config_file,
            output_file=output_file,
            format_type=format_type,
            verbose=ctx.obj.get('verbose', False)
        )
    
    result = asyncio.run(run())
    if not result.get('success', False):
        sys.exit(1)


@cli.command()
@click.option('--topic', '-t', help='Topic to analyze')
@click.option('--perspectives', '-p', help='Comma-separated list of perspectives')
@click.option('--config-file', type=click.Path(), help='JSON configuration file')
@click.option('--output-file', '-o', help='Save results to file')
@click.option('--format', 'format_type', type=click.Choice(['rich', 'json', 'markdown']), default='rich', help='Output format')
@click.pass_context
def multi_perspective(ctx, topic, perspectives, config_file, output_file, format_type):
    """Execute Multi-perspective Synthesis Workflow for comprehensive analysis."""
    cli_interface = CLIInterface()
    
    # Parse perspectives
    perspectives_list = None
    if perspectives:
        perspectives_list = [p.strip() for p in perspectives.split(',')]
    
    async def run():
        return await cli_interface.execute_multi_perspective(
            topic=topic,
            perspectives=perspectives_list,
            config_file=config_file,
            output_file=output_file,
            format_type=format_type,
            verbose=ctx.obj.get('verbose', False)
        )
    
    result = asyncio.run(run())
    if not result.get('success', False):
        sys.exit(1)


@cli.command()
def list_workflows():
    """List available workflows."""
    cli_interface = CLIInterface()
    cli_interface.list_workflows()


@cli.command()
@click.argument('workflow_name')
def help_workflow(workflow_name):
    """Show help for a specific workflow."""
    cli_interface = CLIInterface()
    cli_interface.show_workflow_help(workflow_name)


if __name__ == '__main__':
    cli()