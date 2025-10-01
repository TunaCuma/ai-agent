import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("user_prompt", type=str, help="your prompt here")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="see detailed output"
    )

    return parser.parse_args()


def print_verbose(prompt: str, response: types.GenerateContentResponse):
    print(f"User prompt: {prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


def main():
    args = parse_arguments()

    messages = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)]),
    ]

    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )

    # Check if the LLM made function calls
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                function_call_part = part.function_call
                print(f"Calling function: {function_call_part.name}({function_call_part.args})")
            elif hasattr(part, 'text') and part.text:
                print(part.text)

    if args.verbose:
        print_verbose(args.user_prompt, response)


if __name__ == "__main__":
    main()
