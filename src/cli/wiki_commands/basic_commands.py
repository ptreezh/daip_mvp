# -*- coding: utf-8 -*-
"""@Time    : 2025-07-19 03:00:00
@Author  : DAIP-LIVE Team
@File    : basic_commands.py
@Description: Basic wiki management commands for the DAIP-LIVE CLI.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path

app = typer.Typer(help="Basic wiki management commands.")

@app.command()
def create(
    title: str = typer.Argument(..., help="The title of the new wiki page."),
    content: str = typer.Option("", "--content", "-c", help="The initial content of the wiki page."),
    file: str = typer.Option(None, "--file", "-f", help="The file containing the initial content of the wiki page."),
    tags: str = typer.Option("", "--tags", "-t", help="Comma-separated list of tags for the wiki page."),
    category: str = typer.Option("general", "--category", "-c", help="The category for the wiki page."),
):
    """Create a new wiki page."""
    from src.cli.service_utils import get_wiki_service
    wiki_service = get_wiki_service()
    
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            typer.echo(f"Error reading file {file}: {e}")
            raise typer.Exit(1)
    
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    
    try:
        wiki_version = wiki_service.create_entry(
            entry_name=title,
            content=content,
            author_role="cli_user",  # Default author role for CLI
            tags=tag_list,
            category=category  # Default category
        )
        if wiki_version:
            typer.echo(f"Wiki page '{title}' created successfully with ID: {wiki_version.entry_name}")
        else:
            typer.echo(f"Failed to create wiki page '{title}'")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error creating wiki page: {e}")
        raise typer.Exit(1)


@app.command()
def view(
    title_or_id: str = typer.Argument(..., help="The title or ID of the wiki page."),
):
    """View a wiki page."""
    from src.cli.service_utils import get_wiki_service
    wiki_service = get_wiki_service()
    
    try:
        wiki_version = wiki_service.get_entry(entry_name=title_or_id)
        if wiki_version:
            typer.echo(f"Wiki page '{wiki_version.entry_name}':")
            typer.echo(f"Content: {wiki_version.content}")
            typer.echo(f"Author: {wiki_version.author}")
            typer.echo(f"Created at: {wiki_version.timestamp}")
            typer.echo(f"Change summary: {wiki_version.change_summary}")
            typer.echo(f"Version: {wiki_version.version}")
        else:
            typer.echo(f"Wiki page '{title_or_id}' not found.")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error viewing wiki page: {e}")
        raise typer.Exit(1)


@app.command()
def edit(
    title_or_id: str = typer.Argument(..., help="The title or ID of the wiki page to edit."),
    content: str = typer.Option("", "--content", "-c", help="The new content of the wiki page."),
    file: str = typer.Option(None, "--file", "-f", help="The file containing the new content of the wiki page."),
):
    """Edit an existing wiki page."""
    from src.cli.service_utils import get_wiki_service
    wiki_service = get_wiki_service()
    
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            typer.echo(f"Error reading file {file}: {e}")
            raise typer.Exit(1)
    
    try:
        # Use propose_edit method to create an edit proposal
        proposal_id = wiki_service.propose_edit(
            entry_name=title_or_id,
            new_content=content,
            author_role="cli_user",
            change_summary="CLI edit"
        )
        if proposal_id:
            typer.echo(f"Edit proposal for '{title_or_id}' created successfully with ID: {proposal_id}")
            typer.echo("Note: This edit is proposed and needs to be applied by a wiki administrator.")
        else:
            typer.echo(f"Failed to create edit proposal for '{title_or_id}'")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error editing wiki page: {e}")
        raise typer.Exit(1)


@app.command()
def delete(
    title_or_id: str = typer.Argument(..., help="The title or ID of the wiki page to delete."),
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Skip confirmation prompt."),
):
    """Delete a wiki page."""
    from src.cli.service_utils import get_wiki_service
    wiki_service = get_wiki_service()
    
    if not confirm:
        if not typer.confirm(f"Are you sure you want to delete the wiki page '{title_or_id}'? This action cannot be undone."):
            typer.echo("Deletion cancelled.")
            raise typer.Exit(0)
    
    try:
        success = wiki_service.delete_entry(title_or_id)
        if success:
            typer.echo(f"Wiki page '{title_or_id}' deleted successfully.")
        else:
            typer.echo(f"Failed to delete wiki page '{title_or_id}'.")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error deleting wiki page: {e}")
        raise typer.Exit(1)


@app.command()
def search(
    keywords: str = typer.Argument(..., help="The keywords to search for."),
    limit: int = typer.Option(3, "--limit", "-l", help="Maximum number of results to return."),
):
    """Search for wiki pages."""
    from src.cli.service_utils import get_wiki_service
    wiki_service = get_wiki_service()
    
    try:
        results = wiki_service.search(query=keywords, top_k=limit)
        if results:
            typer.echo(f"Search results for '{keywords}':")
            for i, result in enumerate(results, 1):
                typer.echo(f"{i}. {result}")
        else:
            typer.echo(f"No results found for '{keywords}'.")
    except Exception as e:
        typer.echo(f"Error searching wiki pages: {e}")
        raise typer.Exit(1)


@app.command()
def export(
    title_or_id: str = typer.Argument(..., help="The title or ID of the wiki page to export."),
    format: str = typer.Option("markdown", "--format", "-f", help="Export format (markdown, json, html, pdf)."),
    output: str = typer.Option(None, "--output", "-o", help="Output file path. If not specified, uses title with format extension."),
):
    """Export a wiki page to various formats."""
    from rich.console import Console
    from rich.panel import Panel
    from pathlib import Path
    console = Console()
    
    from src.cli.service_utils import get_wiki_service
    wiki_service = get_wiki_service()
    
    if not output:
        output = f"{title_or_id}.{format}"
        output_path = Path(output)
    
    supported_formats = ["markdown", "json", "html", "pdf"]
    if format.lower() not in supported_formats:
        console.print(f"[red]❌ Unsupported format: {format}[/red]")
        console.print(f"[yellow]Supported formats: {', '.join(supported_formats)}[/yellow]")
        raise typer.Exit(1)
    
    try:
        if format.lower() == "pdf":
            # PDF export requires additional processing
            success = _export_to_pdf(wiki_service, title_or_id, output_path)
        elif format.lower() == "html":
            # HTML export requires additional processing
            success = _export_to_html(wiki_service, title_or_id, output_path)
        else:
            # Use the built-in export functionality for markdown and json
            success = wiki_service.export_entry(title_or_id, str(output_path), format.lower())
        
        if success:
            console.print(f"[green]SUCCESS: Wiki page '{title_or_id}' exported successfully to {output_path}[/green]")
            # Show file size
            if output_path.exists():
                size = output_path.stat().st_size
                console.print(f"[dim]File size: {size:,} bytes[/dim]")
        else:
            console.print(f"[red]ERROR: Failed to export wiki page '{title_or_id}'[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]ERROR: Error exporting wiki page: {e}[/red]")
        raise typer.Exit(1)


def _export_to_pdf(wiki_service, title_or_id: str, output_path: Path) -> bool:
    """Export wiki page to PDF format."""
    try:
        # First export to markdown
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
            temp_md_path = Path(temp_md.name)
        
        # Get the wiki entry
        wiki_version = wiki_service.get_entry(title_or_id)
        if not wiki_version:
            return False
        
        # Create markdown content
        metadata = wiki_service._read_entry_metadata(title_or_id)
        if not metadata:
            return False
        markdown_content = f"""# {title_or_id}

**Author:** {wiki_version.author}  
**Created:** {metadata.created_at}  
**Last Modified:** {metadata.last_modified}  
**Version:** {wiki_version.version}  
**Tags:** {', '.join(metadata.tags) if metadata.tags else 'None'}  
**Category:** {metadata.category}

---
{wiki_version.content}
"""
        # Write markdown to temp file
        temp_md_path.write_text(markdown_content, encoding='utf-8')
        
        # Try to convert to PDF using available tools
        try:
            # Try using weasyprint
            import weasyprint
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{title_or_id}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #333; border-bottom: 2px solid #333; }}
                    .metadata {{ background: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                    .metadata strong {{ color: #666; }}
                    pre {{ background: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                </style>
            </head>
            <body>
                <h1>{title_or_id}</h1>
                <div class="metadata">
                    <p><strong>Author:</strong> {wiki_version.author}</p>
                    <p><strong>Created:</strong> {metadata.created_at}</p>
                    <p><strong>Last Modified:</strong> {metadata.last_modified}</p>
                    <p><strong>Version:</strong> {wiki_version.version}</p>
                    <p><strong>Tags:</strong> {', '.join(metadata.tags) if metadata.tags else 'None'}</p>
                    <p><strong>Category:</strong> {metadata.category}</p>
                </div>
                <div class="content">
                    {markdown_content.split('---', 2)[-1].strip()}
                </div>
            </body>
            </html>
            """
            
            weasyprint.HTML(string=html_content).write_pdf(str(output_path))
            return True
            
        except ImportError:
            # Try using markdown-pdf or other tools
            try:
                import subprocess
                result = subprocess.run([
                    'pandoc', str(temp_md_path), '-o', str(output_path)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True
                else:
                    print(f"Pandoc failed: {result.stderr}")
                    return False
                    
            except (ImportError, FileNotFoundError):
                print("PDF export requires pandoc or weasyprint to be installed")
                return False
        
        finally:
            # Clean up temp file
            if temp_md_path.exists():
                temp_md_path.unlink()
                
    except Exception as e:
        print(f"PDF export failed: {e}")
        return False


def _export_to_html(wiki_service, title_or_id: str, output_path: Path) -> bool:
    """Export wiki page to HTML format using an external template."""
    try:
        # Get the wiki entry
        wiki_version = wiki_service.get_entry(title_or_id)
        if not wiki_version:
            return False

        # Get metadata
        metadata = wiki_service._read_entry_metadata(title_or_id)
        if not metadata:
            return False

        # Prepare data for template
        template_data = {
            "title_or_id": title_or_id,
            "wiki_version": {
                "author": wiki_version.author,
                "version": wiki_version.version
            },
            "metadata": {
                "created_at": metadata.created_at,
                "last_modified": metadata.last_modified,
                "category": metadata.category,
                "tags": metadata.tags
            },
            "content_html": _markdown_to_html(wiki_version.content)
        }

        # Load and render template
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        env = Environment(
            loader=FileSystemLoader("src/cli/templates"),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template('wiki_export_template.html')
        html_content = template.render(template_data)

        # Write HTML file
        output_path.write_text(html_content, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"HTML export failed: {e}")
        return False


def _markdown_to_html(markdown_text: str) -> str:
    """Convert markdown text to HTML."""
    try:
        import markdown
        return markdown.markdown(markdown_text, extensions=['extra', 'codehilite'])
    except ImportError:
        # Simple markdown conversion if markdown library not available
        html = markdown_text
        # Convert headers
        for level in range(1, 7):
            html = html.replace(f'{"#" * level} ', f'<h{level}>')
            html = html.replace(f'\n{"#" * level} ', f'</h{level}>\n<h{level}>')
        # Convert code blocks
        html = html.replace('```', '<pre><code>')
        html = html.replace('\n```\n', '</code></pre>')
        # Convert inline code
        html = html.replace('`', '<code>')
        html = html.replace('<code>', '</code>')
        # Convert bold
        html = html.replace('**', '<strong>')
        html = html.replace('<strong>', '</strong>')
        # Convert italic
        html = html.replace('*', '<em>')
        html = html.replace('<em>', '</em>')
        # Convert links
        import re
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        return html


@app.command()
def list():
    """List all wiki pages."""
    from src.cli.service_utils import get_wiki_service
    wiki_service = get_wiki_service()
    
    try:
        # Note: WikiService doesn't have a direct list method, so we'll need to implement it
        # For now, we'll show the wiki directory contents
        import os
        wiki_dir = wiki_service._wiki_directory
        if wiki_dir.exists():
            entries = [d.name for d in wiki_dir.iterdir() if d.is_dir()]
            if entries:
                typer.echo(f"Available wiki pages ({len(entries)}):")
                for entry in sorted(entries):
                    typer.echo(f"  - {entry}")
            else:
                typer.echo("No wiki pages found.")
        else:
            typer.echo("Wiki directory does not exist.")
    except Exception as e:
        typer.echo(f"Error listing wiki pages: {e}")
        raise typer.Exit(1)


@app.command()
def approve(
    entry_name: str = typer.Argument(..., help="The name of the wiki entry."),
    proposal_id: str = typer.Argument(..., help="The ID of the edit proposal to approve."),
):
    """Approve an edit proposal."""
    from src.cli.service_utils import get_wiki_service
    wiki_service = get_wiki_service()
    
    try:
        success = wiki_service.approve(entry_name, proposal_id)
        if success:
            typer.echo(f"Successfully approved and applied proposal '{proposal_id}' for entry '{entry_name}'.")
        else:
            typer.echo(f"Failed to approve proposal '{proposal_id}' for entry '{entry_name}'.")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error approving edit proposal: {e}")
        raise typer.Exit(1)


@app.command(name="list")
def list_proposals():
    """List all pending edit proposals."""
    from src.cli.service_utils import get_wiki_service
    wiki_service = get_wiki_service()
    
    try:
        proposals = wiki_service.list_pending_proposals()
        if proposals:
            typer.echo(f"Pending edit proposals ({len(proposals)}):")
            for proposal in proposals:
                typer.echo(f"  Entry: {proposal['entry_name']}")
                typer.echo(f"    Proposal ID: {proposal['proposal_id']}")
                typer.echo(f"    Author: {proposal['author']}")
                typer.echo(f"    Timestamp: {proposal['timestamp']}")
                typer.echo(f"    Summary: {proposal['change_summary']}")
                typer.echo()
        else:
            typer.echo("No pending edit proposals found.")
    except Exception as e:
        typer.echo(f"Error listing edit proposals: {e}")
        raise typer.Exit(1)


@app.command(name="reject")
def reject_proposal(
    entry_name: str = typer.Argument(..., help="The name of the wiki entry."),
    proposal_id: str = typer.Argument(..., help="The ID of the edit proposal to reject."),
):
    """Reject an edit proposal."""
    from src.cli.service_utils import get_wiki_service
    wiki_service = get_wiki_service()
    
    try:
        success = wiki_service.reject(entry_name, proposal_id)
        if success:
            typer.echo(f"Successfully rejected proposal '{proposal_id}' for entry '{entry_name}'.")
        else:
            typer.echo(f"Failed to reject proposal '{proposal_id}' for entry '{entry_name}'.")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error rejecting edit proposal: {e}")
        raise typer.Exit(1)