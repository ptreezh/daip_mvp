import logging
import os
from pathlib import Path

# Define a base directory for security. Tools should not access files outside this directory.
try:
    # Assuming the script is run from the project root.
    # A more robust solution might involve environment variables or a config file.
    BASE_DIR = Path(os.getcwd()).resolve()
except FileNotFoundError:
    # Fallback for environments where getcwd is not available
    BASE_DIR = Path("/").resolve()


def list_files(directory: str = ".") -> str:
    """
    Lists the files and subdirectories in a specified directory.

    Args:
        directory (str): The path to the directory, relative to the project root.
                         Defaults to the current directory (".").

    Returns:
        str: A string containing the list of files and directories,
             or an error message if the directory is not found, not accessible,
             or outside the allowed project scope.
    """
    try:
        target_path = BASE_DIR.joinpath(directory).resolve()

        # Security Check: Prevent directory traversal attacks.
        if not str(target_path).startswith(str(BASE_DIR)):
            logging.warning(f"Access denied: Path '{directory}' is outside the allowed base directory.")
            return f"Error: Access denied. Path is outside the allowed project scope."

        if not target_path.is_dir():
            return f"Error: Directory not found at '{directory}'."

        items = os.listdir(target_path)
        if not items:
            return f"The directory '{directory}' is empty."

        return "Files and directories in '{}':\n- {}".format(directory, "\n- ".join(items))

    except PermissionError:
        logging.error(f"Permission denied for directory: {directory}")
        return f"Error: Permission denied to access the directory '{directory}'."
    except Exception as e:
        logging.exception(f"An unexpected error occurred in list_files for directory: {directory}")
        return f"An unexpected error occurred: {e}"


def read_file(file_path: str) -> str:
    """
    Reads the content of a specified file.

    Args:
        file_path (str): The path to the file, relative to the project root.

    Returns:
        str: The content of the file, or an error message if the file
             is not found, not accessible, or outside the allowed scope.
    """
    try:
        target_path = BASE_DIR.joinpath(file_path).resolve()

        # Security Check
        if not str(target_path).startswith(str(BASE_DIR)):
            logging.warning(f"Access denied: Path '{file_path}' is outside the allowed base directory.")
            return "Error: Access denied. Path is outside the allowed project scope."

        if not target_path.is_file():
            return f"Error: File not found at '{file_path}'."

        return target_path.read_text(encoding="utf-8")

    except Exception as e:
        logging.exception(f"An unexpected error occurred in read_file for path: {file_path}")
        return f"An unexpected error occurred while reading the file: {e}"


def write_file(file_path: str, content: str) -> str:
    """
    Writes or overwrites content to a specified file.

    Args:
        file_path (str): The path to the file, relative to the project root.
        content (str): The content to write to the file.

    Returns:
        str: A success message or an error message.
    """
    try:
        target_path = BASE_DIR.joinpath(file_path).resolve()

        # Security Check
        if not str(target_path).startswith(str(BASE_DIR)):
            logging.warning(f"Access denied: Path '{file_path}' is outside the allowed base directory.")
            return "Error: Access denied. Path is outside the allowed project scope."

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to file '{file_path}'."

    except Exception as e:
        logging.exception(f"An unexpected error occurred in write_file for path: {file_path}")
        return f"An unexpected error occurred while writing to the file: {e}"