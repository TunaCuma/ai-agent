import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file


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


def call_function(function_call_part, verbose=False):
    """Handle calling one of the functions based on the function call from the LLM"""
    
    # Dictionary mapping function names to actual functions
    available_functions = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }
    
    function_name = function_call_part.name
    function_args = dict(function_call_part.args)
    
    # Print function call info
    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")
    
    # Check if function exists
    if function_name not in available_functions:
        return types.Content(
            role="user",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    # Add working directory to arguments
    function_args["working_directory"] = "./calculator"
    
    # Call the function
    try:
        function_result = available_functions[function_name](**function_args)
        return types.Content(
            role="user",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        )
    except Exception as e:
        return types.Content(
            role="user",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Error calling {function_name}: {str(e)}"},
                )
            ],
        )


def main():
    args = parse_arguments()

    messages = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)]),
    ]

    load_dotenv()

    api_key: str = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise Exception("No API key found")

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

    # Main feedback loop
    max_iterations = 20
    
    for iteration in range(max_iterations):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt
                ),
            )
            
            # Check if we have a final text response (agent is done)
            # Only check response.text if there are no function calls to avoid warnings
            has_function_calls = False
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                has_function_calls = True
                                break
                    if has_function_calls:
                        break
            
            # If no function calls, check for final text response
            if not has_function_calls and response.text:
                print(response.text)
                break
            
            # Process each candidate response
            if response.candidates:
                for candidate in response.candidates:
                    # Add the model's response to the conversation
                    messages.append(candidate.content)
                    
                    # Process all parts in the response (text and function calls)
                    if candidate.content.parts:
                        for part in candidate.content.parts:
                            # Handle text parts (agent commentary)
                            if hasattr(part, 'text') and part.text:
                                print(part.text)
                            
                            # Handle function calls
                            elif hasattr(part, 'function_call') and part.function_call:
                                # Call the function
                                function_call_result = call_function(part.function_call, verbose=args.verbose)
                                
                                # Add the function result to the conversation
                                messages.append(function_call_result)
                                
                                # Print result if verbose
                                if args.verbose:
                                    print(f"-> {function_call_result.parts[0].function_response.response}")
            
        except Exception as e:
            print(f"Error in iteration {iteration + 1}: {str(e)}")
            break
    
    else:
        print("Maximum iterations reached (20). Agent may not have completed the task.")

    if args.verbose:
        print_verbose(args.user_prompt, response)


if __name__ == "__main__":
    main()
