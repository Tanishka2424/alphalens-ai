import os

import requests

from article_db import connect, normalize_title, now_iso
from fetch_rss import canonical_url, clean_snippet, index_pending
import hashlib
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))
API_URL = "https://newsapi.org/v2/everything"
QUERY = '(Sensex OR Nifty OR "Reserve Bank of India" OR SEBI OR "Indian economy" OR "Indian rupee")'

def main() -> None:
    key = os.environ.get("NEWSAPI_KEY")
    if not key:
        print("Set the NEWSAPI_KEY environment variable first.")
        return

    resp = requests.get(
        API_URL,
        params={"q": QUERY, "language": "en", "sortBy": "publishedAt", "pageSize": 50},
        headers={"X-Api-Key": key},
        timeout=30,
    )
    data = resp.json()
    if data.get("status") != "ok":
        print("NewsAPI error:", data.get("message"))
        return

    conn = connect()
    added = dupes = skipped = 0
    for a in data.get("articles", []):
        link = a.get("url")
        title = clean_snippet(a.get("title")) or ""
        publisher = (a.get("source") or {}).get("name")
        if not link or not title or title == "[Removed]" or not publisher:
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
                "news-" + hashlib.sha1(cu.encode()).hexdigest()[:16],
                cu, title, clean_snippet(a.get("description")), publisher,
                a.get("publishedAt"), now_iso(), "newsapi", tn,
            ),
        )
        added += 1
    conn.commit()
    print(f"NewsAPI: added={added} duplicates={dupes} skipped={skipped}")
    index_pending(conn)


if __name__ == "__main__":
    main()