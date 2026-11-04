import truststore

truststore.inject_into_ssl()
import calendar
import hashlib
import html
import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import feedparser

from article_db import connect, normalize_title, now_iso

HERE = os.path.dirname(os.path.abspath(__file__))
FEEDS_FILE = os.path.join(HERE, "rss_feeds.json")
VECTOR_STORE_PATH = os.path.join(HERE, "vector_store")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def canonical_url(url: str) -> str:
    p = urlparse(url.strip())
    query = [
        (k, v) for k, v in parse_qsl(p.query)
        if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}
    ]
    path = p.path.rstrip("/") or "/"
    return urlunparse((p.scheme.lower() or "https", p.netloc.lower(), path, "", urlencode(query), ""))


def clean_snippet(raw: str | None) -> str | None:
    if not raw:
        return None
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:300] or None


def published_iso(entry) -> str | None:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if t:
        return datetime.fromtimestamp(calendar.timegm(t), tz=timezone.utc).isoformat()
    raw = (entry.get("published") or "").strip()
    for fmt in ("%d %b, %Y %z", "%d %b %Y %z"):
        try:
            return datetime.strptime(raw, fmt).isoformat()
        except ValueError:
            continue
    return None  # never guess a date

def fetch_new(conn) -> None:
    with open(FEEDS_FILE, encoding="utf-8") as f:
        feeds = json.load(f)

    for feed in feeds:
        if "example.com" in feed["url"]:
            print(f"Skipping placeholder feed: {feed['url']}")
            continue
        parsed = feedparser.parse(feed["url"])
        if not parsed.entries:
            print(f"[{feed['publisher']}] no entries (check the URL / network).")
            continue

        added = dupes = skipped = 0
        for e in parsed.entries:
            link = e.get("link")
            title = clean_snippet(e.get("title")) or ""
            allow = feed.get("only_link_contains")
            if allow and link and not any(s in link for s in allow):
                skipped += 1
                continue
            if not link or not title:
                skipped += 1
                continue
            cu = canonical_url(link)
            tn = normalize_title(title)
            if conn.execute(
                "SELECT 1 FROM articles WHERE canonical_url = ? OR title_norm = ?", (cu, tn)
            ).fetchone():
                dupes += 1
                continue
            conn.execute(
                "INSERT INTO articles (article_id, canonical_url, title, snippet, publisher, "
                "published_at, retrieved_at, origin, title_norm, indexed) VALUES (?,?,?,?,?,?,?,?,?,0)",
                (
                    "rss-" + hashlib.sha1(cu.encode()).hexdigest()[:16],
                    cu, title, clean_snippet(e.get("summary")), feed["publisher"],
                    published_iso(e), now_iso(), "rss", tn,
                ),
            )
            added += 1
        conn.commit()
        print(f"[{feed['publisher']}] added={added} duplicates={dupes} skipped={skipped}")


def index_pending(conn) -> None:
    rows = conn.execute("SELECT * FROM articles WHERE indexed = 0").fetchall()
    if not rows:
        print("Nothing new to index.")
        return

    from chromadb import PersistentClient
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    collection = PersistentClient(path=VECTOR_STORE_PATH).get_collection("financial_articles")

    for start in range(0, len(rows), 200):
        batch = rows[start:start + 200]
        metadatas = []
        for r in batch:
            meta = {
                "title": r["title"],
                "source": r["publisher"] or r["origin"],
                "origin": r["origin"],
                "url": r["canonical_url"],
                "published_at": r["published_at"],
            }
            metadatas.append({k: v for k, v in meta.items() if v})  # Chroma rejects None
        collection.upsert(
            ids=[r["article_id"] for r in batch],
            documents=[r["snippet"] or r["title"] for r in batch],
            embeddings=embedder.encode([r["title"] for r in batch]).tolist(),
            metadatas=metadatas,
        )
        conn.executemany(
            "UPDATE articles SET indexed = 1 WHERE article_id = ?", [(r["article_id"],) for r in batch]
        )
        conn.commit()
    print(f"Indexed {len(rows)} articles. Collection size: {collection.count()}")


def main() -> None:
    conn = connect()
    fetch_new(conn)
    index_pending(conn)


if __name__ == "__main__":
    main()