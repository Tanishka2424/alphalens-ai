"""
Small hand-written check of the grounded explainer (20 claims). NOT a benchmark:
the claims were written by the project author and the sample is tiny. It reports
counts, not a general accuracy.

  python evaluation\\explain_eval.py run     # run all claims, save results locally
  python evaluation\\explain_eval.py label   # judge each statement, then print the summary
Run from the backend/ folder.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RESULTS = os.environ.get("EXPLAIN_RESULTS") or os.path.join(HERE, "explain_results.json")
# (category, expected, claim)
CLAIMS = [
    ("covered", "grounded", "Sensex jumps over 500 points and Nifty crosses 22,850 after the Fed holds rates"),
    ("covered", "grounded", "RBI is believed to have stepped in to limit pressure on the rupee"),
    ("covered", "grounded", "Jupiter Wagons shares rise 8% after a Rs 1,140 crore Railway Board order"),
    ("covered", "grounded", "Birlasoft stock surges 11% after its Q2 results"),
    ("covered", "grounded", "BLS Polymers IPO was subscribed more than 42 times by day 3"),
    ("covered", "grounded", "Crompton Greaves shares are down about 38% from their May high"),
    ("covered", "grounded", "SEBI cautions investors about stock tips in invitation-only WhatsApp groups"),
    ("covered", "grounded", "SEBI signs an MoU with the Bank of England on clearing corporations"),
    ("covered", "grounded", "SEBI reviews the call-record requirement for research analysts"),
    ("off_topic", "insufficient_evidence", "Bitcoin will reach one million dollars by next year"),
    ("off_topic", "insufficient_evidence", "Tesla will launch a new car model next month"),
    ("off_topic", "insufficient_evidence", "Apple iPhone sales fell sharply last quarter"),
    ("off_topic", "insufficient_evidence", "The monsoon will be above normal next year"),
    ("off_topic", "insufficient_evidence", "Manchester United will sign a new striker this winter"),
    ("tricky", "either", "Sensex crashes 500 points after the Fed raises interest rates"),
    ("tricky", "either", "Jupiter Wagons shares rally 20% on a Railway Board order"),
    ("tricky", "either", "SEBI bans all retail investors from trading derivatives"),
    ("tricky", "either", "RBI cuts the repo rate by 100 basis points"),
    ("tricky", "either", "Reliance Industries will acquire Adani Ports next week"),
    ("tricky", "either", "Nifty will hit 50,000 by next year"),
]


def run() -> None:
    from app.services.explanation_service import explain_claim

    results = []
    for i, (cat, expected, claim) in enumerate(CLAIMS, 1):
        item = {"id": i, "category": cat, "expected": expected, "claim": claim,
                "status": "error", "statements": [], "evidence": {}, "dropped": 0, "error": None}
        try:
            r = explain_claim(claim, 5)
            item.update(
                status=r.status,
                statements=[s.model_dump() for s in r.statements],
                evidence={e.article_id: e.model_dump() for e in r.evidence},
                dropped=r.dropped_statements,
            )
        except Exception as e:  # keep going; errors are counted, not hidden
            item["error"] = str(e)[:200]
        results.append(item)
        print(f"{i:>2}. [{cat}] {item['status']}  (dropped={item['dropped']})  {claim[:60]}")
        time.sleep(2)  # stay under free-tier rate limits

    with open(RESULTS, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {RESULTS}")
    summary(results)


def label() -> None:
    results = json.load(open(RESULTS, encoding="utf-8"))

    def save() -> None:
        json.dump(results, open(RESULTS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    for item in results:
        if item["status"] != "grounded" or item.get("labeled") or item.get("skip_label"):
            continue
        print("\n" + "=" * 70)
        print(f"CLAIM #{item['id']} [{item['category']}]: {item['claim']}")
        for s in item["statements"]:
            print(f"\nSTATEMENT: {s['text']}")
            for eid in s["evidence_ids"]:
                e = item["evidence"].get(eid, {})
                print(f"  CITED [{eid}] {e.get('title')} | {e.get('source')} | {e.get('published_at')}")
                print(f"     {e.get('snippet')}")
            if "supported" in s:
                print(f"  (already judged: {s['supported']})")
                continue
            ans = ""
            while ans not in {"y", "n", "p", "q"}:
                ans = input("Does the cited article say this?  y=yes  n=no  p=partly  q=save & quit : ").strip().lower()
            if ans == "q":
                save()
                print("Saved. Run 'label' again to continue.")
                return
            s["supported"] = ans
        ans = ""
        while ans not in {"ok", "bad", "q"}:
            ans = input(
                "OVERALL  ok = answer is fine (matches the claim, or clearly says it differs)\n"
                "         bad = answer makes the claim look supported but the articles show a different number/direction/event\n"
                "         q = save & quit  : "
            ).strip().lower()
        if ans == "q":
            save()
            print("Saved. Run 'label' again to continue.")
            return
        item["overclaim"] = "y" if ans == "bad" else "n"
        item["labeled"] = True
        save()
    save()
    summary(results)

def summary(results: list) -> None:
    cov = [r for r in results if r["category"] == "covered"]
    off = [r for r in results if r["category"] == "off_topic"]
    errors = sum(1 for r in results if r["status"] == "error")
    print("\n===== SUMMARY (20 hand-written claims; not a benchmark) =====")
    print(f"Covered claims answered 'grounded':      {sum(r['status']=='grounded' for r in cov)}/{len(cov)}")
    print(f"Off-topic claims correctly refused:      {sum(r['status']=='insufficient_evidence' for r in off)}/{len(off)}")
    print(f"Tricky claims, status: "
          + ", ".join(f"{r['status']}" for r in results if r["category"] == "tricky"))
    print(f"Errors (LLM/service failed):             {errors}")
    print(f"Statements dropped by citation check:    {sum(r['dropped'] for r in results)}")
    stmts = [s for r in results for s in r["statements"] if "supported" in s]
    if stmts:
        n = len(stmts)
        y = sum(s["supported"] == "y" for s in stmts)
        p = sum(s["supported"] == "p" for s in stmts)
        bad = sum(s["supported"] == "n" for s in stmts)
        print(f"Statements judged: {n} -> supported {y}, partly {p}, NOT supported {bad}  (unsupported rate {bad/n:.0%})")
        done = [r for r in results if r.get("labeled")]
        print(f"Answers that overclaim confirmation:     {sum(r['overclaim']=='y' for r in done)}/{len(done)}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "run":
        run()
    elif mode == "label":
        label()
    else:
        print("Usage: python evaluation\\explain_eval.py run | label")