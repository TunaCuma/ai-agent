import os

from google.genai.models import types


def get_files_info(working_directory: str, directory="."):
    """A tool call function for an AI agent to use"""
    try:
        full_path = os.path.abspath(os.path.join(working_directory, directory))

        if not os.path.isdir(full_path):
            return f'Error: "{directory}" is not a directory'
        if not full_path.startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        file_infos_string = "\n".join(
            [
                f"- {file}: file_size={os.path.getsize(os.path.join(full_path, file))} bytes, is_dir={os.path.isdir(os.path.join(full_path, file))}"
                for file in os.listdir(full_path)
            ]
        )
    except OSError as e:
        return f"Error: An OSError has occured: {e}"
    except Exception as e:
        return f"Error: {e}"

    return file_infos_string

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)
