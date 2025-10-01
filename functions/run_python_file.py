import os
import subprocess

def run_python_file(working_directory: str, file_path: str, args=[]):
    """A tool call function for an AI agent to use"""
    try:
        # Get the absolute path of the file
        full_path = os.path.abspath(os.path.join(working_directory, file_path))
        
        # Check if file is outside working directory
        if not full_path.startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        # Check if file exists
        if not os.path.exists(full_path):
            return f'Error: File "{file_path}" not found.'
        
        # Check if file is a Python file
        if not full_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'
        
        # Execute the Python file
        completed_process = subprocess.run(
            ["python", full_path] + args,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Format the output
        output_parts = []
        
        if completed_process.stdout:
            output_parts.append(f"STDOUT:\n{completed_process.stdout}")
        
        if completed_process.stderr:
            output_parts.append(f"STDERR:\n{completed_process.stderr}")
        
        if completed_process.returncode != 0:
            output_parts.append(f"Process exited with code {completed_process.returncode}")
        
        # Return formatted output or default message
        if output_parts:
            return "\n".join(output_parts)
        else:
            return "No output produced."
    
    except subprocess.TimeoutExpired:
        return "Error: executing Python file: Process timed out after 30 seconds"
    except Exception as e:
        return f"Error: executing Python file: {e}"
