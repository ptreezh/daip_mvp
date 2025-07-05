import logging

from src.kernel.tool_executor import ToolExecutor

from .file_system_tools import list_files, read_file, write_file
from .kanban_tools import create_task, list_tasks, update_task
from .wiki_tools import list_wiki_entries, read_wiki_entry, search_wiki, write_wiki_entry
from .tool_definitions import (
    CREATE_TASK_DEF,
    LIST_FILES_DEF,
    LIST_TASKS_DEF,
    LIST_WIKI_ENTRIES_DEF,
    READ_FILE_DEF,
    READ_WIKI_ENTRY_DEF,
    SEARCH_WIKI_DEF,
    UPDATE_TASK_DEF,
    WRITE_FILE_DEF,
    WRITE_WIKI_ENTRY_DEF,
)


def register_all_tools(executor: ToolExecutor) -> None:
    """
    Registers all available tools with the provided ToolExecutor instance.

    This function acts as a single entry point for tool registration, making
    it easy to initialize the system's capabilities.

    Args:
        executor (ToolExecutor): The executor instance to register tools with.
    """
    executor.register_tool(list_files, LIST_FILES_DEF)
    executor.register_tool(read_file, READ_FILE_DEF)
    executor.register_tool(write_file, WRITE_FILE_DEF)

    # Register Kanban tools
    executor.register_tool(create_task, CREATE_TASK_DEF)
    executor.register_tool(list_tasks, LIST_TASKS_DEF)
    executor.register_tool(update_task, UPDATE_TASK_DEF)

    # Register Wiki (Memory Bank) tools
    executor.register_tool(write_wiki_entry, WRITE_WIKI_ENTRY_DEF)
    executor.register_tool(read_wiki_entry, READ_WIKI_ENTRY_DEF)
    executor.register_tool(list_wiki_entries, LIST_WIKI_ENTRIES_DEF)
    executor.register_tool(search_wiki, SEARCH_WIKI_DEF)

    logging.info("All available tools have been registered.")