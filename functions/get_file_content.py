import os

from config import MAX_CHARS



def get_file_content(working_directory: str, file_path: str):
    """A tool call function for an AI agent to use"""
    try:
        full_path = os.path.abspath(os.path.join(working_directory, file_path))

        if not os.path.isfile(full_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        if not full_path.startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        with open(full_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)

        if len(file_content_string) == MAX_CHARS:
            file_content_string = file_content_string + f'\n[...File "{file_path}" truncated at 10000 characters]'

        return file_content_string
    except OSError as e:
        return f"Error: An OSError has occured: {e}"
    except Exception as e:
        return f"Error: {e}"
