# -*- coding: utf-8 -*-
"""@Time    : 2025-07-19 03:00:00
@Author  : DAIP-LIVE Team
@File    : collaborate_commands.py
@Description: Collaborative wiki features for the DAIP-LIVE CLI.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import asyncio

app = typer.Typer(help="Collaborative wiki features.")

@app.command("generate")
def generate_content(
    topic: str = typer.Argument(..., help="Topic for content generation"),
    content_type: str = typer.Option("article", "--type", "-t", help="Content type (article, debate_summary, analysis, tutorial, overview)"),
    audience: str = typer.Option("general", "--audience", "-a", help="Target audience (beginner, intermediate, expert, general)"),
    scope: str = typer.Option("overview", "--scope", "-s", help="Content scope (overview, detailed, comprehensive)"),
    entry_name: str = typer.Option(None, "--entry", "-e", help="Wiki entry name (defaults to topic)"),
    save: bool = typer.Option(True, "--save/--no-save", help="Save generated content to wiki"),
):
    """Generate wiki content using AI debate and collaboration."""
    console = Console()
    
    try:
        console.print(f"[bold blue]🤖 Generating wiki content for: {topic}[/bold blue]")
        console.print(f"[dim]Content type: {content_type}, Audience: {audience}, Scope: {scope}[/dim]")
        
        # Import content generator
        from src.core_services.wiki_content_generator import WikiContentGenerator, ContentGenerationRequest
        
        # Create content generation request
        request = ContentGenerationRequest(
            topic=topic,
            content_type=content_type,
            target_audience=audience,
            scope=scope,
            special_requirements=["AI-generated", "debate-based", "collaborative"]
        )
        
        # Initialize content generator
        generator = WikiContentGenerator()
        
        # Generate content with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating content...", total=None)
            
            # Run async generation
            result = asyncio.run(generator.generate_wiki_content(request))
            progress.update(task, completed=True)
        
        if not result.success:
            console.print(f"[red]❌ Content generation failed: {result.error_message}[/red]")
            raise typer.Exit(1)
        
        # Display generation results
        console.print(f"[green]✅ Content generated successfully![/green]")
        console.print(f"[dim]Content length: {len(result.generated_content)} characters[/dim]")
        console.print(f"[dim]Generation time: {result.generation_time:.2f} seconds[/dim]")
        
        # Show quality metrics
        if result.quality_metrics:
            console.print("\n[bold]📊 Quality Metrics:[/bold]")
            metrics_table = Table(show_header=False, box=None)
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Score", style="magenta")
            
            for metric, score in result.quality_metrics.items():
                if isinstance(score, (int, float)):
                    metrics_table.add_row(metric.replace("_", " ").title(), f"{score:.2f}")
            
            console.print(metrics_table)
        
        # Show preview of generated content
        console.print("\n[bold]📝 Content Preview:[/bold]")
        preview_lines = result.generated_content.split('\n')[:10]
        for line in preview_lines:
            if line.strip():
                console.print(f"[dim]{line}[/dim]")
        
        if len(result.generated_content.split('\n')) > 10:
            console.print("[dim]... (content truncated for preview)[/dim]")
        
        # Save to wiki if requested
        if save:
            entry_name = entry_name or topic
            console.print(f"\n[bold blue]💾 Saving to wiki entry: {entry_name}[/bold blue]")
            
            save_result = asyncio.run(generator.generate_and_save_wiki_entry(
                request, entry_name, "ai_content_generator"
            ))
            
            if save_result["success"]:
                console.print(f"[green]✅ Content saved to wiki successfully![/green]")
                console.print(f"[dim]Wiki version: {save_result.get('wiki_version', 'N/A')}[/dim]")
            else:
                console.print(f"[red]❌ Failed to save to wiki: {save_result.get('error', 'Unknown error')}[/red]")
                raise typer.Exit(1)
        
        # Ask user if they want to see full content
        if typer.confirm("Would you like to see the full generated content?"):
            console.print(f"\n[bold]📄 Full Generated Content:[/bold]")
            console.print(Panel(result.generated_content, title=f"Generated Content: {topic}", border_style="blue"))
        
    except Exception as e:
        console.print(f"[red]❌ Error generating content: {e}[/red]")
        raise typer.Exit(1)


@app.command("capabilities")
def show_capabilities():
    """Show wiki content generation capabilities."""
    console = Console()
    
    try:
        from src.core_services.wiki_content_generator import WikiContentGenerator
        generator = WikiContentGenerator()
        capabilities = generator.get_content_generation_capabilities()
        
        console.print("[bold blue]🤖 Wiki Content Generation Capabilities[/bold blue]")
        
        # Content types
        console.print("\n[bold]Content Types:[/bold]")
        types_table = Table(show_header=True, box=None)
        types_table.add_column("Type", style="cyan")
        types_table.add_column("Description", style="dim")
        
        type_descriptions = {
            "article": "Structured article with introduction, sections, and conclusion",
            "debate_summary": "Summary of debate with participant positions and consensus",
            "analysis": "In-depth analysis with executive summary and recommendations",
            "tutorial": "Step-by-step tutorial with clear instructions",
            "overview": "General overview covering key points and insights"
        }
        
        for content_type in capabilities["content_types"]:
            types_table.add_row(content_type.title(), type_descriptions.get(content_type, "No description"))
        console.print(types_table)
        
        # Target audiences
        console.print("\n[bold]Target Audiences:[/bold]")
        audience_table = Table(show_header=True, box=None)
        audience_table.add_column("Audience", style="cyan")
        audience_table.add_column("Description", style="dim")
        
        audience_descriptions = {
            "beginner": "Introductory content with basic concepts and simple language",
            "intermediate": "Content assuming some prior knowledge and experience",
            "expert": "Advanced content with technical details and depth",
            "general": "Balanced content suitable for all knowledge levels"
        }
        
        for audience in capabilities["target_audiences"]:
            audience_table.add_row(audience.title(), audience_descriptions.get(audience, "No description"))
        console.print(audience_table)
        
        # Quality metrics
        console.print("\n[bold]Quality Metrics:[/bold]")
        metrics_table = Table(show_header=True, box=None)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Description", style="dim")
        
        metric_descriptions = {
            "structure_score": "Measures content organization and logical flow",
            "coherence_score": "Evaluates textual coherence and readability",
            "completeness_score": "Assesses coverage of key topics and points",
            "participant_diversity": "Measures diversity of perspectives and contributions",
            "consensus_strength": "Evaluates strength of consensus and agreement"
        }
        
        for metric in capabilities["quality_metrics"]:
            metrics_table.add_row(metric.replace("_", " ").title(), metric_descriptions.get(metric, "No description"))
        console.print(metrics_table)
        
        # System info
        console.print("\n[bold]System Information:[/bold]")
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="magenta")
        
        info_table.add_row("Max Participants", str(capabilities["max_participants"]))
        info_table.add_row("Estimated Generation Time", capabilities["estimated_generation_time"])
        
        console.print(info_table)
        
        console.print("\n[dim]✨ Content is generated through structured AI debates, ensuring multiple perspectives and high-quality output.[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error showing capabilities: {e}[/red]")
        raise typer.Exit(1)


@app.command("optimize")
def optimize_intent(
    user_input: str = typer.Argument(..., help="User's raw input or request"),
    show_details: bool = typer.Option(False, "--details", "-d", help="Show detailed optimization process"),
):
    """Optimize user intent for better wiki content generation."""
    console = Console()
    
    try:
        console.print(f"[bold blue]🎯 Optimizing Intent for Wiki Generation[/bold blue]")
        console.print(f"[dim]Original input: {user_input}[/dim]")
        
        # Import intent optimization
        from src.core_services.wiki_collaboration_simplified import IntentOptimizer
        
        # Create intent optimizer
        optimizer = IntentOptimizer()
        
        # Optimize intent
        optimization_result = asyncio.run(optimizer.optimize_user_intent(user_input))
        
        if not optimization_result["success"]:
            console.print(f"[red]❌ Intent optimization failed: {optimization_result.get('error', 'Unknown error')}[/red]")
            raise typer.Exit(1)
        
        # Display optimization results
        optimized_intent = optimization_result["optimized_intent"]
        confidence = optimization_result["confidence"]
        suggested_actions = optimization_result["suggested_actions"]
        
        console.print(f"\n[green]✅ Intent optimized successfully![/green]")
        console.print(f"[bold]Optimized Intent:[/bold]")
        console.print(f"[cyan]{optimized_intent}[/cyan]")
        console.print(f"[dim]Confidence: {confidence:.2f}[/dim]")
        
        # Show suggested actions
        if suggested_actions:
            console.print(f"\n[bold]Suggested Actions:[/bold]")
            actions_table = Table(show_header=False, box=None)
            actions_table.add_column("Action", style="cyan")
            actions_table.add_column("Priority", style="magenta")
            
            for i, action in enumerate(suggested_actions, 1):
                priority = "High" if i <= 2 else "Medium" if i <= 4 else "Low"
                actions_table.add_row(action, priority)
            
            console.print(actions_table)
        
        # Show detailed process if requested
        if show_details:
            console.print(f"\n[bold]🔍 Optimization Details:[/bold]")
            
            details = optimization_result.get("optimization_details", {})
            
            if "extracted_keywords" in details:
                console.print("[dim]Extracted Keywords:[/dim]")
                keywords = ", ".join(details["extracted_keywords"])
                console.print(f"[dim]{keywords}[/dim]")
            
            if "intent_category" in details:
                console.print(f"[dim]Intent Category: {details['intent_category']}[/dim]")
            
            if "complexity_score" in details:
                console.print(f"[dim]Complexity Score: {details['complexity_score']:.2f}[/dim]")
        
        # Ask if user wants to generate content with optimized intent
        if typer.confirm("Would you like to generate wiki content with this optimized intent?"):
            # Extract parameters from optimized intent
            topic = optimized_intent.split("about")[-1].strip() if "about" in optimized_intent else optimized_intent.split("for")[-1].strip()
            
            console.print(f"\n[bold]🚀 Generating content for: {topic}[/bold]")
            
            # Import and run content generation
            from src.core_services.wiki_content_generator import WikiContentGenerator, ContentGenerationRequest
            
            generator = WikiContentGenerator()
            request = ContentGenerationRequest(
                topic=topic,
                content_type="article",  # Default type
                target_audience="general",  # Default audience
                scope="overview",  # Default scope
                special_requirements=["intent-optimized", "ai-generated"]
            )
            
            result = asyncio.run(generator.generate_wiki_content(request))
            
            if result.success:
                console.print(f"[green]✅ Content generated with optimized intent![/green]")
                console.print(f"[dim]Content length: {len(result.generated_content)} characters[/dim]")
                
                # Show preview
                preview = result.generated_content[:500] + "..." if len(result.generated_content) > 500 else result.generated_content
                console.print(f"\n[dim]Preview:[/dim]")
                console.print(f"[dim]{preview}[/dim]")
            else:
                console.print(f"[red]❌ Content generation failed: {result.error_message}[/red]")
        
    except Exception as e:
        console.print(f"[red]❌ Error optimizing intent: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def update(
    request: str = typer.Argument(..., help="The update request in natural language."),
):
    """Collaboratively update a wiki entry based on a natural language request."""
    try:
        # 导入必要的模块
        from src.cli.main import get_wiki_service
        from src.core_services.role_manager import RoleManager
        from src.core_services.wiki_collaboration_simplified import (
            SimpleIntentOptimizer,
            SimpleRoleCoordinator,
            SimpleExecutor,
            SimpleTaskCoordinator,
            CollaborationStorageManager
        )
        
        # 获取wiki服务
        wiki_service = get_wiki_service()
        
        # 创建角色管理器实例
        role_manager = RoleManager()
        
        # 创建存储管理器
        storage_manager = CollaborationStorageManager()
        
        # 创建协作组件
        intent_optimizer = SimpleIntentOptimizer()
        role_coordinator = SimpleRoleCoordinator(storage_manager, role_manager)
        executor = SimpleExecutor(wiki_service, storage_manager)
        task_coordinator = SimpleTaskCoordinator(intent_optimizer, role_coordinator, executor, storage_manager)
        
        # 发起协作任务
        typer.echo(f"正在处理您的请求: '{request}'")
        typer.echo("这可能需要几秒钟时间...")
        
        task_id = task_coordinator.initiate_task(request)
        
        # 获取任务状态
        status = task_coordinator.get_task_status(task_id)
        
        if status.get("status") == "completed":
            typer.echo("✅ 词条更新已完成！")
        elif status.get("status") == "failed":
            typer.echo("❌ 词条更新失败，请稍后重试。")
            raise typer.Exit(1)
        else:
            typer.echo("⚠️  词条更新状态未知。")
            
    except Exception as e:
        typer.echo(f"❌ 处理请求时出错: {e}")
        raise typer.Exit(1)


@app.command()
def debate(
    topic: str = typer.Argument(..., help="The topic to debate and create wiki content for."),
):
    """Initiate a debate on a topic and generate wiki content from the discussion."""
    try:
        # 获取wiki服务
        from src.cli.main import get_wiki_service
        wiki_service = get_wiki_service()
        
        # 发起协作编辑任务
        typer.echo(f"正在为话题 '{topic}' 发起辩论...")
        result = wiki_service.initiate_collaborative_edit(topic)
        
        if "error" in result:
            typer.echo(f"[ERROR] 发起辩论失败: {result['error']}")
            raise typer.Exit(1)
        else:
            typer.echo(f"[SUCCESS] 辩论已发起: {result['message']}")
            typer.echo(f"   话题: {result['topic']}")
            typer.echo(f"   会话ID: {result['session_id']}")
            
    except Exception as e:
        typer.echo(f"[ERROR] 处理请求时出错: {e}")
        raise typer.Exit(1)