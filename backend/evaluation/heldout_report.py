"""
Breaks the hand-labeled held-out results down by claim type and lists the failures.

  python evaluation/heldout_report.py              (run from backend/)
  python evaluation/heldout_report.py 16 30        also show the cited text for claims 16 and 30
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
path = os.environ.get("EXPLAIN_RESULTS") or os.path.join(HERE, "explain_results_heldout.json")
results = json.load(open(path, encoding="utf-8"))
labeled = [x for x in results if x.get("labeled")]
ids = {int(a) for a in sys.argv[1:] if a.isdigit()}

if ids:
    for x in results:
        if x["id"] in ids:
            print("=" * 72)
            print(f"#{x['id']} claim: {x['claim']}")
            print("source article:", x.get("source_title"))
            for s in x["statements"]:
                print("  STATEMENT:", s["text"], s["evidence_ids"], "label:", s.get("supported"))
            for e in x["evidence"].values():
                print("  CITED:", e["article_id"], "|", e["title"], "|", e["published_at"])
                print("        ", e["snippet"])
    sys.exit()

print(f"Labeled answers: {len(labeled)}\n")
print(f"{'type':<10}{'answers':>8}   statements y / p / n   overclaims")
for cat in ("covered", "tricky", "off_topic"):
    xs = [x for x in labeled if x["category"] == cat]
    if not xs:
        continue
    st = Counter(s.get("supported") for x in xs for s in x["statements"])
    over = sum(1 for x in xs if x.get("overclaim") == "y")
    print(f"{cat:<10}{len(xs):>8}   {st['y']:>9} / {st['p']} / {st['n']}      {over:>6}")

print("\nOVERCLAIMS and NOT-SUPPORTED statements:")
for x in labeled:
    bad = [s for s in x["statements"] if s.get("supported") == "n"]
    if x.get("overclaim") == "y" or bad:
        print("=" * 72)
        print(f"#{x['id']} [{x['category']}] claim: {x['claim']}")
        if x.get("source_title"):
            print("   source article:", x["source_title"])
        for s in x["statements"]:
            print(f"   [{s.get('supported')}] {s['text']}")
        print("   overclaim:", x.get("overclaim"))