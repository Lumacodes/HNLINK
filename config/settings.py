import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    # OpenRouter
    openrouter_api_key: str = field(
        default_factory=lambda: os.environ["OPENROUTER_API_KEY"]
    )
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "deepseek/deepseek-v4-flash:free"

    # LinkedIn
    linkedin_access_token: str = field(
        default_factory=lambda: os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    )
    linkedin_person_urn: str = field(
        default_factory=lambda: os.environ.get("LINKEDIN_PERSON_URN", "")
    )

    # n8n
    n8n_base_url: str = field(
        default_factory=lambda: os.environ.get("N8N_BASE_URL", "http://localhost:5678")
    )
    n8n_webhook_token: str = field(
        default_factory=lambda: os.environ.get("N8N_WEBHOOK_TOKEN", "")
    )

    # WhatsApp
    whatsapp_recipient: str = field(
        default_factory=lambda: os.environ.get("WHATSAPP_RECIPIENT_NUMBER", "")
    )

    # HN Bot
    hn_top_stories_count: int = field(
        default_factory=lambda: int(os.environ.get("HN_TOP_STORIES_COUNT", "15"))
    )
    hn_random_rising_count: int = field(
        default_factory=lambda: int(os.environ.get("HN_RANDOM_RISING_COUNT", "5"))
    )
    hn_min_score: int = field(
        default_factory=lambda: int(os.environ.get("HN_MIN_SCORE", "50"))
    )
    content_max_chars: int = field(
        default_factory=lambda: int(os.environ.get("CONTENT_MAX_CHARS", "8000"))
    )
    posts_to_generate: int = field(
        default_factory=lambda: int(os.environ.get("POSTS_TO_GENERATE", "3"))
    )


settings = Settings()
