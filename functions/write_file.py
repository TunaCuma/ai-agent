import os

from google.genai.models import types

def write_file(working_directory: str, file_path: str, content: str):
    """A tool call function for an AI agent to use"""
    try:
        full_path = os.path.abspath(os.path.join(working_directory, file_path))
        
        # Security check: ensure the file is within the working directory
        if not full_path.startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        
        # If the file doesn't exist, create the necessary directories
        if not os.path.exists(full_path):
            dir_name = os.path.dirname(full_path)
            if dir_name:  # Only create if there's a directory path
                os.makedirs(dir_name, exist_ok=True)
        
        # Write the content to the file
        with open(full_path, "w") as f:
            f.write(content)
        
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        
    except OSError as e:
        return f"Error: An OSError has occurred: {e}"
    except Exception as e:
        return f"Error: {e}"


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites content to a specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)
