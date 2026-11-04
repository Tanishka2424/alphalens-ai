"""
Why did altered claims rarely find their source article (Recall@5 was 23%)?
Hypothesis: the near-duplicate filter in retrieval_service removes the article because
a one-word change leaves the claim almost identical to its source.

  python evaluation/diagnose_altered.py        (run from backend/; reads claims, no LLM calls)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.services.retrieval_service import NEAR_DUPLICATE_THRESHOLD, retrieval_service  # noqa: E402

claims = json.load(open(os.path.join(HERE, "claims_heldout.json"), encoding="utf-8"))
altered = [c for c in claims if c["category"] == "tricky"]
retrieval_service._ensure_loaded()

print(f"Near-duplicate threshold: {NEAR_DUPLICATE_THRESHOLD}\n")
print(f"{'id':>4}  {'raw rank':>8}  {'similarity':>10}  note")
removed = top1 = missing = 0
for c in altered:
    emb = retrieval_service._embedder.encode([c["claim"]]).tolist()
    res = retrieval_service._collection.query(query_embeddings=emb, n_results=10)
    ids, dist = res["ids"][0], res["distances"][0]
    if c["target_id"] in ids:
        i = ids.index(c["target_id"])
        sim = 1 - dist[i]
        note = ""
        if sim >= NEAR_DUPLICATE_THRESHOLD:
            note = "REMOVED by the near-duplicate filter"
            removed += 1
        if i == 0:
            top1 += 1
        print(f"{c['id']:>4}  {i + 1:>8}  {sim:>10.3f}  {note}")
    else:
        missing += 1
        print(f"{c['id']:>4}  {'>10':>8}  {'-':>10}  not in the raw top 10")

print(f"\nAltered claims: {len(altered)}")
print(f"Source article is the #1 raw match:            {top1}")
print(f"Source article removed by the filter:          {removed}")
print(f"Source article not in the raw top 10 at all:   {missing}")