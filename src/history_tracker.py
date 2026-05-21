"""
SQLite-based tracker to avoid posting duplicate HN stories across runs.
"""

import os
import sqlite3
from datetime import datetime

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "post_history.db")


class HistoryTracker:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = os.path.abspath(db_path)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posted_stories (
                    hn_id INTEGER PRIMARY KEY,
                    title TEXT,
                    url TEXT,
                    linkedin_post_urn TEXT,
                    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def is_posted(self, hn_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM posted_stories WHERE hn_id = ?", (hn_id,)
            ).fetchone()
            return row is not None

    def mark_posted(self, hn_id: int, title: str, url: str, linkedin_post_urn: str = ""):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO posted_stories (hn_id, title, url, linkedin_post_urn, posted_at) VALUES (?, ?, ?, ?, ?)",
                (hn_id, title, url, linkedin_post_urn, datetime.utcnow().isoformat()),
            )

    def get_all_posted_ids(self) -> set[int]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT hn_id FROM posted_stories").fetchall()
            return {row[0] for row in rows}
