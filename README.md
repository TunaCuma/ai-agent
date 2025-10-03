# AI coding agent using gemini

## Installation

Install packages

```bash
uv sync
```

Create an .env file and add your gemini key in it, you can copy example.env file for a template.

## Demo

- Manually update `calculator/pkg/calculator.py` and change the precedence of the + operator to 3.

```python
        self.precedence = {
            "+": 3,
            "-": 1,
            "*": 2,
            "/": 2,
        }
```

- Run the calculator app, to make sure it's now producing incorrect results: uv run calculator/main.py "3 + 7 * 2" (this should be 17, but because we broke it, it says 20)

```bash
uv run calculator/main.py "3 + 7 * 2"
```

- Run the agent, and ask it to "fix the bug: 3 + 7 * 2 shouldn't be 20"

```bash
uv run main.py "fix the bug in my calculator project with your available tools, this gives incorrect output 3 + 7 * 2"
```
