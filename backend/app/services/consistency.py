"""
Code-level checks that compare a claim with the cited articles. No LLM is involved.
They only look at the headline and short snippet we hold, never at the full article,
so every message says "headline or snippet", not "the article".
"""
import re

_NUM = re.compile(r"(\d[\d,]*(?:\.\d+)?)(\s?%)?")
_WORD = re.compile(r"[a-z]+")

# (side A, side B). A difference is reported only when the claim uses one side
# and the cited text uses only the opposite side.
_PAIRS = [
    (
        {"rise", "rises", "rose", "rising", "jump", "jumps", "jumped", "surge", "surges", "surged",
         "rally", "rallies", "rallied", "gain", "gains", "gained", "climb", "climbs", "climbed",
         "soar", "soars", "soared", "advance", "advances", "advanced", "higher"},
        {"fall", "falls", "fell", "falling", "drop", "drops", "dropped", "plunge", "plunges", "plunged",
         "slump", "slumps", "slumped", "crash", "crashes", "crashed", "decline", "declines", "declined",
         "slip", "slips", "slipped", "tumble", "tumbles", "tumbled", "sink", "sinks", "sank", "lower"},
    ),
    ({"likely", "probably", "expected"}, {"unlikely", "improbable"}),
    ({"raise", "raises", "raised", "hike", "hikes", "hiked"}, {"cut", "cuts", "slash", "slashes", "slashed"}),
]


def _clean(token: str) -> str:
    return token.replace(",", "").rstrip(".")


def all_numbers(text: str) -> set:
    """Every number in the text as a plain value (commas removed, % dropped)."""
    return {_clean(m.group(1)) for m in _NUM.finditer(text or "")}


def key_numbers(text: str) -> dict:
    """Numbers worth checking: two or more digits, or any number followed by %.
    Returns {plain value: how it was written}."""
    out = {}
    for m in _NUM.finditer(text or ""):
        value = _clean(m.group(1))
        if len(value.replace(".", "")) >= 2 or m.group(2):
            out.setdefault(value, m.group(0).strip())
    return out


def numbers_grounded(statement: str, claim: str, evidence_texts: list) -> bool:
    """True if every key number in the statement appears in the claim or the cited text."""
    allowed = all_numbers(claim)
    for t in evidence_texts:
        allowed |= all_numbers(t)
    return set(key_numbers(statement)) <= allowed


def number_differences(claim: str, evidence_texts: list) -> list:
    have = set()
    for t in evidence_texts:
        have |= all_numbers(t)
    return [
        f"Your claim mentions {shown}, which does not appear in the cited headline or snippet."
        for value, shown in key_numbers(claim).items()
        if value not in have
    ]


def direction_differences(claim: str, evidence_texts: list) -> list:
    c = set(_WORD.findall((claim or "").lower()))
    e = set()
    for t in evidence_texts:
        e |= set(_WORD.findall((t or "").lower()))
    notes = []
    for a, b in _PAIRS:
        ca, cb, ea, eb = c & a, c & b, e & a, e & b
        if ca and not cb and eb and not ea:
            notes.append(f"Your claim says '{sorted(ca)[0]}', but the cited text says '{sorted(eb)[0]}'.")
        elif cb and not ca and ea and not eb:
            notes.append(f"Your claim says '{sorted(cb)[0]}', but the cited text says '{sorted(ea)[0]}'.")
    return notes


def find_differences(claim: str, evidence_texts: list) -> list:
    return direction_differences(claim, evidence_texts) + number_differences(claim, evidence_texts)