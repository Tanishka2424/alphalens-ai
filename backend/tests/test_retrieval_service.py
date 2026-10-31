from app.services.retrieval_service import RetrievalService


class _Vec:
    def __init__(self, v):
        self._v = v

    def tolist(self):
        return self._v


class FakeEmbedder:
    def encode(self, texts):
        return _Vec([[0.0, 0.0]])


class FakeCollection:
    def __init__(self, rows):
        self.rows = rows
        self.last_n = None

    def query(self, query_embeddings, n_results):
        self.last_n = n_results
        rows = self.rows[:n_results]
        return {
            "ids": [[r["id"] for r in rows]],
            "documents": [[r["doc"] for r in rows]],
            "metadatas": [[r["meta"] for r in rows]],
            "distances": [[r["dist"] for r in rows]],
        }


def row(rid, title, dist, doc=None, **meta):
    return {"id": rid, "doc": doc or title, "dist": dist, "meta": {"title": title, **meta}}


def service(rows):
    s = RetrievalService()
    s._embedder = FakeEmbedder()
    s._collection = FakeCollection(rows)
    return s


def test_exact_self_match_is_excluded_even_with_different_punctuation():
    s = service([row("1", "Earnings season is here again! Top stocks", 0.30), row("2", "Other", 0.40)])
    r = s.find_similar("Earnings season is here again Top stocks", 5)
    assert [x.title for x in r.results] == ["Other"]
    assert r.excluded_duplicates == 1


def test_near_duplicate_by_score_is_excluded():
    s = service([row("1", "Almost same", 0.02), row("2", "Different", 0.40)])
    r = s.find_similar("Some query text here", 5)
    assert [x.title for x in r.results] == ["Different"]
    assert r.excluded_duplicates == 1


def test_item_below_the_duplicate_threshold_is_kept():
    r = service([row("1", "Close but not a copy", 0.05)]).find_similar("Some query text here", 5)
    assert len(r.results) == 1
    assert r.results[0].similarity_score == 0.95


def test_returns_at_most_top_k_and_asks_for_extra_candidates():
    s = service([row(str(i), f"Title {i}", 0.3 + i / 100) for i in range(10)])
    r = s.find_similar("Some query text here", 3)
    assert len(r.results) == 3
    assert s._collection.last_n == 8  # top_k + 5


def test_duplicates_do_not_reduce_the_number_of_results():
    rows = [row("d", "Copy", 0.01)] + [row(str(i), f"Title {i}", 0.4) for i in range(4)]
    r = service(rows).find_similar("Some query text here", 3)
    assert len(r.results) == 3
    assert r.excluded_duplicates == 1


def test_provenance_fields_are_passed_through():
    s = service([row("news-1", "Headline", 0.2, source="The Times of India",
                     url="https://example.com/a", published_at="2026-10-29T04:55:13Z")])
    a = s.find_similar("Some query text here", 5).results[0]
    assert a.article_id == "news-1"
    assert a.source == "The Times of India"
    assert a.url == "https://example.com/a"
    assert a.published_at == "2026-10-29T04:55:13Z"


def test_missing_metadata_becomes_none_and_is_never_invented():
    a = service([row("7248", "Old headline", 0.3)]).find_similar("Some query text here", 5).results[0]
    assert a.source is None and a.url is None and a.published_at is None


def test_similarity_is_clamped_at_zero():
    a = service([row("1", "Far away", 1.2)]).find_similar("Some query text here", 5).results[0]
    assert a.similarity_score == 0.0


def test_snippet_is_cut_to_300_characters():
    a = service([row("1", "T", 0.3, doc="x" * 500)]).find_similar("Some query text here", 5).results[0]
    assert len(a.snippet) == 300


def test_empty_collection_result_returns_empty_list():
    r = service([]).find_similar("Some query text here", 5)
    assert r.results == [] and r.excluded_duplicates == 0