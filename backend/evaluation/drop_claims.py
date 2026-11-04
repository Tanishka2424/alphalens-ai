"""
Review helper for claims_heldout.json. Use it BEFORE run_heldout.py, never after.

  python evaluation/drop_claims.py list              show each article with its claims
  python evaluation/drop_claims.py drop 35 41        remove those ids AND their partner claim
  python evaluation/drop_claims.py drop 36 --only    remove exactly id 36 (keep its partner)

A backup (claims_heldout.backup.json) is made before the first edit.
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = os.environ.get("HELDOUT_TAG", "")
PATH = os.path.join(HERE, f"claims_heldout{TAG}.json")
BACKUP = os.path.join(HERE, f"claims_heldout{TAG}.backup.json")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load() -> list:
    return json.load(open(PATH, encoding="utf-8"))


def cmd_list() -> None:
    claims = load()
    by = {}
    for c in claims:
        if c.get("target_id"):
            by.setdefault(c["target_id"], []).append(c)
    for cs in by.values():
        print("=" * 72)
        print("ARTICLE:", cs[0]["source_title"])
        for c in cs:
            print(f"  #{c['id']} [{c['category']}] {c['claim']}")
    off = sum(1 for c in claims if c["category"] == "off_topic")
    print(f"\n{len(by)} articles, {off} off-topic claims (not listed), {len(claims)} claims in total")


def cmd_drop(args: list) -> None:
    only = "--only" in args
    ids = {int(a) for a in args if a.isdigit()}
    claims = load()
    missing = ids - {c["id"] for c in claims}
    if missing:
        print("Unknown ids (nothing changed):", sorted(missing))
        return
    if not os.path.exists(BACKUP):
        shutil.copy(PATH, BACKUP)
    targets = {c["target_id"] for c in claims if c["id"] in ids and c.get("target_id")}
    keep, gone = [], []
    for c in claims:
        remove = c["id"] in ids or (not only and c.get("target_id") in targets)
        (gone if remove else keep).append(c)
    json.dump(keep, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    sha = hashlib.sha256(open(PATH, "rb").read()).hexdigest()[:12]
    print("Removed ids:", [c["id"] for c in gone])
    print(f"{len(keep)} claims left, file hash {sha}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "list":
        cmd_list()
    elif len(sys.argv) >= 3 and sys.argv[1] == "drop":
        cmd_drop(sys.argv[2:])
    else:
        print(__doc__)