#!/usr/bin/env python3
"""@Time    : 2025-07-24 19:30:00
@Author  : DAIP-LIVE Team
@File    : user_intervention_demo.py
@Description:
    Demonstration of user intervention and workflow customization capabilities.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from user_interface.interactive_controller import InteractiveController
from user_interface.parameter_manager import ParameterDefinition, ParameterType


async def demo_parameter_collection():
    """Demonstrate parameter collection functionality."""
    console = Console()
    controller = InteractiveController(console=console)
    
    console.print(Panel.fit("Parameter Collection Demo", style="blue"))
    
    # Define example parameters for a critical review workflow
    parameter_definitions = [
        ParameterDefinition(
            name="content_topic",
            param_type=ParameterType.STRING,
            description="Topic for content generation",
            default="AI impact on society"
        ),
        ParameterDefinition(
            name="reviewer_count",
            param_type=ParameterType.INTEGER,
            description="Number of reviewers for parallel review",
            default=3,
            min_value=2,
            max_value=5
        ),
        ParameterDefinition(
            name="credibility_threshold",
            param_type=ParameterType.FLOAT,
            description="Minimum credibility threshold for facts",
            default=0.7,
            min_value=0.0,
            max_value=1.0
        ),
        ParameterDefinition(
            name="review_method",
            param_type=ParameterType.CHOICE,
            description="Method for conducting reviews",
            default="parallel",
            choices=["sequential", "parallel", "hybrid"]
        ),
        ParameterDefinition(
            name="enable_fact_checking",
            param_type=ParameterType.BOOLEAN,
            description="Enable automatic fact checking",
            default=True
        ),
        ParameterDefinition(
            name="reviewer_roles",
            param_type=ParameterType.LIST,
            description="List of reviewer roles",
            default=["批判者", "验证者", "专家"]
        )
    ]
    
    console.print("\n[yellow]This demo will collect parameters for a Critical Review Workflow.[/yellow]")
    console.print("[dim]You can press Ctrl+C at any time to skip parameter collection.[/dim]")
    
    try:
        parameters = await controller.collect_workflow_parameters(
            workflow_name="critical_review",
            parameter_definitions=parameter_definitions,
            context={"demo": True, "description": "Critical Review Workflow Demo"}
        )
        
        if parameters:
            console.print("\n[green]✅ Parameters collected successfully![/green]")
            controller.parameter_manager.display_parameter_summary(parameters)
            
            # Offer to save as preset
            from rich.prompt import Confirm
            if Confirm.ask("Save these parameters as a preset?"):
                from rich.prompt import Prompt
                preset_name = Prompt.ask("Enter preset name", default="demo_preset")
                controller.create_parameter_preset(
                    preset_name=preset_name,
                    parameters=parameters,
                    description="Demo parameter preset"
                )
        else:
            console.print("[yellow]No parameters collected.[/yellow]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Parameter collection cancelled by user.[/yellow]")


async def demo_workflow_steering():
    """Demonstrate workflow steering functionality."""
    console = Console()
    controller = InteractiveController(console=console)
    
    console.print(Panel.fit("Workflow Steering Demo", style="green"))
    
    # Setup steering points for a multi-perspective synthesis workflow
    steering_points = [
        {
            "id": "task_decomposition_complete",
            "name": "Task Decomposition Complete",
            "description": "Task has been decomposed into sub-problems",
            "workflow_step": "task_decomposition",
            "actions": ["continue", "modify_parameters", "retry_step"],
            "priority": 2
        },
        {
            "id": "expert_analysis_complete",
            "name": "Expert Analysis Complete",
            "description": "All expert analyses have been completed",
            "workflow_step": "parallel_exploration",
            "actions": ["continue", "pause", "inject_data", "change_direction"],
            "priority": 1
        },
        {
            "id": "synthesis_quality_check",
            "name": "Synthesis Quality Check",
            "description": "Synthesis quality needs review",
            "workflow_step": "synthesis",
            "actions": ["continue", "retry_step", "modify_parameters", "emergency_stop"],
            "priority": 3
        }
    ]
    
    await controller.setup_workflow_steering("multi_perspective_synthesis", steering_points)
    
    console.print("\n[yellow]This demo will simulate workflow steering points.[/yellow]")
    console.print("[dim]You'll be prompted to make decisions at key workflow points.[/dim]")
    
    # Simulate workflow execution with steering points
    for i, point_config in enumerate(steering_points, 1):
        console.print(f"\n[blue]--- Simulating Workflow Step {i} ---[/blue]")
        
        # Simulate some context for the steering point
        context = {
            "current_step": point_config["workflow_step"],
            "progress": i / len(steering_points),
            "execution_id": f"demo_exec_{i}",
            "parameters": {
                "topic": "AI Ethics Analysis",
                "expert_count": 4,
                "quality_threshold": 0.8
            }
        }
        
        try:
            result = await controller.trigger_workflow_steering(
                point_id=point_config["id"],
                context=context
            )
            
            console.print(f"[green]Steering result: {result['action']}[/green]")
            
            if result["action"] == "emergency_stop":
                console.print("[red]Emergency stop triggered. Ending demo.[/red]")
                break
            elif result["action"] == "pause":
                console.print("[yellow]Workflow paused. Continuing demo...[/yellow]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Steering cancelled by user.[/yellow]")
            break
    
    # Show steering history
    history = controller.get_steering_history()
    if history:
        console.print("\n[blue]Steering History:[/blue]")
        controller.display_intervention_summary(history)


async def demo_configuration_management():
    """Demonstrate configuration management functionality."""
    console = Console()
    controller = InteractiveController(console=console)
    
    console.print(Panel.fit("Configuration Management Demo", style="purple"))
    
    console.print("\n[yellow]This demo will show configuration management capabilities.[/yellow]")
    
    # Create a sample configuration
    sample_config = {
        "generation": {
            "role_name": "创作者",
            "capture_metadata": True,
            "max_length": 1000
        },
        "fact_extraction": {
            "min_confidence": 0.6,
            "max_facts": 20,
            "use_external_sources": True
        },
        "parallel_review": {
            "reviewer_roles": ["批判者", "验证者", "专家"],
            "max_parallel_reviews": 5,
            "timeout_seconds": 300
        },
        "consensus": {
            "method": "weighted_average",
            "credibility_threshold": 0.7,
            "require_unanimous": False
        }
    }
    
    # Save the configuration
    config_name = "demo_critical_review_config"
    controller.save_workflow_configuration(config_name, sample_config)
    console.print(f"[green]✅ Saved sample configuration: {config_name}[/green]")
    
    # Show configuration management menu
    try:
        result_config = await controller.handle_workflow_customization_menu(
            workflow_name="critical_review",
            current_config=sample_config
        )
        
        if result_config:
            console.print("\n[green]Final configuration:[/green]")
            controller.configuration_manager._display_configuration_summary(result_config)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Configuration management cancelled by user.[/yellow]")


async def demo_integration_scenario():
    """Demonstrate integration of all user intervention capabilities."""
    console = Console()
    controller = InteractiveController(console=console)
    
    console.print(Panel.fit("Integration Scenario Demo", style="red"))
    
    console.print("\n[yellow]This demo simulates a complete workflow with user intervention.[/yellow]")
    console.print("[dim]You'll experience parameter collection, steering, and configuration management.[/dim]")
    
    # Step 1: Load or create configuration
    console.print("\n[blue]Step 1: Configuration Setup[/blue]")
    
    configs = controller.list_workflow_configurations("critical_review")
    if configs:
        console.print("Available configurations:")
        for i, config in enumerate(configs, 1):
            console.print(f"  {i}. {config}")
        
        from rich.prompt import Confirm, Prompt
        if Confirm.ask("Use existing configuration?"):
            choice = Prompt.ask(
                "Select configuration",
                choices=[str(i) for i in range(1, len(configs) + 1)],
                default="1"
            )
            selected_config = configs[int(choice) - 1]
            workflow_config = controller.load_workflow_configuration(selected_config)
        else:
            workflow_config = await controller.create_workflow_configuration("critical_review", "integration_demo")
    else:
        workflow_config = await controller.create_workflow_configuration("critical_review", "integration_demo")
    
    # Step 2: Setup workflow parameters
    console.print("\n[blue]Step 2: Workflow Parameters[/blue]")
    
    parameter_definitions = [
        ParameterDefinition(
            name="content_topic",
            param_type=ParameterType.STRING,
            description="Topic for analysis",
            default="Climate Change Policy"
        ),
        ParameterDefinition(
            name="analysis_depth",
            param_type=ParameterType.CHOICE,
            description="Depth of analysis",
            default="comprehensive",
            choices=["basic", "detailed", "comprehensive"]
        )
    ]
    
    try:
        workflow_params = await controller.collect_workflow_parameters(
            workflow_name="critical_review",
            parameter_definitions=parameter_definitions
        )
    except KeyboardInterrupt:
        console.print("[yellow]Using default parameters.[/yellow]")
        workflow_params = {"content_topic": "Climate Change Policy", "analysis_depth": "comprehensive"}
    
    # Step 3: Setup steering points
    console.print("\n[blue]Step 3: Workflow Execution with Steering[/blue]")
    
    steering_points = [
        {
            "id": "content_generated",
            "name": "Content Generated",
            "description": "Initial content has been generated",
            "workflow_step": "generation",
            "actions": ["continue", "modify_parameters", "retry_step"]
        },
        {
            "id": "facts_extracted",
            "name": "Facts Extracted",
            "description": "Facts have been extracted from content",
            "workflow_step": "fact_extraction",
            "actions": ["continue", "pause", "inject_data"]
        }
    ]
    
    await controller.setup_workflow_steering("critical_review", steering_points)
    
    # Simulate workflow execution
    for point_config in steering_points:
        console.print(f"\n[cyan]Executing: {point_config['name']}[/cyan]")
        
        context = {
            "workflow_config": workflow_config,
            "workflow_params": workflow_params,
            "current_step": point_config["workflow_step"]
        }
        
        try:
            result = await controller.trigger_workflow_steering(
                point_id=point_config["id"],
                context=context
            )
            
            console.print(f"[green]Action taken: {result['action']}[/green]")
            
            if result["action"] == "emergency_stop":
                break
        
        except KeyboardInterrupt:
            console.print("[yellow]Workflow interrupted.[/yellow]")
            break
    
    # Step 4: Show summary
    console.print("\n[blue]Step 4: Summary[/blue]")
    
    history = controller.get_steering_history()
    if history:
        console.print("Intervention history:")
        controller.display_intervention_summary(history)
    
    console.print("\n[green]✅ Integration demo completed![/green]")


async def main():
    """Main demo function."""
    console = Console()
    
    console.print(Panel.fit(
        Text("User Intervention and Customization Demo", style="bold blue"),
        style="blue"
    ))
    
    demos = [
        ("Parameter Collection", demo_parameter_collection),
        ("Workflow Steering", demo_workflow_steering),
        ("Configuration Management", demo_configuration_management),
        ("Integration Scenario", demo_integration_scenario)
    ]
    
    console.print("\nAvailable demos:")
    for i, (name, _) in enumerate(demos, 1):
        console.print(f"  {i}. {name}")
    console.print(f"  {len(demos) + 1}. Run all demos")
    console.print(f"  {len(demos) + 2}. Exit")
    
    from rich.prompt import Prompt
    
    while True:
        try:
            choice = Prompt.ask(
                "\nSelect demo to run",
                choices=[str(i) for i in range(1, len(demos) + 3)],
                default=str(len(demos) + 2)
            )
            
            choice_num = int(choice)
            
            if choice_num <= len(demos):
                # Run specific demo
                name, demo_func = demos[choice_num - 1]
                console.print(f"\n[blue]Running {name} Demo...[/blue]")
                await demo_func()
                console.print(f"\n[green]{name} Demo completed![/green]")
            
            elif choice_num == len(demos) + 1:
                # Run all demos
                console.print("\n[blue]Running all demos...[/blue]")
                for name, demo_func in demos:
                    console.print(f"\n[yellow]--- {name} Demo ---[/yellow]")
                    try:
                        await demo_func()
                    except KeyboardInterrupt:
                        console.print(f"\n[yellow]{name} demo skipped.[/yellow]")
                        continue
                console.print("\n[green]All demos completed![/green]")
                break
            
            else:
                # Exit
                console.print("[blue]Goodbye![/blue]")
                break
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Demo interrupted. Returning to menu.[/yellow]")
            continue
        except Exception as e:
            console.print(f"\n[red]Error running demo: {e}[/red]")
            continue


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo cancelled by user.")
    except Exception as e:
        print(f"Demo failed: {e}")