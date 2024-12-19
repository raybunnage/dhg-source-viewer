# import sys

# sys.path.append("src")
import os
from anthropic import Anthropic
import dotenv

dotenv.load_dotenv()

""" INSTRUCTIONS

This module provides helper functions for interacting with the Anthropic Claude API.

if __name__ == "__main__":
    get_file_and_questions(file_name, naviaux_questions)

MAIN FUNCTIONS:
1. * get_file_and_questions():
   - Gets a file and asks questions about it

2. ** call_claude_basic():
   - Simple text processing with system prompt
   - Called by many many modules
   - Usage: Call for basic Claude interactions

3. ** call_claude_messages():
   - Processes complex prompts with custom messages
   - Called by citations.py, master_categories.py, transcription_processing.py
   - Usage: Call for complex Claude interactions requiring specific message formats

4. ** call_claude_follow_up():
   - Processes follow up prompts with custom messages
   - Called by concepts_pdfs.py and concepts_txts.py
   - Usage: Call for follow up Claude interactions requiring specific message formats

5. ** call_claude_pdf_with_messages():
   - Processes complex PDF-related prompts with custom messages
   - not yet called externally
   - Usage: Call for PDF analysis requiring specific message formats

4. ** call_claude_pdf_basic():
   - Simple PDF processing with basic prompt
   - not yet called externally
   - Usage: Call for straightforward PDF analysis tasks


INTNERAL HELPER FUNCTIONS:
1. get_pdf_client_and_model():
   - internal helper to Returns configured PDF-enabled Claude client and model name
   - Called by get_file_and_questions()
   - Usage: Call when needing to process PDFs with Claude

2. get_std_client_and_model(): 
   - internal helper to Returns standard Claude client and model name
   - Called by call_claude_basic() and call_claude_messages
   - Usage: Call for non-PDF Claude interactions

3. get_completion():
   - internal helper to get completions
   - Called by call_claude_basic() and call_claude_messages

4. prompt_questions():
   - internal helper to prompt questions about a pdf file
   - Called by get_file_and_questions()

USAGE:
- Import needed client/model getters and processing functions
- Use PDF-specific functions (call_claude_pdf_*) when working with PDFs
- Use call_claude_basic() for text-only processing
- Configure system prompts and messages as needed for specific tasks

STATUS:
The module provides core Claude API interaction functionality, including both standard and PDF-enabled operations. It serves as a central point for Claude API interactions across the project.

FEEDBACK:
1. Consider separating PDF-specific functionality into a dedicated module (e.g., claude_pdf_utils.py)
2. Implement a ClaudeClient class to encapsulate client creation and basic operations
3. Add comprehensive error handling and logging
4. Improve type hints and docstrings for all functions
5. Implement a configuration management system for API keys and model names
6. Add unit tests for each function to ensure reliability

UNUSED/DUPLICATE FUNCTIONS:
This module does not contain unused or duplicate functions. All listed functions serve specific purposes and are likely called from other parts of the project.

"""


class AnthropicService:
    def __init__(self, api_key: str):
        """Initialize Anthropic clients and model name."""
        self.std_client = Anthropic(api_key=api_key)
        self.pdf_client = Anthropic(
            default_headers={"anthropic-beta": "pdfs-2024-09-25"}
        )
        self.model_name = "claude-3-5-sonnet-20241022"

    # def _get_completion(self, client, messages):
    #     """Internal helper to get completions from Claude API."""
    #     return (
    #         client.messages.create(
    #             model=self.model_name, max_tokens=4096, messages=messages
    #         )
    #         .content[0]
    #         .text
    #     )

    def call_claude_basic(
        self, max_tokens: int, input_string: str, system_string: str
    ) -> str:
        """Basic Claude call with system prompt and single user message."""
        response = self.std_client.messages.create(
            model=self.model_name,
            system=system_string,
            messages=[{"role": "user", "content": input_string}],
            max_tokens=max_tokens,
        )
        return response.content[0].text

    def call_claude_messages(
        self, max_tokens: int, messages, system_string: str
    ) -> str:
        """Complex Claude call supporting multiple messages and system prompt."""
        response = self.std_client.messages.create(
            model=self.model_name,
            system=system_string,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.content[0].text

    def call_claude_follow_up(
        self,
        max_tokens: int,
        input_string: str,
        follow_up_message: str,
        system_string: str,
    ) -> str:
        """Follow-up Claude call with conversation history."""
        response = self.std_client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            system=system_string,
            temperature=0,
            messages=[
                {"role": "user", "content": input_string},
                {"role": "assistant", "content": follow_up_message},
            ],
        )
        return response.content[0].text if response.content else None

    # ... existing code ...
    def test_anthropic(self):

        # Test basic call
        response = self.call_claude_basic(
            max_tokens=1000,
            input_string="Hello!",
            system_string="You are a helpful assistant",
        )
        print("Basic Call Response:", response)

        # Test complex call with multiple messages
        messages = [
            {"role": "user", "content": "Tell me a joke."},
            {"role": "assistant", "content": "Why did the chicken cross the road?"},
            {"role": "user", "content": "I don't know, why?"},
        ]
        response = self.call_claude_messages(
            max_tokens=1000, messages=messages, system_string="You are a helpful assistant"
        )
        print("Complex Call Response:", response)

        # Test follow-up call
        response = self.call_claude_follow_up(
            max_tokens=1000,
            input_string="Tell me a joke.",
            follow_up_message="Why did the chicken cross the road?",
            system_string="You are a snarky know it all assistant",
        )
        print("Follow-up Call Response:", response)




if __name__ == "__main__":
    api_key=os.environ.get("ANTHROPIC_API_KEY")
    anthropic = AnthropicService(api_key)
    anthropic.test_anthropic()
