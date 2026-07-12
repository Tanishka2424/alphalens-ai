"""
Rule-based consensus fallback - works with NO API key, NO LLM. Per the
project spec, this must be fully functional on its own, not a stub waiting
for GPT-4o-mini. The future LLM-assisted path will call this same function
as its fallback if the OpenAI API fails or is unavailable.
"""
from app.schemas.consensus import ConsensusResponse, RelatedArticleSentiment
from app.services.emotional_language_service import score_emotional_language
from app.services.retrieval_service import retrieval_service
from app.services.sentiment_service import sentiment_service

SIMILARITY_THRESHOLD = 0.5
AGREEMENT_RATIO_FOR_CONSENSUS = 0.6
AGREEMENT_RATIO_FOR_CONFLICT = 0.4
EXAGGERATION_GAP_THRESHOLD = 0.3


def analyze_consensus_fallback(text: str, top_k: int) -> ConsensusResponse:
    retrieval_result = retrieval_service.find_similar(text, top_k)

    relevant_matches = [
        r for r in retrieval_result.results if r.similarity_score >= SIMILARITY_THRESHOLD
    ]

    if not relevant_matches:
        return ConsensusResponse(
            verdict="Insufficient Coverage",
            explanation=(
                "No sufficiently similar articles were found in the indexed corpus "
                "to compare this claim against. This does not mean the claim is false - "
                "it means there isn't enough related coverage in our corpus to assess it."
            ),
            user_claim_sentiment=None,
            related_articles=[],
            exaggeration_flag=False,
        )

    user_sentiment = sentiment_service.predict(text)
    user_label = user_sentiment.label.value

    related_articles = []
    matching_count = 0
    for match in relevant_matches:
        article_sentiment = sentiment_service.predict(match.title)
        related_articles.append(
            RelatedArticleSentiment(
                title=match.title,
                sentiment=article_sentiment.label.value,
                similarity_score=match.similarity_score,
            )
        )
        if article_sentiment.label.value == user_label:
            matching_count += 1

    agreement_ratio = matching_count / len(relevant_matches)

    if agreement_ratio >= AGREEMENT_RATIO_FOR_CONSENSUS:
        verdict = "Consensus"
        explanation = (
            f"{matching_count}/{len(relevant_matches)} related articles share the same "
            f"sentiment direction ({user_label}) as this claim."
        )
    elif agreement_ratio <= AGREEMENT_RATIO_FOR_CONFLICT:
        verdict = "Conflict"
        explanation = (
            f"Only {matching_count}/{len(relevant_matches)} related articles share the same "
            f"sentiment direction as this claim - most related coverage points a different way."
        )
    else:
        verdict = "Partial Agreement"
        explanation = (
            f"{matching_count}/{len(relevant_matches)} related articles agree with this claim's "
            f"sentiment direction - coverage is mixed."
        )

    user_emotional_score = score_emotional_language(text).score
    related_emotional_scores = [score_emotional_language(m.title).score for m in relevant_matches]
    avg_related_emotional = sum(related_emotional_scores) / len(related_emotional_scores)
    exaggeration_flag = (user_emotional_score - avg_related_emotional) > EXAGGERATION_GAP_THRESHOLD

    if exaggeration_flag:
        explanation += (
            " Additionally, this text uses notably more emotionally loaded language than "
            "the related coverage does."
        )

    return ConsensusResponse(
        verdict=verdict,
        explanation=explanation,
        user_claim_sentiment=user_label,
        related_articles=related_articles,
        exaggeration_flag=exaggeration_flag,
    )