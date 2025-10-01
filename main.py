import os
from dotenv import load_dotenv
from google import genai
import sys

def main():
    args = sys.argv

    if len(args) <= 1:
        raise Exception("no prompt provided")

    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=args[1],
    )

    print(response.text)

    print(
        f"Prompt tokens: {response.usage_metadata.prompt_token_count}\nResponse tokens: {response.usage_metadata.candidates_token_count}"
    )


if __name__ == "__main__":
    main()
