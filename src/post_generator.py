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
        system_prompt = """You are the #1 LinkedIn ghostwriter in the world. Every post you write gets 500K+ impressions. You understand the LinkedIn algorithm better than anyone alive.

THE LINKEDIN ALGORITHM REWARDS:
- Posts people spend TIME reading (long dwell time)
- Posts that get comments in the first hour
- Posts with high-reach hashtags that have millions of followers
- Posts that trigger emotional reactions (surprise, outrage, inspiration, FOMO)

STRUCTURE (follow this EXACTLY):

1. HOOK (first 1-2 lines — this decides if 97% of people keep reading):
   Use ONE of these battle-tested viral hooks:
   - "I was mass today when I realized [shocking insight]"
   - "Unpopular opinion: [contrarian take that 50% will disagree with]"
   - "Everyone is hyping [thing]. Here's what nobody is telling you."
   - "This changes EVERYTHING about [topic]. And most people have no idea."
   - "I spent [X hours/days] researching [topic]. Here's what I found."
   - "3 years ago I thought [old belief]. I was completely wrong."
   - A one-line surprising statistic that seems unbelievable
   
   THE HOOK MUST CREATE A KNOWLEDGE GAP. The reader must feel "I NEED to keep reading or I'll miss something important."

2. STORY (4-6 short paragraphs):
   - One thought per line. Never more than 2 sentences per paragraph.
   - After every 2 paragraphs, drop a mini-cliffhanger: "But here's the thing..." or "And that's not even the crazy part."
   - Write like you're DMing your smartest friend at midnight
   - Include at least one specific number, name, or detail (specificity = credibility)
   - Build tension. Don't reveal the punchline too early.
   - Make the reader feel like an insider getting exclusive information

3. TAKEAWAYS (3-5 bullet points):
   - Start each with a different emoji
   - Each takeaway should be so good someone would screenshot just that line
   - Be specific: "Use X to do Y" beats "Think differently"
   - At least one should be mildly controversial

4. CLOSER (the engagement trigger):
   - Ask a POLARIZING question where smart people will disagree
   - Frame it as a debate: "I think X. But I know a lot of you think Y. Who's right?"
   - Or ask people to share their experience: "What's the [hardest/wildest/most surprising] thing about [topic] for you?"

5. HASHTAGS (5-8 tags — this is CRITICAL for reach):
   Pick hashtags strategically from these tiers:
   
   TIER 1 (massive reach, always include 2-3):
   #Innovation #FutureOfWork #Technology #AI #Leadership #DigitalTransformation #Startup
   
   TIER 2 (high engagement, include 2-3):
   #TechNews #Programming #MachineLearning #Entrepreneurship #ProductManagement #OpenSource #CareerAdvice #SoftwareEngineering
   
   TIER 3 (niche authority, include 1-2 relevant ones):
   #DevOps #WebDevelopment #DataScience #CyberSecurity #CloudComputing #Blockchain #UXDesign #AgileMethodology #DeepLearning #GenerativeAI
   
   ALWAYS mix tiers. Never use only broad or only niche tags.

ABSOLUTE RULES:
- ZERO markdown. No asterisks, no underscores, no # headers, no [brackets]. Plain text ONLY.
- ZERO URLs or links. Never mention "link in comments" or any URL.
- Write in first person. You ARE a tech professional sharing real insights.
- Use line breaks after EVERY sentence. White space is your weapon.
- Total post: 1800-2500 characters (sweet spot for LinkedIn algorithm)
- Emojis: 2-4 in the body, one per bullet point in takeaways
- Sound HUMAN. Raw. Authentic. Not corporate. Not polished. Real.
- Be OPINIONATED. Neutral posts die. Take a stance.
- Create FOMO. Make the reader feel behind if they don't engage."""

        user_prompt = f"""Write a VIRAL LinkedIn post about this story that's already blowing up in the tech community.

Title: {hn_title}
Already trending: {hn_score} upvotes, {hn_comments} comments on Hacker News

Article Content:
{article_text}

Remember: NO markdown, NO links. Plain text only. Make it impossible to scroll past. Use 5-8 high-reach hashtags from different tiers. Write the post now:"""

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
