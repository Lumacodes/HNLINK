"""
Telegram bot for HN-to-LinkedIn approval workflow.

Flow:
  1. /fetch — Fetches HN stories, extracts content + OG images
  2. Generates viral LinkedIn posts via AI
  3. Sends them to you with Approve/Skip buttons + image preview
  4. On approve → uploads image + posts to LinkedIn
  5. Sends confirmation
"""

import asyncio
import json
import os
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from config.settings import settings
from src.hn_fetcher import HNFetcher
from src.content_extractor import ContentExtractor
from src.post_generator import PostGenerator
from src.linkedin_poster import LinkedInPoster
from src.history_tracker import HistoryTracker


# Store pending posts in memory
pending_posts: dict[str, dict] = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "🤖 HN-to-LinkedIn Bot\n\n"
        "Commands:\n"
        "  /fetch — Fetch HN stories & generate 3 viral posts\n"
        "  /fetch N — Generate N posts\n"
        "  /status — Check bot status\n"
        "  /history — Show posted stories count\n",
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    await update.message.reply_text(
        "✅ Bot is running\n"
        f"📝 Pending posts: {len(pending_posts)}\n"
        f"🔑 LinkedIn token: {'✅ Set' if settings.linkedin_access_token else '❌ Missing'}\n"
        f"👤 Person URN: {'✅ Set' if settings.linkedin_person_urn else '❌ Missing'}",
    )


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command."""
    tracker = HistoryTracker()
    posted_ids = tracker.get_all_posted_ids()
    await update.message.reply_text(f"📊 Total stories posted to LinkedIn: {len(posted_ids)}")


async def fetch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fetch — run the full pipeline and send posts for approval."""
    count = 3
    if context.args:
        try:
            count = int(context.args[0])
            count = max(1, min(count, 10))
        except ValueError:
            pass

    await update.message.reply_text(f"🔄 Fetching top stories from Hacker News...\nWill generate {count} viral posts.")

    tracker = HistoryTracker()

    # Step 1: Fetch stories
    try:
        fetcher = HNFetcher(
            top_count=settings.hn_top_stories_count,
            random_rising_count=settings.hn_random_rising_count,
            min_score=settings.hn_min_score,
        )
        stories = fetcher.get_mixed_stories()
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to fetch HN stories: {e}")
        return

    # Filter already posted
    posted_ids = tracker.get_all_posted_ids()
    stories = [s for s in stories if s["id"] not in posted_ids]

    if not stories:
        await update.message.reply_text("🤷 No new stories found. Try again later!")
        return

    await update.message.reply_text(f"📰 Found {len(stories)} new stories. Extracting content & images...")

    # Step 2: Extract content + OG images
    extractor = ContentExtractor(max_chars=settings.content_max_chars)
    stories_with_content = []
    for story in stories:
        url = story.get("url", "")
        if not url:
            continue
        result = extractor.extract_with_image(url)
        if result:
            story["content"] = result["text"]
            story["image_url"] = result.get("image_url")
            stories_with_content.append(story)

    if not stories_with_content:
        await update.message.reply_text("❌ Could not extract content from any stories.")
        return

    # Count stories with images
    with_images = sum(1 for s in stories_with_content if s.get("image_url"))
    await update.message.reply_text(
        f"📄 Extracted {len(stories_with_content)} stories ({with_images} with images)\n"
        f"🤖 Generating {count} viral LinkedIn posts..."
    )

    # Step 3: Generate LinkedIn posts
    generator = PostGenerator()
    generated = 0

    for story in stories_with_content:
        if generated >= count:
            break

        post_text = generator.generate(
            article_text=story["content"],
            hn_title=story["title"],
            hn_url=story["url"],
            hn_score=story.get("score", 0),
            hn_comments=story.get("descendants", 0),
        )

        if not post_text:
            continue

        generated += 1
        post_id = f"post_{story['id']}"

        # Download the image if available
        image_data = None
        if story.get("image_url"):
            image_data = extractor.download_image(story["image_url"])

        # Store pending post
        pending_posts[post_id] = {
            "hn_id": story["id"],
            "hn_title": story["title"],
            "hn_url": story["url"],
            "hn_score": story.get("score", 0),
            "hn_comments": story.get("descendants", 0),
            "linkedin_text": post_text,
            "image_url": story.get("image_url"),
            "image_data": image_data,
        }

        # Build approval keyboard
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Post to LinkedIn", callback_data=f"approve:{post_id}"),
                InlineKeyboardButton("⏭️ Skip", callback_data=f"skip:{post_id}"),
            ]
        ])

        # Header
        header = (
            f"📝 Post {generated}/{count}\n\n"
            f"🔗 {story['title']}\n"
            f"⬆️ {story.get('score', 0)} pts · 💬 {story.get('descendants', 0)} comments\n"
            f"{'🖼️ Image: YES' if image_data else '📝 Image: NO (text-only post)'}\n\n"
            f"━━━ LINKEDIN POST ━━━\n\n"
            f"{post_text}\n\n"
            f"━━━ END ━━━"
        )

        # Send image preview in Telegram if we have one
        if image_data and story.get("image_url"):
            try:
                from io import BytesIO
                photo = BytesIO(image_data)
                photo.name = "preview.jpg"
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"🖼️ Image that will be posted with this:"
                )
            except Exception:
                pass

        # Send the post text with buttons
        if len(header) > 4096:
            chunks = [header[i:i+4096] for i in range(0, len(header), 4096)]
            for i, chunk in enumerate(chunks):
                if i == len(chunks) - 1:
                    await update.message.reply_text(chunk, reply_markup=keyboard)
                else:
                    await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(header, reply_markup=keyboard)

    if generated == 0:
        await update.message.reply_text("❌ AI failed to generate any posts. Try again in a minute (rate limit).")
    else:
        await update.message.reply_text(f"✅ {generated} posts ready for your approval ☝️")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses (approve/skip)."""
    query = update.callback_query
    await query.answer()

    action, post_id = query.data.split(":", 1)

    if post_id not in pending_posts:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("⚠️ This post has already been processed.")
        return

    post = pending_posts.pop(post_id)

    if action == "skip":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(f"⏭️ Skipped: {post['hn_title'][:50]}...")
        return

    if action == "approve":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("📤 Posting to LinkedIn...")

        poster = LinkedInPoster()
        post_urn = None

        # Post with image if available, otherwise text-only
        if post.get("image_data"):
            post_urn = poster.create_image_post(
                text=post["linkedin_text"],
                image_data=post["image_data"],
            )
        else:
            post_urn = poster.create_text_post(
                text=post["linkedin_text"],
            )

        if post_urn:
            tracker = HistoryTracker()
            tracker.mark_posted(
                post["hn_id"], post["hn_title"], post["hn_url"], post_urn
            )
            await query.message.reply_text(
                f"✅ Posted to LinkedIn!\n"
                f"📄 {post['hn_title'][:60]}\n"
                f"🔗 {post_urn}",
            )
        else:
            pending_posts[post_id] = post
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 Retry", callback_data=f"approve:{post_id}"),
                    InlineKeyboardButton("⏭️ Skip", callback_data=f"skip:{post_id}"),
                ]
            ])
            await query.message.reply_text(
                "❌ Failed to post. Check your LinkedIn access token.\nYou can retry or skip:",
                reply_markup=keyboard,
            )


def main():
    """Start the Telegram bot."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env")
        print("   1. Message @BotFather on Telegram")
        print("   2. Send /newbot and follow the steps")
        print("   3. Add the token to your .env file")
        sys.exit(1)

    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    print("🤖 Starting HN-to-LinkedIn Telegram Bot...")
    print(f"   Bot token: ...{bot_token[-8:]}")
    if chat_id:
        print(f"   Chat ID: {chat_id}")
    print("   Send /start to the bot on Telegram to begin\n")

    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("fetch", fetch_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
