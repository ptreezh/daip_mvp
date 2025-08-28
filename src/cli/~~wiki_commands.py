     1 # -*- coding: utf-8 -*-
     """@Time : 2025-07-19 03:00:00
     2 @Author : DAIP-LIVE Team
     3 @File : wiki_commands.py
     4 @Description: Wiki management commands for the DAIP-LIVE CLI.
     5 """
     6
     7 import asyncio
     8 import jsonimport logging
     9 import tempfile
    10 from pathlib import Pathfrom typing import Any, Dict, List, Optional
    11
    12 import typer
    13 from rich.console import Console
    14 from rich.table import Tablefrom rich.panel import Panel
    15
    16 # --- App Definitions ---
    17 app = typer.Typer(help="Wiki management commands for DAIP-LIVE.")# Sub-app for collaborative features
    18 collaborate_app = typer.Typer(help="Collaborative wiki features.")
    19 app.add_typer(collaborate_app, name="collaborate")
    20
    21 # Sub-app for proposal managementproposal_app = typer.Typer(help="Edit proposal management.")
    22 app.add_typer(proposal_app, name="proposal")
    23
    24 # --- Helper Functions ---
    25
    26 def _export_to_pdf(wiki_service, title_or_id: str, output_path: Path) -> bool: """Export wiki page to PDF format."""    try: # First
       export to markdown
    27         import tempfile        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
    28             temp_md_path = Path(temp_md.name)
    29         # Get the wiki entry        wiki_version = wiki_service.get_entry(title_or_id) if not wiki_version:
    30             return False
    31
    32         # Create markdown content metadata = wiki_service._read_entry_metadata(title_or_id)        if not metadata:
    33             return False        markdown_content = f"""# {title_or_id}
    34
    35 **Author:** {wiki_version.author}**Created:** {metadata.created_at}
    36 **Last Modified:** {metadata.last_modified}
    37 **Version:** {wiki_version.version}
    38 **Tags:** {', '.join(metadata.tags) if metadata.tags else 'None'}**Category:** {metadata.category}
    39
    40 ---{wiki_version.content}
    41 """ # Write markdown to temp file        temp_md_path.write_text(markdown_content, encoding='utf-8')
    42
    43         # Try to convert to PDF using available tools        try:
    44             # Try using weasyprint
    45             import weasyprint html_content = f""" <!DOCTYPE html>            <html>            <head>
    46                 <meta charset="utf-8">                <title>{title_or_id}</title>                <style>                    body {{
       font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}                    h1 {{ color: #333; border-bottom: 2px solid #333;
       }}
    47                     .metadata {{ background: #f5f5f5; padding:10px; border-radius: 5px; margin-bottom: 20px; }} .metadata strong {{
       color: #666; }} pre {{ background: #f8f8f8; padding:10px; border-radius: 5px; overflow-x: auto; }}
    48                 </style> </head> <body>                <h1>{title_or_id}</h1>                <div class="metadata">
       <p><strong>Author:</strong> {wiki_version.author}</p>
    49                     <p><strong>Created:</strong> {metadata.created_at}</p>
    50                     <p><strong>Last Modified:</strong> {metadata.last_modified}</p> <p><strong>Version:</strong>
       {wiki_version.version}</p>
    51                     <p><strong>Tags:</strong> {', '.join(metadata.tags) if metadata.tags else 'None'}</p> <p><strong>Category:</strong>
       {metadata.category}</p>
    52                 </div>                <div class="content"> {markdown_content.split('---', 2)[-1].strip()}                </div>
       </body> </html> """
    53             weasyprint.HTML(string=html_content).write_pdf(str(output_path))            return True except ImportError: # Try using
       markdown-pdf or other tools            try:
    54                 import subprocess
    55                 result = subprocess.run([
    56                     'pandoc', str(temp_md_path), '-o', str(output_path)                ], capture_output=True, text=True) if
       result.returncode == 0:
    57                     return True
    58                 else:
    59                     print(f"Pandoc failed: {result.stderr}")                    return False            except (ImportError,
       FileNotFoundError):
    60                 print("PDF export requires pandoc or weasyprint to be installed")                return False        finally: # Clean up
       temp file            if temp_md_path.exists():
    61                 temp_md_path.unlink() except Exception as e:        print(f"PDF export failed: {e}") return False
    62
    63
    64 def _export_to_html(wiki_service, title_or_id: str, output_path: Path) -> bool:
    65     """Export wiki page to HTML format."""
    66     try: # Get the wiki entry
    67         wiki_version = wiki_service.get_entry(title_or_id)
    68         if not wiki_version:            return False
    69
    70         # Get metadata metadata = wiki_service._read_entry_metadata(title_or_id)        if not metadata:
    71             return False        # Create HTML content
    72         html_content = f"""<!DOCTYPE html>
    73 <html lang="en">
    74 <head> <meta charset="utf-8">
    75     <meta name="viewport" content="width=device-width, initial-scale=1.0">
    76     <title>{title_or_id}</title>
    77     <style>        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;            margin:0;
       padding:20px;            line-height: 1.6;            color: #333; background-color: #f9f9f9;
    78         }} .container {{            max-width: 800px;            margin: 0 auto;            background: white;            padding:40px;
       border-radius: 8px;
    79             box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
    80         h1 {{            color: #2c3e50;
    81             border-bottom: 3px solid #3498db;
    82             padding-bottom: 10px;
    83             margin-bottom: 30px; }}        .metadata {{ background: #ecf0f1;
    84             padding:20px;            border-radius: 6px;
    85             margin-bottom: 30px;
    86             border-left: 4px solid #3498db;
    87         }}        .metadata dt {{            font-weight: bold;
    88             color: #2c3e50; margin-top:10px;        }}
    89         .metadata dd {{
    90             margin-left: 0;
    91             margin-bottom: 5px;
    92         }}        .content {{
    93             margin-top: 30px; }}        .content h2, .content h3 {{ color: #2c3e50;
    94         }} .content code {{
    95             background: #f8f9fa;
    96             padding:2px 4px;
    97             border-radius: 3px;
    98             font-family: 'Consolas', 'Monaco', monospace;
    99         }}        .content pre {{
   100             background: #f8f9fa;
   101             padding: 15px; border-radius: 6px;
   102             overflow-x: auto;
   103             border: 1px solid #e9ecef; }}
   104         .content blockquote {{
   105             border-left: 4px solid #3498db;            margin:0;
   106             padding-left: 20px; color: #666;        }}
   107         .tags {{
   108             display: flex;            flex-wrap: wrap;            gap:5px; margin-top:5px; }}        .tag {{            background:
       #3498db;
   109             color: white;
   110             padding:2px 8px;
   111             border-radius: 12px; font-size: 0.8em;
   112         }} </style>
   113 </head>
   114 <body> <div class="container">
   115         <h1>{title_or_id}</h1> <div class="metadata">            <dl>
   116                 <dt>Author</dt>                <dd>{wiki_version.author}</dd>
   117
   118                 <dt>Created</dt> <dd>{metadata.created_at}</dd>
   119                 <dt>Last Modified</dt>
   120                 <dd>{metadata.last_modified}</dd> <dt>Version</dt>
   121                 <dd>{wiki_version.version}</dd>
   122
   123                 <dt>Category</dt> <dd>{metadata.category}</dd>
   124                 <dt>Tags</dt>
   125                 <dd>                    <div class="tags"> {"".join(f'<span class="tag">{tag}</span>' for tag in metadata.tags)} </div>
   126                 </dd>
   127             </dl>
   128         </div>        <div class="content">
   129             {_markdown_to_html(wiki_version.content)}
   130         </div>
   131
   132         <div class="footer">            <p>Exported from DAIP-LIVE Wiki System</p>
   133             <p>Generated on {metadata.last_modified}</p> </div> </div></body>
   134 </html>""" # Write HTML file
   135         output_path.write_text(html_content, encoding='utf-8')        return True    except Exception as e:
   136         print(f"HTML export failed: {e}")
   137         return False
   138
   139
   140 def _markdown_to_html(markdown_text: str) -> str:
   141     """Convert markdown text to HTML.""" try: import markdown return markdown.markdown(markdown_text, extensions=['extra', 'codehilite'
       ])    except ImportError:        # Simple markdown conversion if markdown library not available        html = markdown_text
   142         # Convert headers for level in range(1, 7):
   143             html = html.replace(f'{"#" * level} ', f'<h{level}>') html = html.replace(f'\n{"#" * level} ', f'</h{level}>\n<h{level}>')
       # Convert code blocks
   144         html = html.replace('```', '<pre><code>')
   145         html = html.replace('\n
  `\n', '</code></pre>')
  Convert inline code        html = html.replace('`', '<code>')
          html = html.replace('<code>', '</code>')
  Convert bold html = html.replace('**', '<strong>')        html = html.replace('<strong>', '</strong>')        # Convert italic
          html = html.replace('*', '<em>') html = html.replace('<em>', '</em>') # Convert links        import re
          html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)        return html

  @app.command()def create( title: str = typer.Argument(..., help="The title of the new wiki page."), content: str = typer.Option("", "--content",
  "-c", help="The initial content of the wiki page."),
      file: str = typer.Option(None, "--file", "-f", help="The file containing the initial content of the wiki page."), tags: str = typer.Option("",
  "--tags", "-t", help="Comma-separated list of tags for the wiki page."),
      category: str = typer.Option("general", "--category", "-c", help="The category for the wiki page."),
  ):
      """Create a new wiki page."""
  Get the wiki service    from src.cli.main import get_wiki_service    wiki_service = get_wiki_service()

  Read content from file if provided
      if file:
          try:            with open(file, 'r', encoding='utf-8') as f:
                  content = f.read() except Exception as e:            typer.echo(f"Error reading file {file}: {e}")            raise typer.Exit(1)

  Parse tags
      tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
  Create the wiki page using the service try:        wiki_version = wiki_service.create_entry(            entry_name=title,
              content=content,
              author_role="cli_user",  # Default author role for CLI            tags=tag_list,            category=category  # Default category
          ) if wiki_version:
              typer.echo(f"Wiki page '{title}' created successfully with ID: {wiki_version.entry_name}")
          else:
              typer.echo(f"Failed to create wiki page '{title}'")
              raise typer.Exit(1) from e
      except Exception as e:        typer.echo(f"Error creating wiki page: {e}")
          raise typer.Exit(1) from e

  @app.command()def view( title_or_id: str = typer.Argument(..., help="The title or ID of the wiki page."),
  ):    """View a wiki page."""
  Get the wiki service    from src.cli.main import get_wiki_service wiki_service = get_wiki_service()

  Get the wiki page using the service
      try:        wiki_version = wiki_service.get_entry(entry_name=title_or_id) if wiki_version:            typer.echo(f"Wiki page
  '{wiki_version.entry_name}':")
              typer.echo(f"Content: {wiki_version.content}") typer.echo(f"Author: {wiki_version.author}") typer.echo(f"Created at:
  {wiki_version.timestamp}") typer.echo(f"Change summary: {wiki_version.change_summary}")            typer.echo(f"Version: {wiki_version.version}")
  else:
              typer.echo(f"Wiki page '{title_or_id}' not found.") raise typer.Exit(1) except Exception as e:
          typer.echo(f"Error viewing wiki page: {e}") raise typer.Exit(1)@app.command()
  def edit(
      title_or_id: str = typer.Argument(..., help="The title or ID of the wiki page to edit."),    content: str = typer.Option("", "--content",
  "-c", help="The new content of the wiki page."),
      file: str = typer.Option(None, "--file", "-f", help="The file containing the new content of the wiki page."),
  ): """Edit an existing wiki page."""
  Get the wiki service    from src.cli.main import get_wiki_service    wiki_service = get_wiki_service()

  Read content from file if provided
      if file:
          try:
              with open(file, 'r', encoding='utf-8') as f:                content = f.read() except Exception as e:            typer.echo(f"Error
  reading file {file}: {e}") raise typer.Exit(1)    # Edit the wiki page using the service
      try:        # Use propose_edit method to create an edit proposal proposal_id = wiki_service.propose_edit( entry_name=title_or_id,
  new_content=content,
              author_role="cli_user",
              change_summary="CLI edit"
          ) if proposal_id:
              typer.echo(f"Edit proposal for '{title_or_id}' created successfully with ID: {proposal_id}")            typer.echo("Note: This edit is
  proposed and needs to be applied by a wiki administrator.")
          else:
              typer.echo(f"Failed to create edit proposal for '{title_or_id}'")            raise typer.Exit(1)
      except Exception as e:
          typer.echo(f"Error editing wiki page: {e}")
          raise typer.Exit(1) from e

  @app.command()
  def delete(
      title_or_id: str = typer.Argument(..., help="The title or ID of the wiki page to delete."), confirm: bool = typer.Option(False, "--confirm",
  "-y", help="Skip confirmation prompt."),):
      """Delete a wiki page."""    # Get the wiki service
      from src.cli.main import get_wiki_service    wiki_service = get_wiki_service()
  Confirm deletion if not already confirmed
      if not confirm:
          if not typer.confirm(f"Are you sure you want to delete the wiki page '{title_or_id}'? This action cannot be undone."):
  typer.echo("Deletion cancelled.") raise typer.Exit(0)    # Delete the wiki page    try: success = wiki_service.delete_entry(title_or_id) if
  success: typer.echo(f"Wiki page '{title_or_id}' deleted successfully.")        else: typer.echo(f"Failed to delete wiki page '{title_or_id}'.")
              raise typer.Exit(1) from e
      except Exception as e:        typer.echo(f"Error deleting wiki page: {e}")        raise typer.Exit(1)@app.command()
  def search(
      keywords: str = typer.Argument(..., help="The keywords to search for."),
      limit: int = typer.Option(3, "--limit", "-l", help="Maximum number of results to return."),
  ): """Search for wiki pages."""
  Get the wiki service    from src.cli.main import get_wiki_service
      wiki_service = get_wiki_service()
  Search for wiki pages    try: results = wiki_service.search(query=keywords, top_k=limit)        if results:            typer.echo(f"Search results
  for '{keywords}':") for i, result in enumerate(results, 1): typer.echo(f"{i}. {result}")
          else:            typer.echo(f"No results found for '{keywords}'.")    except Exception as e:        typer.echo(f"Error searching wiki
  pages: {e}")
          raise typer.Exit(1) from e

  @app.command()def export( title_or_id: str = typer.Argument(..., help="The title or ID of the wiki page to export."), format: str =
  typer.Option("markdown", "--format", "-f", help="Export format (markdown, json, html, pdf)."),    output: str = typer.Option(None, "--output",
  "-o", help="Output file path. If not specified, uses title with format extension."),
  ): """Export a wiki page to various formats."""    from rich.console import Console from rich.panel import Panel    from pathlib import Path
  console = Console()
  Get the wiki service    from src.cli.main import get_wiki_service    wiki_service = get_wiki_service()

  Generate output path if not provided
      if not output:
          output = f"{title_or_id}.{format}" output_path = Path(output)

  Validate format supported_formats = ["markdown", "json", "html", "pdf"]    if format.lower() not in supported_formats:
          console.print(f"[red]❌ Unsupported format: {format}[/red]")
          console.print(f"[yellow]Supported formats: {', '.join(supported_formats)}[/yellow]")
          raise typer.Exit(1) from e
  Export the wiki page
      try:        if format.lower() == "pdf":
  PDF export requires additional processing success = _export_to_pdf(wiki_service, title_or_id, output_path)
          elif format.lower() == "html": # HTML export requires additional processing
              success = _export_to_html(wiki_service, title_or_id, output_path)
          else:
  Use the built-in export functionality for markdown and json
              success = wiki_service.export_entry(title_or_id, str(output_path), format.lower())        if success:
              console.print(f"[green]SUCCESS: Wiki page '{title_or_id}' exported successfully to {output_path}[/green]")            # Show file size
  if output_path.exists():                size = output_path.stat().st_size
                  console.print(f"[dim]File size: {size:,} bytes[/dim]")
          else:
              console.print(f"[red]ERROR: Failed to export wiki page '{title_or_id}'[/red]")            raise typer.Exit(1)
      except Exception as e:        console.print(f"[red]ERROR: Error exporting wiki page: {e}[/red]")        logging.error(f"Wiki export failed:
  {e}", exc_info=True) raise typer.Exit(1)

  @collaborate_app.command("generate")
  def generate_content(
      topic: str = typer.Argument(..., help="Topic for content generation"),    content_type: str = typer.Option("article", "--type", "-t",
  help="Content type (article, debate_summary, analysis, tutorial, overview)"),
      audience: str = typer.Option("general", "--audience", "-a", help="Target audience (beginner, intermediate, expert, general)"),
      scope: str = typer.Option("overview", "--scope", "-s", help="Content scope (overview, detailed, comprehensive)"),    entry_name: str =
  typer.Option(None, "--entry", "-e", help="Wiki entry name (defaults to topic)"),    save: bool = typer.Option(True, "--save/--no-save", help="Save
  generated content to wiki"),
  ):
      """Generate wiki content using AI debate and collaboration."""    from rich.console import Console
      from rich.progress import Progress, SpinnerColumn, TextColumn
      import asyncio

      console = Console()
      try:        console.print(f"[bold blue]🤖 Generating wiki content for: {topic}[/bold blue]")        console.print(f"[dim]Content type:
  {content_type}, Audience: {audience}, Scope: {scope}[/dim]")

  Import content generator from src.core_services.wiki_content_generator import WikiContentGenerator, ContentGenerationRequest # Create content
  generation request
          request = ContentGenerationRequest( topic=topic,            content_type=content_type, target_audience=audience,            scope=scope,
           special_requirements=["AI-generated", "debate-based", "collaborative"]        ) # Initialize content generator generator =
  WikiContentGenerator()
  Generate content with progress indicator
          with Progress(
              SpinnerColumn(),
              TextColumn("[progress.description]{task.description}"),
              console=console        ) as progress:
              task = progress.add_task("Generating content...", total=None) # Run async generation            result =
  asyncio.run(generator.generate_wiki_content(request)) progress.update(task, completed=True) if not result.success:
              console.print(f"[red]❌ Content generation failed: {result.error_message}[/red]")            raise typer.Exit(1)
  Display generation results console.print(f"[green]✅ Content generated successfully![/green]") console.print(f"[dim]Content length:
  {len(result.generated_content)} characters[/dim]")        console.print(f"[dim]Generation time: {result.generation_time:.2f} seconds[/dim]")
   # Show quality metrics if result.quality_metrics:            console.print("\n[bold]📊 Quality Metrics:[/bold]")
              metrics_table = Table(show_header=False, box=None) metrics_table.add_column("Metric", style="cyan")
              metrics_table.add_column("Score", style="magenta")            for metric, score in result.quality_metrics.items():                if
  isinstance(score, (int, float)):                    metrics_table.add_row(metric.replace("_", " ").title(), f"{score:.2f}")

              console.print(metrics_table)
  Show preview of generated content        console.print("\n[bold]📝 Content Preview:[/bold]")
          preview_lines = result.generated_content.split('\n')[:10] for line in preview_lines:
              if line.strip():
                  console.print(f"[dim]{line}[/dim]")
          if len(result.generated_content.split('\n')) > 10:            console.print("[dim]... (content truncated for preview)[/dim]")        #
  Save to wiki if requested        if save:            entry_name = entry_name or topic
              console.print(f"\n[bold blue]💾 Saving to wiki entry: {entry_name}[/bold blue]")            save_result =
  asyncio.run(generator.generate_and_save_wiki_entry(
                  request, entry_name, "ai_content_generator"            )) if save_result["success"]:                console.print(f"[green]✅
  Content saved to wiki successfully![/green]") console.print(f"[dim]Wiki version: {save_result.get('wiki_version', 'N/A')}[/dim]")            else:
  console.print(f"[red]❌ Failed to save to wiki: {save_result.get('error', 'Unknown error')}[/red]")
                  raise typer.Exit(1) from e
  Ask user if they want to see full content
          if typer.confirm("Would you like to see the full generated content?"): console.print(f"\n[bold]📄 Full Generated Content:[/bold]")
              console.print(Panel(result.generated_content, title=f"Generated Content: {topic}", border_style="blue"))

      except Exception as e:
          console.print(f"[red]❌ Error generating content: {e}[/red]")
          raise typer.Exit(1) from e@collaborate_app.command("capabilities")
  def show_capabilities():
      """Show wiki content generation capabilities."""    from rich.console import Console from rich.table import Table    from rich.panel import
  Panel
      from src.core_services.wiki_content_generator import WikiContentGenerator console = Console()    try:
          generator = WikiContentGenerator() capabilities = generator.get_content_generation_capabilities() console.print("[bold blue]🤖 Wiki
  Content Generation Capabilities[/bold blue]")        # Content types
          console.print("\n[bold]Content Types:[/bold]")
          types_table = Table(show_header=True, box=None)        types_table.add_column("Type", style="cyan")
          types_table.add_column("Description", style="dim") type_descriptions = {
              "article": "Structured article with introduction, sections, and conclusion",            "debate_summary": "Summary of debate with
  participant positions and consensus",            "analysis": "In-depth analysis with executive summary and recommendations",
              "tutorial": "Step-by-step tutorial with clear instructions",
              "overview": "General overview covering key points and insights"
          }        for content_type in capabilities["content_types"]: types_table.add_row(content_type.title(), type_descriptions.get(content_type,
  "No description")) console.print(types_table)
  Target audiences
          console.print("\n[bold]Target Audiences:[/bold]") audience_table = Table(show_header=True, box=None)
  audience_table.add_column("Audience", style="cyan")
          audience_table.add_column("Description", style="dim") audience_descriptions = {            "beginner": "Introductory content with basic
  concepts and simple language",
              "intermediate": "Content assuming some prior knowledge and experience", "expert": "Advanced content with technical details and depth",
             "general": "Balanced content suitable for all knowledge levels"        } for audience in capabilities["target_audiences"]:
              audience_table.add_row(audience.title(), audience_descriptions.get(audience, "No description"))        console.print(audience_table)
       # Quality metrics        console.print("\n[bold]Quality Metrics:[/bold]")
          metrics_table = Table(show_header=True, box=None)        metrics_table.add_column("Metric", style="cyan")
          metrics_table.add_column("Description", style="dim") metric_descriptions = {            "structure_score": "Measures content organization
  and logical flow", "coherence_score": "Evaluates textual coherence and readability",
              "completeness_score": "Assesses coverage of key topics and points", "participant_diversity": "Measures diversity of perspectives and
  contributions", "consensus_strength": "Evaluates strength of consensus and agreement"
          }        for metric in capabilities["quality_metrics"]: metrics_table.add_row(metric.replace("_", " ").title(),
  metric_descriptions.get(metric, "No description"))        console.print(metrics_table) # System info
          console.print("\n[bold]System Information:[/bold]")        info_table = Table(show_header=False, box=None)
  info_table.add_column("Property", style="cyan")
          info_table.add_column("Value", style="magenta")        info_table.add_row("Max Participants", str(capabilities["max_participants"]))
          info_table.add_row("Estimated Generation Time", capabilities["estimated_generation_time"])

          console.print(info_table)        console.print("\n[dim]✨ Content is generated through structured AI debates, ensuring multiple
  perspectives and high-quality output.[/dim]") except Exception as e:        console.print(f"[red]❌ Error showing capabilities: {e}[/red]")
  raise typer.Exit(1) from e@collaborate_app.command("optimize")
  def optimize_intent(
      user_input: str = typer.Argument(..., help="User's raw input or request"),
      show_details: bool = typer.Option(False, "--details", "-d", help="Show detailed optimization process"),):
      """Optimize user intent for better wiki content generation."""
      from rich.console import Console from rich.table import Table
      from rich.panel import Panel    from rich.text import Text    import asyncio    console = Console()
      try:        console.print(f"[bold blue]🎯 Optimizing Intent for Wiki Generation[/bold blue]") console.print(f"[dim]Original input:
  {user_input}[/dim]")

  Import intent optimization from src.core_services.wiki_collaboration_simplified import IntentOptimizer # Create intent optimizer
          optimizer = IntentOptimizer() # Optimize intent        optimization_result = asyncio.run(optimizer.optimize_user_intent(user_input)) if
  not optimization_result["success"]: console.print(f"[red]❌ Intent optimization failed: {optimization_result.get('error', 'Unknown
  error')}[/red]")
              raise typer.Exit(1) from e # Display optimization results optimized_intent = optimization_result["optimized_intent"] confidence =
  optimization_result["confidence"]
          suggested_actions = optimization_result["suggested_actions"]
          console.print(f"\n[green]✅ Intent optimized successfully![/green]")
          console.print(f"[bold]Optimized Intent:[/bold]")
          console.print(f"[cyan]{optimized_intent}[/cyan]") console.print(f"[dim]Confidence: {confidence:.2f}[/dim]")

  Show suggested actions if suggested_actions: console.print(f"\n[bold]Suggested Actions:[/bold]")            actions_table =
  Table(show_header=False, box=None)
              actions_table.add_column("Action", style="cyan")
              actions_table.add_column("Priority", style="magenta")
              for i, action in enumerate(suggested_actions, 1):                priority = "High" if i <= 2 else "Medium" if i <= 4 else "Low"
  actions_table.add_row(action, priority)            console.print(actions_table)        # Show detailed process if requested
          if show_details:
              console.print(f"\n[bold]🔍 Optimization Details:[/bold]")

              details = optimization_result.get("optimization_details", {}) if "extracted_keywords" in details: console.print("[dim]Extracted
  Keywords:[/dim]")
                  keywords = ", ".join(details["extracted_keywords"])
                  console.print(f"[dim]{keywords}[/dim]")

              if "intent_category" in details:
                  console.print(f"[dim]Intent Category: {details['intent_category']}[/dim]")

              if "complexity_score" in details:
                  console.print(f"[dim]Complexity Score: {details['complexity_score']:.2f}[/dim]")

  Ask if user wants to generate content with optimized intent
          if typer.confirm("Would you like to generate wiki content with this optimized intent?"):            # Extract parameters from optimized
  intent
              topic = optimized_intent.split("about")[-1].strip() if "about" in optimized_intent else optimized_intent.split("for")[-1].strip()
        console.print(f"\n[bold]🚀 Generating content for: {topic}[/bold]")            # Import and run content generation            from
  src.core_services.wiki_content_generator import WikiContentGenerator, ContentGenerationRequest generator = WikiContentGenerator() request =
  ContentGenerationRequest(
                  topic=topic, content_type="article",  # Default type
                  target_audience="general", # Default audience                scope="overview",  # Default scope
  special_requirements=["intent-optimized", "ai-generated"]
              )
              result = asyncio.run(generator.generate_wiki_content(request)) if result.success:
                  console.print(f"[green]✅ Content generated with optimized intent![/green]") console.print(f"[dim]Content length:
  {len(result.generated_content)} characters[/dim]")
  Show preview
                  preview = result.generated_content[:500] + "..." if len(result.generated_content) >500 else result.generated_content
   console.print(f"\n[dim]Preview:[/dim]")
                  console.print(f"[dim]{preview}[/dim]")
              else:                console.print(f"[red]❌ Content generation failed: {result.error_message}[/red]") except Exception as e:
          console.print(f"[red]❌ Error optimizing intent: {e}[/red]")        raise typer.Exit(1)

  @app.command()def list():
      """List all wiki pages.""" # Get the wiki service
      from src.cli.main import get_wiki_service
      wiki_service = get_wiki_service() # List wiki pages
      try:
  Note: WikiService doesn't have a direct list method, so we'll need to implement it        # For now, we'll show the wiki directory contents
  import os        wiki_dir = wiki_service._wiki_directory if wiki_dir.exists():
              entries = [d.name for d in wiki_dir.iterdir() if d.is_dir()]            if entries:                typer.echo(f"Available wiki pages
  ({len(entries)}):") for entry in sorted(entries):
                      typer.echo(f"  - {entry}")            else: typer.echo("No wiki pages found.") else:
              typer.echo("Wiki directory does not exist.")
      except Exception as e:        typer.echo(f"Error listing wiki pages: {e}")
          raise typer.Exit(1) from e

  @app.command()def approve( entry_name: str = typer.Argument(..., help="The name of the wiki entry."), proposal_id: str = typer.Argument(...,
  help="The ID of the edit proposal to approve."),):
      """Approve an edit proposal."""
  Get the wiki service
      from src.cli.main import get_wiki_service    wiki_service = get_wiki_service()

  Approve the edit proposal
      try:
          success = wiki_service.approve(entry_name, proposal_id) if success: typer.echo(f"Successfully approved and applied proposal
  '{proposal_id}' for entry '{entry_name}'.") else:
              typer.echo(f"Failed to approve proposal '{proposal_id}' for entry '{entry_name}'.")
              raise typer.Exit(1) from e
      except Exception as e:
          typer.echo(f"Error approving edit proposal: {e}")
          raise typer.Exit(1) from e

  @proposal_app.command(name="list")
  def list_proposals():    """List all pending edit proposals.""" # Get the wiki service    from src.cli.main import get_wiki_service
      wiki_service = get_wiki_service()
  List pending proposals try:        proposals = wiki_service.list_pending_proposals()        if proposals:            typer.echo(f"Pending edit
  proposals ({len(proposals)}):") for proposal in proposals:                typer.echo(f"  Entry: {proposal['entry_name']}") typer.echo(f"
  Proposal ID: {proposal['proposal_id']}")                typer.echo(f"    Author: {proposal['author']}")                typer.echo(f"    Timestamp:
  {proposal['timestamp']}")
                  typer.echo(f"    Summary: {proposal['change_summary']}")                typer.echo()        else: typer.echo("No pending edit
  proposals found.")
      except Exception as e:
          typer.echo(f"Error listing edit proposals: {e}") raise typer.Exit(1)@proposal_app.command(name="reject")
  def reject_proposal( entry_name: str = typer.Argument(..., help="The name of the wiki entry."), proposal_id: str = typer.Argument(..., help="The
  ID of the edit proposal to reject."),):
      """Reject an edit proposal."""    # Get the wiki service
      from src.cli.main import get_wiki_service    wiki_service = get_wiki_service()

  Reject the edit proposal
      try:
          success = wiki_service.reject(entry_name, proposal_id)
          if success: typer.echo(f"Successfully rejected proposal '{proposal_id}' for entry '{entry_name}'.")
          else:            typer.echo(f"Failed to reject proposal '{proposal_id}' for entry '{entry_name}'.")
              raise typer.Exit(1) from e
      except Exception as e:        typer.echo(f"Error rejecting edit proposal: {e}")
          raise typer.Exit(1) from e@collaborate_app.command()
  def update(    request: str = typer.Argument(..., help="The update request in natural language."),
  ): """Collaboratively update a wiki entry based on a natural language request."""
      try:        # 导入必要的模块 from src.cli.main import get_wiki_service        from src.core_services.role_manager import RoleManager
          from src.core_services.wiki_collaboration_simplified import (
              SimpleIntentOptimizer,
              SimpleRoleCoordinator,
              SimpleExecutor,
              SimpleTaskCoordinator, CollaborationStorageManager
          ) # 获取wiki服务
          wiki_service = get_wiki_service() # 创建角色管理器实例
          role_manager = RoleManager()
  创建存储管理器        storage_manager = CollaborationStorageManager()
  创建协作组件 intent_optimizer = SimpleIntentOptimizer()        role_coordinator = SimpleRoleCoordinator(storage_manager, role_manager)
          executor = SimpleExecutor(wiki_service, storage_manager)
          task_coordinator = SimpleTaskCoordinator(intent_optimizer, role_coordinator, executor, storage_manager)
  发起协作任务        typer.echo(f"正在处理您的请求: '{request}'") typer.echo("这可能需要几秒钟时间...") task_id =
  task_coordinator.initiate_task(request)        # 获取任务状态        status = task_coordinator.get_task_status(task_id)

          if status.get("status") == "completed":
              typer.echo("✅ 词条更新已完成！")        elif status.get("status") == "failed":
              typer.echo("❌ 词条更新失败，请稍后重试。") raise typer.Exit(1)
          else: typer.echo("⚠️  词条更新状态未知。") except Exception as e:
          typer.echo(f"❌ 处理请求时出错: {e}") raise typer.Exit(1)@collaborate_app.command()
  def debate(    topic: str = typer.Argument(..., help="The topic to debate and create wiki content for."),):
      """Initiate a debate on a topic and generate wiki content from the discussion.""" try:        # 获取wiki服务
          from src.cli.main import get_wiki_service        wiki_service = get_wiki_service() # 发起协作编辑任务 typer.echo(f"正在为话题 '{topic}'
  发起辩论...")        result = wiki_service.initiate_collaborative_edit(topic)

          if "error" in result:            typer.echo(f"[ERROR] 发起辩论失败: {result['error']}")            raise typer.Exit(1)
          else: typer.echo(f"[SUCCESS] 辩论已发起: {result['message']}")            typer.echo(f"   话题: {result['topic']}")
              typer.echo(f"   会话ID: {result['session_id']}") except Exception as e:        typer.echo(f"[ERROR] 处理请求时出错: {e}") raise
  typer.Exit(1)

  if __name__ == "__main__": app()
