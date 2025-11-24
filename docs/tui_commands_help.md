# DAIP-LIVE TUI Commands Help

## Available Commands

### Session Management
- `/pa <goal>` - Start a personal assistant session with a specific goal
- `/session list` - List all available sessions
- `/session view [session_id]` - View details of a specific session
- `/session clear` - Clear current session context and reset tokens
- `/session reset` - Reset token usage counter to zero

#### Token Management (80% Auto-Compression)
- **Auto-Compression**: Automatically triggers at 80% token usage
- **Manual Control**: Use `/session clear` or `/session reset` commands
- **Smart Compression**: LLM generates structured summaries to save space

### Role Management
- `/role add <name> <persona>` - Create a new role
- `/role view <name>` - View details of a specific role
- `/role list` - List all available roles

### Debate System
- `/debate <topic>` - Start a debate session on a specific topic

### Permission Management
- `/permission list` - List all permission rules
- `/permission set <tool_name> <permission>` - Set permission for a specific tool
- `/permission reset <tool_name>` - Reset tool permission to default
- `/permission default <permission>` - Set default permission policy

#### Permission Values
- `allow` - Always allow tool execution
- `deny` - Always deny tool execution
- `ask` - Ask user for permission before tool execution

### Document Management
- `/doc fetch <query>` - Fetch academic papers related to the query
- `/doc export <input.md> --to <format>` - Export markdown file to PDF or DOCX format

### Wiki Management
- `/wiki new <title>` - Create a new wiki page with the given title
- `/wiki list` - List all wiki pages
- `/wiki open <title>` - Open a wiki page
- `/wiki search <query>` - Search wiki pages for the query

### System Commands
- `/model [name]` - View current model or change to specified model
- `/help` - Show this help document
- `/quit` - Exit the TUI application

## Command Usage

Most commands follow the pattern: `/command [arguments]`

For example:
- `/pa "Help me plan a project"` - Starts a personal assistant session
- `/role add "researcher" "A research assistant persona"` - Creates a new role
- `/model llama3:70b` - Changes the model to llama3:70b
- `/permission set read_file allow` - Allow read_file tool execution
- `/permission list` - Show all permission rules

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