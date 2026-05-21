FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# HF Spaces expects port 7860 — run a tiny health server alongside the bot
# This keeps the Space from sleeping
EXPOSE 7860

CMD ["python", "src/telegram_bot.py"]
