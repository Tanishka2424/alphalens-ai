import json
from types import SimpleNamespace

import pytest

from app.core.config import settings
from app.schemas.retrieval import SimilarArticlesResponse
from app.services import explanation_service as svc


def reply(statements, uncertainty="Limited."):
    return json.dumps({"statements": statements, "uncertainty": uncertainty})


def install(monkeypatch, articles, llm_reply=None, llm_error=None):
    """Fake retrieval + fake LLM. Returns the list of LLM calls made."""
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "OPENAI_MODEL_NAME", "test-model")
    monkeypatch.setattr(settings, "OPENAI_BASE_URL", None)
    monkeypatch.setattr(
        svc.retrieval_service, "find_similar",
        lambda text, k: SimilarArticlesResponse(results=articles),
    )
    calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            if llm_error:
                raise llm_error
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=llm_reply))])

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(svc, "OpenAI", FakeOpenAI)
    return calls


CLAIM = "Sensex jumps 500 points after the Fed holds rates"


def test_valid_citation_is_grounded_and_returns_only_cited_evidence(monkeypatch, make_article):
    articles = [
        make_article("news-1", "Sensex jumps", "The Times of India"),
        make_article("old-1", "Old headline", "SEntFiN", published_at=None, sim=0.7),
    ]
    install(monkeypatch, articles, reply([
        {"text": "According to The Times of India, Sensex jumped.", "evidence_ids": ["news-1"]}
    ]))
    r = svc.explain_claim(CLAIM, 5)
    assert r.status == "grounded"
    assert len(r.statements) == 1
    assert [e.article_id for e in r.evidence] == ["news-1"]
    assert r.dropped_statements == 0


def test_invented_evidence_id_is_dropped(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1")], reply([
        {"text": "According to Pub, something.", "evidence_ids": ["news-999"]}
    ]))
    r = svc.explain_claim(CLAIM, 5)
    assert r.status == "insufficient_evidence"
    assert r.statements == []
    assert r.evidence == []
    assert r.dropped_statements == 1


def test_one_valid_and_one_invented_keeps_only_the_valid(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1")], reply([
        {"text": "Valid statement.", "evidence_ids": ["news-1"]},
        {"text": "Made-up source.", "evidence_ids": ["news-1", "fake-7"]},
    ]))
    r = svc.explain_claim(CLAIM, 5)
    assert r.status == "grounded"
    assert [s.text for s in r.statements] == ["Valid statement."]
    assert r.dropped_statements == 1


def test_citing_an_article_below_the_similarity_threshold_is_dropped(monkeypatch, make_article):
    articles = [make_article("keep-1", sim=0.8), make_article("drop-1", sim=0.3)]
    install(monkeypatch, articles, reply([
        {"text": "Cites an item that was never sent.", "evidence_ids": ["drop-1"]}
    ]))
    r = svc.explain_claim(CLAIM, 5)
    assert r.statements == []
    assert r.dropped_statements == 1


def test_only_relevant_evidence_is_sent_to_the_llm(monkeypatch, make_article):
    articles = [make_article("keep-1", sim=0.8), make_article("drop-1", sim=0.3)]
    calls = install(monkeypatch, articles, reply([{"text": "Ok.", "evidence_ids": ["keep-1"]}]))
    svc.explain_claim(CLAIM, 5)
    prompt = calls[0]["messages"][1]["content"]
    assert "[keep-1]" in prompt
    assert "drop-1" not in prompt


def test_statement_without_citations_is_dropped(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1")], reply([{"text": "No sources.", "evidence_ids": []}]))
    r = svc.explain_claim(CLAIM, 5)
    assert r.statements == []
    assert r.dropped_statements == 1


def test_statement_missing_text_field_is_dropped(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1")], reply([{"evidence_ids": ["news-1"]}]))
    r = svc.explain_claim(CLAIM, 5)
    assert r.statements == []
    assert r.dropped_statements == 1


def test_at_most_three_statements_are_kept(monkeypatch, make_article):
    five = [{"text": f"Statement {i}.", "evidence_ids": ["news-1"]} for i in range(5)]
    install(monkeypatch, [make_article("news-1")], reply(five))
    r = svc.explain_claim(CLAIM, 5)
    assert len(r.statements) == 3


def test_empty_statements_from_llm_means_insufficient_evidence(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1")], reply([], "Nothing addresses the claim."))
    r = svc.explain_claim(CLAIM, 5)
    assert r.status == "insufficient_evidence"
    assert r.evidence == []
    assert "Nothing addresses" in r.uncertainty


def test_json_inside_markdown_fences_is_accepted(monkeypatch, make_article):
    body = "```json\n" + reply([{"text": "Ok.", "evidence_ids": ["news-1"]}]) + "\n```"
    install(monkeypatch, [make_article("news-1")], body)
    assert svc.explain_claim(CLAIM, 5).status == "grounded"


def test_json_with_text_around_it_is_accepted(monkeypatch, make_article):
    body = "Here is the answer: " + reply([{"text": "Ok.", "evidence_ids": ["news-1"]}]) + " Done."
    install(monkeypatch, [make_article("news-1")], body)
    assert svc.explain_claim(CLAIM, 5).status == "grounded"


@pytest.mark.parametrize("bad_reply", [
    "this is not json",
    "",
    json.dumps({"statements": "oops", "uncertainty": "x"}),
    json.dumps({"statements": []}),
])
def test_unusable_llm_output_raises_unavailable(monkeypatch, make_article, bad_reply):
    install(monkeypatch, [make_article("news-1")], bad_reply)
    with pytest.raises(svc.ExplanationUnavailableError):
        svc.explain_claim(CLAIM, 5)


def test_llm_call_failure_raises_unavailable(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1")], llm_error=RuntimeError("timeout"))
    with pytest.raises(svc.ExplanationUnavailableError):
        svc.explain_claim(CLAIM, 5)


def test_missing_llm_configuration_raises_unavailable(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1")], "{}")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)
    with pytest.raises(svc.ExplanationUnavailableError):
        svc.explain_claim(CLAIM, 5)


def test_no_similar_articles_refuses_without_calling_the_llm(monkeypatch, make_article):
    calls = install(monkeypatch, [make_article("far-1", sim=0.3)], "{}")
    r = svc.explain_claim(CLAIM, 5)
    assert r.status == "insufficient_evidence"
    assert calls == []


def test_only_undated_articles_refuses_without_calling_the_llm(monkeypatch, make_article):
    calls = install(monkeypatch, [make_article("old-1", published_at=None, sim=0.8)], "{}")
    r = svc.explain_claim(CLAIM, 5)
    assert r.status == "insufficient_evidence"
    assert calls == []


def test_source_label_leak_is_removed_from_statements(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1")], reply([
        {"text": "According to Business Standard, shares fell. source=Business Standard", "evidence_ids": ["news-1"]}
    ]))
    r = svc.explain_claim(CLAIM, 5)
    assert "source=" not in r.statements[0].text


def test_evidence_block_labels_source_and_missing_date(make_article):
    block = svc._evidence_block([make_article("old-1", source="Pub", published_at=None)])
    assert "source=Pub" in block
    assert "date=date unknown" in block


# ---- code-level checks added after the held-out evaluation ----

def test_statement_with_an_invented_number_is_dropped(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1", "Sensex jumps over 500 points")], reply([
        {"text": "According to Pub, Sensex jumped over 800 points.", "evidence_ids": ["news-1"]}
    ]))
    r = svc.explain_claim(CLAIM, 5)
    assert r.status == "insufficient_evidence"
    assert r.dropped_statements == 1


def test_number_that_comes_from_the_cited_article_is_allowed(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1", "Sensex jumps over 500 points")], reply([
        {"text": "According to Pub, Sensex jumped over 500 points.", "evidence_ids": ["news-1"]}
    ]))
    r = svc.explain_claim(CLAIM, 5)
    assert r.status == "grounded"
    assert r.dropped_statements == 0


def test_number_that_comes_from_the_claim_is_allowed(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1", "Sensex rises")], reply([
        {"text": "The claim says 500 points, but Pub reports a rise without a figure.", "evidence_ids": ["news-1"]}
    ]))
    assert svc.explain_claim(CLAIM, 5).status == "grounded"


def test_differences_are_added_by_code_when_numbers_differ(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1", "Jupiter Wagons shares rally 8% on order")], reply([
        {"text": "The claim says 20%, but Pub reports 8%.", "evidence_ids": ["news-1"]}
    ]))
    r = svc.explain_claim("Jupiter Wagons shares rally 20% on order", 5)
    assert r.status == "grounded"
    assert any("20%" in d for d in r.differences)


def test_differences_flag_opposite_direction(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1", "Sensex, Nifty rise in early trade")], reply([
        {"text": "Pub reports that they rose.", "evidence_ids": ["news-1"]}
    ]))
    r = svc.explain_claim("Sensex and Nifty fall early in trade", 5)
    assert any("fall" in d and "rise" in d for d in r.differences)


def test_matching_claim_has_no_differences(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1", "Sensex jumps 500 points after Fed holds rates")], reply([
        {"text": "Pub reports a jump of 500 points.", "evidence_ids": ["news-1"]}
    ]))
    assert svc.explain_claim(CLAIM, 5).differences == []


def test_refusal_has_no_differences(monkeypatch, make_article):
    install(monkeypatch, [make_article("news-1")], reply([], "Nothing addresses the claim."))
    assert svc.explain_claim(CLAIM, 5).differences == []