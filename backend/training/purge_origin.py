import sys
import os

from chromadb import PersistentClient

from article_db import connect

HERE = os.path.dirname(os.path.abspath(__file__))


def main(origin: str) -> None:
    conn = connect()
    ids = [r[0] for r in conn.execute("SELECT article_id FROM articles WHERE origin = ?", (origin,))]
    if not ids:
        print(f"No rows with origin '{origin}'.")
        return
    collection = PersistentClient(path=os.path.join(HERE, "vector_store")).get_collection("financial_articles")
    for start in range(0, len(ids), 200):
        collection.delete(ids=ids[start:start + 200])
    conn.execute("DELETE FROM articles WHERE origin = ?", (origin,))
    conn.commit()
    print(f"Removed {len(ids)} '{origin}' articles. Collection size now: {collection.count()}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"newsapi", "rss"}:
        print("Usage: python training\\purge_origin.py newsapi")
    else:
        main(sys.argv[1])