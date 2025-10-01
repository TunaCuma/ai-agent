import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


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

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
    )

    print(response.text)

    if args.verbose:
        print_verbose(args.user_prompt, response)


if __name__ == "__main__":
    main()
