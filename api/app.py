"""
Flask API server that bridges n8n and the Python pipeline.

Endpoints:
  GET  /health                      - Health check
  POST /pipeline/fetch-and-generate - Run full pipeline, return generated posts
  POST /pipeline/post-to-linkedin   - Post approved content to LinkedIn
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from flask import Flask, request, jsonify

from config.settings import settings
from src.hn_fetcher import HNFetcher
from src.content_extractor import ContentExtractor
from src.post_generator import PostGenerator
from src.linkedin_poster import LinkedInPoster
from src.history_tracker import HistoryTracker

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/pipeline/fetch-and-generate")
def fetch_and_generate():
    """Run the full pipeline: fetch HN -> extract -> generate posts."""
    data = request.get_json(silent=True) or {}
    count = data.get("count", settings.posts_to_generate)

    tracker = HistoryTracker()

    # Step 1: Fetch stories
    fetcher = HNFetcher(
        top_count=settings.hn_top_stories_count,
        random_rising_count=settings.hn_random_rising_count,
        min_score=settings.hn_min_score,
    )
    stories = fetcher.get_mixed_stories()

    # Filter out already-posted
    posted_ids = tracker.get_all_posted_ids()
    stories = [s for s in stories if s["id"] not in posted_ids]

    if not stories:
        return jsonify({"posts": [], "message": "No new stories found"})

    # Step 2: Extract content
    extractor = ContentExtractor(max_chars=settings.content_max_chars)
    stories_with_content = []
    for story in stories:
        url = story.get("url", "")
        if not url:
            continue
        content = extractor.extract(url)
        if content:
            story["content"] = content
            stories_with_content.append(story)

    # Step 3: Generate LinkedIn posts
    generator = PostGenerator()
    generated_posts = []
    for story in stories_with_content:
        if len(generated_posts) >= count:
            break
        post_text = generator.generate(
            article_text=story["content"],
            hn_title=story["title"],
            hn_url=story["url"],
            hn_score=story.get("score", 0),
            hn_comments=story.get("descendants", 0),
        )
        if post_text:
            generated_posts.append({
                "hn_id": story["id"],
                "hn_title": story["title"],
                "hn_url": story["url"],
                "hn_score": story.get("score", 0),
                "hn_comments": story.get("descendants", 0),
                "article_summary": story["content"][:300],
                "linkedin_text": post_text,
            })

    return jsonify({
        "posts": generated_posts,
        "count": len(generated_posts),
    })


@app.post("/pipeline/post-to-linkedin")
def post_to_linkedin():
    """Post approved content to LinkedIn."""
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    text = data["text"]
    article_url = data.get("article_url", "")
    article_title = data.get("article_title", "")
    hn_id = data.get("hn_id", 0)
    hn_title = data.get("hn_title", "")

    poster = LinkedInPoster()

    if article_url:
        post_urn = poster.create_article_post(text, article_url, article_title)
    else:
        post_urn = poster.create_text_post(text)

    if post_urn:
        tracker = HistoryTracker()
        tracker.mark_posted(hn_id, hn_title, article_url, post_urn)
        return jsonify({"status": "posted", "post_urn": post_urn})

    return jsonify({"error": "Failed to post to LinkedIn"}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
