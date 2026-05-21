"""
Generates viral LinkedIn posts using OpenRouter API.

Uses the OpenAI Python SDK pointed at OpenRouter's base URL.
Model: deepseek/deepseek-v4-flash:free

Posts are optimized for maximum engagement:
- Clickbait hooks that stop the scroll
- Short punchy lines (mobile-first)
- No markdown (LinkedIn doesn't render it)
- No external links (keep users on your post)
"""

import re
from typing import Optional

from openai import OpenAI

from config.settings import settings


class PostGenerator:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
        )
        self.model = settings.openrouter_model

    def _clean_output(self, text: str) -> str:
        """Strip markdown artifacts that LinkedIn can't render."""
        # Remove bold/italic markdown
        text = text.replace("**", "")
        text = text.replace("__", "")
        text = text.replace("*", "")
        text = text.replace("_", " ")
        # Remove markdown headers
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
        # Remove markdown links [text](url) -> text
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        # Remove any leftover URLs at the end
        text = re.sub(r"https?://\S+\s*$", "", text, flags=re.MULTILINE)
        # Clean up excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _is_valid_output(self, text: str) -> bool:
        """Check if generated text is valid (not garbled/corrupted)."""
        if not text or len(text) < 200:
            return False
        # Check for excessive non-ASCII gibberish (sign of model degeneration)
        ascii_chars = sum(1 for c in text if ord(c) < 128)
        ratio = ascii_chars / len(text)
        if ratio < 0.85:
            return False
        # Check for common corruption patterns
        corruption_signs = ["\\u", "\\n\\n\\n", "---nam", "婴儿", "感染", "収購"]
        for sign in corruption_signs:
            if sign in text:
                return False
        return True

    def _build_messages(self, article_text: str, hn_title: str,
                        hn_score: int, hn_comments: int) -> list[dict]:
        system_prompt = """You are a LinkedIn ghostwriter who creates VIRAL posts that get millions of impressions. Your posts are designed to STOP THE SCROLL and make people engage.

STRUCTURE (follow this exactly):

1. HOOK (first 2 lines): This is EVERYTHING. Use one of these proven formats:
   - "I just discovered something that changes everything about [topic]."
   - "Everyone is talking about [thing]. But nobody is talking about THIS."
   - "This will sound crazy, but [surprising claim]."
   - A shocking statistic or contrarian hot take
   - "Stop scrolling. This is important."

2. STORY (3-5 short paragraphs): 
   - Each paragraph is 1-2 sentences MAX
   - Every line should make them want to read the next one
   - Use cliffhanger transitions between paragraphs
   - Make it feel like YOU discovered this personally
   - Write like you're texting a smart friend, not writing an essay

3. TAKEAWAYS (3-5 bullet points):
   - Start each with an emoji
   - Make each one a standalone insight that could be shared
   - Be specific and actionable, not generic advice

4. CLOSER:
   - End with a polarizing question that FORCES people to comment
   - Something people will disagree on (disagreement = engagement)

CRITICAL RULES:
- NEVER use markdown formatting. No asterisks, no underscores, no headers, no brackets.
- NEVER include URLs or links anywhere in the post
- NEVER mention "link in comments" or "article link" or anything about links
- Use plain text ONLY. Bold does NOT work on LinkedIn.
- Write in first person. Make it personal.
- Use line breaks AGGRESSIVELY. One thought per line.
- Keep total length under 2500 characters
- Use 3-5 hashtags at the very end
- Use emojis sparingly but strategically (2-4 max in the main text)
- Sound like a HUMAN who is genuinely excited, not a corporate account
- Be slightly controversial. Safe posts don't go viral.
- Make it feel urgent. FOMO drives shares."""

        user_prompt = f"""Write a VIRAL LinkedIn post based on this trending tech story.

Title: {hn_title}
Popularity: {hn_score} upvotes, {hn_comments} comments (it's already trending)

Article Content:
{article_text}

Remember: NO markdown, NO links, NO URLs. Plain text only. Make it scroll-stopping clickbait that gets massive engagement. Write the post now:"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def generate(
        self,
        article_text: str,
        hn_title: str,
        hn_url: str,
        hn_score: int,
        hn_comments: int,
        max_retries: int = 3,
    ) -> Optional[str]:
        """
        Generate a viral LinkedIn post from article content.
        Retries on garbled output. Returns clean plain text or None.
        """
        messages = self._build_messages(article_text, hn_title, hn_score, hn_comments)

        for attempt in range(max_retries):
            try:
                # Vary temperature slightly on retries to get different output
                temp = 0.8 + (attempt * 0.05)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=1500,
                    extra_headers={
                        "HTTP-Referer": "https://localhost",
                        "X-Title": "HN-to-LinkedIn Bot",
                    },
                )
                raw_text = response.choices[0].message.content.strip()

                if self._is_valid_output(raw_text):
                    return self._clean_output(raw_text)
                else:
                    print(f"[PostGenerator] Attempt {attempt + 1}: garbled output, retrying...")

            except Exception as e:
                print(f"[PostGenerator] Attempt {attempt + 1} error: {e}")

        print("[PostGenerator] All attempts failed")
        return None
