"""
Runs the frozen held-out claims and prints automatic metrics.

  python evaluation/run_heldout.py            (run from backend/)

- Saves after every claim, so Ctrl+C is safe: run it again and it resumes.
- Waits and retries when the LLM provider rate-limits (HTTP 429).
- Refuses to overwrite finished results (use --force). Do not tune anything between runs.
Automatic metrics need no hand labels:
  known-item retrieval (the claim was written from article X: is X in the top 5?),
  target cited, off-topic refusal rate, a rough mismatch-flagging proxy, latency.
Hand labeling of statements comes next (explain_eval.py label).
"""
import hashlib
import json
import os
import random
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TAG = os.environ.get("HELDOUT_TAG", "")
CLAIMS = os.path.join(HERE, f"claims_heldout{TAG}.json")
OUT = os.path.join(HERE, f"explain_results_heldout{TAG}.json")
PARTIAL = os.path.join(HERE, f"explain_results_heldout{TAG}.partial.json")
LABEL_SAMPLE = 30
PACE_SECONDS = 8      # gap between claims, to stay under free-tier limits
RATE_WAIT = 45        # wait after a 429 before retrying
NUM = re.compile(r"\d[\d,]*\.?\d*")


def nums(s: str) -> set:
    return {x.rstrip(".,") for x in NUM.findall(s) if len(x.rstrip(".,")) >= 2}


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))] if xs else float("nan")


def process(c: dict, sha: str, explain_claim, retrieval_service) -> dict:
    item = {**c, "status": "error", "statements": [], "evidence": {}, "dropped": 0, "error": None,
            "rank": None, "cited_target": False, "t_retrieval_ms": None, "t_explain_ms": None,
            "claims_sha256": sha}
    for attempt in range(4):
        try:
            t0 = time.perf_counter()
            ret = retrieval_service.find_similar(c["claim"], 5)
            item["t_retrieval_ms"] = round((time.perf_counter() - t0) * 1000, 1)
            if c.get("target_id"):
                item["rank"] = next((i + 1 for i, r in enumerate(ret.results) if r.article_id == c["target_id"]), None)
            t0 = time.perf_counter()
            r = explain_claim(c["claim"], 5)
            item["t_explain_ms"] = round((time.perf_counter() - t0) * 1000, 1)
            item.update(status=r.status, statements=[s.model_dump() for s in r.statements],
                        evidence={e.article_id: e.model_dump() for e in r.evidence},
                        dropped=r.dropped_statements, error=None)
            item["cited_target"] = bool(c.get("target_id")) and c["target_id"] in item["evidence"]
            return item
        except Exception as e:
            item["error"] = str(e)[:200]
            if "429" in str(e) or "rate" in str(e).lower():
                print(f"      rate limited, waiting {RATE_WAIT}s (attempt {attempt + 1}/4)")
                time.sleep(RATE_WAIT)
                continue
            return item
    return item


def summarize(results: list, sha: str) -> None:
    cov = [r for r in results if r["category"] == "covered"]
    alt = [r for r in results if r["category"] == "tricky"]
    off = [r for r in results if r["category"] == "off_topic"]
    errs = sum(1 for r in results if r["status"] == "error")

    def recall(rs):
        return sum(1 for r in rs if r["rank"]) / len(rs) if rs else float("nan")

    def mrr(rs):
        return sum(1 / r["rank"] for r in rs if r["rank"]) / len(rs) if rs else float("nan")

    proxy = []
    for r in alt:
        orig = nums(r["source_title"] or "") - nums(r["claim"])
        if orig and r["status"] == "grounded":
            text = " ".join(s["text"] for s in r["statements"])
            proxy.append(any(n in text for n in orig))

    lat = [r["t_explain_ms"] for r in results if r["t_explain_ms"]]
    print(f"\n===== HELD-OUT SUMMARY (claims file {sha}) =====")
    print(f"Claims: covered={len(cov)} altered={len(alt)} off-topic={len(off)}  errors={errs}")
    print(f"Known-item retrieval, covered:  Recall@5 {recall(cov):.0%}  MRR {mrr(cov):.2f}")
    print(f"Known-item retrieval, altered:  Recall@5 {recall(alt):.0%}  MRR {mrr(alt):.2f}")
    print(f"Covered answered 'grounded':    {sum(r['status'] == 'grounded' for r in cov)}/{len(cov)}")
    print(f"Target article cited (covered): {sum(r['cited_target'] for r in cov)}/{len(cov)}")
    print(f"Off-topic refused:              {sum(r['status'] == 'insufficient_evidence' for r in off)}/{len(off)}")
    print(f"Altered answered 'grounded':    {sum(r['status'] == 'grounded' for r in alt)}/{len(alt)}")
    if proxy:
        print(f"Altered, answer mentions the real number (rough proxy): {sum(proxy)}/{len(proxy)}")
    print(f"Statements dropped by citation check: {sum(r['dropped'] for r in results)}")
    print(f"Explain latency ms: p50 {pct(lat, 50):.0f}  p95 {pct(lat, 95):.0f}")
    print(f"\nHand-label sample: {sum(1 for r in results if r['status'] == 'grounded' and not r['skip_label'])} claims")


def main() -> None:
    if os.path.exists(OUT) and "--force" not in sys.argv:
        print("Finished results already exist. The held-out set is meant to be run once. Use --force to override.")
        return
    from app.services.explanation_service import explain_claim
    from app.services.retrieval_service import retrieval_service

    raw = open(CLAIMS, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()[:12]
    claims = json.loads(raw.decode("utf-8"))
    done = {}
    if os.path.exists(PARTIAL):
        prev = json.load(open(PARTIAL, encoding="utf-8"))
        if prev and prev[0].get("claims_sha256") == sha:
            done = {r["id"]: r for r in prev}
            print(f"Resuming: {len(done)} claims already done")
        else:
            print("A partial run exists for a DIFFERENT claims file. Delete the .partial.json file to start over.")
            return
    print(f"{len(claims)} claims, file hash {sha}")

    results = []
    for c in claims:
        if c["id"] in done:
            results.append(done[c["id"]])
            continue
        item = process(c, sha, explain_claim, retrieval_service)
        results.append(item)
        json.dump(results, open(PARTIAL, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"{c['id']:>3}. [{c['category']}] {item['status']} rank={item['rank']} ({item['t_explain_ms']} ms)")
        time.sleep(PACE_SECONDS)

    eligible = [r for r in results if r["status"] == "grounded" and r["category"] in ("covered", "tricky")]
    keep = {r["id"] for r in random.Random(1).sample(eligible, min(LABEL_SAMPLE, len(eligible)))}
    for r in results:
        r["skip_label"] = r["status"] == "grounded" and r["category"] != "off_topic" and r["id"] not in keep
    json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if os.path.exists(PARTIAL):
        os.remove(PARTIAL)
    summarize(results, sha)


if __name__ == "__main__":
    main()