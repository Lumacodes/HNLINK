# HNLINK

I got tired of manually scrolling Hacker News, finding interesting stuff, and then writing LinkedIn posts about it. So I built this.

It grabs trending stories from HN, reads the articles, writes LinkedIn posts, and sends them to my Telegram so I can approve before they go live. The whole thing runs on autopilot — I just tap "Approve" or "Skip" from my phone.

## How it works

```
Hacker News → Extract Article → AI writes post → Telegram notification → You approve → LinkedIn
```

- Pulls top + rising stories from the HN API
- Scrapes the actual article (not just the title)
- Grabs the OG image from the article
- Generates a LinkedIn post using DeepSeek via OpenRouter (free)
- Sends it to Telegram with inline buttons
- On approve: uploads the image and posts to LinkedIn
- Keeps track of what's been posted so you don't get duplicates

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/HNLINK.git
cd HNLINK
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill in your keys in .env
python src/telegram_bot.py
```

## You'll need

- **OpenRouter API key** (free) — for AI post generation
- **LinkedIn Developer App** — for posting (Share on LinkedIn + Sign In products)
- **Telegram Bot** — message @BotFather, takes 30 seconds

## Telegram commands

| Command | What it does |
|---|---|
| `/fetch` | Grab stories and generate 3 posts |
| `/fetch 1` | Just generate 1 (faster for testing) |
| `/status` | Check if everything's connected |
| `/history` | How many posts you've made |

## Hosting

Runs anywhere that supports Docker. I use Koyeb (free tier). Just connect your repo and set the env vars.

## Why not use n8n / WhatsApp?

I originally built this with n8n + WhatsApp but it was overkill. Telegram bot is simpler, faster to set up, and doesn't need Meta Business verification. The n8n workflow is still in the repo if you want it though (`n8n/workflows/`).

## License

MIT — do whatever you want with it.
