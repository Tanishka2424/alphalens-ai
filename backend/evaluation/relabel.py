"""
Clears the hand labels for the given claim ids, so `explain_eval.py label` asks about them again.
Use it only to fix a label that clearly broke the rule ("does the cited text say this?"),
and write down every change in the README.

  python evaluation/relabel.py 16 30           (run from backend/)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
path = os.environ.get("EXPLAIN_RESULTS") or os.path.join(HERE, "explain_results_heldout.json")
ids = {int(a) for a in sys.argv[1:] if a.isdigit()}
if not ids:
    print(__doc__)
    sys.exit()
results = json.load(open(path, encoding="utf-8"))
changed = []
for x in results:
    if x["id"] in ids:
        x.pop("labeled", None)
        x.pop("overclaim", None)
        for s in x["statements"]:
            s.pop("supported", None)
        changed.append(x["id"])
json.dump(results, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("Cleared labels for ids:", changed, "in", os.path.basename(path))