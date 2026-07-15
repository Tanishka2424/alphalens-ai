# AlphaLens AI

I built this as a portfolio project while prepping for campus placements. It's an AI-powered financial news intelligence platform, you give it a headline or article, and it looks at it from four different angles at once: what's the market tone, how trustworthy does it look, what else has been reported on the same topic, and do those other sources actually agree with it.

None of this is a "this is 100% fake" verdict. Think of it more like a second opinion you'd want before sharing or acting on a financial headline every score here is a heuristic signal, not a fact check.

## What it actually does

- **Sentiment** — FinBERT reads the market tone (Bullish / Bearish / Neutral)
- **Credibility** — a DistilBERT classifier I fine-tuned myself, combined with clickbait detection, emotional-language scoring, and a source reputation lookup, into one risk score and action bucket
- **Related coverage** — semantic search (meaning based, not keyword match) across 10,686 real financial headlines
- **Consensus** — an LLM reads the claim against related coverage and judges whether they agree, partially agree, or conflict; automatically falls back to a rule based method if the LLM is unavailable, no manual switching needed

## Screenshots

<img width="1920" height="1080" alt="Screenshot 2026-07-13 105923" src="https://github.com/user-attachments/assets/3b81e8f3-fadb-4562-9fa2-d98f0b7837f5" />
<img width="1920" height="1080" alt="Screenshot 2026-07-13 110132" src="https://github.com/user-attachments/assets/ebea284e-abc2-4d50-a0eb-9deccfb837b0" />
<img width="1920" height="1080" alt="Screenshot 2026-07-13 110044" src="https://github.com/user-attachments/assets/7f17c5f8-926e-4c19-9d48-ef3377892538" />
<img width="1920" height="1080" alt="Screenshot 2026-07-13 110051" src="https://github.com/user-attachments/assets/26d7e19d-9048-47de-a89c-db78576b8f24" />
<img width="1920" height="1080" alt="Screenshot 2026-07-13 110235" src="https://github.com/user-attachments/assets/9485dea6-4d88-427d-b2a8-a176deb9a34a" />
<img width="1920" height="1080" alt="Screenshot 2026-07-13 110240" src="https://github.com/user-attachments/assets/479de9a5-d362-429c-8b84-fc769adfc18d" />


## Why it's built this way

- **Four separate signals, not one model doing everything** — sentiment, credibility, retrieval, and consensus each answer a genuinely different question. A fabricated article can still score "Bullish"; a well-corroborated one can still use dramatic language. No single score can carry all of that.
- **The credibility classifier's limitation is documented, not hidden** — it's trained on general/political news (no open financial fake-news dataset exists), and I found a real example where it confidently misclassifies a neutral financial headline. That's exactly why it's one signal among several, not the only one.
- **The LLM integration is provider-agnostic** — built against the OpenAI SDK interface, but the actual base URL and model are just config values. I ended up verifying it live with Groq (free, no card) rather than OpenAI, and switching back is a two line `.env` change, not a code change.
- **Everything's been tested with real data, not just "it compiles"** — dataset label directions were manually verified, not assumed; a data leakage bug was found and fixed mid project (test accuracy went *up* after the fix, which is itself evidence the fix was correct, not just cautious); a concurrency bug was reproduced and fixed with a proper lock, verified under simulated concurrent load.

## Running it locally

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Visit `http://localhost:8000/docs` for the interactive API docs.

**Frontend** (in a second terminal):
```bash
cd frontend
npm install
npm run dev
```

Note: the credibility classifier checkpoint and the retrieval vector store are both gitignored (large binary files) — see `PROJECT_DOCUMENTATION.md` for how to regenerate them (fine-tuning notebook + corpus ingestion script, both included in `backend/training/`).

## Honest limitations

- Credibility classifier's financial-domain accuracy is unverified beyond a small hand checked sample this is a real, currently-unsolved gap in available datasets, not something unique to this project
- The retrieval corpus skews toward Indian financial markets, not global coverage
- Credibility scoring weights are a designed heuristic, not statistically fit to data
- No authentication or multi user support  intentionally out of scope for this project's goals

