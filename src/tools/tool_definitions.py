from typing import Any

# This file centralizes the JSON Schema definitions for all tools.
# This makes them easy to manage and import for registration.

LIST_FILES_DEF: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "List all files and subdirectories within a specified directory of the project.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "The relative path to the directory. Defaults to the project root if not specified.",
                }
            },
            "required": [],
        },
    },
}

READ_FILE_DEF: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Reads the entire content of a specified file within the project.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The relative path to the file that needs to be read.",
                }
            },
            "required": ["file_path"],
        },
    },
}

WRITE_FILE_DEF: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Writes content to a specified file within the project. If the file exists, it will be overwritten. If the directory does not exist, it will be created.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The relative path to the file to be written.",
                },
                "content": {
                    "type": "string",
                    "description": "The text content to write into the file.",
                },
            },
            "required": ["file_path", "content"],
        },
    },
}

CREATE_TASK_DEF: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "create_task",
        "description": "Creates a new task on the project Kanban board.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the task.",
                },
                "description": {
                    "type": "string",
                    "description": "A detailed description of the task.",
                },
                "status": {
                    "type": "string",
                    "description": "The initial status of the task. Defaults to 'TODO'.",
                    "enum": ["TODO", "IN_PROGRESS", "DONE", "BLOCKED"],
                },
            },
            "required": ["title", "description"],
        },
    },
}

LIST_TASKS_DEF: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "list_tasks",
        "description": "Lists all tasks on the Kanban board, with an option to filter by status.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Optional. Filters tasks by this status.",
                    "enum": ["TODO", "IN_PROGRESS", "DONE", "BLOCKED"],
                }
            },
            "required": [],
        },
    },
}

UPDATE_TASK_DEF: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "update_task",
        "description": "Updates the status or description of an existing task by its ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The unique ID of the task to update.",
                },
                "new_status": {
                    "type": "string",
                    "description": "The new status to assign to the task.",
                    "enum": ["TODO", "IN_PROGRESS", "DONE", "BLOCKED"],
                },
                "new_description": {
                    "type": "string",
                    "description": "The new, updated description for the task.",
                },
            },
            "required": ["task_id"],
        },
    },
}

WRITE_WIKI_ENTRY_DEF: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "write_wiki_entry",
        "description": "Creates or overwrites a knowledge entry in the shared Memory Bank (Wiki).",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The unique title for the wiki entry.",
                },
                "content": {
                    "type": "string",
                    "description": "The full content of the wiki entry, preferably in Markdown format.",
                },
            },
            "required": ["title", "content"],
        },
    },
}

READ_WIKI_ENTRY_DEF: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "read_wiki_entry",
        "description": "Reads the content of a specific knowledge entry from the Memory Bank (Wiki).",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the wiki entry to read.",
                }
            },
            "required": ["title"],
        },
    },
}

LIST_WIKI_ENTRIES_DEF: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "list_wiki_entries",
        "description": "Lists the titles of all knowledge entries currently stored in the Memory Bank (Wiki).",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

SEARCH_WIKI_DEF: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_wiki",
        "description": "Performs a semantic search for a query across all knowledge entries in the Memory Bank (Wiki) to find the most relevant information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The natural language query or concept to search for.",
                }
            },
            "required": ["query"],
        },
    },
}
