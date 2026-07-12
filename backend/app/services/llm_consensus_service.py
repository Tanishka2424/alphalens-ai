"""
LLM-assisted consensus reasoning using GPT-4o-mini.

This is the PRIMARY path - richer reasoning than the rule-based fallback,
since it actually reads and compares the claim against related articles
in plain language instead of just comparing sentiment labels.

Any failure here (missing key, network error, rate limit, malformed
response) raises LLMUnavailableError. The caller (consensus.py's combined
/analyze endpoint) catches that and calls the rule-based fallback instead -
this is the required behavior from the spec: the fallback must trigger
automatically, not be a manual alternative the user has to choose.
"""
import json

from openai import OpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.consensus import ConsensusResponse, RelatedArticleSentiment
from app.services.retrieval_service import retrieval_service

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = 0.5


class LLMUnavailableError(Exception):
    """Raised for any failure in the LLM path - the caller should fall back."""


SYSTEM_PROMPT = """You are a financial news consensus-reasoning assistant. You will be given a claim and a list of related articles found via semantic search. Determine whether the related articles support, partially support, conflict with, or are unrelated to the claim, and whether the claim uses exaggerated language compared to the related coverage.

Respond ONLY with valid JSON, no markdown formatting, no other text, matching exactly this shape:
{"verdict": "Consensus" or "Partial Agreement" or "Conflict" or "Insufficient Coverage", "explanation": "one or two sentence plain-language explanation", "exaggeration_flag": true or false}"""


def _build_user_prompt(text, related_titles):
    if related_titles:
        articles_block = "\n".join(f"- {t}" for t in related_titles)
    else:
        articles_block = "(none found)"
    return f"Claim: {text}\n\nRelated articles found:\n{articles_block}"


def analyze_consensus_llm(text: str, top_k: int) -> ConsensusResponse:
    if not settings.OPENAI_API_KEY:
        raise LLMUnavailableError("No OPENAI_API_KEY configured.")

    retrieval_result = retrieval_service.find_similar(text, top_k)
    relevant_matches = []
    for r in retrieval_result.results:
        if r.similarity_score >= SIMILARITY_THRESHOLD:
            relevant_matches.append(r)

    related_titles = []
    for m in relevant_matches:
        related_titles.append(m.title)

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(text, related_titles)},
            ],
            temperature=0.2,
            max_tokens=300,
        )
        raw_content = response.choices[0].message.content
    except Exception as e:
        raise LLMUnavailableError(f"OpenAI API call failed: {e}") from e

    try:
        parsed = json.loads(raw_content)
        verdict = parsed["verdict"]
        explanation = parsed["explanation"]
        exaggeration_flag = bool(parsed["exaggeration_flag"])
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise LLMUnavailableError(f"Malformed LLM response: {e}") from e

    valid_verdicts = {"Consensus", "Partial Agreement", "Conflict", "Insufficient Coverage"}
    if verdict not in valid_verdicts:
        raise LLMUnavailableError(f"LLM returned unexpected verdict value: {verdict}")

    related_articles = []
    for m in relevant_matches:
        related_articles.append(
            RelatedArticleSentiment(title=m.title, sentiment="N/A (LLM path)", similarity_score=m.similarity_score)
        )

    return ConsensusResponse(
        verdict=verdict,
        explanation=explanation,
        user_claim_sentiment=None,
        related_articles=related_articles,
        exaggeration_flag=exaggeration_flag,
        method="llm_assisted",
    )