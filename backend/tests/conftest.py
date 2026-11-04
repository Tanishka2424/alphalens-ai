import pytest

from app.schemas.retrieval import SimilarArticleResult


@pytest.fixture
def make_article():
    def _make(article_id="a1", title="Title", source="Pub",
              published_at="2026-10-29T00:00:00Z", sim=0.8, snippet=None):
        return SimilarArticleResult(
            article_id=article_id, title=title, snippet=snippet or title,
            source=source, url=None, published_at=published_at, similarity_score=sim,
        )
    return _make