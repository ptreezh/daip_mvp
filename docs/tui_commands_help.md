# DAIP-LIVE TUI Commands Help

## Available Commands

### Session Management
- `/pa <goal>` - Start a personal assistant session with a specific goal
- `/c` - Abort the current session
- `/g` - Continue the current session
- `/p` - Pause the current session
- `/l` - List session history
- `/v [query]` - Search sessions by query or list all
- `/t` - Show session tree
- `/tc <index>` - Abort current session and jump to specified session
- `/tt <index>` - Pause current session and jump to specified session

### Role Management
- `/role add <name> <persona>` - Create a new role
- `/role view <name>` - View details of a specific role
- `/role list` - List all available roles

### Knowledge Base
- `/0 [query]` - Search knowledge base or sync if no query

### Debate System
- `/debate <topic>` - Start a debate session on a specific topic

### System Commands
- `/model [name]` - View current model or change to specified model
- `/help` - Show this help document
- `/init` - Generate a daip.md project overview document
- `/quit` - Exit the TUI application
- `/exit` - Exit the TUI application

## Command Usage

Most commands follow the pattern: `/command [arguments]`

For example:
- `/pa "Help me plan a project"` - Starts a personal assistant session
- `/role add "researcher" "A research assistant persona"` - Creates a new role
- `/model llama3:70b` - Changes the model to llama3:70b

## Navigation

- Use `Ctrl+Tab` to toggle focus between input and output areas
- Use `Escape` to abort all sessions and return to default
- Use `Ctrl+A` to select all text in output mode
- Use `Ctrl+C` to copy selected text in output mode

## Status Bar Information

The status bar at the bottom shows:
- Current model name
- Token usage (used/total percentage)
- System status (Idle, Thinking, etc.)
- Current focus mode (Input/Output)