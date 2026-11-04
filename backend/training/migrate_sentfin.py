import os

import pandas as pd

from article_db import connect, normalize_title, now_iso

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "SEntFiN-v1.1.csv")
ORIGIN = "SEntFiN dataset (India-market financial news)"


def main() -> None:
    df = pd.read_csv(CSV_PATH).dropna(subset=["Title"]).drop_duplicates(subset=["Title"])
    conn = connect()
    ts = now_iso()
    rows = [
        (str(sno), None, title, title, None, None, ts, "sentfin", normalize_title(title), 1)
        for sno, title in zip(df["S No."].tolist(), df["Title"].tolist())
    ]
    before = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    conn.executemany(
        "INSERT OR IGNORE INTO articles (article_id, canonical_url, title, snippet, publisher, "
        "published_at, retrieved_at, origin, title_norm, indexed) VALUES (?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()
    after = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    print(f"Rows before: {before} | added: {after - before} | total now: {after}")
    print(f"Origin label stored: {ORIGIN}")


if __name__ == "__main__":
    main()