#!/usr/bin/env python3
"""
Standalone pipeline script.

Usage:
    python -m scripts.run_pipeline [--count 3] [--dry-run]

    --count N    Number of posts to generate (default: 3)
    --dry-run    Print posts without posting to LinkedIn
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from config.settings import settings
from src.hn_fetcher import HNFetcher
from src.content_extractor import ContentExtractor
from src.post_generator import PostGenerator
from src.linkedin_poster import LinkedInPoster
from src.history_tracker import HistoryTracker


def main():
    parser = argparse.ArgumentParser(description="HN-to-LinkedIn Pipeline")
    parser.add_argument("--count", type=int, default=3, help="Number of posts to generate")
    parser.add_argument("--dry-run", action="store_true", help="Don't post to LinkedIn")
    args = parser.parse_args()

    print("=" * 60)
    print("HN-to-LinkedIn Bot")
    print("=" * 60)

    tracker = HistoryTracker()

    # Step 1: Fetch stories
    print("\n[1/4] Fetching stories from Hacker News...")
    fetcher = HNFetcher(
        top_count=settings.hn_top_stories_count,
        random_rising_count=settings.hn_random_rising_count,
        min_score=settings.hn_min_score,
    )
    stories = fetcher.get_mixed_stories()

    posted_ids = tracker.get_all_posted_ids()
    stories = [s for s in stories if s["id"] not in posted_ids]
    print(f"  Found {len(stories)} new stories (excluding {len(posted_ids)} already posted)")

    if not stories:
        print("  No new stories. Exiting.")
        return

    # Step 2: Extract content
    print("\n[2/4] Extracting article content...")
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
            print(f"  [OK] {story['title'][:60]}...")
        else:
            print(f"  [SKIP] Could not extract: {story['title'][:60]}...")

    print(f"  Extracted content from {len(stories_with_content)} stories")

    # Step 3: Generate LinkedIn posts
    print("\n[3/4] Generating LinkedIn posts with AI...")
    generator = PostGenerator()
    generated_posts = []
    for story in stories_with_content:
        if len(generated_posts) >= args.count:
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
                "linkedin_text": post_text,
            })
            print(f"  [OK] {story['title'][:50]}...")
        else:
            print(f"  [FAIL] {story['title'][:50]}...")

    print(f"  Generated {len(generated_posts)} posts")

    # Step 4: Post to LinkedIn (or dry-run)
    print(f"\n[4/4] {'[DRY RUN] Previewing' if args.dry_run else 'Posting to LinkedIn'}...")

    for i, post in enumerate(generated_posts):
        print(f"\n{'='*50}")
        print(f"Post #{i+1}: {post['hn_title']}")
        print(f"HN: {post['hn_score']} points, {post['hn_comments']} comments")
        print(f"{'='*50}")
        print(post["linkedin_text"])
        print()

        if not args.dry_run:
            poster = LinkedInPoster()
            post_urn = poster.create_article_post(
                text=post["linkedin_text"],
                article_url=post["hn_url"],
                article_title=post["hn_title"],
            )
            if post_urn:
                tracker.mark_posted(post["hn_id"], post["hn_title"], post["hn_url"], post_urn)
                print(f"  -> Posted! URN: {post_urn}")
            else:
                print("  -> FAILED to post")

    # Save pending posts for n8n approval flow
    if args.dry_run:
        with open("pending_posts.json", "w") as f:
            json.dump(generated_posts, f, indent=2)
        print(f"\nSaved {len(generated_posts)} posts to pending_posts.json")

    print("\nDone!")


if __name__ == "__main__":
    main()
