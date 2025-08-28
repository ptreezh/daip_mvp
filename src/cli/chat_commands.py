# -*- coding: utf-8 -*-
"""Chat commands for the DAIP-LIVE CLI."""

import typer
from typing import Optional

app = typer.Typer(
    name="chat",
    help="Commands for managing chat rooms.",
    add_completion=False,
)


def get_chat_coordinator():
    """Get the global chat coordinator instance."""
    from src.cli.service_utils import get_chat_coordinator
    return get_chat_coordinator()


@app.command()
def start(
    topic: str = typer.Option(..., "--topic", "-t", help="The topic of the chat room."),
    room: Optional[str] = typer.Option(None, "--room", "-r", help="The name of the chat room."),
):
    """Start a new chat room."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    coordinator.load_state()
    
    # Create the chat room using the coordinator
    room_id = coordinator.create_chat_room(
        topic=topic,
        room_name=room
    )
    
    # Print the room ID
    typer.echo(f"Chat room created with ID: {room_id}")
    coordinator.save_state()


@app.command()
def message(
    content: str = typer.Argument(..., help="The message to send."),
    room: Optional[str] = typer.Option(None, "--room", "-r", help="The ID of the chat room."),
    sender: str = typer.Option("user", "--sender", "-s", help="The sender of the message."),
):
    """Send a message to a chat room."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    coordinator.load_state()
    
    # Send the message using the coordinator
    try:
        if room:
            success = coordinator.send_message_to_room(room_id=room, message=content, sender=sender)
            if success:
                typer.echo(f"Message sent to room {room}: {content}")
            else:
                typer.echo(f"Failed to send message to room {room}. The room may not exist or there may be no active session.")
        else:
            # Send to current room
            current_room = coordinator.get_current_room_id()
            if current_room:
                success = coordinator.send_message_to_room(message=content, sender=sender)
                if success:
                    typer.echo(f"Message sent to current room ({current_room}): {content}")
                else:
                    typer.echo("Failed to send message to current room. There may be no active session.")
            else:
                typer.echo("No current chat room is active. Please specify a room ID or start a new chat room.")
    except Exception as e:
        typer.echo(f"Error sending message: {e}")
    finally:
        coordinator.save_state()


@app.command()
def history(
    room: Optional[str] = typer.Option(None, "--room", "-r", help="The ID of the chat room."),
):
    """View the history of a chat room."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    
    # Get the room history using the coordinator
    try:
        if room:
            history = coordinator.get_room_history(room_id=room)
            typer.echo(f"History for room {room}:")
        else:
            # For now, we'll just get history for a default room
            # In a real implementation, we would get history for the "current" room
            history = coordinator.get_room_history()  # This will need to be implemented in ChatCoordinator
            typer.echo("History for current room:")
        
        # Format and print the history
        if history:
            for message in history:
                typer.echo(f"  [{message['timestamp']}] {message['sender']}: {message['content']}")
        else:
            typer.echo("  No messages found.")
    except Exception as e:
        typer.echo(f"Error retrieving chat history: {e}")


@app.command()
def clear(
    room: Optional[str] = typer.Option(None, "--room", "-r", help="The ID of the chat room."),
):
    """Clear the history of a chat room."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    
    # Clear the room history using the coordinator
    try:
        if room:
            success = coordinator.clear_room_history(room_id=room)
            if success:
                typer.echo(f"Chat history cleared for room {room}.")
            else:
                typer.echo(f"Failed to clear chat history for room {room}.")
        else:
            # For now, we'll just clear history for a default room
            # In a real implementation, we would clear history for the "current" room
            success = coordinator.clear_room_history()  # This will need to be implemented in ChatCoordinator
            if success:
                typer.echo("Chat history cleared for current room.")
            else:
                typer.echo("Failed to clear chat history for current room.")
    except Exception as e:
        typer.echo(f"Error clearing chat history: {e}")


@app.command()
def close():
    """Close the current chat room."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    
    # Close the current room using the coordinator
    try:
        success = coordinator.close_current_room()
        if success:
            typer.echo("Chat room closed successfully.")
        else:
            typer.echo("Failed to close chat room.")
    except Exception as e:
        typer.echo(f"Error closing chat room: {e}")


@app.command()
def delete(
    room_id: str = typer.Argument(..., help="The ID of the chat room to delete."),
):
    """Delete a chat room."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    coordinator.load_state()
    
    # Delete the room using the coordinator
    try:
        success = coordinator.delete_room(room_id=room_id)
        if success:
            typer.echo(f"Chat room {room_id} deleted successfully.")
        else:
            typer.echo(f"Failed to delete chat room {room_id}.")
    except Exception as e:
        typer.echo(f"Error deleting chat room {room_id}: {e}")
    finally:
        coordinator.save_state()


@app.command()
def recommend(
    topic: str = typer.Argument(..., help="The topic to recommend roles for."),
    limit: int = typer.Option(5, "--limit", "-l", help="Maximum number of recommendations to return."),
    auto_confirm: bool = typer.Option(False, "--auto-confirm", "-a", help="Automatically confirm and create chat room with recommended roles."),
    room_name: Optional[str] = typer.Option(None, "--room-name", "-n", help="Name for the chat room when auto-confirming."),
):
    """Recommend roles for a chat topic."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    
    try:
        recommendations = coordinator.recommend_roles_for_topic(topic, limit)
        if recommendations:
            typer.echo(f"Role recommendations for topic '{topic}':")
            for i, role in enumerate(recommendations, 1):
                typer.echo(f"  {i}. {role['name']} (Score: {role['score']})")
                typer.echo(f"     {role['description']}")
            
            # 如果启用了自动确认，则自动创建聊天室
            if auto_confirm:
                typer.echo("\nAuto-confirming recommended roles and creating chat room...")
                
                # 获取推荐角色的ID
                role_ids = [role["id"] for role in recommendations[:3]]  # 使用前3个推荐角色
                
                # 创建聊天室
                room_id = coordinator.create_chat_room(
                    topic=topic,
                    room_name=room_name or f"讨论:{topic}",
                    roles=role_ids,
                    auto_recommend_roles=False
                )
                
                if room_id:
                    typer.echo(f"✅ Chat room created successfully with ID: {room_id}")
                    typer.echo(f"   Room name: {room_name or f'讨论:{topic}'}")
                    typer.echo(f"   Topic: {topic}")
                    typer.echo(f"   Roles: {', '.join([role['name'] for role in recommendations[:3]])}")
                else:
                    typer.echo("❌ Failed to create chat room.")
        else:
            typer.echo(f"No role recommendations found for topic '{topic}'.")
    except Exception as e:
        typer.echo(f"Error getting role recommendations: {e}")


@app.command()
def upload(
    room_id: str = typer.Argument(..., help="The ID of the chat room."),
    file_path: str = typer.Argument(..., help="Path to the document file to upload."),
    description: str = typer.Option("", "--description", "-d", help="Optional description of the document."),
):
    """Upload a document to a chat room."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    
    try:
        success = coordinator.upload_document_to_chat(room_id, file_path, description)
        if success:
            typer.echo(f"Document uploaded successfully to chat room {room_id}.")
        else:
            typer.echo(f"Failed to upload document to chat room {room_id}.")
    except Exception as e:
        typer.echo(f"Error uploading document: {e}")


@app.command()
def consensus(
    room_id: str = typer.Argument(..., help="The ID of the chat room to analyze."),
):
    """View consensus information for a chat room."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    
    try:
        consensus_info = coordinator.get_chat_consensus_info(room_id)
        typer.echo(f"Consensus analysis for chat room {room_id}:")
        typer.echo(f"  Consensus Level: {consensus_info['consensus_level']}")
        typer.echo(f"  Total Messages: {consensus_info['total_messages']}")
        
        if consensus_info['agreement_points']:
            typer.echo("  Agreement Points:")
            for point in consensus_info['agreement_points']:
                typer.echo(f"    - {point}")
        
        if consensus_info['disagreement_points']:
            typer.echo("  Disagreement Points:")
            for point in consensus_info['disagreement_points']:
                typer.echo(f"    - {point}")
    except Exception as e:
        typer.echo(f"Error getting consensus information: {e}")


@app.command()
def list_rules():
    """Show available chat rules/primitives."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    
    try:
        primitives = coordinator.get_available_chat_primitives()
        if primitives:
            typer.echo("Available chat rules/primitives:")
            for primitive in primitives:
                typer.echo(f"  - {primitive['type']}: {primitive['description']}")
        else:
            typer.echo("No chat rules/primitives available.")
    except Exception as e:
        typer.echo(f"Error getting chat rules: {e}")


@app.command()
def current():
    """Show the current active chat room."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    
    try:
        current_room_id = coordinator.get_current_room_id()
        if current_room_id:
            typer.echo(f"Current active chat room: {current_room_id}")
        else:
            typer.echo("No chat room is currently active.")
    except Exception as e:
        typer.echo(f"Error getting current room: {e}")


@app.command()
def switch(
    room_id: str = typer.Argument(..., help="The ID of the chat room to switch to."),
):
    """Switch to a different chat room."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    
    try:
        success = coordinator.set_current_room(room_id)
        if success:
            typer.echo(f"Switched to chat room: {room_id}")
        else:
            typer.echo(f"Failed to switch to chat room {room_id}. The room may not exist.")
    except Exception as e:
        typer.echo(f"Error switching chat room: {e}")


@app.command()
def list():
    """List all chat rooms."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    
    try:
        # Get chat room summaries from the chat room manager
        room_summaries = coordinator.chat_room_manager.list_chat_rooms()
        
        if not room_summaries:
            typer.echo("No chat rooms found.")
            return
        
        # Display the chat rooms in a formatted table
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        table = Table(title="Chat Rooms")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Topic", style="green")
        table.add_column("Roles", justify="right", style="yellow")
        table.add_column("Status", style="blue")
        table.add_column("Last Active", style="dim")
        
        for summary in room_summaries:
            table.add_row(
                summary.id,
                summary.name,
                summary.topic,
                str(summary.role_count),
                summary.status,
                summary.last_active.strftime("%Y-%m-%d %H:%M:%S")
            )
        
        console.print(table)
    except Exception as e:
        typer.echo(f"Error listing chat rooms: {e}")


@app.command()
def rules(
    room_id: str = typer.Argument(..., help="The ID of the chat room to configure rules for."),
    mode: Optional[str] = typer.Option(None, "--mode", "-m", help="Interaction mode (free_form, structured, debate)."),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode for detailed output."),
):
    """Configure chat room rules."""
    # Get the chat coordinator with debug mode if requested
    coordinator = get_chat_coordinator()
    
    try:
        # Get the chat room
        room = coordinator.chat_room_manager.get_chat_room(room_id)
        if not room:
            typer.echo(f"Chat room with ID '{room_id}' not found.")
            raise typer.Exit(1) from e
        
        # Update interaction mode if provided
        updated = False
        if mode:
            # Validate mode
            valid_modes = ["free_form", "structured", "debate", "turn_based", "random"]
            if mode not in valid_modes:
                typer.echo(f"Invalid mode: {mode}. Valid modes are: {', '.join(valid_modes)}")
                raise typer.Exit(1) from e
                
            room.config.mode = mode
            updated = True
            
        # If no options provided, show current rules
        if not updated:
            typer.echo(f"Chat room rules for '{room_id}':")
            typer.echo(f"  Mode: {room.config.mode}")
            typer.echo(f"  Prompt Strategy: {room.config.interaction_rules.get('prompt_strategy', 'contextual')}")
            return
            
        # Save updated configuration
        success = coordinator.chat_room_manager.update_chat_room(room_id, room.config)
        if success:
            typer.echo(f"[SUCCESS] Chat room rules updated for '{room_id}':")
            typer.echo(f"   Mode: {room.config.mode}")
            typer.echo(f"   Prompt Strategy: {room.config.interaction_rules.get('prompt_strategy', 'contextual')}")
        else:
            typer.echo(f"[ERROR] Failed to update chat room rules for '{room_id}'.")
            raise typer.Exit(1)
            
    except Exception as e:
        typer.echo(f"Error configuring chat room rules: {e}")
        raise typer.Exit(1) from e


@app.command()
def test_rules(
    room_id: str = typer.Argument(..., help="The ID of the chat room to test rules for."),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode for detailed output."),
):
    """Test chat room rules with virtual roles."""
    # Get the chat coordinator
    coordinator = get_chat_coordinator()
    
    # 如果启用了调试模式，重新初始化协调器以启用调试
    if debug:
        # 重新创建协调器并启用调试模式
        from src.cli.service_utils import (
            get_chat_room_manager as chat_room_manager, 
            get_chat_session_service as chat_session_service, 
            get_role_manager as role_manager, 
            get_primitive_registry as primitive_registry, 
            get_wiki_service as wiki_service
        )
        
        from src.virtual_role_chat.chat_coordinator import ChatCoordinator
        coordinator = ChatCoordinator(
            chat_room_manager=chat_room_manager,
            chat_session_service=chat_session_service,
            role_manager=role_manager,
            primitive_registry=primitive_registry,
            wiki_service=wiki_service,
            debug=True
        )
    
    try:
        # Get the chat room
        room = coordinator.chat_room_manager.get_chat_room(room_id)
        if not room:
            typer.echo(f"Chat room with ID '{room_id}' not found.")
            raise typer.Exit(1) from e
        
        typer.echo(f"Testing chat room rules for '{room_id}' with mode: {room.config.mode}")
        typer.echo(f"Debug mode: {'enabled' if debug else 'disabled'}")
        
        # 获取房间历史记录
        history = coordinator.get_room_history(room_id)
        typer.echo(f"Room history messages: {len(history)}")
        
        # 创建规则上下文
        from src.virtual_role_chat.chat_rules_engine import ChatRuleContext
        context = ChatRuleContext(
            room_config=room.config,
            current_turn=len(history),
            last_speaker=history[-1].sender_id if history else None,
            message_history=history,
            active_participants=room.config.roles
        )
        
        # 测试确定下一个发言者
        typer.echo("\n--- Testing Next Speaker Determination ---")
        next_speaker = coordinator.rules_engine.determine_next_speaker(context)
        if next_speaker:
            typer.echo(f"Next speaker determined by rules: {next_speaker}")
        else:
            typer.echo("No specific speaker determined by rules (free form mode)")
        
        # 测试每个角色是否应该响应
        typer.echo("\n--- Testing Role Response Decisions ---")
        for role_id in room.config.roles:
            should_respond = coordinator.rules_engine.should_role_respond(role_id, context)
            typer.echo(f"Role '{role_id}' should respond: {should_respond}")
            
            # 为应该响应的角色生成提示词
            if should_respond:
                typer.echo(f"\n--- Generating Prompt for Role '{role_id}' ---")
                prompt = coordinator.rules_engine.generate_role_prompt(role_id, context)
                typer.echo("Generated prompt:")
                typer.echo(prompt)
                typer.echo("-" * 50)
                
    except Exception as e:
        typer.echo(f"Error testing chat room rules: {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()