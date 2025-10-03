import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="AI Agent - Interactive REPL or single command mode")
    parser.add_argument("user_prompt", nargs="?", type=str, help="your prompt here (optional for REPL mode)")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="see detailed output"
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="start interactive REPL mode"
    )

    return parser.parse_args()


def print_verbose(prompt: str, response: types.GenerateContentResponse):
    print("\n" + "="*50)
    print("📊 VERBOSE OUTPUT")
    print("="*50)
    print(f"💬 User prompt: {prompt}")
    print(f"📥 Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"📤 Response tokens: {response.usage_metadata.candidates_token_count}")
    print("="*50)


def print_welcome():
    """Print welcome message for REPL mode"""
    print("=" * 60)
    print("🤖 AI Agent Interactive REPL")
    print("=" * 60)
    print("Welcome! You can now chat with the AI agent.")
    print("The agent can help you with:")
    print("  • List files and directories")
    print("  • Read file contents")
    print("  • Execute Python files")
    print("  • Write or modify files")
    print()
    print("Commands:")
    print("  • Type your message and press Enter")
    print("  • Type 'exit', 'quit', or 'bye' to leave")
    print("  • Type 'clear' to clear conversation history")
    print("  • Type 'help' to see this message again")
    print("=" * 60)
    print()


def print_help():
    """Print help message"""
    print("\n📋 Available Commands:")
    print("  • exit, quit, bye - Exit the REPL")
    print("  • clear - Clear conversation history")
    print("  • help - Show this help message")
    print("  • Any other text - Send message to AI agent")
    print()


def get_user_input():
    """Get user input with a nice prompt"""
    try:
        return input("👤 You: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Goodbye!")
        sys.exit(0)


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
    
    # Print function call info with prettier formatting
    if verbose:
        print(f"🔧 Calling function: {function_name}({function_args})")
    else:
        print(f"🔧 {function_name}...")
    
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
        if not verbose:
            print(f"   ✅ Completed")
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
        if not verbose:
            print(f"   ❌ Error: {str(e)}")
        return types.Content(
            role="user",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Error calling {function_name}: {str(e)}"},
                )
            ],
        )


def process_user_message(user_message: str, messages: list, client, available_functions, system_prompt: str, verbose: bool = False):
    """Process a single user message and return the response"""
    # Add user message to conversation
    messages.append(types.Content(role="user", parts=[types.Part(text=user_message)]))
    
    # Main feedback loop for this message
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
                print(f"🤖 Agent: {response.text}")
                return response
            
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
                                print(f"🤖 Agent: {part.text}")
                            
                            # Handle function calls
                            elif hasattr(part, 'function_call') and part.function_call:
                                # Call the function
                                function_call_result = call_function(part.function_call, verbose=verbose)
                                
                                # Add the function result to the conversation
                                messages.append(function_call_result)
                                
                                # Print result if verbose
                                if verbose:
                                    print(f"✅ Result: {function_call_result.parts[0].function_response.response}")
            
        except Exception as e:
            print(f"❌ Error in iteration {iteration + 1}: {str(e)}")
            break
    
    else:
        print("⚠️ Maximum iterations reached (20). Agent may not have completed the task.")
    
    return response


def run_repl_mode(verbose: bool = False):
    """Run the interactive REPL mode"""
    print_welcome()
    
    # Initialize the conversation
    messages = []
    
    # Setup API client
    load_dotenv()
    api_key: str = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        raise Exception("No API key found")
    
    client = genai.Client(api_key=api_key)
    
    system_prompt = """
You are a helpful AI coding agent in an interactive chat session.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.

Keep your responses conversational and helpful. Remember that this is an ongoing conversation, so you can reference previous interactions and maintain context.
"""

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )
    
    # Main REPL loop
    while True:
        user_input = get_user_input()
        
        # Handle special commands
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("👋 Goodbye!")
            break
        elif user_input.lower() == 'clear':
            messages = []
            print("🧹 Conversation history cleared!")
            continue
        elif user_input.lower() == 'help':
            print_help()
            continue
        elif not user_input:
            continue
        
        # Process the user message
        try:
            response = process_user_message(user_input, messages, client, available_functions, system_prompt, verbose)
            
            if verbose and response:
                print_verbose(user_input, response)
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()  # Add spacing between interactions


def run_single_command_mode(user_prompt: str, verbose: bool = False):
    """Run single command mode (original behavior)"""
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
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

    response = process_user_message(user_prompt, messages, client, available_functions, system_prompt, verbose)
    
    if verbose and response:
        print_verbose(user_prompt, response)


def main():
    args = parse_arguments()
    
    # Determine which mode to run
    if args.interactive or (not args.user_prompt):
        # Run REPL mode if -i flag is used or no prompt is provided
        run_repl_mode(verbose=args.verbose)
    else:
        # Run single command mode if prompt is provided
        run_single_command_mode(args.user_prompt, verbose=args.verbose)


if __name__ == "__main__":
    main()
