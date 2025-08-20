# -*- coding: utf-8 -*-
"""Wiki commands for the DAIP-LIVE CLI."""

import typer
import logging
from typing import Optional
from pathlib import Path

app = typer.Typer(
    name="wiki",
    help="Commands for managing wiki.",
    add_completion=False,
)


@app.command()
def create(
    title: str = typer.Argument(..., help="The title of the wiki page."),
    content: str = typer.Option("", "--content", "-c", help="The content of the wiki page."),
    file: str = typer.Option(None, "--file", "-f", help="The file containing the content of the wiki page."),
):
    """Create a new wiki page."""
    # Get the wiki service
    from src.cli.main import get_wiki_service
    wiki_service = get_wiki_service()
    
    # Read content from file if provided
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            typer.echo(f"Error reading file {file}: {e}")
            raise typer.Exit(1)
    
    # Create the wiki page using the service
    try:
        # Use create_entry method with default values for author_role, tags, and category
        wiki_version = wiki_service.create_entry(
            entry_name=title,
            content=content,
            author_role="cli_user",  # Default author role for CLI
            tags=[],  # No tags by default
            category="general"  # Default category
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
    # Get the wiki service
    from src.cli.main import get_wiki_service
    wiki_service = get_wiki_service()
    
    # Get the wiki page using the service
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
    # Get the wiki service
    from src.cli.main import get_wiki_service
    wiki_service = get_wiki_service()
    
    # Read content from file if provided
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            typer.echo(f"Error reading file {file}: {e}")
            raise typer.Exit(1)
    
    # Edit the wiki page using the service
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
    # Get the wiki service
    from src.cli.main import get_wiki_service
    wiki_service = get_wiki_service()
    
    # Confirm deletion if not already confirmed
    if not confirm:
        if not typer.confirm(f"Are you sure you want to delete the wiki page '{title_or_id}'? This action cannot be undone."):
            typer.echo("Deletion cancelled.")
            raise typer.Exit(0)
    
    # Delete the wiki page
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
    # Get the wiki service
    from src.cli.main import get_wiki_service
    wiki_service = get_wiki_service()
    
    # Search for wiki pages
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
    
    # Get the wiki service
    from src.cli.main import get_wiki_service
    wiki_service = get_wiki_service()
    
    # Generate output path if not provided
    if not output:
        output = f"{title_or_id}.{format}"
    
    output_path = Path(output)
    
    # Validate format
    supported_formats = ["markdown", "json", "html", "pdf"]
    if format.lower() not in supported_formats:
        console.print(f"[red]❌ Unsupported format: {format}[/red]")
        console.print(f"[yellow]Supported formats: {', '.join(supported_formats)}[/yellow]")
        raise typer.Exit(1)
    
    # Export the wiki page
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
        logger.error(f"Wiki export failed: {e}", exc_info=True)
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
    """Export wiki page to HTML format."""
    try:
        # Get the wiki entry
        wiki_version = wiki_service.get_entry(title_or_id)
        if not wiki_version:
            return False
        
        # Get metadata
        metadata = wiki_service._read_entry_metadata(title_or_id)
        if not metadata:
            return False
        
        # Create HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_or_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f9f9f9;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        .metadata {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
            border-left: 4px solid #3498db;
        }}
        .metadata dt {{
            font-weight: bold;
            color: #2c3e50;
            margin-top: 10px;
        }}
        .metadata dd {{
            margin-left: 0;
            margin-bottom: 5px;
        }}
        .content {{
            margin-top: 30px;
        }}
        .content h2, .content h3 {{
            color: #2c3e50;
        }}
        .content code {{
            background: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        .content pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            border: 1px solid #e9ecef;
        }}
        .content blockquote {{
            border-left: 4px solid #3498db;
            margin: 0;
            padding-left: 20px;
            color: #666;
        }}
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 5px;
        }}
        .tag {{
            background: #3498db;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title_or_id}</h1>
        
        <div class="metadata">
            <dl>
                <dt>Author</dt>
                <dd>{wiki_version.author}</dd>
                
                <dt>Created</dt>
                <dd>{metadata.created_at}</dd>
                
                <dt>Last Modified</dt>
                <dd>{metadata.last_modified}</dd>
                
                <dt>Version</dt>
                <dd>{wiki_version.version}</dd>
                
                <dt>Category</dt>
                <dd>{metadata.category}</dd>
                
                <dt>Tags</dt>
                <dd>
                    <div class="tags">
                        {"".join(f'<span class="tag">{tag}</span>' for tag in metadata.tags)}
                    </div>
                </dd>
            </dl>
        </div>
        
        <div class="content">
            {_markdown_to_html(wiki_version.content)}
        </div>
        
        <div class="footer">
            <p>Exported from DAIP-LIVE Wiki System</p>
            <p>Generated on {metadata.last_modified}</p>
        </div>
    </div>
</body>
</html>"""
        
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
    # Get the wiki service
    from src.cli.main import get_wiki_service
    wiki_service = get_wiki_service()
    
    # List wiki pages
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
    proposal_id: str = typer.Argument(..., help="The ID of the edit proposal to approve."),
):
    """Approve an edit proposal."""
    # Get the wiki service
    from src.cli.main import get_wiki_service
    wiki_service = get_wiki_service()
    
    # Approve the edit proposal
    try:
        # Note: WikiService doesn't have a direct approve method, so we'll need to implement it
        # For now, we'll show a message that this functionality is not yet implemented
        typer.echo(f"Approve functionality for proposal '{proposal_id}' is not yet implemented.")
        typer.echo("Please manually apply the edit proposal.")
    except Exception as e:
        typer.echo(f"Error approving edit proposal: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()