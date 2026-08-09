"""CLI commands for intelligent role management"""

from pathlib import Path
from typing import Optional

import typer

from daip_live.container import Container
from daip_live.p4_role_manager_tools.intelligent_role_manager import (
    IntelligentRoleManager,
)

app = typer.Typer()


@app.command("create-role")
def create_role(
    topic: str = typer.Argument(..., help="The debate topic or subject area"),
    position: str = typer.Option(
        "supporting", help="Role position: supporting, opposing, neutral, or moderator"
    ),
    role_name: Optional[str] = typer.Option(None, help="Custom role name"),
    roles_dir: str = typer.Option("roles", help="Directory to save roles"),
):
    """Create a new role based on a topic and save it to a file."""
    try:
        container = Container()
        model_provider = container.model_provider()

        role_manager = IntelligentRoleManager(
            roles_dir=roles_dir, model_provider=model_provider
        )

        # If a custom role name is provided, create the role with that name
        if role_name:
            # Create a role with the specified name and topic
            import asyncio

            from daip_live.p4_role_manager_tools.role_model_config import (
                EnhancedRole,
            )

            # Analyze topic to create appropriate persona
            topic_analysis = role_manager.analyze_topic(topic)
            persona = role_manager._generate_role_persona(
                topic, position, topic_analysis
            )

            # Determine appropriate model configuration based on the topic
            model_config = role_manager._generate_model_config_for_topic(topic_analysis)

            # Create and return the role
            role = EnhancedRole(
                name=role_name,
                persona=persona,
                tools=[],
                model_configs=[model_config],
                debate_model_config=model_config,
            )
        else:
            # Use the automatic role creation
            import asyncio

            role = asyncio.run(
                role_manager.create_and_save_role_for_topic(topic, position)
            )

        if role:
            typer.echo(f"✅ Successfully created role: {role.name}")
            typer.echo(f"   Persona: {role.persona[:100]}...")

            # Update models based on availability and save
            import asyncio

            updated_role = asyncio.run(role_manager.update_role_models(role))
            save_success = role_manager.save_role_to_file(updated_role)

            if save_success:
                typer.echo(f"💾 Role saved to: {roles_dir}/{updated_role.name}.yaml")
            else:
                typer.echo("⚠️  Failed to save role to file")
        else:
            typer.echo("❌ Failed to create role")

    except Exception as e:
        typer.echo(f"❌ Error creating role: {e}")


@app.command("analyze-topic")
def analyze_topic(topic: str = typer.Argument(..., help="The debate topic to analyze")):
    """Analyze a topic and suggest appropriate roles."""
    try:
        container = Container()
        model_provider = container.model_provider()

        role_manager = IntelligentRoleManager(model_provider=model_provider)

        # Analyze the topic
        analysis = role_manager.analyze_topic(topic)

        typer.echo(f"🔬 Topic Analysis for: {topic}")
        typer.echo(f"   Domains: {', '.join(analysis['domains'])}")
        typer.echo(f"   Debate Type: {analysis['debate_type']}")
        typer.echo(f"   Complexity: {analysis['complexity_score']:.2f}")

    except Exception as e:
        typer.echo(f"❌ Error analyzing topic: {e}")


@app.command("suggest-roles")
def suggest_roles(
    topic: str = typer.Argument(..., help="The debate topic"),
    num_roles: int = typer.Option(3, help="Number of suggested roles"),
    roles_dir: str = typer.Option("roles", help="Directory containing existing roles"),
):
    """Suggest roles for a topic based on existing roles."""
    try:
        container = Container()
        model_provider = container.model_provider()

        role_manager = IntelligentRoleManager(
            roles_dir=roles_dir, model_provider=model_provider
        )

        # Load existing roles
        available_roles = []
        roles_path = Path(roles_dir)

        for file_path in roles_path.glob("*.yaml"):
            role = role_manager.load_role_from_file(file_path.stem)
            if role:
                available_roles.append(role)

        if not available_roles:
            typer.echo(f"⚠️  No existing roles found in {roles_dir}")
            typer.echo("💡 Create some roles first using 'create-role' command")
            return

        # Suggest roles for the topic
        suggested_roles = role_manager.suggest_roles_for_topic(
            topic, available_roles, num_suggestions=num_roles
        )

        typer.echo(f"🎯 Role suggestions for: {topic}")
        for i, role in enumerate(suggested_roles, 1):
            typer.echo(f"   {i}. {role.name}")
            typer.echo(f"      {role.persona[:80]}...")

    except Exception as e:
        typer.echo(f"❌ Error suggesting roles: {e}")


@app.command("check-models")
def check_models():
    """Check available models for role creation."""
    try:
        container = Container()
        model_provider = container.model_provider()

        role_manager = IntelligentRoleManager(model_provider=model_provider)

        import asyncio

        available_models = asyncio.run(role_manager.check_model_availability())

        if available_models:
            typer.echo(f"✅ Found {len(available_models)} available models:")
            for model in available_models:
                typer.echo(f"   • {model}")
        else:
            typer.echo(
                "⚠️  No models available. Please check your model provider setup."
            )

    except Exception as e:
        typer.echo(f"❌ Error checking models: {e}")


@app.command("auto-select-roles")
def auto_select_roles(
    topic: str = typer.Argument(..., help="The debate topic"),
    num_roles: int = typer.Option(2, help="Number of roles to select"),
    roles_dir: str = typer.Option("roles", help="Directory containing existing roles"),
):
    """Automatically select the best roles for a debate topic."""
    try:
        container = Container()
        model_provider = container.model_provider()

        role_manager = IntelligentRoleManager(
            roles_dir=roles_dir, model_provider=model_provider
        )

        # Load existing roles
        available_roles = []
        roles_path = Path(roles_dir)

        for file_path in roles_path.glob("*.yaml"):
            role = role_manager.load_role_from_file(file_path.stem)
            if role:
                available_roles.append(role)

        if not available_roles:
            typer.echo(f"⚠️  No existing roles found in {roles_dir}")
            typer.echo("💡 Create some roles first using 'create-role' command")
            return

        # Auto-select roles for the topic
        selected_roles = role_manager.auto_select_roles(
            topic, available_roles, num_roles=num_roles
        )

        typer.echo(f"🤖 Auto-selected roles for: {topic}")
        for i, role in enumerate(selected_roles, 1):
            typer.echo(f"   {i}. {role.name}")
            typer.echo(f"      {role.persona[:80]}...")

    except Exception as e:
        typer.echo(f"❌ Error auto-selecting roles: {e}")


if __name__ == "__main__":
    app()
