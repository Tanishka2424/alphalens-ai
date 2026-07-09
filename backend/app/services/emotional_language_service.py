"""
Rule-based emotional/loaded language scorer.

Deliberately excludes normal financial vocabulary ("crash", "plunge",
"crisis", "recession", "selloff", etc.) even though it sounds dramatic -
those are legitimate, descriptive terms in financial reporting, not
manipulation. This lexicon targets words whose main function is to
provoke reaction rather than describe an event.
"""
import re

from app.schemas.emotional_language import EmotionalLanguageResponse

EMOTIONAL_WORDS = [
    "bombshell",
    "meltdown",
    "explosive",
    "terrifying",
    "devastating",
    "outrageous",
    "chaos",
    "hysteria",
    "furious",
    "obliterate",
    "obliterates",
    "destroys",
    "annihilate",
    "annihilates",
    "catastrophic",
    "unbelievable",
    "insane",
    "mind-blowing",
    "mindblowing",
    "jaw-dropping",
    "slams",
    "blasts",
    "shocking",
    "stunning",
    "nightmare",
    "horrifying",
    "brutal",
    "savage",
    "epic fail",
]

WORD_PATTERN = re.compile(r"\b\w+\b")


def score_emotional_language(text: str) -> EmotionalLanguageResponse:
    text_lower = text.lower()
    all_words = WORD_PATTERN.findall(text_lower)

    unique_lexicon = list(dict.fromkeys(EMOTIONAL_WORDS))
    matched_words = [w for w in unique_lexicon if w in text_lower]

    word_count = max(len(all_words), 1)
    density = len(matched_words) / word_count

    score = min(density * 5, 1.0)

    return EmotionalLanguageResponse(
        score=round(score, 4),
        matched_words=matched_words,
        density=round(density, 4),
    )