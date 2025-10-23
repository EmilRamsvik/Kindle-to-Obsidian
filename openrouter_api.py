from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider


from typing import List
from pydantic import BaseModel, field_validator
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BookReview(BaseModel):
    summary: str
    impressions: str
    tags: List[str]

    @field_validator("tags")
    @classmethod
    def tags_format(cls, tags):
        import re

        # Allow tags like "- main/name" or "- main-name", starting with hyphen + space,
        # then lowercase letters, with optional hyphens or slashes separating parts.
        pattern = re.compile(r"^- [a-z]+([-/][a-z]+)*$")
        if not isinstance(tags, list):
            raise ValueError("Tags must be a list.")
        for tag in tags:
            t = tag.strip()
            if not pattern.fullmatch(t):
                raise ValueError(
                    f"Invalid tag: '{tag}'. Tags must start with '- ', use lowercase, and use hyphens or slashes as separators (e.g., '- name', '- this-name', '- main/name')."
                )
        return tags


model = OpenAIChatModel(
    "anthropic/claude-3.5-sonnet",
    provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
)


SYSTEM_PROMPT = """You are an expert book analyst helping to create concise, insightful book notes from Kindle highlights.

Your task is to analyze the provided quotes from a book and generate:

1. **The Book in 3 Sentences**: A concise 2-3 sentence summary that captures the core themes, main arguments, or key insights of the book. Focus on WHAT the book covers and WHY it matters. Keep it informative and direct. Use linebreaks for readability.

2. **Impressions**: A personal, reflective commentary (2-4 sentences) about the book's quality, impact, or notable aspects. This should feel conversational and honest, capturing what stood out - whether positive observations, criticisms, or interesting patterns. Think about:
   - Overall quality and writing style
   - Key takeaways or memorable aspects
   - How the book relates to other works or ideas

3. **Tags**: Generate 3-15 relevant tags that categorize the book by topic, genre, or theme. Tags must:
   - Start with a hyphen (e.g., "-business", "-biography")
   - Use lowercase letters only
   - Use hyphens to separate multi-word tags (e.g., "-digital-transformation")
   - use slashes to separate parts of a tag (e.g., "-history/modern-history")
Guidelines:
- Be honest and direct - avoid generic praise
- Match the tone of the examples: thoughtful, slightly informal, and authentic
- Don't make up information not supported by the quotes
- Keep summaries factual; keep impressions more subjective

Examples of good outputs:

Example 1:
Summary: "This book covers how digital transformations are shaping all industries (Software eating the world). It covers platforms, product as a service and analytics as important concepts."
Impressions: "It was interesting, but a bit of the usual business book nonsense. I kinda felt it did a good job of highlighting concepts within digitalization as well as strategies and examples."
Tags: ["-books", "-digital-transformation", "-business", "-technology", "-strategy"]

Example 2:
Summary: "This is the penultimate biography of Churchill. It develops quite deeply into Churchill, the man, the adventurer and the statesman. It needed over 1000 pages, and probably more could have been written."
Impressions: "Great men gather divisive opinions. Churchill was an imperialist, leave no doubt about that. He lived for the British empire."
Tags: ["-books", "-biography", "-history", "-leadership", "-military", "-political-history", "-politics", "-world-war", "-british-empire", "-digital-garden", "-book-review", "-history-british", "-history-military"]
"""

agent = Agent(model, output_type=BookReview, system_prompt=SYSTEM_PROMPT)
