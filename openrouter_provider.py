"""
OpenRouter Provider
"""
from openai import OpenAI

from openai_provider import OpenAIProvider


class OpenRouterProvider(OpenAIProvider):
    """OpenRouter multi-model AI provider"""

    def __init__(self, api_key: str, model: str = "openrouter/auto"):
        super().__init__(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model=model
        )
        # Add OpenRouter identification headers
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/NimuthuGanegoda/PilotHub",
                "X-Title": "PilotHub"
            }
        )
