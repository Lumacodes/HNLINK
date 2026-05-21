# HN-to-LinkedIn Bot

Automated bot that fetches trending Hacker News stories, generates viral LinkedIn posts using AI, and sends them to you on Telegram for approval before posting.

## Features
- Fetches top + rising posts from Hacker News
- Extracts article content and OG images
- Generates viral LinkedIn posts via DeepSeek AI
- Sends posts to Telegram with Approve/Skip buttons
- Uploads images to LinkedIn with posts
- Tracks posted stories to avoid duplicates

## Setup
1. Copy `.env.example` to `.env` and fill in your keys
2. `pip install -r requirements.txt`
3. `python src/telegram_bot.py`

## Telegram Commands
- `/start` — Show help
- `/fetch` — Generate 3 viral posts
- `/fetch 1` — Generate 1 post
- `/status` — Check bot health
- `/history` — Show post count

## Environment Variables
See `.env.example` for all required variables.
