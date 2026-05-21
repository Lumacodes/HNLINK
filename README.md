<!-- Updated README with aesthetic enhancements and SEO‑friendly tags -->
<div align="center">

# 🔥 HNLINK

### Turn Hacker News into LinkedIn Virality — On Autopilot

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-API-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://developer.linkedin.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![HF Spaces](https://img.shields.io/badge/🤗-Deploy%20Free-yellow?style=for-the-badge)](https://huggingface.co/spaces)

**Stop writing LinkedIn posts manually. Let AI do the work, you just hit approve.**

[Getting Started](#-getting-started) · [How It Works](#-how-it-works) · [Deploy Free](#-deploy-for-free) · [Commands](#-telegram-commands)

</div>

<!--
  SEO Keywords: LinkedIn automation, Hacker News scraper, AI viral content, Telegram bot, Python AI, OpenRouter, content generation, social media growth
  Tags: AI, Automation, LinkedIn, HackerNews, TelegramBot, ViralContent, OpenRouter, Python
-->

---

## 💡 The Problem

You know that feeling. You see a killer article on Hacker News. You think "this would make a great LinkedIn post." Then you spend 20 minutes writing it, second‑guessing every word, and by the time you post it… nobody cares because the timing is off.

I built HNLINK because I was tired of that loop.

## ⚡ What It Does

HNLINK is a fully automated pipeline that:

1️⃣ **Scrapes** trending stories from Hacker News (top + rising)
2️⃣ **Reads** the full article content (not just titles)
3️⃣ **Grabs** the featured image
4️⃣ **Generates** scroll‑stopping LinkedIn posts with AI
5️⃣ **Delivers** them to Telegram with Approve / Skip buttons
6️⃣ **Publishes** to LinkedIn with the image on approval
7️⃣ **Tracks** everything so you never repost the same story

**You literally just tap a button on your phone. That's it.**

## 🔁 How It Works

```mermaid
flowchart LR
  HN[Hacker News] --> Extract[Extract Content + Image]
  Extract --> AI[AI Writer (DeepSeek / OpenRouter)]
  AI --> TG[Telegram Bot]
  TG -->|Approve| LI[LinkedIn Auto‑Post]
  TG -->|Skip| End[End]
```

## 🧠 The Secret Sauce

The AI doesn’t just summarise – it crafts **viral‑ready** posts:

- 🎣 **Pattern‑interrupt hooks** that stop the scroll
- 🧩 **Knowledge‑gap gaps** that force readers to keep reading
- 📈 **3‑tier hashtag strategy** (broad + engagement + niche)
- ⚡ **Polarising closers** that spark comments (the algorithm loves comments)
- ✅ **No markdown, no links** – pure LinkedIn‑ready text
- 🖼️ **OG image upload** – posts with images get ~2× engagement

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- OpenRouter API key (free tier works) – [Get yours](https://openrouter.ai)
- LinkedIn Developer App with *Share on LinkedIn* product
- Telegram Bot (create via @BotFather)

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
OPENROUTER_API_KEY=sk-or-…
LINKEDIN_ACCESS_TOKEN=YOUR_TOKEN
LINKEDIN_PERSON_URN=urn:li:person:your_id
TELEGRAM_BOT_TOKEN=1234567890:ABC…
TELEGRAM_CHAT_ID=your_chat_id
```

### Run

```bash
python src/telegram_bot.py
```

Open Telegram and send `/fetch 1` to the bot.

## 📱 Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Show all commands |
| `/fetch` | Generate 3 viral posts from trending HN stories |
| `/fetch 5` | Generate 5 posts |
| `/status` | Check bot health + API connections |
| `/history` | See how many posts you’ve published |

## ☁️ Deploy for Free

HNLINK runs on **Hugging Face Spaces** for free – no credit card needed.

1️⃣ Fork this repo
2️⃣ Create a new HF Space (Docker SDK)
3️⃣ Add your env vars as Secrets in Space settings
4️⃣ Push – it auto‑deploys

Your bot runs 24/7. No laptop required.

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

Found a bug? Want a feature? PRs are welcome.

**Ideas:**
- Reddit support (r/programming, r/technology)
- Twitter/X cross‑posting
- Scheduled auto‑fetch (cron)
- Post analytics dashboard
- Multi‑language support

## 📄 License

MIT — use it however you want.

---

<div align="center">

**Built by [Luma](https://github.com/Lumacodes) ⚡**

*If this helped you grow on LinkedIn, star the repo ⭐*

</div>
