<div align="center">

# 🔥 HNLINK

### Turn Hacker News into LinkedIn Virality — On Autopilot

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-API-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://developer.linkedin.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![HF Spaces](https://img.shields.io/badge/🤗-Deploy%20Free-yellow?style=for-the-badge)](https://huggingface.co/spaces)

**Stop writing LinkedIn posts manually. Let AI do the work, you just hit approve.**

[Getting Started](#-getting-started) · [How It Works](#-how-it-works) · [Deploy Free](#-deploy-for-free) · [Commands](#-telegram-commands)

</div>

---

## 💡 The Problem

You know that feeling. You see a killer article on Hacker News. You think "this would make a great LinkedIn post." Then you spend 20 minutes writing it, second-guessing every word, and by the time you post it... nobody cares because the timing is off.

I built HNLINK because I was tired of that loop.

## ⚡ What It Does

HNLINK is a fully automated pipeline that:

1. 🕵️ **Scrapes** trending stories from Hacker News (top + rising)
2. 📰 **Reads** the actual article content (not just titles)
3. 🖼️ **Grabs** the article's featured image
4. 🤖 **Generates** a scroll-stopping LinkedIn post using AI
5. 📱 **Sends** it to your Telegram with Approve / Skip buttons
6. ✅ **Posts** to LinkedIn with the image when you tap Approve
7. 📊 **Tracks** everything so you never post the same story twice

**You literally just tap a button on your phone. That's it.**

## 🔁 How It Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Hacker News │────▶│   Extract    │────▶│  AI Writer  │
│  Top Posts  │     │ Content+Image│     │ (DeepSeek)  │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                    ┌──────────────┐     ┌───────▼──────┐
                    │   LinkedIn   │◀────│   Telegram   │
                    │  Auto-Post   │     │  ✅ Approve  │
                    └──────────────┘     │  ⏭️ Skip     │
                                         └──────────────┘
```

## 🧠 The Secret Sauce

The AI doesn't just summarize articles. It writes posts that are **engineered to go viral**:

- **Pattern-interrupt hooks** that stop the scroll
- **Knowledge gaps** that force people to keep reading
- **3-tier hashtag strategy** mixing high-reach + engagement + niche tags
- **Polarizing closers** that trigger comments (the algorithm loves comments)
- **No markdown, no links** — clean text that LinkedIn actually renders properly
- **OG image upload** — posts with images get 2x engagement

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [OpenRouter API key](https://openrouter.ai) (free tier works)
- [LinkedIn Developer App](https://developer.linkedin.com) with "Share on LinkedIn" product
- [Telegram Bot](https://t.me/BotFather) (takes 30 seconds to create)

### Install

```bash
git clone https://github.com/Lumacodes/HNLINK.git
cd HNLINK
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
```

Fill in your keys:

```env
OPENROUTER_API_KEY=sk-or-v1-...
LINKEDIN_ACCESS_TOKEN=AQUt...
LINKEDIN_PERSON_URN=urn:li:person:your_id
TELEGRAM_BOT_TOKEN=1234567890:ABC...
TELEGRAM_CHAT_ID=your_chat_id
```

### Run

```bash
python src/telegram_bot.py
```

Then open Telegram and send `/fetch 1` to your bot.

## 📱 Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Show all commands |
| `/fetch` | Generate 3 viral posts from trending HN stories |
| `/fetch 5` | Generate 5 posts |
| `/status` | Check bot health + API connections |
| `/history` | See how many posts you've published |

## ☁️ Deploy for Free

HNLINK runs on **Hugging Face Spaces** for free. No credit card.

1. Fork this repo
2. Create a [new HF Space](https://huggingface.co/new-space) (SDK: Docker)
3. Add your env vars as Secrets in Space settings
4. Push and it auto-deploys

Your bot runs 24/7. No laptop needed.

## 🏗️ Project Structure

```
HNLINK/
├── src/
│   ├── telegram_bot.py      # Telegram bot + approval flow
│   ├── hn_fetcher.py         # Hacker News API scraper
│   ├── content_extractor.py  # Article content + OG image extraction
│   ├── post_generator.py     # AI viral post generation
│   ├── linkedin_poster.py    # LinkedIn UGC API (text + image posts)
│   └── history_tracker.py    # SQLite dedup tracker
├── config/
│   └── settings.py           # Environment config
├── scripts/
│   └── run_pipeline.py       # CLI pipeline (no Telegram)
├── Dockerfile                # Deploy anywhere
└── requirements.txt
```

## 🤝 Contributing

Found a bug? Want to add a feature? PRs are welcome.

Some ideas:
- Reddit support (r/programming, r/technology)
- Twitter/X cross-posting
- Scheduled auto-fetch (cron)
- Post analytics dashboard
- Multi-language support

## 📄 License

MIT — use it however you want.

---

<div align="center">

**Built by [Luma](https://github.com/Lumacodes)** ⚡

*If this helped you grow on LinkedIn, star the repo ⭐*

</div>
