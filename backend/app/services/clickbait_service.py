"""
Rule-based clickbait detector. Deliberately NOT ML - this is one of the
heuristic signals combined with the classifier, and its whole value is
being simple and explainable: every flag it raises can be pointed to
directly in the text, unlike the classifier's black-box confidence score.
"""
import re

from app.schemas.clickbait import ClickbaitResponse

CLICKBAIT_PHRASES = [
    "you won't believe",
    "you wont believe",
    "won't believe what",
    "this one trick",
    "one weird trick",
    "doctors hate",
    "what happened next",
    "you'll never guess",
    "youll never guess",
    "number will shock you",
    "will shock you",
    "goes viral",
    "breaks the internet",
    "left speechless",
    "changed everything",
    "secret they don't want you to know",
    "secret they dont want you to know",
    "shocking truth",
    "the truth about",
    "gone wrong",
    "top 10",
    "this is why",
]

CAPS_WORD_PATTERN = re.compile(r"\b[A-Z]{4,}\b")
REPEATED_PUNCTUATION_PATTERN = re.compile(r"[!?]{2,}")


def detect_clickbait(text: str) -> ClickbaitResponse:
    text_lower = text.lower()
    matched_phrases = [p for p in CLICKBAIT_PHRASES if p in text_lower]

    words = text.split()
    caps_words = CAPS_WORD_PATTERN.findall(text)
    excessive_caps = len(words) > 0 and (len(caps_words) / len(words)) > 0.15

    excessive_punctuation = bool(REPEATED_PUNCTUATION_PATTERN.search(text))

    score = 0.0
    score += min(len(matched_phrases) * 0.4, 0.6)
    score += 0.25 if excessive_caps else 0.0
    score += 0.15 if excessive_punctuation else 0.0
    score = min(score, 1.0)

    return ClickbaitResponse(
        score=round(score, 4),
        matched_phrases=matched_phrases,
        excessive_caps=excessive_caps,
        excessive_punctuation=excessive_punctuation,
    )