import os
import re
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "articles.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    article_id    TEXT PRIMARY KEY,
    canonical_url TEXT UNIQUE,
    title         TEXT NOT NULL,
    snippet       TEXT,
    publisher     TEXT,
    published_at  TEXT,
    retrieved_at  TEXT NOT NULL,
    origin        TEXT NOT NULL,
    title_norm    TEXT NOT NULL,
    indexed       INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_title_norm ON articles(title_norm);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def normalize_title(s: str) -> str:
    return re.sub(r"\W+", " ", s.lower()).strip()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()