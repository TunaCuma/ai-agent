# AI Coding Agent using Gemini

An intelligent AI coding assistant powered by Google's Gemini 2.0 Flash model that can interact with your codebase, read files, execute Python scripts, and help debug issues.

## Features

- **File Operations**: List directories, read file contents, and write/modify files
- **Code Execution**: Run Python files with arguments and see results
- **Interactive REPL**: Chat with the AI in an interactive session
- **Single Command Mode**: Execute one-off commands quickly
- **Debugging Assistant**: Analyze and fix code issues

## Installation

Install packages using uv:

```bash
uv sync
```

Create a `.env` file and add your Gemini API key (you can copy `example.env` as a template):

```bash
cp example.env .env
# Edit .env and add your GEMINI_API_KEY
```

## Usage

### REPL Mode (Interactive Chat)

Start an interactive session where you can chat with the AI agent:

```bash
uv run main.py
```

**Example REPL session:**

```
============================================================
🤖 AI Agent Interactive REPL
============================================================
Welcome! You can now chat with the AI agent.
The agent can help you with:
  • List files and directories
  • Read file contents
  • Execute Python files
  • Write or modify files

Commands:
  • Type your message and press Enter
  • Type 'exit', 'quit', or 'bye' to leave
  • Type 'clear' to clear conversation history
  • Type 'help' to see this message again
============================================================

👤 You: what files are in my project?
🔧 get_files_info...
   ✅ Completed

🤖 Agent: I can see your project structure! Here are the main files and directories:

**Root directory:**
- `main.py` - The main AI agent script
- `config.py` - Configuration file
- `tests.py` - Test file
- `pyproject.toml` - Project configuration
- `README.md` - Documentation

**Directories:**
- `calculator/` - Contains a calculator application
- `functions/` - Contains the AI agent's function implementations

**Calculator directory contents:**
- `main.py` - Calculator main script
- `tests.py` - Calculator tests
- `README.md` - Calculator documentation
- `pkg/` directory with `calculator.py` and `render.py`

Would you like me to explore any specific files or help you with something?

👤 You: run the calculator with "3 + 7 * 2"
🔧 run_python_file...
   ✅ Completed

🤖 Agent: I ran the calculator with "3 + 7 * 2" and got the result: **17**

This is the correct result following proper mathematical order of operations (PEMDAS/BODMAS), where multiplication is performed before addition: 7 * 2 = 14, then 3 + 14 = 17.

👤 You: exit
👋 Goodbye!
```

### Single Command Mode

Execute a single command without entering interactive mode:

```bash
uv run main.py "your command here"
```

### Demo: Bug Fixing

Here's a demonstration of the AI agent's debugging capabilities:

1. **Introduce a bug** - Manually update `calculator/pkg/calculator.py` and change the precedence of the + operator to 3:

```python
        self.precedence = {
            "+": 3,  # Wrong! Should be 1
            "-": 1,
            "*": 2,
            "/": 2,
        }
```

2. **Verify the bug** - Run the calculator to confirm incorrect results:

```bash
uv run calculator/main.py "3 + 7 * 2"
# Output: 20 (incorrect, should be 17)
```

3. **Fix with AI agent** - Ask the agent to debug and fix the issue:

```bash
uv run main.py "fix the bug in my calculator project with your available tools, this gives incorrect output: 3 + 7 * 2 should be 17 but returns 20"
```

The AI agent will:
- Analyze the calculator code
- Identify the incorrect operator precedence
- Fix the precedence values
- Verify the fix works correctly

## Command Line Options

- `-v, --verbose`: Show detailed output including token usage
- `-i, --interactive`: Force interactive REPL mode (same as running without arguments)

## Available Functions

The AI agent has access to these functions:

- **get_files_info**: List files and directories
- **get_file_content**: Read file contents
- **run_python_file**: Execute Python scripts with optional arguments
- **write_file**: Create or modify files
