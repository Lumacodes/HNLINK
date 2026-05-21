"""
Fetches stories from the Hacker News Firebase API.

Selection strategy:
1. Fetch topstories.json (500 IDs)
2. Fetch individual item details concurrently
3. Filter by minimum score, exclude jobs/polls/text-only
4. Select top N by points
5. Also fetch newstories.json, pick random "rising" posts
6. Return merged, deduplicated list
"""

import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

HN_BASE_URL = "https://hacker-news.firebaseio.com/v0"


class HNFetcher:
    def __init__(
        self,
        top_count: int = 15,
        random_rising_count: int = 5,
        min_score: int = 50,
        max_workers: int = 10,
    ):
        self.top_count = top_count
        self.random_rising_count = random_rising_count
        self.min_score = min_score
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "HN-LinkedIn-Bot/1.0"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _fetch_item(self, item_id: int) -> Optional[dict]:
        """Fetch a single HN item by ID."""
        try:
            resp = self.session.get(f"{HN_BASE_URL}/item/{item_id}.json", timeout=10)
            resp.raise_for_status()
            item = resp.json()
            if (
                item
                and item.get("type") == "story"
                and item.get("score", 0) >= self.min_score
                and item.get("url")
            ):
                return item
        except requests.RequestException:
            return None

    def _fetch_items_batch(self, item_ids: list[int]) -> list[dict]:
        """Fetch multiple items concurrently."""
        items = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._fetch_item, iid): iid for iid in item_ids}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    items.append(result)
        return items

    def get_top_stories(self) -> list[dict]:
        """Fetch top stories sorted by score (descending), return top N."""
        resp = self.session.get(f"{HN_BASE_URL}/topstories.json", timeout=15)
        resp.raise_for_status()
        all_ids = resp.json()

        # Fetch first 100 to find top-scoring ones
        items = self._fetch_items_batch(all_ids[:100])
        items.sort(key=lambda x: x.get("score", 0), reverse=True)
        return items[: self.top_count]

    def get_random_rising(self, exclude_ids: set[int] | None = None) -> list[dict]:
        """Fetch newstories and pick random ones meeting score threshold."""
        resp = self.session.get(f"{HN_BASE_URL}/newstories.json", timeout=15)
        resp.raise_for_status()
        all_ids = resp.json()

        # Sample random IDs from newest 200, excluding already-seen
        pool = [iid for iid in all_ids[:200] if iid not in (exclude_ids or set())]
        sample_size = min(50, len(pool))
        if sample_size == 0:
            return []
        sample_ids = random.sample(pool, sample_size)
        items = self._fetch_items_batch(sample_ids)
        random.shuffle(items)
        return items[: self.random_rising_count]

    def get_mixed_stories(self) -> list[dict]:
        """
        Get a mix of top + random rising stories, deduplicated by ID.
        Returns top N from front page + random rising posts.
        """
        top = self.get_top_stories()
        top_ids = {s["id"] for s in top}

        rising = self.get_random_rising(exclude_ids=top_ids)

        # Combine: all top + rising additions
        combined = top + rising
        return combined
