"""
Builds the held-out claim set. Run once, review the file by hand, then freeze it.

  python evaluation/build_heldout.py [N]      (run from backend/, default N=30)

For N recent dated articles, the LLM writes two claims per headline:
  covered = a paraphrase (the source article is the known right answer)
  tricky  = the same event with ONE fact changed (should not be confirmed)
Plus 20 fixed off-topic claims (nothing in the index should match them).
Note: the claims are written by an LLM from the same family as the explainer,
so paraphrases may be easier than real user claims. State this in the README.
"""
import json
import os
import random
import re
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from openai import OpenAI  # noqa: E402

from app.core.config import settings  # noqa: E402

DB = os.path.join(os.path.dirname(HERE), "training", "articles.db")
TAG = os.environ.get("HELDOUT_TAG", "")          # e.g. _v2 for a second, fresh set
OUT = os.path.join(HERE, f"claims_heldout{TAG}.json")
SEED = int(os.environ.get("HELDOUT_SEED", "7"))
FINANCE = re.compile(
    r"\b(sensex|nifty|stocks?|shares?|market|markets|rbi|sebi|rupee|ipo|banks?|funds?|invest\w*|econom\w*|profit|"
    r"earnings?|tax|gdp|inflation|bonds?|crore|lakh|revenue|dividend|loans?|fii|dii|nse|bse|q[1-4]|fy\d+)\b|%",
    re.IGNORECASE,
)

SYSTEM = (
    "You write test claims from one news headline. Reply with ONLY JSON: "
    '{"paraphrase": "...", "altered": "..."}. '
    '"paraphrase" says the same thing in different words and keeps every number. '
    '"altered" is about the same event but exactly ONE concrete fact is wrong '
    "(change a number, or reverse a direction such as rise/fall). "
    "Both must read like real headlines. No explanations."
)

OFF_TOPIC = [
    "Bitcoin will reach one million dollars by next year",
    "Manchester United will sign a new striker this winter",
    "Apple will launch a foldable iPhone next month",
    "The monsoon will be above normal next year",
    "A new Marvel film breaks the opening weekend box office record",
    "A volcano erupts in Iceland and cancels flights",
    "Argentina wins the football World Cup again",
    "NASA announces a crewed mission to Mars by 2035",
    "Netflix renews its most popular series for another season",
    "London records its hottest day this decade",
    "A chess grandmaster wins the world championship",
    "The Nobel Prize in literature goes to a first-time author",
    "Tesla unveils a cheaper electric car model",
    "The European Union passes a new cookie consent law",
    "A major earthquake hits Japan",
    "Samsung releases a smartphone with a satellite camera",
    "OpenAI announces a new image generation model",
    "India wins the cricket series against Australia",
    "A new study links coffee to longer life",
    "The Olympic Games add a new sport",
]


def norm(s: str) -> str:
    return re.sub(r"\W+", " ", s.lower()).strip()


def parse(raw: str) -> dict:
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON")
    return json.loads(raw[start:end + 1])


def main(n: int) -> None:
    if os.path.exists(OUT):
        print(f"{os.path.basename(OUT)} already exists. Delete it only if you really want a new set.")
        return
    if not (settings.OPENAI_API_KEY and settings.OPENAI_MODEL_NAME):
        print("LLM is not configured in backend/.env")
        return

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT article_id, title FROM articles WHERE origin IN ('newsapi','rss') "
        "AND published_at IS NOT NULL AND title != '[Removed]' AND length(title) > 30"
    ).fetchall()
    # only financial headlines, and never an article used in an earlier claim set
    used = set()
    for name in ("claims_heldout.json", "claims_heldout.backup.json"):
        earlier = os.path.join(HERE, name)
        if TAG and os.path.exists(earlier):
            used |= {c["target_id"] for c in json.load(open(earlier, encoding="utf-8")) if c.get("target_id")}
    rows = [r for r in rows if FINANCE.search(r["title"]) and r["article_id"] not in used]
    picked = random.Random(SEED).sample(rows, min(n, len(rows)))
    print(f"{len(rows)} eligible recent articles, using {len(picked)}")

    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL or None, timeout=60)
    claims = []

    def add(category, expected, claim, target_id, source_title):
        claims.append({"id": len(claims) + 1, "category": category, "expected": expected,
                       "claim": claim, "target_id": target_id, "source_title": source_title})

    for row in picked:
        try:
            resp = client.chat.completions.create(
                model=settings.OPENAI_MODEL_NAME,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": row["title"]}],
                temperature=0, max_tokens=2000,
            )
            data = parse(resp.choices[0].message.content or "")
            para, alt = str(data["paraphrase"]).strip(), str(data["altered"]).strip()
        except Exception as e:
            print("skip", row["article_id"], str(e)[:80])
            continue
        if len(para) < 10 or len(alt) < 10 or norm(para) == norm(row["title"]) or norm(alt) == norm(para):
            print("skip (unusable)", row["article_id"])
            continue
        add("covered", "grounded", para, row["article_id"], row["title"])
        add("tricky", "either", alt, row["article_id"], row["title"])
        time.sleep(2)

    for t in OFF_TOPIC:
        add("off_topic", "insufficient_evidence", t, None, None)

    json.dump(claims, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    c = [x["category"] for x in claims]
    print(f"Saved {len(claims)} claims: covered={c.count('covered')} tricky={c.count('tricky')} off_topic={c.count('off_topic')}")
    print("NEXT: open claims_heldout.json and read it. Delete any 'tricky' claim that is not actually wrong,")
    print("and any nonsense claim. Do NOT run the system on them or change them after that.")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 30)