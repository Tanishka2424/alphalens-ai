# AlphaLens AI

AI-powered financial news intelligence platform. Helps users evaluate
sentiment, credibility indicators, and source consensus across financial
news articles — a heuristic assistance tool, **not** a fact-verification
or fake-news-certainty system.

## Structure
```
alphalens-ai/
├── backend/    # FastAPI service — sentiment, credibility, retrieval, consensus
└── frontend/   # React UI (added Phase 5)
```

## Status: Phase 1 complete
- Modular FastAPI backend
- FinBERT sentiment analysis endpoint (`POST /api/v1/sentiment/analyze`)
- Centralized config, structured logging, centralized error handling
- Swagger docs, health check, Dockerized

## Run locally
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Visit `http://127.0.0.1:8000/docs`.
