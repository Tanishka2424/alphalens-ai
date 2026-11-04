"""
Measures where the time goes, per stage, in-process (no HTTP).

  python evaluation/latency.py                 (run from backend/, with Uvicorn STOPPED)

'explain' includes its own retrieval plus the LLM call. The page waits for the slowest
of the four parallel requests, so 'page wait' is the max per claim. Check real browser
timings too (DevTools > Network) because parallel requests compete for the CPU.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FALLBACK = [
    "Sensex jumps 500 points after the Fed holds rates",
    "RBI is believed to have stepped in to support the rupee",
    "Jupiter Wagons shares rally 20% on a Railway Board order",
    "SEBI cautions investors about WhatsApp stock tips",
    "Bitcoin will reach one million dollars by next year",
    "Birlasoft stock surges 11% after Q2 results",
]


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))]


def main() -> None:
    from app.services.credibility_aggregator_service import analyze_credibility
    from app.services.explanation_service import explain_claim
    from app.services.retrieval_service import retrieval_service
    from app.services.sentiment_service import sentiment_service

    stages = {
        "sentiment (FinBERT)": lambda t: sentiment_service.predict(t),
        "writing signals": lambda t: analyze_credibility(t, None, None),
        "retrieval": lambda t: retrieval_service.find_similar(t, 5),
        "explain (retrieval + LLM)": lambda t: explain_claim(t, 5),
    }
    path = os.path.join(HERE, "claims_heldout.json")
    claims = FALLBACK
    if os.path.exists(path):
        claims = [c["claim"] for c in json.load(open(path, encoding="utf-8")) if c["category"] == "covered"][:12] or FALLBACK

    print("Cold start (first call, includes model loading):")
    for name, fn in stages.items():
        t0 = time.perf_counter()
        try:
            fn(claims[0])
            print(f"  {name:<28}{(time.perf_counter() - t0) * 1000:>9.0f} ms")
        except Exception as e:
            print(f"  {name:<28}failed: {str(e)[:60]}")

    times = {n: [] for n in stages}
    waits = []
    for c in claims:
        row = []
        for name, fn in stages.items():
            t0 = time.perf_counter()
            try:
                fn(c)
                ms = (time.perf_counter() - t0) * 1000
            except Exception:
                continue
            times[name].append(ms)
            row.append(ms)
        if row:
            waits.append(max(row))
        time.sleep(2)

    print(f"\nWarm latency over {len(claims)} claims (ms):")
    print(f"  {'stage':<28}{'p50':>8}{'p95':>8}{'max':>8}")
    for name, xs in times.items():
        if xs:
            print(f"  {name:<28}{pct(xs, 50):>8.0f}{pct(xs, 95):>8.0f}{max(xs):>8.0f}")
    if waits:
        print(f"  {'page wait (slowest stage)':<28}{pct(waits, 50):>8.0f}{pct(waits, 95):>8.0f}{max(waits):>8.0f}")


if __name__ == "__main__":
    main()